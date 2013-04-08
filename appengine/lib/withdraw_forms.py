# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from wtforms import Form, BooleanField, TextField, SelectField
from wtforms import validators, ValidationError

from utils import is_valid_cbu, is_valid_bitcoin_address

class WithdrawForm(Form):
  def is_decimal(self, val):

    try:
      dummy = Decimal(val)
      return True
    except:
      return False

  def validate_amount(self, field):

    if not self.is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

  def validate_address(self, field):
    if not is_valid_bitcoin_address(field.data):
      raise ValidationError(u'La dirección es inválida')
  
  def validate_cbu(self, field):
    if not is_valid_cbu(field.data):
      raise ValidationError(u'El CBU es inválido')

class WithdrawBTCForm(WithdrawForm):
  btc_address   = TextField()
  btc_amount    = TextField()
  #btc_pin       = TextField() 
  
  def validate_btc_amount(self, field):
    return self.validate_amount(field)

  def validate_btc_address(self, field):
    return self.validate_address(field)

  def amount(self):
    return Decimal(self.btc_amount.data)

  def address(self):
    return self.btc_address.data

  
class WithdrawCurrencyForm(WithdrawForm):

  currency_amount  = TextField()
  currency_cbu     = SelectField(choices=[('','')])
  #currency_pin     = TextField() 
  
  def validate_currency_amount(self, field):
    return self.validate_amount(field)

  def validate_currency_cbu(self, field):
    return self.validate_cbu(field)

  def amount(self):
    return Decimal(self.currency_amount.data)

  def cbu(self):
    return self.currency_cbu.data
