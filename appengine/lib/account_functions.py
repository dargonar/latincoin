# -*- coding: utf-8 -*-

from models import AccountBalance
from google.appengine.ext import db

def get_account_balance(account):

  # TODO: assert input
  assert(account is not None), u'Account invalida'
  if isinstance(account, basestring):
    account = db.Key(account)

  balances = AccountBalance.all().ancestor(account).filter('account =', account).fetch(100)
  assert(balances is not None), u'No tiene balance'
  assert(len(balances) >= 2), u'No tiene todos los balances %s => %s' % (len(balances),account.key())
  assert(len(balances) == 2), u'Tiene muchos balances! (%d)' % len(balances)

  balance = {}
  for b in balances:
    balance[b.currency] = b

  assert('ARS' in balance), u'No tiene balance en ARS'
  assert('BTC' in balance), u'No tiene balance en BTC'

  return balance
