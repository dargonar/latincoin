# -*- coding: utf-8 -*-
import logging
import urllib
from datetime import datetime
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import abort, cached_property, RequestHandler, Response, HTTPException, uri_for as url_for, get_app
from webapp2_extras import jinja2, sessions, json

from models import AccountBalance
from account_functions import get_account_balance

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
  
def get_or_404(key):
  try:
      obj = db.get(key)
      if obj:
          return obj
  except db.BadKeyError, e:
      # Falling through to raise the NotFound.
      pass

  abort(404)

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
    env.globals['ars_balance']  = self.ars_balance
    env.globals['btc_balance']  = self.btc_balance
    
    pass
          
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

    user.sign_in_count        = user.sign_in_count + 1
    user.last_sign_in_at      = user.current_sign_in_at
    user.current_sign_in_at   = datetime.now()
    user.last_sign_in_ip      = user.current_sign_in_ip
    user.current_sign_in_ip   = self.request.remote_addr
    user.reset_password_token = ''
    user.put()

    balance = get_account_balance(user)
    
    # BORRAR -----
    from random import uniform
    balance['BTC'].amount += Decimal('%.5f'% uniform(10,100))
    balance['BTC'].put();
    balance['ARS'].amount += Decimal('%.2f'% uniform(10,10000))
    balance['ARS'].put();

    # BORRAR ----

    self.session['account.user'] = str(user.key())
    self.session['account.btc']  = str(balance['BTC'].key())
    self.session['account.ars']  = str(balance['ARS'].key())

    self.session['account.logged'] = True

  def do_logout(self):
    self.session.clear()

  @property
  def btc_balance(self):
    return '%.5f' % self.try_get_balance('btc')

  @property
  def ars_balance(self):
    return '%.2f' % self.try_get_balance('ars')

  @property
  def is_logged(self):
    return self.session_value('account.logged', False)

  @property
  def user(self):
    return self.session_value('account.user')

  def try_get_balance(self, currency):
    tmp = self.session_value('account.%s' % currency, None)
    if tmp is None:
      return Decimal('0')

    balance = db.get(tmp)
    return (balance.amount - balance.amount_comp)

  def session_value(self, key, default=None):
    return self.session[key] if key in self.session else default

  def mine_or_404(self, key):
    obj = get_or_404(key)
    if str(obj.user.key()) != self.user:
      abort(404)
    
    return obj