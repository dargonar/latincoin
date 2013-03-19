# -*- coding: utf-8 -*-
from decimal import Decimal

from wtforms import Form, BooleanField, TextField
from wtforms import validators, ValidationError

class TradeForm(Form):
  def __repr__(self):
    return 'TradeForm'

  def is_decimal(self, val):

    try:
      dummy = Decimal(val)
      return True
    except:
      return False

  def validate_amount(self, field):

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

  def validate_ppc(self, field):
    if self.market.data:
      return

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

  amount = TextField()
  ppc    = TextField()
  market = BooleanField()
