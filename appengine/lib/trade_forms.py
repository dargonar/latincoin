# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from wtforms import Form, BooleanField, TextField
from wtforms import validators, ValidationError

from models import get_system_config

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

    if Decimal(field.data) <= 0:
      raise ValidationError(u'Debe ser mayor que 0')

  def validate_ppc(self, field, market):

    if self.market():
      return

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')
    
    logging.error(field.data)

    if Decimal(field.data) <= 0:
      raise ValidationError(u'Debe ser mayor que 0')

class AskForm(TradeForm):
  ask_amount = TextField()
  ask_ppc    = TextField()
  ask_total  = TextField()
  ask_market = BooleanField() 
  
  def validate_ask_amount(self, field):
    self.validate_amount(field)

    sconf = get_system_config()
    amount = Decimal(field.data)

    if amount > Decimal('21e8'):
      raise ValidationError(u'Mas de 21M ... seguro?')

    if amount < sconf.min_ask_amount:
      raise ValidationError(u'No puede ser menor a %.8f BTC' % sconf.min_ask_amount )

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

    sconf = get_system_config()
    amount = Decimal(field.data)

    if amount > Decimal('21e8'):
      raise ValidationError(u'Más de 21M ... seguro?')

    if amount < sconf.min_bid_amount:
      raise ValidationError(u'No puede ser menor a %.8f BTC' % sconf.min_bid_amount )

  def validate_bid_ppc(self, field):
    return self.validate_ppc(field, self.bid_market)

  def amount(self):
    return self.bid_amount.data

  def market(self):
    return self.bid_market.data

  def ppc(self):
    return self.bid_ppc.data
