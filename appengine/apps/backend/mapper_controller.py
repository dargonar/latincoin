# -*- coding: utf-8 -*-
import fix_path

import logging
from decimal import Decimal
from random import uniform


from google.appengine.ext import db
from google.appengine.ext import deferred

from webapp2 import RequestHandler
from config import config

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation, Ticker, create_password
from trader import Trader

from my_test_utils import TestUtilMixin

from my_mapper import TickerMapper, OperationNotificationMapper

class RunTickerMapper(RequestHandler):
  def build(self, **kwargs):
    
    #self.delete_all(False)
    for ticker in Ticker.all().filter('status =', Ticker.IN_PROGRESS):
      db.delete(ticker)
      logging.info('Ticker IN-PROGRESS borrado')
      
    last_ticker = Ticker.all().order('-created_at').get()
    if last_ticker is None:
      pass
    
    mTestUtilMixin = TestUtilMixin()
    b = mTestUtilMixin.generate_trade_operations()
    if b:
      self.response.write('deberiamos haber creado todo :)')
    self.response.write('<br/>ready!')
    return
    
    mapper = TickerMapper(str(last_ticker.key()))
    deferred.defer(mapper.run)
    self.response.write('TickerMapper corriendo')
  
  def delete_all(self, delete_ticker=True):
    for user in Account.all():
      if str(user.key()) not in ['ag9kZXZ-YnRjLXhjaGFuZ2VyDQsSB0FjY291bnQYAww', 'ag9kZXZ-YnRjLXhjaGFuZ2VyEQsSB0FjY291bnQiBHhjaGcM']:
        db.delete(user)
    for accbal in AccountBalance.all():
      if accbal.key().name()=='xchg-ars' or accbal.key().name()=='xchg-btc':
        continue
      db.delete(accbal)
    for accoper in AccountOperation.all():
      db.delete(accoper)
    for trade in TradeOrder.all():
      db.delete(trade)
    for oper in Operation.all():
      db.delete(oper)
    if delete_ticker:
      for ticker in Ticker.all():
        db.delete(ticker)
    return
  
class RunOperationNotificationMapper(RequestHandler):
  def run(self, **kwargs):
    mapper = OperationNotificationMapper()
    deferred.defer(mapper.run)
    self.response.write('OperationNotificationMapper corriendo')