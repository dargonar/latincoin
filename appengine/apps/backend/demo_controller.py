# -*- coding: utf-8 -*-
import logging

from decimal import Decimal
from random import uniform

from google.appengine.ext import db
from google.appengine.ext import deferred

from webapp2 import RequestHandler
from config import config

from models import Account, TradeOrder, AccountBalance, Dummy, Operation, AccountOperation, create_password



class GenerateTradeData(RequestHandler):
  def generate(self, **kwargs):
    return
    from _my_test_utils import TestUtilMixin
    mTestUtilMixin = TestUtilMixin()
    b = mTestUtilMixin.generate_trade_operations()
    if b:
      self.response.write('deberiamos haber creado todo :)')
    self.response.write('<br/>ready!')
    
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
    return
  