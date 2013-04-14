# -*- coding: utf-8 -*-
import unittest

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from models import Account, AccountBalance, BitcoinAddress
from my_test_utils import TestUtilMixin
from bitcoin_helper import encrypt_private, decrypt_private, generate_new_address
from electrum.bitcoin import *

class TestPrivKeys(unittest.TestCase, TestUtilMixin):

  def setUp(self):

    priv = '13067dc1ab3d49f5cfaf84e787bcf1c98f740cce2a30a0fcb9af8a271dbc42188b0e41940edb63ce2cae633d5166b225c1d957107845b546a6213084c2dd2152a77d648dd0ed9e7fa2b444849558c21d'
    print decrypt_private(priv)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    self.users = []

    for i in xrange(0,50):
      
      user = self.aux_create_new_user('usuario%d@test.com' % i)
      user.confirm()
        
      balance_curr = AccountBalance(parent=user, account=user, currency='ARS')
      balance_btc  = AccountBalance(parent=user, account=user, currency='BTC')

      addr = generate_new_address()
      if not addr['result']:
        raise(BaseException('no se puede generar direccion btc'))

      addys = []
      
      for j in xrange(0,2):
        btc_addr = BitcoinAddress(key_name    = addr['public'],
                                  user        = user,
                                  address     = addr['public'], 
                                  private_key = encrypt_private(addr['private']))

        addys.append(btc_addr)

      db.put([user, balance_curr, balance_btc] + addys)
      self.users.append(user)
    
  def tearDown(self):
    self.testbed.deactivate()

  def test_primero(self):

    print

    for user in self.users:

      for addy in user.bitcoin_addresses:
        print addy.private_key
        asec = decrypt_private(addy.private_key)
        print asec
        print '----------------'
        tmp = address_from_private_key(asec)

        self.assertEqual(addy.address, tmp)
      


