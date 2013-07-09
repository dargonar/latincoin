# -*- coding: utf-8 -*-
import logging

from decimal import Decimal
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import memcache

from models import PriceBar, TradeOrder, Operation, Account, AccountOperation, Dummy, ForwardTx, BankAccount, AccountBalance

from bitcoin_helper import zero_btc

from mail.mailer import enqueue_mail

def on_operation_applied(last_price, last_amount):
  memcache.set('last_price', last_price)

  ticker = get_ticker()
  
  ticker['high']    = max(ticker['high'], last_price)
  ticker['low']     = min(ticker['low'],  last_price)
  ticker['volume'] += last_amount

  memcache.replace('ticker', ticker)

def get_last_price():
  last_price = memcache.get('last_price')
  if last_price:
    return last_price

  last_price = Decimal('0')

  last_op = Operation.all().filter('-created_at').get()
  if last_op:
    last_price = last_op.ppc

  memcache.set('last_price', last_price)
  return last_price

def get_ticker():
  ticker = memcache.get('ticker')
  if ticker:
    return ticker

  high = low = volume = Decimal('0')
  
  query = PriceBar.all()
  query = query.filter('bar_interval =', PriceBar.H1)
  query = query.order('-bar_time')

  count = 0
  for bar in query:
    
    high    = max(bar.high, high)
    low     = min(bar.low, low)
    volume += bar.volume

    count = count + 1
    if count > 23:
      break

  ticker = {'high':high, 'low':low, 'volume':volume}
  memcache.set('ticker', ticker)
  return ticker

def get_ohlc(from_ts, to_ts, prev_close=0):
  
  _open = high = low = close = None ; volume = 0
  for o in Operation.all().filter('created_at >=', from_ts).filter('created_at <', to_ts):
    price  = o.ppc
    vol    = o.traded_btc

    if not _open : _open = prev_close
    if not high or price > high: high = price
    if not low or price < low: low = price      
    close = price
    
    volume = volume + vol

  # Si no habia nada en el intervalo ponemos ohlc en prev_close
  if _open is None:
    _open = high = low = close = prev_close

  return {'open':_open, 'high':high, 'low':low, 'close':close, 'volume':volume}


def get_account_balance(account):

  # TODO: assert input
  assert(account is not None), u'Account invalida'
  if isinstance(account, basestring):
    account = db.Key(account)

  # NOTA: El query por ancestor se hace dado que esta función se utiliza dentro de una 
  # transacción y no puede haber mas de cinco (5) entity groups dentro de la misma  
  balances = AccountBalance.all().ancestor(account).filter('account =', account).fetch(100)
  
  assert(balances is not None), u'No tiene balance'
  assert(len(balances) >= 2), u'No tiene todos los balances %s => %s' % (len(balances),account.key())
  assert(len(balances) == 2), u'Tiene muchos balances! (%d)' % len(balances)

  balance = {}
  for b in balances:
    balance[b.currency] = b

  assert('ARS' in balance), u'No tiene balance en ARS'
  assert('BTC' in balance), u'No tiene balance en BTC'

  return balance

def add_currency_balance(user, amount, bank_account=None, currency='ARS'):

  assert(isinstance(user, basestring) and len(user) > 0 ), u'Key de usuario inválida'  
  assert(isinstance(amount, Decimal) and amount > Decimal('0')), u'Cantidad inválida'
  assert(isinstance(currency, basestring) and currency in ['ARS','BTC']), u'Moneda inválida'

  @db.transactional(xg=False)
  def _tx():
    
    balance = get_account_balance(user)
    balance[currency].amount += Decimal(amount)
    
    account = Account.get(user)
    bank_account_entity = None
    if bank_account and len(bank_account)>0:
      bank_account_entity = BankAccount.get(bank_account) 
      
    add_cur_op = AccountOperation( parent         = account, 
                                   operation_type = AccountOperation.MONEY_IN, 
                                   account        = account,
                                   amount         = Decimal(amount),
                                   currency       = currency,
                                   bank_account   = bank_account_entity,
                                   state          = AccountOperation.STATE_DONE)

    db.put([balance[currency], add_cur_op])
    
    enqueue_mail('deposit_received', {'user_key':user, 'ao_key':str(add_cur_op.key())}, tx=True)
    
    return [add_cur_op, u'ok']
  return _tx()

