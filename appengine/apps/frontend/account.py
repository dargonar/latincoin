# -*- coding: utf-8 -*-

from webapp2 import cached_property
from models import Account
from utils import FrontendHandler
from account_forms import SignUpForm

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

    # Registrado ok, generamos el usuario y mandamos a confirmar
    return self.redirect_to('account-confirm')

  def confirm(self, **kwargs):
    return self.render_response('frontend/confirm.html')

  def login(self, **kwargs):
    return self.render_response('frontend/login.html')

  def confirm(self, **kwargs):
    return self.render_response('frontend/confirm.html')

  @cached_property
  def signup_form(self):
    return SignUpForm(self.request.POST)
