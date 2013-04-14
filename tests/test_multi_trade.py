# -*- coding: utf-8 -*-
import unittest

from time import sleep
from decimal import Decimal
from random import uniform

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation
from trader import Trader

from exchanger import get_account_balance
from my_test_utils import TestUtilMixin

from bitcoin_helper import zero_btc

class TestOrders(unittest.TestCase, TestUtilMixin):

  def setUp(self):
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    self.aux_init_all()

    self.users = []
  
    total_in = {'ARS': Decimal('0'), 'BTC': Decimal('0')}

    # Generamos 10 usuarios
    for i in xrange(10):
      
      user = self.aux_create_new_user('usuario%d@test.com' % i)

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

    trader = Trader()
    
    # Agregamos ordenes random
    for i in xrange(100):
      
      user = str(self.users[int(uniform(0,10))].key())
      bal  = get_account_balance(user)

      r = None

      # 90% chances de meter orden
      if uniform(1,100) > 10:

        # 50% chances de meter bid o ask
        if uniform(1,100) > 50:
          r = self.aux_add_random_bid(user, 1, 10, 100, 200)
        else:
          r = self.aux_add_random_ask(user, 1, 10, 150, 250)

      # 10%
      else:

        # 90% chances de retirar
        if uniform(1,100) > 10:

          # 50% chances de retirar BTC / ARS
          cuanto = Decimal('1') if uniform(1,100) > 50 else Decimal('0.5')
          currency = 'ARS' if uniform(1,100) > 50 else 'BTC'
          
          if bal[currency].available()*cuanto < Decimal('1e-8'):
            print 'ya no puede sacar nada'
          else:
            print 'mando a sacar: %.5f %s' % (bal[currency].available()*cuanto, currency)
            trader.add_widthdraw_order(user, currency, bal[currency].available()*cuanto)

      # 70% chances de correr el match_orders
      if uniform(1,100) > 30:
        res = trader.match_orders() 
        if res[0] is not None:
          trader.apply_operation( str(res[0].key()) )

      # 15% de chances de cancelar una orden
      if r and r[0] and uniform(1,100) > 85:
        tmp = trader.cancel_order(str(r[0].key()))
        if tmp:
          self.assertFalse(trader.cancel_order(str(r[0].key())))

    # Corremos las ultimas veces hasta que no se toquen las puntas
    print 'corremos una mas ...'
    res = trader.match_orders()
    while res[0] is not None:
      print 'print una mas ...'
      trader.apply_operation(str(res[0].key()))
      res = trader.match_orders()

    bba = self.aux_get_best_bid_ask()

    self.assertTrue(bba['bid'].ppc < bba['ask'].ppc)

    # Comparamos las sumas de los accountoperation contra el balance global
    res = self.aux_compare_guita()
    self.assertTrue( zero_btc(res['in']['ARS'] - res['sumbal']['ARS']) )
    self.assertTrue( zero_btc(res['in']['BTC'] - res['sumbal']['BTC']) )

    # Por todos los usuarios, verificamos que el balance comprometido 
    # sea igual a las ordenes que tienen abiertas aun
    for u in Account.all():

      res1 = self.aux_ops_sum(u)
      res2 = get_account_balance(u)

      self.assertTrue( zero_btc(res1['ARS']-res2['ARS'].amount) )
      self.assertTrue( zero_btc(res1['BTC']-res2['BTC'].amount) )

      res = self.aux_sum_trade_orders(u)
      
      print 
      print 'sum ask ord : %.5f' % res['BTC']
      print 'amt btc comp: %.5f' % res2['BTC'].amount_comp
      print 
      print 'sum bid ord : %.5f' % res['ARS']
      print 'amt ars comp: %.5f' % res2['ARS'].amount_comp

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
      self.assertTrue(zero_btc(t.amount))

    # Todas las trades ordenes canceladas
    for t in TradeOrder.all().filter('status =', TradeOrder.ORDER_CANCELED):
      print t

    # Pedidos de retiro
    for t in AccountOperation.all().filter('operation_type = ', AccountOperation.MONEY_OUT):
      print t






    