def add_btc_balance(ftx_key):

  # TODO: assert input
  assert(isinstance(ftx_key, basestring) and len(ftx_key) > 0 ), u'Key de forwardtx inválida'
  @db.transactional(xg=True)
  def _tx():

    ftx = ForwardTx.get(ftx_key)
    if not ftx.is_forwarded():
      return

    ftx.set_credited()

    balance = get_account_balance(ftx.user)
    balance['BTC'].amount += ftx.value

    add_btc_op = AccountOperation( parent         = ftx.user, 
                                   operation_type = AccountOperation.MONEY_IN, 
                                   account        = ftx.user,
                                   amount         = ftx.value,
                                   currency       = 'BTC',
                                   bt_tx_id       = ftx.tx,
                                   state          = AccountOperation.STATE_DONE)

    db.put([ftx, balance['BTC'], add_btc_op])
    
    # Notificamos por mail
    user_key = str(ForwardTx.user.get_value_for_datastore(ftx))
    enqueue_mail('deposit_received', {'user_key':user_key, 'ao_key':str(add_btc_op.key())}, tx=True)

    return True

  _tx()


def cancel_withdraw_order(order_key):
  
  # TODO: assert input
  assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

  @db.transactional(xg=True)
  def _tx():

    # Tiene que ser una operacion pendiente y de retiro
    ao = AccountOperation.get(db.Key(order_key))
    if not ao.is_pending() or not ao.is_money_out():
      return [False, u'No se puede cancelar la orden']
  
    # Cambiamos el estado a cancelada
    ao.set_cancel()

    balance = get_account_balance(ao.account)
    balance[ao.currency].amount += (-ao.amount)

    db.put([ao, balance[ao.currency]])

    # Notificamos por mail
    user_key = str(AccountOperation.account.get_value_for_datastore(ao))
    enqueue_mail('cancel_withdraw_request', {'user_key':user_key, 'ao_key':str(ao.key())}, tx=True)

    return [ao, u'ok']

  return _tx()

def accept_withdraw_order(order_key):
  
  # TODO: assert input
  assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

  @db.transactional(xg=True)
  def _tx():

    # Tiene que ser una operacion pendiente y de retiro
    ao = AccountOperation.get(db.Key(order_key))
    if not ao.is_pending() or not ao.is_money_out():
      return [False, u'No se puede aceptar la orden']
  
    # Cambiamos el estado a cancelada
    ao.set_accepted()

    db.put(ao)

    # Notificamos por mail
    user_key = str(AccountOperation.account.get_value_for_datastore(ao))
    enqueue_mail('accept_withdraw_request', {'user_key':user_key, 'ao_key':str(ao.key())}, tx=True)

    return [ao, u'ok']

  return _tx()

def done_withdraw_order(order_key):
  
  # TODO: assert input
  assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

  @db.transactional(xg=True)
  def _tx():

    # Tiene que ser una operacion pendiente y de retiro
    ao = AccountOperation.get(db.Key(order_key))
    if not ao.is_accepted() or not ao.is_money_out():
      return [False, u'No se puede finalizar la orden']
  
    # Cambiamos el estado a cancelada
    ao.set_done()

    db.put(ao)

    # Notificamos por mail
    user_key = str(AccountOperation.account.get_value_for_datastore(ao))
    enqueue_mail('done_withdraw_request', {'user_key':user_key, 'ao_key':str(ao.key())}, tx=True)

    return [ao, u'ok']

  return _tx()
  

