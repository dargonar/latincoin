# -*- coding: utf-8 -*-
import logging 
from decimal import Decimal
from random import uniform
from datetime import datetime 

from google.appengine.ext import db

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation
from exchanger import *

class TestUtilMixin:
  users = []
  def generate_trade_operations(self):
    
    # generamos 5 operaciones
    for i in xrange(10):
    
      user = self.aux_create_new_user('usuario%d@test.com' % i)
      self.users.append(user)
      for i in xrange(int(uniform(1,5))):

        ars = Decimal(50000)
        btc = Decimal(1000)

        dep_ars = self.aux_deposit_ars(user,ars)
        dep_btc = self.aux_deposit_btc(user,btc)
        
        b = get_account_balance(user)
        b['ARS'].amount += ars
        b['BTC'].amount += btc

        db.put([b['ARS'],b['BTC']])
      #trade = add_limit_trade(str(user.key()), TradeOrder.BID_ORDER, Decimal('5.0'), Decimal('5.0'))
      #logging.info('trade: %s', trade)
  
    # Agregamos ordenes random
    for i in xrange(100):
      
      user = str(self.users[int(uniform(0,10))].key())
      bal  = get_account_balance(user)

      r = None

      # 50% chances de meter bid o ask
      if uniform(1,100) > 50:
        r = self.aux_add_random_bid(user, 1, 10, 100, 200)
      else:
        r = self.aux_add_random_ask(user, 1, 10, 150, 250)

      logging.info(' Trade metida? [%s] balance:[%s]',r, bal)
      
      res = match_orders() 
      if res[0] is not None:
        rop = apply_operation( str(res[0].key()) )
        rop.traders_were_notified = True # para no mandarles mails a esos recontra putos
        logging.info(' Oper realizada? [%s]',rop)
        
    # Corremos las ultimas veces hasta que no se toquen las puntas
    print 'corremos una mas ...'
    res = match_orders()
    while res[0] is not None:
      print 'print una mas ...'
      apply_operation(str(res[0].key()))
      res[0].traders_were_notified = True # para no mandarles mails a esos recontra putos
      res = match_orders()

    bba = self.aux_get_best_bid_ask()
    return True
  
  
  def aux_sum_trade_orders(self, user):
    ret = {'ARS':Decimal('0'), 'BTC':Decimal('0')}

    parent = Dummy.get_by_key_name('trade_orders')
    ords = TradeOrder.all() \
          .ancestor(parent) \
          .filter('user =', user) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.ASK_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE)
    
    for o in ords:
      ret['BTC'] += o.amount

    oords = TradeOrder.all() \
          .ancestor(parent) \
          .filter('user =', user) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.BID_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE)

    for x in oords:
      ret['ARS'] += (x.amount*x.ppc)

    return ret

  def aux_compare_guita(self):

    # Toda la plata que entro
    total_in = {'ARS': Decimal('0'), 'BTC': Decimal('0')}
    for ao in AccountOperation.all().filter('operation_type = ', AccountOperation.MONEY_IN):
      total_in[ao.currency] += ao.amount

    # Toda la plata que salio
    for ao in AccountOperation.all().filter('operation_type = ', AccountOperation.MONEY_OUT):
      total_in[ao.currency] += ao.amount

    print 
    
    # La suma de todos los balances
    total_bal = {'ARS':Decimal('0'), 'BTC':Decimal('0')}
    for a in Account.all():
      b = get_account_balance(a)
      print 'usr: %s: %.2f BTC %.2f ARS' % (a.key(), b['BTC'].amount, b['ARS'].amount)
      total_bal['ARS'] += b['ARS'].amount
      total_bal['BTC'] += b['BTC'].amount

    return {'in':total_in, 'sumbal':total_bal}

  
  def aux_get_best_bid_ask(self):
    parent = Dummy.get_by_key_name('trade_orders')

    # Tomamos la mejor (mas alta) BID activa
    best_bid = TradeOrder.all() \
          .ancestor(parent) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.BID_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE) \
          .order('-ppc_int') \
          .get()

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
    
    return {'bid':best_bid, 'ask':best_ask}

  def aux_get_best_ask(self):
    parent = Dummy.get_by_key_name('trade_orders')

    # Tomamos la mejor (mas baja) ASK activa
    best_ask = TradeOrder.all() \
          .ancestor(parent) \
          .filter('order_type =', TradeOrder.LIMIT_ORDER) \
          .filter('bid_ask =', TradeOrder.ASK_ORDER) \
          .filter('status =', TradeOrder.ORDER_ACTIVE) \
          .order('ppc_int') \
          .get()
    
    return best_ask



  def aux_add_random_bid(self, user, min_amount, max_amount, min_ppc, max_ppc):
    amount = Decimal(uniform(min_amount,max_amount))
    ppc    = Decimal(uniform(min_ppc,max_ppc))
    return self.aux_add_bid(user, amount, ppc)

  def aux_add_random_ask(self, user, min_amount, max_amount, min_ppc, max_ppc):
    amount = Decimal(uniform(min_amount,max_amount))
    ppc    = Decimal(uniform(min_ppc,max_ppc))
    return self.aux_add_ask(user, amount, ppc)

  def aux_create_new_user(self, name):
    user = Account.new_user(name, 'beto')
    user.confirmed_at = datetime.now()
    user.put()

    balance_ars  = AccountBalance(parent=user, account=user, currency='ARS')
    balance_ars.put()

    balance_btc  = AccountBalance(parent=user, account=user, currency='BTC')
    balance_btc.put()

    return user

  def aux_deposit_ars(self, user, ars):
    user_deposit_ars = AccountOperation(parent   = user, 
                                        operation_type = AccountOperation.MONEY_IN, 
                                        account        = user,
                                        amount         = ars,
                                        currency       = 'ARS',
                                        state          = AccountOperation.STATE_DONE)
    user_deposit_ars.put()
    return user_deposit_ars
    
  def aux_deposit_btc(self, user, btc):
    user_deposit_btc = AccountOperation(parent   = user, 
                                        operation_type = AccountOperation.MONEY_IN, 
                                        account        = user,
                                        amount         = btc,
                                        currency       = 'BTC',
                                        state          = AccountOperation.STATE_DONE)
    user_deposit_btc.put()
    return user_deposit_btc

  def aux_init_all(self):
    parent=Dummy.get_or_insert('trade_orders')
    parent=Dummy.get_or_insert('operations')

    xchg = Account(key_name='xchg')
    xchg.email                 = 'x@x.com'
    xchg.password              = 'sdsd'
    xchg.confirmation_token    = 'sdsd'
    xchg.put()

    b_ars = AccountBalance(parent=xchg, account=xchg, currency='ARS')
    b_ars.put()

    b_btc = AccountBalance(parent=xchg, account=xchg, currency='BTC')
    b_btc.put()

  def aux_add_trade(self, user, amount, ppc, bid_ask):
    return add_limit_trade(user, bid_ask, amount, ppc)

  def aux_add_bid(self, user, amount, ppc):
    return self.aux_add_trade(user, amount, ppc, TradeOrder.BID_ORDER)

  def aux_add_ask(self, user, amount, ppc):
    return self.aux_add_trade(user, amount, ppc, TradeOrder.ASK_ORDER)

  def aux_assert_pending_op(self, op, usr_bid, usr_ask, bid, ask, amount, ppc):
    return self.aux_assert_op(op, usr_bid, usr_ask, bid, ask, amount, ppc, Operation.OPERATION_PENDING)

  def aux_assert_op(self, op, usr_bid, usr_ask, bid, ask, amount, ppc, status):

    self.assertEqual( str(bid.key()), str(op.purchase_order.key())  )
    self.assertEqual( str(ask.key()), str(op.sale_order.key())  )
    self.assertEqual( amount, op.traded_btc )
    self.assertEqual( amount*ppc, op.traded_currency )
    self.assertEqual( ppc, op.ppc )
    self.assertEqual( 'ARS', op.currency )
    self.assertEqual( str(op.seller.key()), str(usr_ask.key()) )
    self.assertEqual( str(op.buyer.key()), str(usr_bid.key()) )
    self.assertEqual( op.status, status)

    self.assertEqual(bid.amount, bid.original_amount - amount)
    self.assertEqual(ask.amount, ask.original_amount - amount)

    return True

  def aux_ops_sum(self, user):
    btc = Decimal('0')
    ars = Decimal('0')

    for o in AccountOperation.all().ancestor(user).filter('account = ',user):
      if o.state == AccountOperation.STATE_CANCELED:
        continue

      if o.currency == 'ARS':
        ars += o.amount
      elif o.currency == 'BTC':
        btc += o.amount  

    return {'ARS':ars, 'BTC':btc}