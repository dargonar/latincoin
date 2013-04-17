# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import urllib
import time

from datetime import datetime, timedelta
from decimal import Decimal

import re

import hashlib

from google.appengine.api import memcache
from google.appengine.ext import db, blobstore
from google.appengine.api import files

from webapp2 import abort, cached_property, RequestHandler, Response, HTTPException, uri_for as url_for, get_app
from webapp2_extras import jinja2, sessions, json

from models import AccountBalance , Account
from exchanger import get_account_balance

from filters import *

def read_blobstore_file(blob_key):  
  blob_reader = blobstore.BlobReader(blob_key)
  value = blob_reader.read()
  return value

def remove_blobstore_file(blob_key):
  blobstore.delete(blob_key)

def create_blobstore_file(data, name, mime_type='application/octet-stream'):

  file_name = files.blobstore.create(mime_type=mime_type,_blobinfo_uploaded_filename=name)
  
  with files.open(file_name, 'a') as f:
    f.write(data)

  files.finalize(file_name)

  blob_key = files.blobstore.get_blob_key(file_name)

  # ------ BEGIN HACK -------- #
  # GAE BUG => http://code.google.com/p/googleappengine/issues/detail?id=5142
  for i in range(1,10):
    if not blob_key:
      time.sleep(0.5)
      blob_key = files.blobstore.get_blob_key(file_name)
    else:
      break
  
  return blob_key
  # ------ END HACK -------- #

class need_admin_auth(object):
  def __init__(self, code=0, url='backend-login'):
    self.url      = url
    self.code     = code

  def __call__(self, f):
    def validate_user(handler, *args, **kwargs):
      if handler.is_logged and handler.is_admin:
        return f(handler, *args, **kwargs)
      
      if self.code:
        handler.abort(self.code)
      else:
        return handler.redirect_to(self.url)
      
    return validate_user

class need_auth(object):
  def __init__(self, code=0, url='account-login'):
    self.url      = url
    self.code     = code

  def __call__(self, f):
    def validate_user(handler, *args, **kwargs):
      if handler.is_logged:
        return f(handler, *args, **kwargs)
      
      if self.code:
        handler.abort(self.code)
      else:
        return handler.redirect_to(self.url)
      
    return validate_user
  
def get_or_404(key, code=404, msg='not found'):
  try:
      obj = db.get(key)
      if obj:
          return obj
  except db.BadKeyError, e:
      # Falling through to raise the NotFound.
      pass

  abort(code,title=msg)

class FlashBuildMixin(object):
  def set_error(self, msg):
    self.session.add_flash(self.build_error(msg))
    
  def set_ok(self, msg):
    self.session.add_flash(self.build_ok(msg))
    
  def set_info(self, msg):
    self.session.add_flash(self.build_info(msg))
    
  def set_warning(self, msg):
    self.session.add_flash(self.build_warning(msg))
  
  def build_error(self, msg):
    return { 'type':'error', 'message':msg }
    
  def build_ok(self, msg):
    return { 'type':'success', 'message':msg }
  
  def build_info(self, msg):
    return { 'type':'info', 'message':msg }
    
  def build_warning(self, msg):
    return { 'type':'warning', 'message':msg }
    
class Jinja2Mixin(object):
  
  @cached_property
  def jinja2(self):
    j2 = jinja2.get_jinja2(app=self.app)
      
    self.setup_jinja_enviroment(j2.environment)
      
    # Returns a Jinja2 renderer cached in the app registry.
    return j2

  def setup_jinja_enviroment(self, env):
    env.globals['url_for'] = self.uri_for
    
    if hasattr(self.session, 'get_flashes'):
      flashes = self.session.get_flashes()
      env.globals['flash'] = flashes[0][0] if len(flashes) and len(flashes[0]) else None
    
    env.globals['session']      = self.session
    env.globals['is_logged']    = self.is_logged
    env.globals['is_admin']     = self.is_admin
    env.globals['is_verified']  = self.is_verified
    env.globals['ars_balance']  = self.ars_balance
    env.globals['btc_balance']  = self.btc_balance
    env.globals['user_name']    = self.user_name
    
    
    # cargamos el ticker
    #env.globals['ticker']         = self.ticker
    env.filters['marketarrowfy']            = do_marketarrowfy
    env.filters['label_for_order']          = do_label_for_order
    env.filters['orderamountfy']            = do_orderamountfy
    env.filters['time_distance_in_words']   = do_time_distance_in_words
    env.filters['short_time_distance_in_words']  = do_short_time_distance_in_words
    env.filters['label_for_oper']           = do_label_for_oper
    env.filters['operation_type']           = do_operation_type
    env.filters['format_btc']               = do_format_btc
    env.filters['label_for_user_identity']  = do_label_for_user_identity
    
  def render_response(self, _template, **context):
    # Renders a template and writes the result to the response.
    rv = self.jinja2.render_template(_template, **context)
    self.response.write(rv)
  
  def render_template(self, _template, **context):
    # Renders a template and writes the result to the response.
    rv = self.jinja2.render_template(_template, **context)
    return rv
      
