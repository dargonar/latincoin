# -*- coding: utf-8 -*-
from google.appengine.ext import db
from appengine_properties import DecimalProperty

class Account(db.Model):
  name                  = db.StringProperty() 
  email                 = db.StringProperty()
  bitcoin_address       = db.StringProperty()
  password              = db.StringProperty(indexed=False)
  password_salt         = db.StringProperty(indexed=False)
  time_zone             = db.StringProperty(indexed=False)
  
  reset_password_token  = db.StringProperty(indexed=False)

  confirmation_token    = db.StringProperty(indexed=False)
  confirmation_sent_at  = db.DateProperty()
  confirmed_at          = db.DateProperty()

  sign_in_count         = db.IntegerProperty()
  current_sign_in_at    = db.DateProperty()
  last_sign_in_at       = db.DateProperty()
  current_sign_in_ip    = db.StringProperty()
  last_sign_in_ip       = db.StringProperty()
  failed_attempts       = db.IntegerProperty(indexed=False)
  
  unlock_token          = db.StringProperty(indexed=False)
  locked_at             = db.DateProperty()
  
  authentication_token  = db.StringProperty()
  ga_otp_secret         = db.StringProperty()
  last_address_refresh  = db.DateProperty()
  require_ga_otp        = db.IntegerProperty()
  full_name             = db.StringProperty()
  address               = db.TextProperty()
  notify_on_trade       = db.IntegerProperty()
  commission_rate       = DecimalProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class AccountOperation(db.Model):
  operation_type        = db.StringProperty()
  account               = db.ReferenceProperty(Account, collection_name='accounts') 
  address               = db.StringProperty()
  amount                = DecimalProperty()
  currency              = db.StringProperty()
  bt_tx_id              = db.StringProperty()
  bt_tx_from            = db.StringProperty()
  bt_tx_confirmations   = db.IntegerProperty()
  payee                 = db.ReferenceProperty(Account, collection_name='payees')
  email                 = db.StringProperty()
  px_tx_id              = db.StringProperty()
  px_payer              = db.StringProperty()
  px_fee                = DecimalProperty()
  comment               = db.StringProperty()
  state                 = db.StringProperty()
  bank_account_id       = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)


class BankAccount(db.Model):
  user                  = db.ReferenceProperty(Account)
  cbu                   = db.StringProperty()
  account_holder        = db.StringProperty()
  state                 = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class TradeOrder(db.Model):
  user                  = db.ReferenceProperty(Account)
  amount                = DecimalProperty()
  ppc                   = DecimalProperty()
  currency              = db.StringProperty()
  active                = db.IntegerProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class Operation(db.Model):
  purchase_order_id     = db.ReferenceProperty(TradeOrder, collection_name='purchases')
  sale_order_id         = db.ReferenceProperty(TradeOrder, collection_name='sales')
  traded_btc            = DecimalProperty()
  traded_currency       = DecimalProperty()
  ppc                   = DecimalProperty()
  currency              = db.StringProperty()
  seller_id             = db.ReferenceProperty(Account, collection_name='sellers')
  buyer_id              = db.ReferenceProperty(Account, collection_name='buyers')
  operation_type        = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)