def _add_withdraw_order(user, currency, amount, bank_account=None, btc_address=None):

  # TODO: assert input
  assert(isinstance(user, basestring) and len(user) > 0 ), u'Key de usuario inválida'
  assert(isinstance(currency, basestring) and currency in ['ARS','BTC']), u'Moneda inválida'
  assert(isinstance(amount, Decimal) and amount > Decimal('0')), u'Cantidad inválida'
  
  
  @db.transactional(xg=True)
  def _tx():
    
    # Checkeamos el balance disponible en la moneda correspondiente al retiro
    balance = get_account_balance(user)
    if amount > balance[currency].available():
      return [None, u'No tiene suficiente balance para realizar ese retiro']

    # Generamos una operacion de retiro pendiente
    # Esta puede ser cancelada mientras este en pendiente, si pasa a aceptada ya no
    user_key = db.Key(user)
    withdraw_op = AccountOperation(parent         = user_key, 
                                   operation_type = AccountOperation.MONEY_OUT, 
                                   account        = user_key,
                                   amount         = amount,
                                   currency       = currency,
                                   state          = AccountOperation.STATE_PENDING, 
                                   bank_account   = bank_account,
                                   address        = btc_address)
          
    balance[currency].amount -= amount
    
    db.put([balance[currency], withdraw_op])

    # Notificamos por mail
    enqueue_mail('withdraw_request', {'user_key':str(user_key), 'ao_key':str(withdraw_op.key())}, tx=True)

    return [withdraw_op, u'ok']

  return _tx()

# validamos el cbu
def add_withdraw_currency_order(user, amount, bank_account_key, currency='ARS'):
  assert(isinstance(bank_account_key, basestring) and len(bank_account_key) > 0 ), u'CBU inválido'
  return _add_withdraw_order(user, currency, amount, bank_account=BankAccount.get(db.Key(bank_account_key)) )
  
# validamos que la direccion sea valida
def add_withdraw_btc_order(user, amount, address):
  assert(isinstance(address, basestring) and len(address) > 0 ), u'Direccion no valida'
  return _add_withdraw_order(user, 'BTC', amount, btc_address=address)

# Elimina una orden de compra o venta
# Acomoda el balance del usuario dueño de esa orden
def cancel_order(order_key):

  # TODO: assert input
  assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

  @db.transactional(xg=True)
  def _tx():

    order = TradeOrder.get(db.Key(order_key))

    # Solo cancelamos ordenes que esten ACTIVAS
    if order.status != TradeOrder.ORDER_ACTIVE:
      return False

    order.status = TradeOrder.ORDER_CANCELED

    user_balance = get_account_balance(order.user)

    if order.bid_ask == TradeOrder.BID_ORDER:
      balance = user_balance['ARS']
      balance.amount_comp -= order.amount*order.ppc
    else:
      balance = user_balance['BTC']
      balance.amount_comp -= order.amount

    db.put([order, balance])
    return True

  return _tx()

# Acomoda la historia de operaciones sobre las cuentas involucradas en una Operation
# 2 AccountOperation + arreglo de balance para el comprador
# 2 AccountOperation + arreglo de balance para el vendedor
# 2 AccountOperation + arreglo de balance para el x-changer

