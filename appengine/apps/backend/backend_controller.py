# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal
from google.appengine.ext import deferred
from google.appengine.ext import db

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import Account, AccountValidationFile

from utils import FrontendHandler, need_admin_auth
from forms.account import SignUpForm, ForgetPasswordForm, ResetPasswordForm

from mail.mailer import enqueue_mail, enqueue_mail_tx 
from bitcoin_helper import generate_new_address, encrypt_private

class BackendController(FrontendHandler):

  @need_admin_auth()
  def deposits(self, **kwargs):
    return self.render_response('backend/deposits.html', **kwargs)
  
  @need_admin_auth()
  def withdrawals(self, **kwargs):
    return self.render_response('backend/withdrawals.html', **kwargs)
  
  @need_admin_auth()
  def users(self, **kwargs):
    
    if self.request.method == 'GET':
      kwargs['users'] = Account.all()
      return self.render_response('backend/users.html', **kwargs)
    
    email = self.request.POST['email'].strip()
    kwargs['users'] = Account.all().filter('email = ', email)
    
    return self.render_response('backend/users.html', **kwargs)
  
  @need_admin_auth()
  def list_user_files(self, **kwargs):
    
    if self.request.method != 'GET':
      return self.redirect_to('backend-users')
    
    account_key = db.Key(kwargs['key'])
    kwargs['user']  = db.get(account_key)
    kwargs['files'] = AccountValidationFile.all() \
            .filter('account =', account_key) \
            .order('created_at')
            
    return self.render_response('backend/user_files.html', **kwargs)
    
  @need_admin_auth()
  def dashboard(self, **kwargs):
    return self.render_response('backend/dashboard.html', **kwargs)
    
  def home(self, **kwargs):
    return self.redirect_to('backend-login')
    
  def login(self, **kwargs):

    if self.request.method == 'GET':
      return self.render_response('backend/login.html')  
    
    email    = self.request.POST['email']
    password = self.request.POST['password']

    # Traemos el usuario y nos fijamos que no este inhabilitado
    user = Account.all().filter('email =', email).get()
    if user and user.user_need_captcha():
      return self.redirect_to('backend-login')

    # Usuario y password validos?
    if user and user.is_active() and user.has_password(password) and user.is_admin():
      
      user.login(self.request.remote_addr)
      user.put()

      self.do_login(user)
      return self.redirect_to('backend-dashboard')

    # Usuario valido y password invalido?
    if user and user.is_active():
      user.failed_login(self.request.remote_addr)
      user.put()

    self.set_error(u'Usuario o contraseña inválido')
    
    return self.redirect_to('backend-login')

  def logout(self, **kwargs):
    self.do_logout()
    return self.redirect_to('backend')

  