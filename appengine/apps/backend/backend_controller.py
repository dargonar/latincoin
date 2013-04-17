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

from mail.mailer import enqueue_mail 
from bitcoin_helper import generate_new_address, encrypt_private

class BackendController(FrontendHandler):

  # @need_admin_auth()
  # def deposits(self, **kwargs):
    # kwargs['html']='deposits'
    # return self.render_response('backend/deposits.html', **kwargs)
  
  @need_admin_auth()
  def withdrawals(self, **kwargs):
    kwargs['html']='withdrawals'
    return self.render_response('backend/withdrawals.html', **kwargs)
  
  @need_admin_auth()
  def users(self, **kwargs):
    kwargs['html']='users'
    if self.request.method == 'GET':
      kwargs['users'] = Account.all()
      return self.render_response('backend/users.html', **kwargs)
    
    email = self.request.POST['email'].strip()
    kwargs['users'] = Account.all().filter('email = ', email)
    
    return self.render_response('backend/users.html', **kwargs)
  
  @need_admin_auth()
  def list_user_files(self, **kwargs):
    kwargs['html']='users'
    if self.request.method != 'GET':
      return self.redirect_to('backend-users')
    
    account_key = db.Key(kwargs['user'])
    kwargs['user']  = db.get(account_key)
    kwargs['files'] = AccountValidationFile.all() \
            .filter('account =', account_key) \
            .order('created_at')
            
    return self.render_response('backend/user_files.html', **kwargs)
  
  @need_admin_auth()
  def validate_user(self, **kwargs):
    kwargs['html']='users'
    if self.request.method != 'GET':
      return self.redirect_to('backend-users')
    
    is_valid = kwargs['valid']
    user = db.get(db.Key(kwargs['user']))
    
    user.identity_is_validated = True if is_valid.strip()=='1' else False
    
    @db.transactional()
    def _tx():
      user.put()
      # Mandamos email de aviso de validacino de archivo
      enqueue_mail('identity_validated', {'user_key': str(user.key()) })
    
    _tx()
    
    self.set_ok(u'El usuario fue actualizado satisfactoriamente.')
    # enviar mail
    return self.redirect_to('backend-users')
    
  @need_admin_auth()
  def validate_user_file(self, **kwargs):
    kwargs['html']='users'
    if self.request.method != 'GET':
      return self.redirect_to('backend-users')
    
    is_valid = kwargs['valid']
    file = db.get(db.Key(kwargs['file']))
    
    file.is_valid = True if is_valid.strip()=='1' else False
    if file.is_valid==False:
      invalid_reason = self.request.GET['invalid_reason']
      if invalid_reason and len(invalid_reason.strip()):
        file.not_valid_reason = invalid_reason.strip()
      else:
        self.set_error(u'Indique un motivo para invalidar un archivo.')
        return self.redirect_to('backend-list_user_files', user=str(file.account.key()))
    
    @db.transactional(xg=True)
    def _tx():
      file.put()
      # Mandamos email de aviso de validacino de archivo
      enqueue_mail('validation_file_validated', {'user_key': str(file.account.key()), 'file_key': str(file.key()) }, tx=True)
    
    _tx()
    
    self.set_ok(u'El archivo fue actualizado satisfactoriamente.')
    # enviar mail
    return self.redirect_to('backend-list_user_files', user=str(file.account.key()))
  
  @need_admin_auth()
  def dashboard(self, **kwargs):
    kwargs['html']='dashboard'
    return self.render_response('backend/dashboard.html', **kwargs)
    
  def home(self, **kwargs):
    if self.is_logged and self.is_admin:
      return self.redirect_to('backend-dashboard')
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

  