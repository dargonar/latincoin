# -*- coding: utf-8 -*-
import decimal
import time

from datetime import datetime, timedelta

from google.appengine.ext import db, blobstore
from google.appengine.api import memcache

from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from config import config
from appengine.properties import DecimalProperty

def create_password(password):
  return generate_password_hash(password, method='sha256', pepper=config['my']['secret_key'])

class Dummy(db.Model):
  pass

def get_system_config():
  sconf = memcache.get('system-config')
  
  if not sconf:
    sconf = SystemConfig.get_by_key_name('system-config')
    memcache.set('system-config', sconf)

  return sconf

class SystemConfig(db.Model):
  remote_rpc              = db.StringProperty(choices=['ec2', 'blockchain'], default='ec2')
  confirmations           = db.StringProperty(default='6')
  trade_enable            = db.StringProperty(default='N')
  import_delay            = db.StringProperty(default='0')
  import_enable           = db.StringProperty(default='Y')
  forward_enable          = db.StringProperty(default='Y')
  
  min_btc_withdraw        = DecimalProperty(default=decimal.Decimal('0'))
  max_btc_withdraw        = DecimalProperty(default=decimal.Decimal('21e8'))

  min_curr_withdraw       = DecimalProperty(default=decimal.Decimal('0'))
  max_curr_withdraw       = DecimalProperty(default=decimal.Decimal('1e8'))

  min_curr_deposit        = DecimalProperty(default=decimal.Decimal('0'))
  max_curr_deposit        = DecimalProperty(default=decimal.Decimal('1e8'))
  
  max_ask_amount          = DecimalProperty(default=decimal.Decimal('21e8'))
  min_ask_amount          = DecimalProperty(default=decimal.Decimal('0'))

  max_bid_amount          = DecimalProperty(default=decimal.Decimal('21e8'))
  min_bid_amount          = DecimalProperty(default=decimal.Decimal('0'))

  def can_trade(self):
    return self.trade_enable == 'Y'
    
  def can_import(self):
    return self.import_enable == 'Y'

  def can_forward(self):
    return self.forward_enable == 'Y'

class Block(db.Model):
  number                = db.IntegerProperty(required=True)
  hash                  = db.StringProperty(required=True)
  txs                   = db.IntegerProperty(required=True)
  data                  = blobstore.BlobReferenceProperty()
  processed             = db.StringProperty(default='N')
  updated_at            = db.DateTimeProperty(auto_now=True)
  created_at            = db.DateTimeProperty(auto_now_add=True)

class Account(db.Model):
  name                  = db.StringProperty() 
  last_name             = db.StringProperty() 
  telephone             = db.StringProperty() 
  email                 = db.StringProperty()
  bitcoin_address       = db.StringProperty()
  password              = db.StringProperty(indexed=False)
  time_zone             = db.StringProperty(indexed=False)

  email_verified        = db.BooleanProperty(default=False)
  cuit                  = db.StringProperty()  
  
  identity_is_validated = db.BooleanProperty(default=False)
  address_is_validated  = db.BooleanProperty(default=False)
  
  reset_password_token  = db.StringProperty()
  last_resetpass_at     = db.DateTimeProperty()
  last_resetpass_ip     = db.StringProperty()

  confirmation_token    = db.StringProperty()
  confirmation_sent_at  = db.DateTimeProperty()
  confirmed_at          = db.DateTimeProperty()

  sign_in_count         = db.IntegerProperty(default=0)
  current_sign_in_at    = db.DateTimeProperty()
  last_sign_in_at       = db.DateTimeProperty()
  current_sign_in_ip    = db.StringProperty()
  last_sign_in_ip       = db.StringProperty()
  
  last_failed_at        = db.DateTimeProperty()
  last_failed_ip        = db.StringProperty()
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
  
  last_changepass_at    = db.DateTimeProperty()
  last_changepass_ip    = db.StringProperty()
  last_bad_changepass_at= db.DateTimeProperty()
  last_bad_changepass_ip= db.StringProperty()
    
  def fail_change_pass(self, remote_addr):
    self.last_bad_changepass_at = datetime.now()
    self.last_bad_changepass_ip = remote_addr

  def change_password(self, new_password, remote_addr, is_reset=False):
    old_password = self.password
  
    self.password = generate_password_hash(new_password, method='sha256', pepper=config['my']['secret_key'])
    self.failed_attempts = 0
    
    if is_reset:
      self.reset_password_token = ''
      self.last_reset_at        = datetime.now()
      self.last_reset_ip        = remote_addr
    else:
      self.last_changepass_at   = datetime.now()
      self.last_changepass_ip   = remote_addr

    to_save.append(self)
    return to_save
    
  def create_reset_token(self):
    self.reset_password_token = generate_random_string(length=40)

  def login(self, remote_addr):
    self.sign_in_count        = self.sign_in_count + 1
    self.last_sign_in_at      = self.current_sign_in_at
    self.current_sign_in_at   = datetime.now()
    self.last_sign_in_ip      = self.current_sign_in_ip
    self.current_sign_in_ip   = remote_addr
    self.reset_password_token = ''
    self.failed_attempts      = 0

  def failed_login(self, remote_addr):
    self.failed_attempts = self.failed_attempts + 1
    self.last_failed_at  = datetime.now()
    self.last_failed_ip  = remote_addr

  def has_password(self, password):
    return check_password_hash(password, self.password, config['my']['secret_key'])

  def is_active(self):
    return self.confirmed_at != None

  def user_need_captcha(self):
    return self.failed_attempts > 5

  def can_confirm(self):
    return ((datetime.now() - self.confirmation_sent_at).seconds < 3600 and self.confirmed_at is None)
  
  def confirm(self):
    self.email_verified     = True
    self.confirmed_at       = datetime.now()
    self.confirmation_token = ''

  def validate_email(self):
    self.email_verified     = True
    self.confirmed_at       = datetime.now()
    self.confirmation_token = ''

  @classmethod
  def new_user(klass, email, password):
    user = Account()
    user.email                 = email
    user.password              = generate_password_hash(password, method='sha256', pepper=config['my']['secret_key'])
    user.confirmation_token    = generate_random_string(length=40)
    user.confirmation_sent_at  = datetime.now()
    return user

