# -*- coding: utf-8 -*-
import decimal

from google.appengine.ext import db
from appengine_properties import DecimalProperty

class Dummy(db.Model):
  pass

class Account(db.Model):
  name                  = db.StringProperty() 
  email                 = db.StringProperty()
  bitcoin_address       = db.StringProperty()
  password              = db.StringProperty(indexed=False)
  time_zone             = db.StringProperty(indexed=False)
  
  reset_password_token  = db.StringProperty()

  confirmation_token    = db.StringProperty()
  confirmation_sent_at  = db.DateTimeProperty()
  confirmed_at          = db.DateTimeProperty()

  sign_in_count         = db.IntegerProperty(default=0)
  current_sign_in_at    = db.DateTimeProperty()
  last_sign_in_at       = db.DateTimeProperty()
  current_sign_in_ip    = db.StringProperty()
  last_sign_in_ip       = db.StringProperty()
  failed_attempts       = db.IntegerProperty(default=0)
  
  unlock_token          = db.StringProperty()
  locked_at             = db.DateTimeProperty()

  authentication_token  = db.StringProperty()
  ga_otp_secret         = db.StringProperty()
  last_address_refresh  = db.DateTimeProperty()
  require_ga_otp        = db.IntegerProperty()
  full_name             = db.StringProperty()
  address               = db.TextProperty()
  notify_on_trade       = db.IntegerProperty()
  commission_rate       = DecimalProperty(required=True, default=decimal.Decimal('0.006'))
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class AccountBalance(db.Model):
  
  def __repr__(self):
    return 'bal: %s %s %.5f' % (self.account.key() if self.account.key().name() is None else self.account.key().name(), self.currency, self.amount)

  def available(self):
    return self.amount - self.amount_comp

  account               = db.ReferenceProperty(Account, collection_name='balances', required=True) 
  currency              = db.StringProperty(required=True)
  amount                = DecimalProperty(default=decimal.Decimal('0'))
  amount_comp           = DecimalProperty(default=decimal.Decimal('0'))

class AccountOperation(db.Model):
  XCHG_FEE     = 'XF'

  MONEY_IN     = 'MI'
  MONEY_OUT    = 'MO'

  BTC_BUY      = 'BB'
  BTC_SELL     = 'BS'

  STATE_PENDING  = 'P'
  STATE_ACCEPTED = 'A'
  STATE_CANCELED = 'C'
  STATE_DONE     = 'D'
  
  def __repr__(self):
    return 'ao: %s %s %s %.5f' % (self.operation_type, self.account.key(), self.currency, self.amount)

  operation_type        = db.StringProperty(choices=[BTC_BUY,BTC_SELL,MONEY_IN,MONEY_OUT,XCHG_FEE], required=True)
  account               = db.ReferenceProperty(Account, collection_name='accounts', required=True)
  address               = db.StringProperty()
  amount                = DecimalProperty(required=True)
  currency              = db.StringProperty(required=True)
  bt_tx_id              = db.StringProperty()
  bt_tx_from            = db.StringProperty()
  bt_tx_confirmations   = db.IntegerProperty()
  payee                 = db.ReferenceProperty(Account, collection_name='payees')
  comment               = db.StringProperty()
  state                 = db.StringProperty(choices=[STATE_PENDING,STATE_ACCEPTED,STATE_CANCELED,STATE_DONE], required=True)
  bank_account_id       = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)


class BankAccount(db.Model):
  user                  = db.ReferenceProperty(Account, collection_name='bank_accounts')
  cbu                   = db.StringProperty()
  account_holder        = db.StringProperty()
  state                 = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class TradeOrder(db.Model):
  
  def __repr__(self):
    return 'to: amount:%s amount_orig:%s ppc:%.5f %s' % (self.amount, self.original_amount, self.ppc, self.status)

  LIMIT_ORDER  = 'L'
  MARKET_ORDER = 'M'

  ASK_ORDER    = 'A'
  BID_ORDER    = 'B'

  ORDER_ACTIVE    = 1
  ORDER_CANCELED  = 2
  ORDER_COMPLETED = 3

  user                  = db.ReferenceProperty(Account, required=True)
  original_amount       = DecimalProperty(required=True)
  amount                = DecimalProperty(required=True)
  ppc                   = DecimalProperty(default=decimal.Decimal('0'))
  ppc_int               = db.IntegerProperty(required=True)
  currency              = db.StringProperty(required=True)
  status                = db.IntegerProperty(required=True, choices=[ORDER_ACTIVE, ORDER_CANCELED, ORDER_COMPLETED])
  bid_ask               = db.StringProperty(required=True, choices=[ASK_ORDER, BID_ORDER])
  order_type            = db.StringProperty(required=True, choices=[LIMIT_ORDER, MARKET_ORDER])
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

  def is_bid(self):
    return self.bid_ask == self.BID_ORDER

  def is_ask(self):
    return not is_bid()

class Operation(db.Model):

  def __repr__(self):
    return 'op: btc:%.5f cur:%.5f ppc:%.5f ' % (self.traded_btc, self.traded_currency, self.ppc)

  OPERATION_PENDING = 'P'
  OPERATION_DONE    = 'D'

  purchase_order        = db.ReferenceProperty(TradeOrder, collection_name='purchases')
  sale_order            = db.ReferenceProperty(TradeOrder, collection_name='sales')
  traded_btc            = DecimalProperty(required=True)
  traded_currency       = DecimalProperty(required=True)
  ppc                   = DecimalProperty(required=True)
  currency              = db.StringProperty(required=True)
  seller                = db.ReferenceProperty(Account, collection_name='sellers')
  buyer                 = db.ReferenceProperty(Account, collection_name='buyers')
  status                = db.StringProperty(required=True, choices=[OPERATION_PENDING, OPERATION_DONE])
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)