def apply_operation(operation_key):

  # TODO: assert input
  assert(isinstance(operation_key, basestring) and len(operation_key) > 0 ), u'Key de operación invalida'

  @db.transactional(xg=True)
  def _tx():

    # Traemos la operacion que resulto del match de dos TradeOrders
    op = Operation.get(db.Key(operation_key))
    
    # Si ya se habia aplicado no la aplico nuevamente
    if not op.is_pending():
      return op

    seller_rate = op.seller.commission_rate
    buyer_rate  = op.buyer.commission_rate

    assert(seller_rate > Decimal('0')), u'Comisión inválida'
    assert(buyer_rate  > Decimal('0')), u'Comisión inválida'

    # Traemos la cuenta del xchanger
    xchg = Account.get_by_key_name('xchg')

    # Calculamos los fees del xchanger
    xchg_curr_fee = op.traded_currency*seller_rate
    xchg_btc_fee  = op.traded_btc*buyer_rate

    sellers_curr = (op.traded_currency - xchg_curr_fee)
    buyers_btc   = (op.traded_btc - xchg_btc_fee)

    seller_balance = get_account_balance(op.seller)
    buyer_balance  = get_account_balance(op.buyer)
    xchg_balance   = get_account_balance(xchg)

    # Actualizamos los balances del vendedor
    seller_balance['ARS'].amount      += sellers_curr
    seller_balance['BTC'].amount      -= op.traded_btc
    seller_balance['BTC'].amount_comp -= op.traded_btc

    # Actualizamos los balances del comprador
    buyer_balance['BTC'].amount      += buyers_btc

    # DIFICIL DE VER: el balance comprometido del comprador disminuye
    # en funcion de lo que se transo x lo que el estaba dispuesto a pagar, no 
    # por el ppc del vendedor.

    buyer_balance['ARS'].amount      -= op.traded_currency
    buyer_balance['ARS'].amount_comp -= (op.traded_btc*op.purchase_order.ppc)

    # Actualizamos los balances del xchg
    xchg_balance['BTC'].amount       += xchg_btc_fee
    xchg_balance['ARS'].amount       += xchg_curr_fee

    # Cremos los AccountOperation para el vendedor
    seller_op1 = AccountOperation(parent         = op.seller, 
                                  operation_type = AccountOperation.BTC_SELL, 
                                  account        = op.seller,
                                  amount         = sellers_curr, 
                                  ppc            = op.ppc,
                                  commission_rate= seller_rate,
                                  trade_operation= op,
                                  currency       = 'ARS',
                                  state          = AccountOperation.STATE_DONE)

    seller_op2 = AccountOperation(parent         = op.seller, 
                                  operation_type = AccountOperation.BTC_SELL, 
                                  account        = op.seller,
                                  amount         = op.traded_btc,
                                  ppc            = op.ppc,
                                  #commission_rate= None,
                                  trade_operation= op,
                                  currency       = 'BTC',
                                  state          = AccountOperation.STATE_DONE)

    # Cremos los AccountOperation para el comprador
    buyer_op1 = AccountOperation( parent         = op.buyer, 
                                  operation_type = AccountOperation.BTC_BUY, 
                                  account        = op.buyer,
                                  amount         = buyers_btc, 
                                  ppc            = op.ppc,
                                  commission_rate= buyer_rate,
                                  trade_operation= op,
                                  currency       = 'BTC',
                                  state          = AccountOperation.STATE_DONE)

    buyer_op2 = AccountOperation( parent         = op.buyer, 
                                  operation_type = AccountOperation.BTC_BUY, 
                                  account        = op.buyer,
                                  amount         = op.traded_currency,
                                  ppc            = op.ppc,
                                  #commission_rate= None,
                                  trade_operation= op,
                                  currency       = 'ARS',
                                  state          = AccountOperation.STATE_DONE)
    
    # Cremos los AccountOperation para el xchanger
    xchg_op1 = AccountOperation(  parent         = xchg, 
                                  operation_type = AccountOperation.XCHG_FEE, 
                                  account        = xchg,
                                  amount         = xchg_btc_fee, 
                                  #ppc            = None,
                                  #commission_rate= None,
                                  trade_operation= op,
                                  currency       = 'BTC',
                                  state          = AccountOperation.STATE_DONE)

    xchg_op2 = AccountOperation(  parent         = xchg, 
                                  operation_type = AccountOperation.XCHG_FEE, 
                                  account        = xchg,
                                  amount         = xchg_curr_fee,
                                  #ppc            = None,
                                  #commission_rate= None,
                                  trade_operation= op,
                                  currency       = 'ARS',
                                  state          = AccountOperation.STATE_DONE)

    op.status = Operation.OPERATION_DONE
    #logging.info('  OPERATION_DONE')

    to_save =  [op]

    # Grabamos el balance nuevo del comprador si la compra NO ES una market order
    # Ya que lo hicimos previamente al momento de generar la operacion
    if op.purchase_order.order_type != TradeOrder.MARKET_ORDER:
      to_save += [buyer_balance['ARS'], buyer_balance['BTC']]

    to_save += [buyer_op1, buyer_op2]
    
    # Grabamos el balance nuevo del vendedor si la compra NO ES una market order
    # Ya que lo hicimos previamente al momento de generar la operacion
    if op.sale_order.order_type != TradeOrder.MARKET_ORDER:
      to_save += [seller_balance['ARS'], seller_balance['BTC']]

    to_save += [seller_op1, seller_op2]
    
    to_save += [xchg_balance['ARS'], xchg_balance['BTC']]
    to_save += [xchg_op1, xchg_op2]

    db.put(to_save)

    return op

  last_op = _tx()
  on_operation_applied(last_op.ppc, last_op.traded_btc)
  return last_op


