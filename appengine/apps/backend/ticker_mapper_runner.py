# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib'))

# sys.path[0:0] = ['../appengine/lib', '../appengine/distlib', '../appengine']

import logging
from decimal import Decimal
from random import uniform


from google.appengine.ext import db
from google.appengine.ext import deferred

from webapp2 import RequestHandler
from config import config

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation, Ticker, create_password
from trader import Trader

# from account_functions import get_account_balance
# from my_test_utils import TestUtilMixin

from my_mapper import TickerMapper

class RunTickerMapper(RequestHandler): #, TestUtilMixin
  users = []
  
  def delete_all(self, delete_ticker=True):
    for user in Account.all():
      if str(user.key()) not in ['ag9kZXZ-YnRjLXhjaGFuZ2VyDQsSB0FjY291bnQYAww', 'ag9kZXZ-YnRjLXhjaGFuZ2VyEQsSB0FjY291bnQiBHhjaGcM']:
        db.delete(user)
    for accoper in AccountOperation.all():
      db.delete(accoper)
    for accbal in AccountBalance.all():
      if accbal.key().name()=='xchg-ars' or accbal.key().name()=='xchg-btc':
        continue
      db.delete(accbal)
    for oper in Operation.all():
      db.delete(oper)
    for trade in TradeOrder.all():
      db.delete(trade)
    if delete_ticker:
      for ticker in Ticker.all():
        db.delete(ticker)
    return
  
  # def generate_trade_operations(self):
    # # generamos un ticker, el primero y mas puto de todos
    # last_ticker = Ticker( status                = Ticker.DONE,
                          # last_price            = Decimal('0.0'),
                          # avg_price             = Decimal('0.0'),
                          # high_price            = Decimal('0.0'),
                          # low_price             = Decimal('0.0'),
                          # volume                = Decimal('0.0'),  
                          # last_price_slope      = 0,
                          # avg_price_slope       = 0,
                          # high_price_slope      = 0,
                          # low_price_slope       = 0,
                          # volume_slope          = 0,
                          # open                  = Decimal('0.0'),  
                          # close                 = Decimal('0.0'), 
                        # )
    # last_ticker.put()
    
    
    # # generamos 5 operaciones
    # trader = Trader()
    # for i in xrange(10):
    
      # user = self.aux_create_new_user('usuario%d@test.com' % i)
      # self.users.append(user)
      # for i in xrange(int(uniform(1,5))):

        # ars = Decimal(50000)
        # btc = Decimal(1000)

        # dep_ars = self.aux_deposit_ars(user,ars)
        # dep_btc = self.aux_deposit_btc(user,btc)
        
        # b = get_account_balance(user)
        # b['ARS'].amount += ars
        # b['BTC'].amount += btc

        # db.put([b['ARS'],b['BTC']])
      # #trade = trader.add_limit_trade(str(user.key()), TradeOrder.BID_ORDER, Decimal('5.0'), Decimal('5.0'))
      # #logging.info('trade: %s', trade)
  
    # # Agregamos ordenes random
    # for i in xrange(100):
      
      # user = str(self.users[int(uniform(0,10))].key())
      # bal  = get_account_balance(user)

      # r = None

      # # 50% chances de meter bid o ask
      # if uniform(1,100) > 50:
        # r = self.aux_add_random_bid(user, 1, 10, 100, 200)
      # else:
        # r = self.aux_add_random_ask(user, 1, 10, 150, 250)

      # logging.info(' Trade metida? [%s] balance:[%s]',r, bal)
      # res = trader.match_orders() 
      # if res[0] is not None:
        # rop = trader.apply_operation( str(res[0].key()) )
        # logging.info(' Oper realizada? [%s]',rop)
        
    # # Corremos las ultimas veces hasta que no se toquen las puntas
    # print 'corremos una mas ...'
    # res = trader.match_orders()
    # while res[0] is not None:
      # print 'print una mas ...'
      # trader.apply_operation(str(res[0].key()))
      # res = trader.match_orders()

    # bba = self.aux_get_best_bid_ask()
    # return True
    
  def build_ticker(self, **kwargs):
    
    #self.delete_all(False)
    for ticker in Ticker.all().filter('status =', Ticker.IN_PROGRESS):
      db.delete(ticker)
      logging.info('Ticker IN-PROGRESS borrado')
      
    last_ticker = Ticker.all().order('-created_at').get()
    if last_ticker is None:
      pass
      #b = self.generate_trade_operations()
      #if b:
        #self.response.write('deberiamos haber creado todo :)')
    
    mapper = TickerMapper(str(last_ticker.key()))
    
    deferred.defer(mapper.run)
    self.response.write('TickerMapper corriendo')