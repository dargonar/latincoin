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

class DepositCurrencyForm(Form):

  def __init__(self, formdata=None, obj=None, **kwargs):
    super(DepositCurrencyForm, self).__init__(formdata=formdata, obj=obj, **kwargs)
    
    ba_list = self.get_ba_list(kwargs.get('user'))
    if not len(ba_list):
      ba_list = [('', '')]
    
    self.bank_account.choices = ba_list

  amount        = TextField()
  bank_account  = SelectField(u'',[])

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
    if amount < sconf.min_curr_deposit:
      raise ValidationError(u'La cantidad minima para depositar es $%.2f' % sconf.min_curr_deposit)