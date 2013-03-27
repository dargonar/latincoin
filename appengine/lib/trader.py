# -*- coding: utf-8 -*-
from decimal import Decimal
from google.appengine.ext import db

from models import TradeOrder, Operation, Account, AccountOperation, Dummy
from account_functions import get_account_balance

class Trader:

  def cancel_widthdraw_order(self, order_key):
    
    # TODO: assert input
    assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

    @db.transactional(xg=True)
    def _tx():

      ao = AccountOperation.get(db.Key(order_key))
      if ao.status == AccountOperation.OPERATION_PENDING:
        return [None, u'No se puede cancelar la orden']

      ao.status = AccountOperation.OPERATION_CANCELED

      balance = get_account_balance(ao.account)
      balance[ao.currency].amount += (-ao.amount)

      db.put([ao, balance[ao.currency]])

      return [ao, u'ok']

    return _tx()


  def add_widthdraw_order(self, user, currency, amount):

    # TODO: assert input
    assert(isinstance(user, basestring) and len(user) > 0 ), u'Key de orden inválida'
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
                                     amount         = -amount,
                                     currency       = currency,
                                     state          = AccountOperation.STATE_PENDING)

      balance[currency].amount -= amount
      db.put([balance[currency], withdraw_op])

      return [withdraw_op, u'ok']

    return _tx()

  # Elimina una orden de compra o venta
  # Acomoda el balance del usuario dueño de esa orden
  def cancel_order(self, order_key):

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

  def apply_operation(self, operation_key):

    # TODO: assert input
    assert(isinstance(operation_key, basestring) and len(operation_key) > 0 ), u'Key de operación invalida'

    @db.transactional(xg=True)
    def _tx():

      # Traemos la operacion que resulto del match de dos TradeOrders
      op = Operation.get(db.Key(operation_key))
      
      # Si ya se habia aplicado no la aplico nuevamente
      if op.status == Operation.OPERATION_DONE:
        return op

      assert(op.seller.commission_rate > Decimal('0')), u'Comisión inválida'
      assert(op.buyer.commission_rate > Decimal('0')), u'Comisión inválida'

      # Traemos la cuenta del xchanger
      xchg = Account.get_by_key_name('xchg')

      # Calculamos los fees del xchanger
      xchg_curr_fee = op.traded_currency*op.seller.commission_rate
      xchg_btc_fee  = op.traded_btc*op.buyer.commission_rate

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
                                    currency       = 'ARS',
                                    state          = AccountOperation.STATE_DONE)

      seller_op2 = AccountOperation(parent         = op.seller, 
                                    operation_type = AccountOperation.BTC_SELL, 
                                    account        = op.seller,
                                    amount         = -op.traded_btc,
                                    currency       = 'BTC',
                                    state          = AccountOperation.STATE_DONE)

      # Cremos los AccountOperation para el comprador
      buyer_op1 = AccountOperation( parent         = op.buyer, 
                                    operation_type = AccountOperation.BTC_BUY, 
                                    account        = op.buyer,
                                    amount         = buyers_btc, 
                                    currency       = 'BTC',
                                    state          = AccountOperation.STATE_DONE)

      buyer_op2 = AccountOperation( parent         = op.buyer, 
                                    operation_type = AccountOperation.BTC_BUY, 
                                    account        = op.buyer,
                                    amount         = -op.traded_currency,
                                    currency       = 'ARS',
                                    state          = AccountOperation.STATE_DONE)
      
      # Cremos los AccountOperation para el xchanger
      xchg_op1 = AccountOperation(  parent         = xchg, 
                                    operation_type = AccountOperation.XCHG_FEE, 
                                    account        = xchg,
                                    amount         = xchg_btc_fee, 
                                    currency       = 'BTC',
                                    state          = AccountOperation.STATE_DONE)

      xchg_op2 = AccountOperation(  parent         = xchg, 
                                    operation_type = AccountOperation.XCHG_FEE, 
                                    account        = xchg,
                                    amount         = xchg_curr_fee,
                                    currency       = 'ARS',
                                    state          = AccountOperation.STATE_DONE)

      op.status = Operation.OPERATION_DONE


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

    return _tx()


  # Intenta matchear la mejor BID con la mejor ASK
  # Si hay posibilidades de trade, genera una nueva Operation 
  # y acomoda las TradeOrders

  def match_orders(self):

    @db.transactional(xg=True)
    def _tx():
      
      parent = Dummy.get_by_key_name('trade_orders')

      # Tomamos la mejor (mas alta) BID activa
      best_bid = TradeOrder.all() \
            .ancestor(parent) \
            .filter('order_type =', TradeOrder.LIMIT_ORDER) \
            .filter('bid_ask =', TradeOrder.BID_ORDER) \
            .filter('status =', TradeOrder.ORDER_ACTIVE) \
            .order('-ppc_int') \
            .get()

      # Tienen que ser válido el bid
      if best_bid is None:
        return [None, u'No hay suficientes ordenes para matchear']

      # Tomamos la mejor (mas baja) ASK activa (que no sea del usuario del bid)
      best_ask = None
      for ask_order in TradeOrder.all() \
            .ancestor(parent) \
            .filter('order_type =', TradeOrder.LIMIT_ORDER) \
            .filter('bid_ask =', TradeOrder.ASK_ORDER) \
            .filter('status =', TradeOrder.ORDER_ACTIVE) \
            .order('ppc_int'):

        if str(TradeOrder.user.get_value_for_datastore(ask_order)) != str(TradeOrder.user.get_value_for_datastore(best_bid)):
           best_ask = ask_order
           break

      # Tienen que ser válido el ask
      if best_ask is None:
        return [None, u'No hay suficientes ordenes para matchear']

      # Nos fijamos si hacen el match
      if best_bid.ppc < best_ask.ppc:
        return [None, u'No hay coincidencia (bet_bid=%.2f, best_ask=%.2f)' % (best_bid.ppc, best_ask.ppc)]

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
                     seller            = best_ask.user,
                     buyer             = best_bid.user,
                     status            = Operation.OPERATION_PENDING
            );

      # Acomodamos los valores de los TradeOrders y los marcamos como completos en caso 
      # Que den 0

      best_bid.amount -= amount
      if abs(best_bid.amount) < Decimal(1e-8):
        best_bid.status = TradeOrder.ORDER_COMPLETED
      
      best_ask.amount -= amount
      if abs(best_ask.amount) < Decimal(1e-8):
        best_ask.status = TradeOrder.ORDER_COMPLETED

      # Grabamos todo
      db.put([op,best_bid,best_ask])

      return [op, u'ok']

    return _tx()

  def add_market_trade(self, user_key, bid_ask, amount_wanted):

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
      

      res             = [to, u'No se pude llenar la orden']

      # Las iteramos y vamos viendo si "llenamos" la market order
      for order in orders:
        
        # Me fijo que no sea una orden mia
        if str(TradeOrder.user.get_value_for_datastore(order)) == user_key:
          continue

        op_amount = min(amount, order.amount)
        
        order.amount -= op_amount
        amount       -= op_amount

        # Nos comimos esta orden?
        if abs(order.amount) < Decimal(1e-8):
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
                       status            = Operation.OPERATION_PENDING
              );

        ops_list.append(op)
        order_list.append(order)

        # Se completo la orden, mandamos a guardar 
        # 1) las operaciones generadas
        # 2) las ordenes modificadas y la nueva orden creada
        # 3) el balance del usuario modificado
        if abs(amount) < Decimal(1e-8):
          
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

      # Borramos el market order
      if res[1] != u'ok':
        res[0].delete()
        res[0] = None

      return res

    return _tx()


  # Agrega un limit order a la DB
  # Checkea dentro de una transaccion el balance disponible
  def add_limit_trade(self, user, bid_ask, amount, ppc):

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
          return [None, u'No tiene suficiente balance disponible en BTC']
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