class BankAccount(db.Model):
  account               = db.ReferenceProperty(Account, collection_name='bank_accounts')
  cbu                   = db.StringProperty()
  description           = db.StringProperty(required=True)
  account_holder        = db.StringProperty()
  state                 = db.StringProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)
  active                = db.BooleanProperty(default=True)
  def __repr__(self):
    return u'%s [%s]%s' % (self.description, self.cbu, ('' if self.active else ' - DESACTIVADA'))
    
class UserBitcoinAddress(db.Model):
  address         = db.StringProperty(required=True)
  description     = db.StringProperty(required=True)
  account         = db.ReferenceProperty(Account, required=True)
  created_at      = db.DateTimeProperty(auto_now_add=True)
  updated_at      = db.DateTimeProperty(auto_now=True)
  active          = db.BooleanProperty(default=True)
  def __repr__(self):
    return u'%s [%s]%s' % (self.description, self.address, ('' if self.active else ' - DESACTIVADA'))
    
class AccountValidationFile(db.Model):
  VALIDATION_IDENTITY     = u'identidad'
  VALIDATION_ADDRESS      = u'domicilio'
  VALIDATION_UNDEFINED    = u'undefined' 
  
  serving_url         = db.StringProperty(required=True)
  file                = blobstore.BlobReferenceProperty(required=True)
  filename            = db.StringProperty(required=True)
  filetype            = db.StringProperty(required=True)
  filesize            = db.StringProperty()
  account             = db.ReferenceProperty(Account, required=True)
  created_at          = db.DateTimeProperty(auto_now_add=True)
  validation_type     = db.StringProperty(choices=[VALIDATION_IDENTITY, VALIDATION_ADDRESS, VALIDATION_UNDEFINED], required=True)
  is_valid            = db.BooleanProperty(default=False)
  not_valid_reason    = db.StringProperty(indexed=False)
  def __repr__(self):
    return u'Validación de %s: %s.' % (self.validation_type, ('VALIDO' if self.is_valid else 'INVALIDO'))
  
  def isIdentityType(self, _type):
    return _type==VALIDATION_IDENTITY
  
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
  
  def is_money_out(self):
    return self.operation_type == self.MONEY_OUT

  def is_money_in(self):
    return self.operation_type == self.MONEY_IN

  def is_done(self):
    return self.state == self.STATE_DONE

  def is_accepted(self):
    return self.state == self.STATE_ACCEPTED

  def is_pending(self):
    return self.state == self.STATE_PENDING

  def is_canceled(self):
    return self.state == self.STATE_CANCELED

  def is_btc(self):
    return self.currency == 'BTC'

  def set_cancel(self):
    self.state = self.STATE_CANCELED

  def set_accepted(self):
    self.state = self.STATE_ACCEPTED

  def set_done(self):
    self.state = self.STATE_DONE

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
  bank_account          = db.ReferenceProperty(BankAccount)
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
  
  OPERATION_BUY     = 'B'
  OPERATION_SELL    = 'S'
  
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
  type                  = db.StringProperty(required=True, choices=[OPERATION_BUY, OPERATION_SELL]) # , 'BUY', 'SELL', 'NA'
  
  buyer_was_notified    = db.BooleanProperty(default=False)
  seller_was_notified   = db.BooleanProperty(default=False)
  traders_were_notified = db.BooleanProperty(default=False, indexed=True)
  last_notification     = db.DateTimeProperty()
  
