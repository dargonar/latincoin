# -*- coding: utf-8 -*-
import unittest

from time import sleep
from decimal import Decimal
from random import uniform

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

import webapp2

from config import config
from urls import get_rules

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation
from exchanger import *

from exchanger import get_account_balance
from my_test_utils import TestUtilMixin

from bitcoin_helper import zero_btc

class TestMarketTrade(unittest.TestCase, TestUtilMixin):

  def setUp(self):

    # Creamos el contexto webapp2
    app = webapp2.WSGIApplication(routes=get_rules(config), config=config, debug=True)

    req = webapp2.Request.blank('/bet_casela')
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
  
    # Generamos 10 usuarios
    for i in xrange(10):
      
      user = self.aux_create_new_user('usuario%d@test.com' % i)

      ars = Decimal('5000')
      btc = Decimal('100')

      self.aux_deposit_ars(user,ars)
      self.aux_deposit_btc(user,btc)

      b = get_account_balance(user)
      b['ARS'].amount += ars
      b['BTC'].amount += btc

      db.put([b['ARS'],b['BTC']])

      self.users.append(user)


  def tearDown(self):
    self.testbed.deactivate()

  def u(self, usr):
    return str(self.users[usr].key())

  def test_MarketTradeASK(self):

    u0bal_pre = get_account_balance(self.u(0))
    u1bal_pre = get_account_balance(self.u(1))
    u2bal_pre = get_account_balance(self.u(2))
    u3bal_pre = get_account_balance(self.u(3))

    self.aux_add_bid(self.u(0), Decimal('6'), Decimal('200'))
    self.aux_add_bid(self.u(0), Decimal('5'), Decimal('250'))
    self.aux_add_bid(self.u(0), Decimal('5'), Decimal('300'))
    
    for x in xrange(2000):
      self.aux_add_bid(self.u(1), Decimal('5')/Decimal('2000'), Decimal('350'))
    
    for x in xrange(25):
      self.aux_add_bid(self.u(2), Decimal('5')/Decimal('25'), Decimal('400'))

    self.aux_add_bid(self.u(3), Decimal('5'), Decimal('500'))

    
    p = add_market_trade(self.u(3), TradeOrder.ASK_ORDER, Decimal('25'))
    
    self.assertTrue(p[0] is not None) and self.assertEqual(p[1], u'ok')

    sales = p[0].sales.fetch(10000)
    print 'sales:%d' % len(sales)

    for s in sales:
      r = apply_operation(str(s.key()))
      self.assertTrue(r is not None)

    u0bal_post = get_account_balance(self.u(0))
    u1bal_post = get_account_balance(self.u(1))
    u2bal_post = get_account_balance(self.u(2))
    u3bal_post = get_account_balance(self.u(3))

    # --- del vendedor ----

    # Balance nuevo en BTC (ant-25=post)
    self.assertTrue(u3bal_pre['BTC'].amount - Decimal('25') - u3bal_post['BTC'].amount < Decimal('1e-8') )
    
    # Balance nuevo en ARS (ant+tmp=post)
    tmp = (5*400 + 5*350 + 5*300 + 5*250 + 5*200)*0.994
    self.assertTrue(u3bal_pre['ARS'].amount - u3bal_post['ARS'].amount + Decimal(tmp) < Decimal('1e-8') )


    res = self.aux_compare_guita()
    print 
    print res['in']['ARS']
    print res['sumbal']['ARS']
    self.assertTrue( zero_btc(res['in']['ARS'] - res['sumbal']['ARS']) )
    self.assertTrue( zero_btc(res['in']['BTC'] - res['sumbal']['BTC']) )


  def test_MarketTradeBID(self):

    u0bal_pre = get_account_balance(self.u(0))
    u1bal_pre = get_account_balance(self.u(1))
    u2bal_pre = get_account_balance(self.u(2))
    u3bal_pre = get_account_balance(self.u(3))

    self.aux_add_ask(self.u(0), Decimal('6'), Decimal('200'))
    self.aux_add_ask(self.u(0), Decimal('5'), Decimal('250'))
    self.aux_add_ask(self.u(0), Decimal('5'), Decimal('300'))
    self.aux_add_ask(self.u(1), Decimal('5'), Decimal('350'))
    self.aux_add_ask(self.u(2), Decimal('5'), Decimal('400'))
    self.aux_add_ask(self.u(3), Decimal('5'), Decimal('500'))

    
    p = add_market_trade(self.u(3), TradeOrder.BID_ORDER, Decimal('10'))
    
    self.assertTrue(p[0] is not None) and self.assertEqual(p[1], u'ok')

    for s in p[0].purchases:
      r = apply_operation(str(s.key()))
      self.assertTrue(r is not None)

    u0bal_post = get_account_balance(self.u(0))
    u1bal_post = get_account_balance(self.u(1))
    u2bal_post = get_account_balance(self.u(2))
    u3bal_post = get_account_balance(self.u(3))

    res = self.aux_compare_guita()
    print 
    print res['in']['ARS']
    print res['sumbal']['ARS']
    self.assertTrue( zero_btc(res['in']['ARS'] - res['sumbal']['ARS']) )
    self.assertTrue( zero_btc(res['in']['BTC'] - res['sumbal']['BTC']) )










    






