# -*- coding: utf-8 -*-
import unittest

from time import sleep
from decimal import Decimal

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from models import Account, TradeOrder, AccountBalance
from trader import Trader

class DemoTestCase(unittest.TestCase):

  def setUp(self):
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    self.users = []

    # Generamos 10 usuaris
    for i in xrange(10):
      
      user = Account()
      user.email    = 'usuario%d@test.com' % i
      user.password = 'beto'
      user.put()

      balance_ars  = AccountBalance(parent=user, account=user, currency='ARS')
      balance_ars.amount = 1000;

      balance_btc  = AccountBalance(parent=user, account=user, currency='BTC')
      balance_btc.amount = 100;
      db.put([balance_ars,balance_btc])

      self.users.append(user)


  def tearDown(self):
    self.testbed.deactivate()

  def test_AddAskOrder(self):
    trader = Trader() 
    
    # Agrega order
    res = trader.add_limit_trade( str(self.users[0].key()) , 
                                  TradeOrder.ASK_ORDER, 
                                  Decimal('10'), 
                                  Decimal('300') )

    dummy = db.get(res[0].key())

    self.assertEqual( True, res[0] != None )
    self.assertEqual( u'ok', res[1] )

    orders = TradeOrder.all().fetch(10)
    self.assertEqual(1,len(orders))

    order = orders[0]

    self.assertEqual(order.ppc_int, int(Decimal(300)*100))
    self.assertEqual(order.ppc, Decimal(300))
    self.assertEqual(order.bid_ask, TradeOrder.ASK_ORDER)

  def test_AddBidOrder(self):
    trader = Trader() 
    
    # Agrega order
    res = trader.add_limit_trade( str(self.users[0].key()) , 
                                  TradeOrder.BID_ORDER, 
                                  Decimal('10'), 
                                  Decimal('90') )

    dummy = db.get(res[0].key())

    

    self.assertEqual( True, res[0] != None )
    self.assertEqual( u'ok', res[1] )

    orders = TradeOrder.all().fetch(10)
    
    self.assertEqual(1,len(orders))

    order = orders[0]

    self.assertEqual(order.ppc_int, int(Decimal(90)*100))
    self.assertEqual(order.ppc, Decimal(90))
    self.assertEqual(order.bid_ask, TradeOrder.BID_ORDER)


  def test_NoBTC(self):
    trader = Trader() 
    
    # No hay balance BTC
    res = trader.add_limit_trade( str(self.users[0].key()) , 
                                  TradeOrder.BID_ORDER, 
                                  Decimal('101'), 
                                  Decimal('300') )
    
    self.assertEqual( None, res[0] )

  def test_NoARS(self):
    trader = Trader() 
    
    # No hay balance ARS
    res = trader.add_limit_trade( str(self.users[0].key()) , 
                                  TradeOrder.BID_ORDER, 
                                  Decimal('10'), 
                                  Decimal('300') )
    
    self.assertEqual( None, res[0] )

  def test_InvalidKey(self):
    trader = Trader() 
    self.assertRaises( AssertionError, trader.add_limit_trade, None ,  TradeOrder.BID_ORDER,  Decimal('10'), Decimal('300') )

  def test_InvalidOrderType(self):
    trader = Trader() 
    self.assertRaises( AssertionError, trader.add_limit_trade, str(self.users[0].key()) , 'moko',  Decimal('10'), Decimal('300') )

  def test_NegativeAmount(self):
    trader = Trader() 
    self.assertRaises( AssertionError, trader.add_limit_trade, str(self.users[0].key()) , 'moko',  Decimal('-10'), Decimal('300') )

  def test_NegativePPC(self):
    trader = Trader() 
    self.assertRaises( AssertionError, trader.add_limit_trade, str(self.users[0].key()) , 'moko',  Decimal('10'), Decimal('-300') )    