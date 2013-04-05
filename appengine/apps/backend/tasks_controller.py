# -*- coding: utf-8 -*-
import logging
import pickle
import hashlib

from decimal import Decimal

from google.appengine.ext import db

from webapp2 import RequestHandler, uri_for as url_for

from config import config
from models import Block, BitcoinAddress, ForwardTx, SystemConfig

from utils import create_blobstore_file, read_blobstore_file
from google.appengine.api import taskqueue

from bitcoin_helper import generate_forward_transaction, decrypt_private
from electrum.bitcoin import address_from_private_key

from bitcoinrpc import connection
from bitcoinrpc.authproxy import JSONRPCException

class TasksController(RequestHandler):

  def forward_txs(self, **kwargs):

    for ftx in ForwardTx.all().filter('forwarded =', 'N'):
      src_add  = ftx.address.address
      src_priv = decrypt_private(ftx.address.private_key, ftx.user.password)
      
      # Por si justo el usuario cambio el password cuando estaba por forwardearse un tx
      if src_add != address_from_private_key(src_priv):
        ftx.forwarded = 'KE'
        ftx.put()
        continue

      dst_add  = config['my']['cold_wallet']
      tx_hash  = ftx.tx
      index    = ftx.index
      amount   = ftx.value
      
      error, rawtx = generate_forward_transaction(src_add, src_priv, dst_add, tx_hash, amount, index)
      if error:
        logging.error('generate_forward_transaction error')

      access = connection.get_proxy( SystemConfig.get_by_key_name('system-config').remote_rpc )
      
      try:
        access.pushtx(rawtx)
      except JSONRPCException as err:
        logging.error('forward_tx error: %s' % err.error)
      else:
        ftx.forwarded = 'Y'
        ftx.put()

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

      forward_tx = []
      addys = BitcoinAddress.get_by_key_name(out_address)
      for i in range(0, len(addys)):

        if not addys[i]:
          continue

        # El nombre de la key es unico
        # Se hace con el hash256(tx+address+index) por corren al mismo tiempo

        key_name = hashlib.sha256('%s%s%s' % (tx['txid'],out_address[i],out_index[i]) ).digest().encode('hex')

        fwdtx = ForwardTx(key_name = key_name,
                          tx       = tx['txid'], 
                          address  = addys[i], 
                          value    = out_values[i], 
                          index    = out_index[i],
                          user     = BitcoinAddress.user.get_value_for_datastore(addys[i]))

        forward_tx.append(fwdtx)

      # Guardamos el forward
      if len(forward_tx):
        db.put(forward_tx)

    block.processed = 'Y'
    block.put()

    taskqueue.add(url=url_for('task-forward-txs'))

  def import_block(self, **kwargs):

    access = connection.get_proxy( SystemConfig.get_by_key_name('system-config').remote_rpc )

    block_num = Block.all(keys_only=True).order('-number').get().id()+1

    # Nos fijamos si el bloque que tengo que importar ya esta en el chain    
    try:
      last_block = access.getblockcount()
      if last_block < block_num:
        return

      block_info = access.getblk(block_num)
    except JSONRPCException as err:
      logging.error('import_block error: %s' % err.error)

    @db.transactional(xg=True)
    def _tx():

      file_key = create_blobstore_file(pickle.dumps(block_info).encode('zlib'), 'block-%s' % block_num)
      if not file_key:
        logging.error('import_block: Error creating file in blobstore')
        abort(500)

      block_key = db.Key.from_path('Block', block_num)

      block = Block(key    = block_key, 
                    hash   = block_info['hash'], 
                    number = block_num,
                    data   = file_key, 
                    txs    = len(block_info['tx']))

      taskqueue.add(url=url_for('task-process-block'), transactional=True)
      db.put(block)

    _tx()