# Intenta matchear la mejor BID con la mejor ASK
# Si hay posibilidades de trade, genera una nueva Operation 
# y acomoda las TradeOrders
def match_orders():

  parent = Dummy.get_by_key_name('trade_orders')

  @db.transactional(xg=True)
  def _tx():

    # Tomamos las bids ordenadas (la mas alta primero)
    bids = TradeOrder.all() \
          .ancestor(parent) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.BID_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE) \
          .order('-ppc_int') \
          .run()


    # Tomamos las asks ordenadas (la mas baja primero)
    asks = TradeOrder.all() \
          .ancestor(parent) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.ASK_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE) \
          .order('ppc_int') \
          .run()

    def get_next(q):
      res = None
      try:
        res = q.next()
      except:
        pass

      return res

    modified_orders = []
    new_operations  = []

    # Traemos las primeras ordenes
    best_bid = get_next(bids)
    if best_bid:
      best_ask = get_next(asks)

    # Iteramos mientras tengamos ask y bid
    while best_bid and best_ask:

      # Nos fijamos si hay match
      if best_bid.ppc < best_ask.ppc:
        break

      # Hay posibilidad de operacion, obtenemos los valores para armar la operacion
      amount = min(best_bid.amount, best_ask.amount)
      ppc    = best_ask.ppc

      # Se crea una nueva operation Operation.OPERATION_PENDING
      # Luego, cuando se generen los 6 AccountOperations y la actualizacion de
      # los balances se pasa a OPERATION_DONE
      
      op = Operation(parent=Dummy.get_by_key_name('operations'),
                     purchase_order    = best_bid,
                     sale_order        = best_ask,
                     traded_btc        = amount,
                     traded_currency   = amount*ppc,
                     ppc               = ppc,
                     currency          = 'ARS',
                     seller            = TradeOrder.user.get_value_for_datastore(best_ask),
                     buyer             = TradeOrder.user.get_value_for_datastore(best_bid),
                     status            = Operation.OPERATION_PENDING,
                     type              = Operation.OPERATION_BUY if best_bid.created_at > best_ask.created_at else Operation.OPERATION_SELL
            );

      # Guardamos la operacion para salvar posteriormente
      new_operations.append(op)
    
      # Acomodamos los valores de los TradeOrders 
      # y los marcamos como completos en caso que den 0

      best_bid.amount -= amount
      if zero_btc(best_bid.amount):
        best_bid.status = TradeOrder.ORDER_COMPLETED
        modified_orders.append(best_bid)

        best_bid = get_next(bids)
      
      best_ask.amount -= amount
      if zero_btc(best_ask.amount):
        best_ask.status = TradeOrder.ORDER_COMPLETED
        modified_orders.append(best_ask)

        best_ask = get_next(asks)

    # Grabamos si hay algo para grabar
    if len(new_operations):
      db.put(new_operations + modified_orders)

    return new_operations

  return _tx()