class MyBaseHandler(RequestHandler, Jinja2Mixin, FlashBuildMixin):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store   = sessions.get_store(request=self.request)
    self.request.charset = 'utf-8'
    
    try:
      # Dispatch the request.
      RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)

  @cached_property
  def session(self):
    # Returns a session using the default cookie key.
    return self.session_store.get_session()
  
  def render_json_response(self, *args, **kwargs):
    self.response.content_type = 'application/json'
    self.response.write(json.encode(*args, **kwargs))
    
  # def handle_exception(self, exception=None, debug=False):
  #   logging.exception(exception)
    
  #   text = 'Se ha producido un error en el servidor,<br/>intenta volver al inicio'
  #   code = 500
    
  #   if isinstance(exception,HTTPException):
  #     if exception.code == 404:
  #       text = u'La página solicitada no ha sido encontrada,<br/>intenta volver al inicio'
      
  #     code = exception.code
    
  #   self.render_response('error.html', code=code, text=text )
  #   self.response.status = str(code)+' '

  @cached_property
  def config(self):
    return get_app().config
    
class FrontendHandler(MyBaseHandler):

  def do_login(self, user):

    balance = get_account_balance(user)
    self.session['account.btc']     = str(balance['BTC'].key())
    self.session['account.ars']     = str(balance['ARS'].key())
    self.session['account.user']    = str(user.key())
    self.session['account.logged']  = True
    self.session['account.rol']     = user.rol
    self.update_user_info(user)
  
  def update_user_info(self, user):
    self.session['account.name'] = user.name if user.name and len(user.name) else user.email
    self.session['account.verified'] = user.email_verified
  
  # @property
  # def ticker(self):
    # data = memcache.get('ticker')
    # if data is None:
      # last_ticker = Ticker.all() \
              # .order('created_at') \
              # .get()
      
      # data = SessionTicker(last_ticker)
      # memcache.add('ticker', data, 60)
    # return data 
 
  def do_logout(self):
    self.session.clear()

  @property
  def btc_balance(self):
    return self.try_get_balance('btc') # '%.8f' % 

  @property
  def ars_balance(self):
    return '%.2f' % self.try_get_balance('ars')

  @property
  def is_logged(self):
    return self.session_value('account.logged', False)
  
  @property 
  def is_admin(self):
    return self.session_value('account.rol', None)==Account.ADMIN_ROL
    
  @property
  def is_verified(self):
    return self.session_value('account.verified', False)

  @property
  def user_name(self):
    return self.session_value('account.name', '---')

  @property
  def user(self):
    return self.session_value('account.user')

  def try_get_balance(self, currency):
    tmp = self.session_value('account.%s' % currency, None)
    if tmp is None:
      return Decimal('0')

    balance = AccountBalance.get(tmp)
    return (balance.amount - balance.amount_comp)

  def session_value(self, key, default=None):
    return self.session[key] if key in self.session else default

  def mine_or_404(self, key, code=404, msg='not found'):
    obj = get_or_404(key)

    if hasattr(obj,'user') and str(obj.user.key()) == self.user:
      return obj

    if hasattr(obj,'account') and str(obj.account.key()) == self.user:
      return obj

    abort(code, title=msg)
  
class SessionTicker(object):
  def __init__(self, last_ticker=None):
    self.ticker_data = last_ticker
    
  # Ticker Data
  @property
  def lastprice(self):
    return '%.5f' % (self.ticker_data.last_price if self.ticker_data is not None else Decimal('0'))

  @property
  def lastprice_slope(self):
    return self.ticker_data.last_price_slope if self.ticker_data is not None else 0
    
  @property
  def high(self):
    return '%.5f' % self.ticker_data.high if self.ticker_data is not None else Decimal('0')
  @property
  def high_slope(self):
    return self.ticker_data.high_slope if self.ticker_data is not None else 0
  
  @property
  def low(self):
    return '%.5f' % self.ticker_data.low if self.ticker_data is not None else Decimal('0')
  @property
  def low_slope(self):
    return self.ticker_data.low_slope if self.ticker_data is not None else 0
  
  @property
  def volume(self):
    return self.ticker_data.volume if self.ticker_data is not None else Decimal('0')
  
  @property
  def volume_slope(self):
    return self.ticker_data.volume_slope if self.ticker_data is not None else 0  
  
def is_valid_cbu(cbu):
  # Portado de java
  # https://code.google.com/p/cbu/source/browse/trunk/src/main/java/ar/gov/bcra/CBU.java  
  def cbu_v2(v1):
    mod = v1 % 10
    return 0 if mod == 0 else (10 - mod)

  def cbu_v1(pos1, pos2):
    M = [9, 7, 1, 3]  
    total = 0; i = pos2; j = -1
    while i >= pos1:
      if (j == -1): j = 3
      total += int(cbu[i]) * M[j]
      i -= 1; j -= 1

    return cbu_v2(total);
  
  cbu = cbu.strip()
  if re.match(r"[0-9]{22}$", cbu) is None:
    return False

  if int(cbu[7]) != cbu_v1(0, 6):
    return False

  if int(cbu[21]) != cbu_v1(8, 20):
    return False

  return True

def is_valid_bitcoin_address(address):
  from electrum import bitcoin
  return bitcoin.is_valid(address.strip())

  
