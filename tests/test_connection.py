# -*- coding: utf-8 -*-
import unittest

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from bitcoinrpc.connection_helper import BlockChainProxy,EC2Proxy

class TestMarketTrade(unittest.TestCase):

  def setUp(self):
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    self.bchain = BlockChainProxy()
    self.ec2    = EC2Proxy()
  
  def tearDown(self):
    self.testbed.deactivate()

  def test_DualConnection(self):

    b1 = self.bchain.getblockcount()
    b2 = self.ec2.getblockcount()

    self.assertEqual(b1,b2)

    blk1 = self.bchain.getblk(229755)
    blk2 = self.ec2.getblk(229755)

    self.assertTrue(blk1.has_key('hash'))
    self.assertTrue(blk1.has_key('tx'))

    self.assertTrue(blk2.has_key('hash'))
    self.assertTrue(blk2.has_key('tx'))

    self.assertEqual(blk1['hash'], blk2['hash'])
    self.assertEqual(len(blk1['tx']), len(blk2['tx']))

    print
    blk1['tx'].sort(key=lambda x: x['txid'], reverse=True)
    blk2['tx'].sort(key=lambda x: x['txid'], reverse=True)

    for i in range(0,len(blk1['tx'])):
      
      tx1 = blk1['tx'][i]
      tx2 = blk2['tx'][i]


      self.assertTrue(tx1.has_key('txid'))
      self.assertTrue(tx2.has_key('txid'))
      self.assertEqual(tx1['txid'], tx2['txid'])

      print tx1['txid']

      self.assertTrue(tx1.has_key('outs'))
      self.assertTrue(tx2.has_key('outs'))

      outs1 = tx1['outs']
      outs2 = tx2['outs']
      self.assertEqual(len(outs1), len(outs2))

      print len(outs1)

      outs1.sort(key=lambda x: x['n'], reverse=True)
      outs2.sort(key=lambda x: x['n'], reverse=True)

      for j in range(0, len(outs1)):
        out1 = outs1[j]
        out2 = outs2[j]

        self.assertTrue( out1.has_key('scriptPubKey') )
        self.assertTrue( out1.has_key('scriptPubKey') )

        self.assertEqual( out1['scriptPubKey'].has_key('addresses'), out2['scriptPubKey'].has_key('addresses') )
        
        self.assertTrue( out1.has_key('n') )
        self.assertTrue( out2.has_key('n') )
        self.assertEqual( out1['n'], out2['n'])

        self.assertTrue( out1.has_key('value') )
        self.assertTrue( out2.has_key('value') )
        self.assertEqual( out1['value'], out2['value'])



      