def add_market_trade(user_key, bid_ask, amount_wanted):

  # TODO: assert input
  assert(isinstance(user_key, basestring) and len(user_key) > 0 ), u'Key de usuario invalida'
  assert(isinstance(bid_ask, basestring) and bid_ask in [TradeOrder.ASK_ORDER, TradeOrder.BID_ORDER]), u'Tipo de orden invalida'
  assert(isinstance(amount_wanted, Decimal) and amount_wanted > Decimal('0') ), u'Cantidad invalida'

  parent_to = Dummy.get_by_key_name('trade_orders')
  parent_op = Dummy.get_by_key_name('operations')
  

  @db.transactional(xg=True)
  def _tx():

    amount   = amount_wanted

    user    = Account.get(db.Key(user_key))
    balance = get_account_balance(user)  

    # Quiere vender mas de lo que tiene?
    if bid_ask == TradeOrder.ASK_ORDER and amount > balance['BTC'].available():
      return [None, u'No tiene esa cantidad disponible para vender (balance disponible %.5f)' % balance['BTC'].available()]

    to = TradeOrder(parent          = parent_to, 
                    user            = user,
                    original_amount = amount,
                    amount          = amount,
                    ppc             = Decimal('0'),
                    ppc_int         = 0,
                    currency        = 'ARS',
                    status          = TradeOrder.ORDER_COMPLETED,
                    bid_ask         = bid_ask,
                    order_type      = TradeOrder.MARKET_ORDER
                  )
    to.put()


    # Itermaos las ordenes de a batch 20 (default appstore)
    # Si la orden es un ASK (venta) : traemos las bids ordenadas
    # Si la orden es un BID (compra): traemos las ask ordenadas

    orders = TradeOrder.all() \
          .ancestor(parent_to) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.BID_ORDER if bid_ask == TradeOrder.ASK_ORDER else TradeOrder.ASK_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE) \
          .order('%sppc_int' % ('-' if bid_ask == TradeOrder.ASK_ORDER else ''  ))

    ops_list        = []
    order_list      = [] 
    total_currency  = Decimal('0')
    

    res             = [to, u'No se pude completar la orden']

    # Las iteramos y vamos viendo si "llenamos" la market order
    for order in orders:
      
      # Me fijo que no sea una orden mia
      if str(TradeOrder.user.get_value_for_datastore(order)) == user_key:
        continue

      op_amount = min(amount, order.amount)
      
      order.amount -= op_amount
      amount       -= op_amount

      # Nos comimos esta orden?
      if zero_btc(order.amount):
        order.status = TradeOrder.ORDER_COMPLETED

      traded_currency = op_amount*order.ppc
      total_currency += traded_currency

      if bid_ask == TradeOrder.BID_ORDER and balance['ARS'].available() < total_currency:
        res = [to, u'No tiene suficiente balance disponible para comprar esa cantidad']
        break

      # TradeOrder.user.get_value_for_datastore(order) para no hacer un query al datatore dentro de la 
      # transaccion.
      # http://stackoverflow.com/questions/5425618/entity-groups-referenceproperty-or-key-as-a-string
      op = Operation(parent            = parent_op,
                     sale_order        = to if bid_ask == TradeOrder.ASK_ORDER else order,
                     purchase_order    = to if bid_ask == TradeOrder.BID_ORDER else order,
                     traded_btc        = op_amount,
                     traded_currency   = traded_currency,
                     ppc               = order.ppc,
                     currency          = 'ARS',
                     seller            = user if bid_ask == TradeOrder.ASK_ORDER else TradeOrder.user.get_value_for_datastore(order),
                     buyer             = user if bid_ask == TradeOrder.BID_ORDER else TradeOrder.user.get_value_for_datastore(order),
                     type              = Operation.OPERATION_BUY if bid_ask == TradeOrder.BID_ORDER else Operation.OPERATION_SELL,
                     status            = Operation.OPERATION_PENDING
            );

      ops_list.append(op)
      order_list.append(order)

      # Se completo la orden, mandamos a guardar 
      # 1) las operaciones generadas
      # 2) las ordenes modificadas y la nueva orden creada
      # 3) el balance del usuario modificado
      if zero_btc(amount):
        
        to.ppc     = total_currency/amount_wanted
        to.ppc_int = int(to.ppc*Decimal('100'))

        to_save = [to]

        if bid_ask == TradeOrder.ASK_ORDER:
          balance['BTC'].amount -= to.amount
          balance['ARS'].amount += total_currency*(Decimal('1') - user.commission_rate)
        else:
          balance['BTC'].amount += to.amount*(Decimal('1') - user.commission_rate)
          balance['ARS'].amount -= total_currency

        
        to_save += [balance['ARS'],balance['BTC']]

        to_save += ops_list
        to_save += order_list
       
        db.put(to_save)
        res = [to, u'ok']

        break

    # Borramos el market order si lo habiamos creado
    if res[1] != u'ok':
       
      if res[0]:
        res[0].delete()

      res[0] = None

    return res

  return _tx()


