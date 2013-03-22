# -*- coding: utf-8 -*-
from decimal import Decimal

from wtforms import Form, BooleanField, TextField
from wtforms import validators, ValidationError

class TradeForm(Form):

  def is_decimal(self, val):

    try:
      dummy = Decimal(val)
      return True
    except:
      return False

  def validate_amount(self, field):

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

  def validate_ppc(self, field, market):
    if market.data:
      return

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')


class AskForm(TradeForm):
  ask_amount = TextField()
  ask_ppc    = TextField()
  ask_total  = TextField()
  ask_market = BooleanField() 
  
  def validate_ask_amount(self, field):
    return self.validate_amount(field)

  def validate_ask_ppc(self, field):
    return self.validate_ppc(field, self.ask_market)

  def amount(self):
    return self.ask_amount.data

  def market(self):
    return self.ask_market.data

  def ppc(self):
    return self.ask_ppc.data

class BidForm(TradeForm):
  bid_amount = TextField()
  bid_total  = TextField()
  bid_ppc    = TextField()
  bid_market = BooleanField() 
  
  def validate_bid_amount(self, field):
    return self.validate_amount(field)

  def validate_bid_ppc(self, field):
    return self.validate_ppc(field, self.bid_market)

  def amount(self):
    return self.bid_amount.data

  def market(self):
    return self.bid_market.data

  def ppc(self):
    return self.bid_ppc.data
