# -*- coding: utf-8 -*-
import logging
from decimal import Decimal
from google.appengine.ext import db

from wtforms import Form, BooleanField, TextField, SelectField
from wtforms import validators, ValidationError

from utils import is_valid_cbu, is_valid_bitcoin_address
from models import get_system_config, BankAccount, UserBitcoinAddress

from webapp2 import cached_property

def is_decimal(val):
  try:
    dummy = Decimal(val)
    return True
  except:
    return False

class WithdrawBTCForm(Form):

  def __init__(self, formdata=None, obj=None, **kwargs):
    super(WithdrawBTCForm, self).__init__(formdata=formdata, obj=obj, **kwargs)

    self.btc_address.choices = self.get_bitcoin_addresses(kwargs.get('user'))

  amount       = TextField()
  btc_address  = SelectField(u'',[validators.Required(message=u'Debe indicar una dirección.')])
  

  def get_bitcoin_addresses(self, user):
    query = UserBitcoinAddress.all()
    query = query.filter('active =', True)
    query = query.filter('account =', db.Key(user))

    return [(str(addy.address), addy.description + ' ('+addy.address+')') for addy in query]

  def validate_amount(self, field):
    
    if not is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

    sconf = get_system_config()

    amount = Decimal(field.data)
    if amount < sconf.min_btc_withdraw:
      raise ValidationError(u'La cantidad minima para retiro BTC es %.8f' % sconf.min_btc_withdraw)

  def validate_btc_address(self, field):
    if not is_valid_bitcoin_address(field.data):
      raise ValidationError(u'La dirección es inválida')


class WithdrawCurrencyForm(Form):

  def __init__(self, formdata=None, obj=None, **kwargs):
    super(WithdrawCurrencyForm, self).__init__(formdata=formdata, obj=obj, **kwargs)
    
    ba_list = self.get_ba_list(kwargs.get('user'))
    if not len(ba_list):
      ba_list = [('', '')]
    
    self.bank_account.choices = ba_list

  amount        = TextField()
  bank_account  = SelectField(u'',[validators.Required(message=u'Debe seleccionar una cuenta de banco.')])

  def get_ba_list(self, user):
    query = BankAccount.all().filter('active =', True)
    query = query.filter('account =', db.Key(user))
    query = query.order('created_at')
    return [(str(ba.key()), ba.description + ' ('+ba.cbu+')') for ba in query]

  def validate_amount(self, field):

    if not is_decimal(field.data):
      raise ValidationError(u'La cantidad ingresada es inválida')

    sconf = get_system_config()

    amount = Decimal(field.data)
    if amount < sconf.min_curr_withdraw:
      raise ValidationError(u'La cantidad minima para retiro es %.2f' % sconf.min_curr_withdraw)