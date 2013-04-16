# -*- coding: utf-8 -*-
import logging
import pickle
import hashlib
import time

from datetime import datetime
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import RequestHandler, uri_for as url_for

from config import config
from models import PriceBar, Block, BitcoinAddress, ForwardTx, Operation, get_system_config

from utils import create_blobstore_file, read_blobstore_file, remove_blobstore_file
from google.appengine.api import taskqueue

from bitcoin_helper import generate_forward_transaction, decrypt_private
from electrum.bitcoin import address_from_private_key

from bitcoinrpc import connection
from bitcoinrpc.authproxy import JSONRPCException

from exchanger import get_account_balance, get_ohlc

from mail.mailer import send_mail

class TasksController(RequestHandler):

  def build_1h_bar(self, **kwargs):
    
    # Traemos la ultima barra de hora
    last_bar = PriceBar.all().filter('bar_interval =', PriceBar.H1) \
                             .order('-bar_time') \
                             .get()
    
    # Tenemos que armar la siguiente?
    have_to_build, new_bar_time  = last_bar.next_bar()
    if not have_to_build:
      return

    # Limites de fechas para calculo de la nueva barra
    from_ts = datetime.fromtimestamp(new_bar_time * last_bar.bar_interval)
    to_ts   = datetime.fromtimestamp((new_bar_time+1) * last_bar.bar_interval)

    ohlc = get_ohlc(from_ts, to_ts, last_bar.close)

    # Aramamos el próximo bar
    next_bar = PriceBar(open         = ohlc['open'],
                        high         = ohlc['high'],
                        low          = ohlc['low'],
                        close        = ohlc['close'],
                        volume       = ohlc['volume'], 
                        bar_time     = new_bar_time,
                        bar_interval = last_bar.bar_interval)

    next_bar.put()
        

  def match_orders(self, **kwargs):
    
    sconfig = get_system_config()
    if not sconfig.can_trade():
      return

    trader = Trader()
    tmp = trader.match_orders()

  def apply_operations(self, **kwargs):
    
    trader = Trader()
    for op in Operation.all().filter('status =', Operation.OPERATION_PENDING):
      tmp = trader.apply_operation(op.key())

  def update_btc_balance(self, **kwargs):
  
    sconfig = get_system_config()
    
    access = connection.get_proxy( sconfig.remote_rpc )
    current_block = access.getblockcount()

    trader = Trader()
    for ftx in ForwardTx.all().filter('forwarded =', 'Y'):

      # Esta confirmada la transaccion original?
      if current_block > ftx.in_block + int(sconfig.confirmations):
        trader.add_btc_balance(str(ftx.key()))

  def forward_txs(self, **kwargs):
  
    sconf = get_system_config()
    if not sconf.can_forward():
      logging.warning('forward_txs disabled')
      return

    access = connection.get_proxy( sconf.remote_rpc )

    for ftx in ForwardTx.all().filter('forwarded =', 'N'):
      src_add  = ftx.address.address
      src_priv = decrypt_private(ftx.address.private_key)
      
      dst_add  = config['my']['cold_wallet']
      tx_hash  = ftx.tx
      index    = int(ftx.index)
      amount   = ftx.value
      
      ok, tx = generate_forward_transaction(src_add, src_priv, dst_add, tx_hash, amount, index)
      if not ok:
        logging.error('forward_tx error: generate_forward_transaction %s' % tx)
        continue

      # Nota: aca puede ser el unico error donde queda en un estado incosistente pero arreglable
      # manualmente.
      # Caso 1: la tx se transmite => pero da timeout por network
      #         * Da exception (Exception o JSONRPCException) -> no se actualiza la como enviada
      #         * No se le actualiza el balance al usuario
      #         * Pero la transaccion esta segura en la billetera offline
      #         * Queda una ForwardTx dando error, por que ese input ya se "gasto"
      #
      # Caso 2: la tx de transmite => pero el salvado del ftx da exception
      #         * Da exception (Exception o TransactionFailedError) -> no se actualiza la como enviada
      #         * No se le actualiza el balance al usuario
      #         * Pero la transaccion esta segura en la billetera offline
      #         * Queda una ForwardTx dando error, por que ese input ya se "gasto"
      #
      # Quizas lo que hay que hacer simplemente es manejar bien el error de "ya gastada" y marcarla como enviada.
      # Lo unico que se perderia en ese momento es el rawtx, dado que eso se guarda posteriori.
      # Tambien se puede encuestar por esa transaccion ID y guardarlo (esta es la mejor)

      rawtx = tx.as_dict()['hex']
      try:
        access.pushtx(rawtx)
      except JSONRPCException as err:
        logging.error('forward_tx error: JSONRPCException %s' % err.error)
        return
      except Exception as ex:
        logging.error('forward_tx error: Unknown Error %s %s' % (str(type(ex)),str(ex)))
        return

      try:
        ftx.tx_fw  = tx.hash()
        ftx.tx_raw = rawtx
        ftx.forwarded  = 'Y'
        ftx.put()
      except TransactionFailedError as wf:
        logging.error('forward_tx error: TransactionFailedError tx_cold:%s' % tx.hash())
      except Exception as ex:
        logging.error('forward_tx error: Unknown Error %s %s %s' % ( str(type(ex)), str(ex), tx.hash() ) )


  def process_block(self, **kwargs):

    block = Block.all().filter('processed =', 'N').order('number').get()
    
    if not block:
      logging.info('No blocks to process')
      return

    block_info = pickle.loads( read_blobstore_file(block.data.key()).decode('zlib') )

    # Por cada transaccion
    for tx in block_info['tx']:
  
      out_address = []
      out_values  = []
      out_index   = []

      # Por cada salida guardamos la direccion destino y el valor
      for out in tx['outs']:
        
        # Posible que venga sin address
        if not out.has_key('n') or \
           not out.has_key('value') or \
           not out.has_key('scriptPubKey') or \
           not out['scriptPubKey'].has_key('addresses'):

           logging.warning('process_block strange transaction! %s' % tx['txid'])
           continue

        out_address.append(out['scriptPubKey']['addresses'][0])
        out_values.append(out['value'])
        out_index.append(out['n'])

      # Vemos si alguna salida de la transaccion es para una direccion de
      # alguno de nuestros usuarios, en tal caso, creamos una pedido de forward a 
      # la billetera offline

      forward_tx   = []
      forward_keys = []
      addys = BitcoinAddress.get_by_key_name(out_address)
      for i in range(0, len(addys)):

        if not addys[i]:
          continue

        # El nombre de la key es unico
        # Se hace con el hash256(tx+address+index) por corren al mismo tiempo

        key_name = hashlib.sha256('%s%s%s' % (tx['txid'],out_address[i],out_index[i]) ).digest().encode('hex')
        forward_keys.append(key_name)

        fwdtx = ForwardTx(key_name = key_name,
                          tx       = tx['txid'], 
                          in_block = block.number,
                          address  = addys[i], 
                          value    = out_values[i], 
                          index    = str(out_index[i]),
                          user     = BitcoinAddress.user.get_value_for_datastore(addys[i]))

        forward_tx.append(fwdtx)

      # Guardamos las forward
      if len(forward_tx):

        @db.transactional(xg=True)
        def _tx():
          
          # Solo las que no estan en el datastore
          in_db = ForwardTx.get_by_key_name(forward_keys)
          
          filtered = []
          for x,y in zip(forward_tx, in_db):
            if not y: filtered.append(x)
          
          if(len(filtered)):
            db.put(filtered)

        _tx()
        

    block.processed = 'Y'
    block.put()

  def import_block(self, **kwargs):

    sconf = get_system_config()
    if not sconf.can_import():
      logging.warning('import_block disable')
      return

    access = connection.get_proxy( sconf.remote_rpc )

    block_num = Block.all().order('-number').get().number+1

    # Nos fijamos si el bloque que tengo que importar ya esta en el chain    
    try:
      last_block = access.getblockcount() - int(sconf.import_delay)
      if last_block < block_num:
        return

      block_info = access.getblk(block_num)
    except JSONRPCException as err:
      logging.error('import_block error: %s' % err.error)

    file_key = create_blobstore_file(pickle.dumps(block_info).encode('zlib'), 'block-%s' % block_num)
    if not file_key:
      logging.error('import_block: Error creating file in blobstore')
      return

    @db.transactional
    def _tx():

      key_name = 'Block%d' % block_num
      block = Block.get_by_key_name(key_name)
      if block:
        logging.warning('import_block: The block already exists')
        remove_blobstore_file(file_key)
        return

      block = Block(key_name = key_name, 
                    hash     = block_info['hash'],
                    number   = block_num,
                    data     = file_key,
                    txs      = len(block_info['tx']))

      db.put(block)

    _tx()

  def send_mail(self, **kwargs):
    self.request.charset = 'utf-8'
    params = self.request.POST.mixed()
    mail = self.request.POST.get('mail')
    send_mail(mail, params)
    return
