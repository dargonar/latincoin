# -*- coding: utf-8 -*-
import unittest

from time import sleep
from decimal import Decimal
from datetime import datetime

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from my_test_utils import TestUtilMixin

from models import PriceBar, TradeOrder, Operation, Dummy
from exchanger import get_ohlc, add_limit_trade

class TestOHLC(unittest.TestCase, TestUtilMixin):

  def setUp(self):
    
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    #15/16/17/18
    ops = [
      [(2013,1,1,15,30,10), 1400, 5.5],
      [(2013,1,1,15,31,10), 1500, 3.5],
      [(2013,1,1,15,35,10), 1200, 1],
      [(2013,1,1,15,37,10), 1100, 10.5],
      [(2013,1,1,15,39,10), 1000, 1],
      [(2013,1,1,15,55,10), 1600, 4],
      [(2013,1,1,16,20,10), 2000, 5],
      [(2013,1,1,16,21,10), 1222, 4],
      [(2013,1,1,16,34,10), 1000, 12],
      [(2013,1,1,16,59,10), 1600, 15],
      [(2013,1,1,17,30,10), 1250, 12],
      [(2013,1,1,17,31,10), 1255, 15],
      [(2013,1,1,17,32,10), 1600, 2],
      [(2013,1,1,18,11,10), 1700, 4],
      [(2013,1,1,18,12,10), 1690, 5],
    ]

    # 1/1/2013 14:00
    bar_time = int(datetime(2013,1,1,14,00,00).strftime('%s'))/PriceBar.H1
    date = datetime.fromtimestamp(bar_time*PriceBar.H1)

    dummy_bar = PriceBar.get_or_insert('dummy_bar',
                        open         = 0,
                        high         = 0,
                        low          = 0,
                        close        = 0,
                        volume       = 0, 
                        bar_time     = bar_time,
                        bar_interval = PriceBar.H1,
                        year         = date.year,
                        month        = date.month,
                        day          = date.day)

    dummy_user  = self.aux_create_new_user('user1', 1000000, 1000)
    dummy_order = add_limit_trade(str(dummy_user.key()), TradeOrder.BID_ORDER, Decimal(1), Decimal(1) )


    for o in ops:
      
      amount = Decimal(o[2])
      ppc = Decimal(o[1])

      op = Operation(parent=Dummy.get_by_key_name('operations'),
                     purchase_order    = dummy_order[0],
                     sale_order        = dummy_order[0],
                     traded_btc        = amount,
                     traded_currency   = amount*ppc,
                     ppc               = ppc,
                     currency          = 'ARS',
                     seller            = dummy_user,
                     buyer             = dummy_user,
                     status            = Operation.OPERATION_PENDING,
                     type              = Operation.OPERATION_BUY,
                     created_at        = datetime(o[0][0], o[0][1], o[0][2], o[0][3], o[0][4], o[0][5]))

      op.put()

    # print
    # for xx in Operation.all():
    #   print xx

    # return
    print

    for i in xrange(20):
  
      # Traemos la ultima barra de hora
      last_bar = PriceBar.all().filter('bar_interval =', PriceBar.H1) \
                               .order('-bar_time') \
                               .get()
      
      #print "la last: " + str(last_bar)
      # Tenemos que armar la siguiente?
      have_to_build, new_bar_time  = last_bar.next_bar()
      if not have_to_build:
        print "me voy"
        return

      # Limites de fechas
      from_ts = datetime.fromtimestamp(new_bar_time * last_bar.bar_interval)
      to_ts   = datetime.fromtimestamp((new_bar_time+1) * last_bar.bar_interval)

      ohlc = get_ohlc(from_ts, to_ts, last_bar.close)
      # print from_ts,to_ts,ohlc
      # return

      date = datetime.fromtimestamp(new_bar_time * last_bar.bar_interval)

      # Aramamos el próximo bar
      next_bar = PriceBar(open         = ohlc['open'],
                          high         = ohlc['high'],
                          low          = ohlc['low'],
                          close        = ohlc['close'],
                          volume       = ohlc['volume'], 
                          bar_time     = new_bar_time,
                          bar_interval = last_bar.bar_interval,
                          year         = date.year,
                          month        = date.month,
                          day          = date.day)

      next_bar.put()
        
    for pb in PriceBar.all().filter('bar_interval =', PriceBar.H1).order('-bar_time'):
      print pb

  def tearDown(self):
    self.testbed.deactivate()

  def test_BuildOHLC(self):

    #15/16/17/18
    ops = [
      [(2013,1,1,15,30,10), 1400, 5.5], #0 -
      [(2013,1,1,15,31,10), 1500, 3.5], #1
      [(2013,1,1,15,35,10), 1200, 1],   #2
      [(2013,1,1,15,37,10), 1100, 10.5],#3
      [(2013,1,1,15,39,10), 1000, 1],   #4
      [(2013,1,1,15,55,10), 1600, 4],   #5
      
      [(2013,1,1,16,20,10), 2000, 5],   #6 -
      [(2013,1,1,16,21,10), 1222, 4],   #7
      [(2013,1,1,16,34,10), 1000, 12],  #8
      [(2013,1,1,16,59,10), 1600, 15],  #9
      
      [(2013,1,1,17,30,10), 1250, 12],  #10 -
      [(2013,1,1,17,31,10), 1255, 15],  #11
      [(2013,1,1,17,32,10), 1600, 2],   #12
      
      [(2013,1,1,18,11,10), 1700, 4],   #13 -
      [(2013,1,1,18,12,10), 1690, 5],   #14
    ]

    print '-----'

    # 15-16   -> o:1400|h
    def get_bar(dd):
      bar_time = int(dd.strftime('%s'))/PriceBar.H1
      return PriceBar.all().filter('bar_interval =', PriceBar.H1).filter('bar_time =',bar_time).get()
    
    bar15h = get_bar(datetime(2013,1,1,15))
    self.assertEqual(bar15h.open, 1400*1e3)
    self.assertEqual(bar15h.high, 1600*1e3)
    self.assertEqual(bar15h.low,  1000*1e3)
    self.assertEqual(bar15h.close,1600*1e3)

    bar16h = get_bar(datetime(2013,1,1,16))
    self.assertEqual(bar16h.open, 2000*1e3)
    self.assertEqual(bar16h.high, 2000*1e3)
    self.assertEqual(bar16h.low,  1000*1e3)
    self.assertEqual(bar16h.close,1600*1e3)
    

    bar17h = get_bar(datetime(2013,1,1,17))
    self.assertEqual(bar17h.open, 1250*1e3)
    self.assertEqual(bar17h.high, 1600*1e3)
    self.assertEqual(bar17h.low,  1250*1e3)
    self.assertEqual(bar17h.close,1600*1e3)
    
    bar18h = get_bar(datetime(2013,1,1,18))
    self.assertEqual(bar18h.open, 1700*1e3)
    self.assertEqual(bar18h.high, 1700*1e3)
    self.assertEqual(bar18h.low,  1690*1e3)
    self.assertEqual(bar18h.close,1690*1e3)
    
    bar19h = get_bar(datetime(2013,1,1,19))
    self.assertEqual(bar19h.open, 1690*1e3)
    self.assertEqual(bar19h.high, 1690*1e3)
    self.assertEqual(bar19h.low,  1690*1e3)
    self.assertEqual(bar19h.close,1690*1e3)
    

      
