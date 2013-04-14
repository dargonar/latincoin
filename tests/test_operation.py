# -*- coding: utf-8 -*-
import unittest

from time import sleep
from decimal import Decimal

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation
from trader import Trader

from exchanger import get_account_balance

from my_test_utils import *
from bitcoin_helper import zero_btc

class TestOperation(unittest.TestCase, TestUtilMixin):

  def setUp(self):
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    # aux
    self.aux_init_all()

    self.users = []

    # Generamos 10 usuarios
    for i in xrange(10):
      
      user = self.aux_create_new_user('usuario%d@test.com' % i)
      ars = Decimal('1000')
      btc = Decimal('100')

      self.aux_deposit_ars(user, ars)
      self.aux_deposit_btc(user, btc)

      b = get_account_balance(user)
      b['ARS'].amount = ars
      b['BTC'].amount = btc

      db.put([b['ARS'],b['BTC']])

      self.users.append(user)

  def tearDown(self):
    self.testbed.deactivate()

  def test_GlobalBalance(self):

    btc = Decimal('0')
    ars = Decimal('0')

    for u in Account.all():
      b = self.aux_ops_sum(u)
      btc += b['BTC']
      ars += b['ARS']

      r = get_account_balance(u)
      ars -= r['ARS'].amount
      btc -= r['BTC'].amount

    self.assertTrue(zero_btc(ars))
    self.assertTrue(zero_btc(btc))

  def u(self,user):
    return str(self.users[user].key())

  def test_MatchOrders(self):

    self.aux_add_bid(self.u(3), Decimal('3'), Decimal('298'))
    self.aux_add_bid(self.u(4), Decimal('3'), Decimal('299'))
    
    res1 = self.aux_add_bid(self.u(0), Decimal('3'), Decimal('301'))
    self.assertEqual( True, res1[0] != None )
    self.assertEqual( u'ok', res1[1] )

    res2 = self.aux_add_ask(self.u(1), Decimal('2'), Decimal('300'))
    self.assertEqual( True, res2[0] != None )
    self.assertEqual( u'ok', res2[1] )

    self.aux_add_ask(self.u(4), Decimal('10'), Decimal('301'))
    self.aux_add_ask(self.u(4), Decimal('10'), Decimal('302'))

    trader = Trader() 
    op = trader.match_orders()
    self.assertEqual( True, op[0] != None )
    dummy = db.get(op[0].key())
    

    ops = Operation.all().fetch(10)
    self.assertEqual( 1, len(ops) )

    res1[0] = db.get(res1[0].key())
    res2[0] = db.get(res2[0].key())

    self.aux_assert_pending_op(ops[0], self.users[0], self.users[1], res1[0], res2[0], Decimal('2'), Decimal('300'))

    # No camina
    self.assertRaises( AssertionError, trader.apply_operation, 1)

    self.assertEqual(ops[0].status,Operation.OPERATION_PENDING)


    buy_b  = get_account_balance(self.users[0])
    print buy_b['BTC'].amount_comp
    print buy_b['ARS'].amount_comp



    # La aplico dos veces (de onda)
    for i in xrange(2):
      res = trader.apply_operation(str(ops[0].key()))
      self.assertEqual(True, res != None)

      opdone = db.get(ops[0].key())
      self.assertEqual(opdone.status,Operation.OPERATION_DONE)


    buy_b  = get_account_balance(self.users[0])
    print buy_b['BTC'].amount_comp
    print buy_b['ARS'].amount_comp



    xchg = Account.get_by_key_name('xchg')

    xchg_b = get_account_balance(xchg)
    buy_b  = get_account_balance(self.users[0])
    sell_b = get_account_balance(self.users[1])

    # Balance del que compro
    self.assertEqual(buy_b['BTC'].amount, Decimal('100')  + Decimal('2')*Decimal('0.994') )
    self.assertEqual(buy_b['ARS'].amount, Decimal('1000') - Decimal('2')*Decimal('300'))


    # Balance del que vendio
    self.assertEqual(sell_b['BTC'].amount, Decimal('100')  - Decimal('2') )
    self.assertEqual(sell_b['ARS'].amount, Decimal('1000') + Decimal('2')*Decimal('300')*Decimal('0.994'))
    
    # Balance del xchg
    self.assertEqual(xchg_b['BTC'].amount, Decimal('2')*Decimal('0.006') )
    self.assertEqual(xchg_b['ARS'].amount, Decimal('2')*Decimal('300')*Decimal('0.006') )

    # 4 account ops (2 deposito + 2 trade)
    for i in [0,1]:
      aops_buy = AccountOperation.all().ancestor(self.users[i]).fetch(10)
      self.assertEqual(len(aops_buy),4)

      res = self.aux_ops_sum(self.users[i])
      self.assertEqual(res['ARS'], buy_b['ARS'].amount if i == 0 else sell_b['ARS'].amount)
      self.assertEqual(res['BTC'], buy_b['BTC'].amount if i == 0 else sell_b['BTC'].amount)

    # 2 del xchg
    aops_xchg = AccountOperation.all().ancestor(xchg).fetch(10)
    self.assertEqual(len(aops_xchg),2)

    




