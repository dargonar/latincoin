# -*- coding: utf-8 -*-
from decimal import Decimal
from google.appengine.ext import db

from models import TradeOrder, Operation, Account, Dummy
from account_functions import get_account_balance

class Trader:

  # Elimina una orden de compra o venta
  # Acomoda el balance del usuario dueño de esa orden
  def cancel_order(self, order_key):

    # TODO: assert input
    assert(isinstance(order_key, basestring) and len(order_key) > 0 ), u'Key de orden inválida'

    @db.transactional(xg=True)
    def _tx():

      order = db.get(db.Key(order_key))

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
    assert(operation_key is not None), u'Operation key invalida'

    @db.transactional(xg=True)
    def _tx():

      # Traemos la operacion que resulto del match de dos TradeOrders
      op = db.get(db.Key(operation_key))
      
      # Si ya se habia aplicado no la aplico nuevamente
      if op.status == Operation.OPERATION_DONE:
        return True

      assert(op.seller.commission_rate > Decimal('0')), u'Comisión inválida'
      assert(op.buyer.commission_rate > Decimal('0')), u'Comisión inválida'

      # Traemos la cuenta del xchanger
      xchg = Account.get_by_key_name('xchg')

      # Traemos los balances del comprador, vendedor y el xchanger
      seller_balance = get_account_balance(op.seller)
      buyer_balance  = get_account_balance(op.buyer)
      xchg_balance   = get_account_balance(xchg)

      # Calculamos los fees del xchanger
      xchg_curr_fee = op.traded_currency*op.seller.commission_rate
      xchg_btc_fee  = op.traded_btc*op.buyer.commission_rate

      # Actualizamos los balances del vendedor
      seller_balance['ARS'].amount      += op.traded_currency - xchg_curr_fee
      seller_balance['BTC'].amount      -= op.traded_btc
      seller_balance['BTC'].amount_comp -= op.traded_btc

      # Actualizamos los balances del comprador
      buyer_balance['BTC'].amount      += op.traded_btc - xchg_btc_fee
      buyer_balance['ARS'].amount      -= op.traded_currency
      buyer_balance['ARS'].amount_comp -= op.traded_currency

      # Actualizamos los balances del xchg
      xchg_balance['BTC'].amount       += xchg_btc_fee
      xchg_balance['ARS'].amount       += xchg_curr_fee

      # Cremos los AccountOperation para el vendedor
      seller_op1 = AccountOperation(parent         = op.seller, 
                                    operation_type = BTC_SELL, 
                                    account        = op.seller,
                                    amount         = op.traded_currency - xchg_curr_fee, 
                                    currency       = 'ARS',
                                    state          = STATE_DONE)

      seller_op2 = AccountOperation(parent         = op.seller, 
                                    operation_type = BTC_SELL, 
                                    account        = op.seller,
                                    amount         = -op.traded_btc,
                                    currency       = 'BTC',
                                    state          = STATE_DONE)

      # Cremos los AccountOperation para el comprador
      buyer_op1 = AccountOperation( parent         = op.buyer, 
                                    operation_type = BTC_BUY, 
                                    account        = op.buyer,
                                    amount         = op.traded_btc - xchg_btc_fee, 
                                    currency       = 'BTC',
                                    state          = STATE_DONE)

      buyer_op2 = AccountOperation( parent         = op.buyer, 
                                    operation_type = BTC_BUY, 
                                    account        = op.buyer,
                                    amount         = -op.traded_currency,
                                    currency       = 'ARS',
                                    state          = STATE_DONE)
      
      # Cremos los AccountOperation para el xchanger
      xchg_op1 = AccountOperation(  parent         = xchg, 
                                    operation_type = BTC_FEE, 
                                    account        = xchg,
                                    amount         = xchg_btc_fee, 
                                    currency       = 'BTC',
                                    state          = STATE_DONE)

      xchg_op2 = AccountOperation(  parent         = xchg, 
                                    operation_type = BTC_FEE, 
                                    account        = xchg,
                                    amount         = xchg_curr_fee,
                                    currency       = 'ARS',
                                    state          = STATE_DONE)

      op.status = Operation.OPERATION_DONE


      to_save =  [op]
      
      to_save += [buyer_balance['ARS'], buyer_balance['BTC']]
      to_save += [buyer_op1, buyer_op2]

      to_save += [seller_balance['ARS'], seller_balance['BTC']]
      to_save += [seller_op1, seller_op2]

      to_save += [xchg_balance['ARS'], xchg_balance['BTC']]
      to_save += [xchg_op1, xchg_op2]

      db.put(to_save)

      return True

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
            .order('ppc') \
            .get()

      # Tomamos la mejor (mas baja) ASK activa
      best_ask = TradeOrder.all() \
            .ancestor(parent) \
            .filter('order_type =', TradeOrder.LIMIT_ORDER) \
            .filter('bid_ask =', TradeOrder.ASK_ORDER) \
            .filter('status =', TradeOrder.ORDER_ACTIVE) \
            .order('ppc') \
            .get()

      # Tienen que ser validas las dos (not None)
      if best_bid is None or best_ask is None:
        return [None, u'No hay suficientes ordenes para matchear']

      # Nos fijamos si hacen el match
      if best_bid.ppc < best_ask.ppc:
        return [None, u'No hay coincidencia']

      # Hay posibilidad de operacion, obtenemos los valores para armar la operacion
      amount = min(best_bid.amount, best_ask.amount)
      ppc    = best_ask.ppc

      # Se crea una nueva operation Operation.OPERATION_PENDING
      # Luego, cuando se generen los 6 AccountOperations y la actualizacion de
      # los balances se pasa a OPERATION_DONE

      op = Operation(parent=Dummy.get_by_key_name('operations'),
                     purchase_order_id = best_bid,
                     sale_order_id     = best_ask,
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
      if best_bid.amount == Decimal('0'):
        best_bid.status = TradeOrder.ORDER_COMPLETED
      
      best_ask.amount -= amount
      if best_ask.amount == Decimal('0'):
        best_ask.status = TradeOrder.ORDER_COMPLETED

      # Grabamos todo
      db.put([op,best_bid,best_ask])

      return op

    return _tx()

  # Agrega un limit trade a la DB
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
        if balance['BTC'].amount - balance['BTC'].amount_comp < amount:
          return [None, u'No tiene suficiente balance disponible en BTC']
        else:
          balance['BTC'].amount_comp += amount
      
      else: #if bid_ask == TradeOrder.ASK_ORDER:
        if balance['ARS'].amount - balance['ARS'].amount_comp < amount * ppc:
          return [None, u'No tiene suficiente balance disponible en ARS']
        else:
          balance['ARS'].amount_comp += amount * ppc

      # Creamos la orden ya que el balance dio para que se pueda meter
      # y mandamos a guardar las dos cosas juntas.
      # Si el usuario modifico su balance de alguna manera (retiro, otra order, etc)
      # la transaccion se vuelve a ejecutar y si no da el balance no se mete.

      to = TradeOrder(parent=Dummy.get_by_key_name('trade_orders'), 
            user            = db.Key(user),
            original_amount = amount,
            amount          = amount,
            ppc             = ppc,
            currency        = 'ARS',
            status          = TradeOrder.ORDER_ACTIVE,
            bid_ask         = bid_ask,
            order_type      = TradeOrder.LIMIT_ORDER
          )

      balance = balance['BTC'] if bid_ask == TradeOrder.ASK_ORDER else balance['ARS']

      db.put([balance,to])
      return [to, u'ok']

    return _tx()
