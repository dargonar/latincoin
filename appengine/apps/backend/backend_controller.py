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

class BackendController(BackendHandler):

  @need_admin_auth()
  def dashboard(self, **kwargs):
    return self.redirect_to('backend-user-list')
    #kwargs['html']='dashboard'
    #return self.render_response('backend/dashboard.html', **kwargs)

  @need_admin_auth()    
  def home(self, **kwargs):
    return self.redirect_to('backend-user-list')
    
  def login(self, **kwargs):
    if self.request.method == 'GET':
      return self.render_response('backend/login.html')  
    
    email    = self.request.POST['email']
    password = self.request.POST['password']

    # Traemos el usuario y nos fijamos que no este inhabilitado
    admin = Admin.all().filter('email =', email).get()
    if admin and admin.need_captcha():
      return self.redirect_to('backend-login')

    # Usuario y password validos?
    if admin and admin.has_password(password):
      
      admin.login(self.request.remote_addr)
      admin.put()

      self.do_login(admin)
      return self.redirect_to('backend-dashboard')

    # Usuario valido y password invalido?
    if admin and admin.is_active():
      admin.failed_login(self.request.remote_addr)
      admin.put()

    self.set_error(u'Usuario o contraseña inválido')
    
    return self.redirect_to('backend-login')

  def logout(self, **kwargs):
    self.do_logout()
    return self.redirect_to('backend')

  