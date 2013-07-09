# -*- coding: utf-8 -*-
import unittest
from random import uniform

# import time
# now=time.time()

# def mytime(): 
#   #print '---------------------------------'
#   mynow = now + uniform(5,15)*60
#   return mynow

# time.time = mytime

from decimal import Decimal

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

import webapp2

from config import config
from urls import get_rules

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation
#from trader import Trader

from exchanger import *
from my_test_utils import TestUtilMixin

from bitcoin_helper import zero_btc



class TestOrders(unittest.TestCase, TestUtilMixin):

  def setUp(self):
    
    # Creamos el contexto webapp2
    app = webapp2.WSGIApplication(routes=get_rules(config), config=config, debug=True)

    req = webapp2.Request.blank('/beto_casela')
    req.app = app
    webapp2._local.request = req
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
    self.testbed.init_taskqueue_stub()
    self.testbed.init_memcache_stub()

    self.aux_init_all()

    self.users = []
  
    total_in = {'ARS': Decimal('0'), 'BTC': Decimal('0')}

    # Generamos 10 usuarios
    for i in xrange(10):
      
      user = self.aux_create_new_user('usuario%d@test.com' % i, create_bank_account=True)
      
      for i in xrange(int(uniform(1,5))):

        ars = Decimal(uniform(100 , 50000))
        btc = Decimal(uniform(0.1 ,  1000))

        self.aux_deposit_ars(user,ars)
        self.aux_deposit_btc(user,btc)

        total_in['ARS'] += ars
        total_in['BTC'] += btc

        b = get_account_balance(user)
        b['ARS'].amount += ars
        b['BTC'].amount += btc
  
        db.put([b['ARS'],b['BTC']])

      self.users.append(user)

    print 'total in (generado)'
    print total_in


  def tearDown(self):
    self.testbed.deactivate()

  def test_BetoTest(self):

    
    
    # Agregamos ordenes random
    for i in xrange(100):
      
      account = self.users[int(uniform(0,10))]
      user = str(account.key())
      bal  = get_account_balance(user)

      r = None

      # 60% chances de comprar/vender
      if uniform(1,100) > 40:

        # 50% chances de meter bid o ask
        if uniform(1,100) > 50:
          
          # 70 % chances limit
          if uniform(1,100) > 30:
            r = self.aux_add_random_bid(user, 1, 10, 100, 200)
            if r[0]: print 'meti limit bid %s' % r[0].created_at.strftime("%Y-%m-%d %H:%M:%S")
          else:
            p = add_market_trade(user, TradeOrder.BID_ORDER, Decimal(uniform(1,5)) )
            if p[0]:
              print 'meti de mercado bid %s' % p[0].created_at.strftime("%Y-%m-%d %H:%M:%S")
              self.aux_apply_operations()
        else:
          # 70 % chances limit
          if uniform(1,100) > 30:
            r = self.aux_add_random_ask(user, 1, 10, 150, 250)
            if r[0]: print 'meti limit ask %s' % r[0].created_at.strftime("%Y-%m-%d %H:%M:%S")
          else:
            p = add_market_trade(user, TradeOrder.ASK_ORDER, Decimal(uniform(1,5)) )
            if p[0]:
              print 'meti de mercado ask %s' % p[0].created_at.strftime("%Y-%m-%d %H:%M:%S")
              self.aux_apply_operations()

          

      # 40%
      else:

        # 50% chances de retirar
        if uniform(1,100) > 50:

          # 50% chances de retirar todo y 50% de retirar la mitad del balance BTC/ARS
          cuanto = Decimal('1') if uniform(1,100) > 50 else Decimal('0.5')
          currency = 'ARS' if uniform(1,100) > 50 else 'BTC'
          
          if bal[currency].available()*cuanto < Decimal('1e-8'):
            print 'ya no puede sacar nada'
          else:
            print 'mando a sacar: %.5f %s' % (bal[currency].available()*cuanto, currency)
            if currency=='BTC':
              add_withdraw_btc_order(user, bal[currency].available()*cuanto, '13WnH6hAbmeuHAWSnbsAcMcaWWkBsjZY27')
            else:
              add_withdraw_currency_order(user, bal[currency].available()*cuanto, str(account.bank_accounts[0].key()))
        
        # 50% chances de depositar
        else:

          # 50% chances btc/ars
          currency = 'ARS' if uniform(1,100) > 50 else 'BTC'
          if currency == 'ARS':
            cuanto = Decimal(uniform(100 , 50000))
            add_currency_balance(user, cuanto)
          else:
            cuanto = Decimal(uniform(1 , 50))
            ftx = self.aux_fake_forward_tx(cuanto, account)
            add_btc_balance(str(ftx.key()))
          
          print 'mando a depositar: %.5f %s' % (cuanto, currency)

            
      # 20% chances de correr el match_orders
      if uniform(1,100) > 80:
        self.aux_apply_ops(match_orders())

      # 15% de chances de cancelar una orden
      if r and r[0] and uniform(1,100) > 85:
        tmp = cancel_order(str(r[0].key()))
        if tmp:
          self.assertFalse(cancel_order(str(r[0].key())))

    # Corremos las ultimas veces hasta que no se toquen las puntas
    print '-----------------corremos una mas--------------------'
    self.aux_apply_ops(match_orders())

    bba = self.aux_get_best_bid_ask()

    self.assertTrue(bba['bid'].ppc < bba['ask'].ppc)

    # Comparamos las sumas de los accountoperation contra el balance global
    res = self.aux_compare_guita()
    self.assertTrue( zero_btc(res['in']['ARS'] - res['sumbal']['ARS']) )
    
    print res['in']['BTC']
    print res['sumbal']['BTC']
    
    self.assertTrue( zero_btc(res['in']['BTC'] - res['sumbal']['BTC']) )

    # Por todos los usuarios, verificamos que el balance comprometido 
    # sea igual a las ordenes que tienen abiertas aun
    for u in Account.all():

      res1 = self.aux_ops_sum(u)
      res2 = get_account_balance(u)

      self.assertTrue( zero_btc(res1['ARS']-res2['ARS'].amount) )
      self.assertTrue( zero_btc(res1['BTC']-res2['BTC'].amount) )

      res = self.aux_sum_trade_orders(u)
      
      # print 
      # print 'sum ask ord : %.5f' % res['BTC']
      # print 'amt btc comp: %.5f' % res2['BTC'].amount_comp
      # print 
      # print 'sum bid ord : %.5f' % res['ARS']
      # print 'amt ars comp: %.5f' % res2['ARS'].amount_comp

      self.assertTrue( zero_btc(res2['ARS'].amount_comp-res['ARS']) )
      self.assertTrue( zero_btc(res2['BTC'].amount_comp-res['BTC']) )

    # Todas las operaciones
    tot_op = Operation.all().count()

    tot1 = AccountOperation.all().filter('operation_type = ', AccountOperation.BTC_SELL).count()
    tot2 = AccountOperation.all().filter('operation_type = ', AccountOperation.BTC_BUY).count()
    tot3 = AccountOperation.all().filter('operation_type = ', AccountOperation.XCHG_FEE).count()

    print tot1,tot2,tot3,tot_op

    self.assertEqual(tot1+tot2+tot3, tot_op*6)

    # Todas las trades ordenes cerradas
    for t in TradeOrder.all().filter('status =', TradeOrder.ORDER_COMPLETED):
      
      if not t.is_market():
        self.assertTrue(zero_btc(t.amount))

    # Todas las trades ordenes canceladas
    # for t in TradeOrder.all().filter('status =', TradeOrder.ORDER_CANCELED):
    #   print t

    # # Pedidos de retiro
    # for t in AccountOperation.all().filter('operation_type = ', AccountOperation.MONEY_OUT):
    #   print t






    






