# -*- coding: utf-8 -*-
from datetime import datetime

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

import models

from config import config
from utils import FrontendHandler
from account_forms import SignUpForm

from mailer import send_welcome_email

class Account(FrontendHandler):

  def signup(self, **kwargs):    
    
    self.request.charset = 'utf-8'

    # Muestro el form
    if self.request.method == 'GET':
      kwargs['form']    = self.signup_form
      return self.render_response('frontend/signup.html', **kwargs)

    # Proceso el form
    form_validated = self.signup_form.validate()
    if not form_validated:
      kwargs['form'] = self.signup_form
      
      if self.signup_form.errors:
        kwargs['flash'] = self.build_error(u'Hay errores en los datos de registración.')
      
      return self.render_response('frontend/signup.html', **kwargs)

    # Generamos el usuario
    user = models.Account()
    user.email                 = self.signup_form.email.data
    user.password              = generate_password_hash(self.signup_form.password.data, method='sha256', pepper=config['my']['secret_key'])
    user.confirmation_token    = generate_random_string(length=40)
    user.confirmation_sent_at  = datetime.now()
    user.put()

    # Mandamos email de confirmacion
    send_welcome_email(user, self.request.host)

    return self.render_response('frontend/signup_success.html')

  def confirm(self, **kwargs):
    token = kwargs['token']
    
    user = models.Account.all().filter('confirmation_token =', token).get()
    if user and (datetime.now() - user.confirmation_sent_at).seconds < 3600 and user.confirmed_at is None:
      
      user.confirmed_at = datetime.now()
      user.put()

      self.set_ok(u'<strong>Su cuenta ha sido confirmada</strong>. Puede acceder ahora ingresando sus datos.')
      return self.redirect_to('account-login')

    self.set_error(u'<strong>Codigo de registro inválido</strong>')
    return self.redirect_to('account-signup')

  def login(self, **kwargs):
    
    if self.request.method == 'GET':
      return self.render_response('frontend/login.html')  
    
    email    = kwargs['email']
    password = kwargs['password']

    user = models.Account.all().filter('email =', email).get()
    if user and user.confirmed_at and check_password_hash(password, user.password, config['my']['secret']) :
      return

    self.set_error(u'Usuario o contraseña invalidos')
    return self.render_response('frontend/login.html')

  def forget(self, **kwargs):
    return self.render_response('frontend/forget_password.html')

  @cached_property
  def signup_form(self):
    return SignUpForm(self.request.POST)
