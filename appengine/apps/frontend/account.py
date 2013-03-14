# -*- coding: utf-8 -*-
from datetime import datetime

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

import models

from config import config
from utils import FrontendHandler
from account_forms import SignUpForm, ForgetPasswordForm, ResetPasswordForm

from mailer import send_welcome_email, send_resetpassword_email

class Account(FrontendHandler):

  def signup(self, **kwargs):    

    kwargs['form']    = self.signup_form
    
    # Muestro el form
    if self.request.method == 'GET':
      return self.render_response('frontend/signup.html', **kwargs)

    # Proceso el form
    form_validated = self.signup_form.validate()
    if not form_validated:
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
    
    email    = self.request.POST['email']
    password = self.request.POST['password']

    user = models.Account.all().filter('email =', email).get()
    if user and user.confirmed_at and check_password_hash(password, user.password, config['my']['secret_key']):
      self.do_login(user)
      return self.redirect_to('trade-buysell')

    if user:
      user.failed_attempts = user.failed_attempts + 1
      user.put()

    self.set_error(u'Usuario o contraseña inválidos')

    return self.redirect_to('account-login')

  def logout(self, **kwargs):
    self.do_logout()
    return self.redirect_to('trade-buysell')

  def forget(self, **kwargs):
    
    kwargs['form'] = self.forget_form

    if self.request.method == 'GET':
      return self.render_response('frontend/forget_password.html', **kwargs)

    # Proceso el form
    form_validated = self.forget_form.validate()
    if not form_validated:
      return self.render_response('frontend/forget_password.html', **kwargs)
    
    # Envio correo si existe el mail
    user = models.Account.all().filter('email =', self.forget_form.email.data).get()
    if user:
      user.reset_password_token = generate_random_string(length=40)
      user.put()
      send_resetpassword_email(user, self.request.host)

    self.set_ok(u'Si su correo existe en nuestro sitio, recibirá un enlace para crear un nuevo password en su correo.')
    return self.redirect_to('account-login')

  def reset(self, **kwargs):

    kwargs['form'] = self.reset_form

    # Existe el token
    user = models.Account.all().filter('reset_password_token =', kwargs['token']).get()
    if not user:
      return self.redirect_to('account-login')

    if self.request.method == 'GET':
      return self.render_response('frontend/reset_password.html', **kwargs)      

    # Proceso el form
    form_validated = self.reset_form.validate()
    if not form_validated:
      return self.render_response('frontend/reset_password.html', **kwargs)

    user.password  = generate_password_hash(self.reset_form.password.data, method='sha256', pepper=config['my']['secret_key'])
    user.reset_password_token = ''
    user.put()

    self.set_ok(u'La contraseña fue cambiada con exito.')
    return self.redirect_to('account-login')

  @cached_property
  def reset_form(self):
    return ResetPasswordForm(self.request.POST)

  @cached_property
  def forget_form(self):
    return ForgetPasswordForm(self.request.POST)

  @cached_property
  def signup_form(self):
    return SignUpForm(self.request.POST)