class BitcoinAddress(db.Model):
  user                  = db.ReferenceProperty(Account, collection_name='bitcoin_addresses', required=True)
  address               = db.StringProperty(required=True)
  private_key           = db.StringProperty(required=True)
  created_at            = db.DateTimeProperty(auto_now_add=True)

class ForwardTx(db.Model):
  tx                    = db.StringProperty(required=True)
  tx_fw                 = db.StringProperty()
  tx_raw                = db.TextProperty()
  in_block              = db.IntegerProperty()
  out_block             = db.IntegerProperty()
  user                  = db.ReferenceProperty(Account)
  address               = db.ReferenceProperty(BitcoinAddress)
  value                 = DecimalProperty(required=True)
  index                 = db.StringProperty(required=True)
  forwarded             = db.StringProperty(default='N')
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)

class PriceBar(db.Model):
  
  def __repr__(self):
    return 'pb: %s o:%08d h:%08d l:%08d c:%08d v:%08d' % ( datetime.fromtimestamp(self.bar_time*self.bar_interval), self.open, self.high, self.low, self.close, self.volume) 
 
  M1    = 60
  H1    = 3600
  H24   = 86400

  open                  = db.IntegerProperty(required=True)
  high                  = db.IntegerProperty(required=True)
  low                   = db.IntegerProperty(required=True)
  close                 = db.IntegerProperty(required=True)
  volume                = db.IntegerProperty(required=True)
  
  bar_time              = db.IntegerProperty(required=True)
  bar_interval          = db.IntegerProperty(required=True, choices=[M1,H1,H24])

  year                  = db.IntegerProperty(required=True)
  month                 = db.IntegerProperty(required=True)
  day                   = db.IntegerProperty(required=True)
  created_at            = db.DateTimeProperty(auto_now_add=True)

  def next_bar(self):
    now = time.time()

    current_time_bar = int(now/self.bar_interval)
    next_bar_time    = self.bar_time + 1
    
    if current_time_bar >= next_bar_time:
      return (True, next_bar_time)

    return (False, 0)

# <keyname= 'welcome' + LANG>
# un registro por idioma    
class JinjaTemplate(db.Model):
  name                  = db.StringProperty(indexed=True)
  language              = db.StringProperty(choices=['es', 'en', 'pt'], default='es', indexed=True)
  source                = db.TextProperty(indexed=False)
  last_read             = db.DateTimeProperty()
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)
  type                  = db.StringProperty(indexed=False, default='txt')
  
# <keyname= 'mail_' + JinjaTemplate.key_name + LANG>
# un registro por idioma
class MailTemplate(db.Model):
  name                  = db.StringProperty()
  subject               = db.StringProperty()
  language              = db.StringProperty(choices=['es', 'en', 'pt'], default='es', indexed=True)
  body_txt              = db.ReferenceProperty(JinjaTemplate, collection_name='txt_mail_templates')
  #body_html             = db.ReferenceProperty(JinjaTemplate, collection_name='html_mail_templates')
  
  created_at            = db.DateTimeProperty(auto_now_add=True)
  updated_at            = db.DateTimeProperty(auto_now=True)
  
  NAME_PREFIX = 'mail_'
  
  def get_jinja_template(self):
    if self.name is None or self.name.count(MailTemplate.NAME_PREFIX)<1:
      return None
    # Le quitamos el prefijo 'mail_' y buscamos el template por keyname
    template_name = self.name.replace(MailTemplate.NAME_PREFIX, '')
    return JinjaTemplate.get_by_key_name(template_name)
    