# Agrega un limit order a la DB
# Checkea dentro de una transaccion el balance disponible
def add_limit_trade(user, bid_ask, amount, ppc):

  # TODO: assert input
  assert(isinstance(user, basestring) and len(user) > 0 ), u'Key de usuario invalida'
  assert(isinstance(bid_ask, basestring) and bid_ask in [TradeOrder.ASK_ORDER, TradeOrder.BID_ORDER]), u'Tipo de orden invalida'
  assert(isinstance(amount, Decimal) and amount > Decimal('0') ), u'Cantidad invalida'
  assert(isinstance(ppc, Decimal )and ppc > Decimal('0') ), u'PPC invalido'

  @db.transactional(xg=True)
  def _tx():

    # Verificamos si le da el balance disponible para meter la orden
    # El balance disponible es balance reale - balance comprometido en ordenes
    # Si quiere vender BTC, verificamos que tenga esa cantidad de bitcoins disponibles para vender
    # Si quiere comprar BTC, verificamos que tenga los ARS suficientes 
    # para el precio (ppc) al que los quiere comprar

    balance = get_account_balance(user)

    if bid_ask == TradeOrder.ASK_ORDER:
      if balance['BTC'].available() < amount:
        return [None, u'No tiene suficiente balance disponible en BTC (disponible %.8f) ' % balance['BTC'].available() ]
      else:
        balance['BTC'].amount_comp += amount
    
    else: #if bid_ask == TradeOrder.ASK_ORDER:
      if balance['ARS'].available() < amount * ppc:
        return [None, u'No tiene suficiente balance disponible en ARS']
      else:
        balance['ARS'].amount_comp += amount * ppc

    # Creamos la orden ya que el balance dio para que se pueda meter
    # y mandamos a guardar las dos cosas juntas.
    # Si el usuario modifico su balance de alguna manera (retiro, otra order, etc)
    # la transaccion se vuelve a ejecutar y si no da el balance no se mete.

    to = TradeOrder(parent = Dummy.get_by_key_name('trade_orders'), 
          user             = db.Key(user),
          original_amount  = amount,
          amount           = amount,
          ppc              = ppc,
          ppc_int          = int(ppc*100),
          currency         = 'ARS',
          status           = TradeOrder.ORDER_ACTIVE,
          bid_ask          = bid_ask,
          order_type       = TradeOrder.LIMIT_ORDER
        )

    balance = balance['BTC'] if bid_ask == TradeOrder.ASK_ORDER else balance['ARS']
    db.put([balance,to])
    return [to, u'ok']

  return _tx()
