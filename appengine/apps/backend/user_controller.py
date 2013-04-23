# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal
from google.appengine.ext import deferred
from google.appengine.ext import db

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import AccountValidationFile, Admin, Account

from utils import BackendHandler, need_admin_auth, get_or_404
from forms.account import SignUpForm, ForgetPasswordForm, ResetPasswordForm

from mail.mailer import enqueue_mail 
from bitcoin_helper import generate_new_address, encrypt_private

class UserController(BackendHandler):

  @need_admin_auth()
  def edit(self, **kwargs):
    kwargs['html']='users'
    
    if self.request.method != 'GET':
      return self.redirect_to('backend-user-list')
    
    account_key = db.Key(kwargs['user'])
    kwargs['account']   = get_or_404(account_key)
    kwargs['user_key']  = kwargs['user']
    
    return self.render_response('backend/user_dashboard.html', **kwargs)
  
  @need_admin_auth()
  def list(self, **kwargs):
    kwargs['html']='users'
    if self.request.method == 'GET':
      kwargs['users'] = None #Account.all()
      return self.render_response('backend/users.html', **kwargs)
    
    email = self.request.POST['email'].strip()
    kwargs['users'] = Account.all().filter('email = ', email)
    
    return self.render_response('backend/users.html', **kwargs)
  
  @need_admin_auth()
  def list_files(self, **kwargs):
    kwargs['html']='users'
    if self.request.method != 'GET':
      return self.redirect_to('backend-user-list')
    
    account_key = db.Key(kwargs['user'])
    kwargs['account']   = get_or_404(account_key)
    kwargs['files']     = AccountValidationFile.all() \
                            .filter('account =', account_key) \
                            .order('created_at')
    kwargs['user_key']  = kwargs['user']
    return self.render_response('backend/user_files.html', **kwargs)
  
  @need_admin_auth()
  def validate(self, **kwargs):
    kwargs['html']='users'
    if self.request.method != 'GET':
      return self.redirect_to('backend-user-list')
    
    is_valid = kwargs['valid']
    user = get_or_404(db.Key(kwargs['user']))
    
    user.identity_is_validated = True if is_valid.strip()=='1' else False
    
    @db.transactional()
    def _tx():
      user.put()
      # Mandamos email de aviso de validacino de archivo
      enqueue_mail('identity_validated', {'user_key': str(user.key()) }, tx=True)
    
    _tx()
    
    self.set_ok(u'El usuario fue actualizado satisfactoriamente.')
    # enviar mail
    return self.redirect_to('backend-user-edit', user=kwargs['user'])
    
  @need_admin_auth()
  def validate_file(self, **kwargs):
    
    kwargs['html']='users'
    
    if self.request.method != 'GET':
      return self.redirect_to('backend-user-list')
    
    is_valid = kwargs['valid']
    file = get_or_404(db.Key(kwargs['file']))
    
    file.is_valid = True if is_valid.strip()=='1' else False
    if file.is_valid==False:
      invalid_reason = self.request.GET['invalid_reason']
      if invalid_reason and len(invalid_reason.strip()):
        file.not_valid_reason = invalid_reason.strip()
      else:
        self.set_error(u'Indique un motivo para invalidar un archivo.')
        return self.redirect_to('backend-user-list_files', user=str(file.account.key()))
    
    @db.transactional(xg=True)
    def _tx():
      file.put()
      # Mandamos email de aviso de validacino de archivo
      enqueue_mail('validation_file_validated', {'user_key': str(file.account.key()), 'file_key': str(file.key()) }, tx=True)
    
    _tx()
    
    self.set_ok(u'El archivo fue actualizado satisfactoriamente.')
    # enviar mail
    return self.redirect_to('backend-user-list_files', user=str(file.account.key()))