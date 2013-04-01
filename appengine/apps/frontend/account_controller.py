# -*- coding: utf-8 -*-
from datetime import datetime

from google.appengine.ext import deferred
from google.appengine.ext import db

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import Account, AccountBalance, BitcoinAddress

from config import config
from utils import FrontendHandler
from account_forms import SignUpForm, ForgetPasswordForm, ResetPasswordForm

from mailer import send_welcome_email, send_resetpassword_email, mail_contex_for
from bitcoin_helper import generate_new_address,encrypt_private

class AccountController(FrontendHandler):

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
    user = Account()
    user.email                 = self.signup_form.email.data
    user.password              = generate_password_hash(self.signup_form.password.data, method='sha256', pepper=config['my']['secret_key'])
    user.confirmation_token    = generate_random_string(length=40)
    user.confirmation_sent_at  = datetime.now()
    user.put()

    # Mandamos email de confirmacion
    deferred.defer(send_welcome_email, mail_contex_for('send_welcome_email', user))

    return self.render_response('frontend/signup_success.html')

  def confirm(self, **kwargs):
    token = kwargs['token']
    
    user = Account.all().filter('confirmation_token =', token).get()

    @db.transactional(xg=True)
    def _tx():
      if user and (datetime.now() - user.confirmation_sent_at).seconds < 3600 and user.confirmed_at is None:

        user.confirmed_at = datetime.now()
        user.confirmation_token = ''

        balance_curr = AccountBalance(parent=user, account=user, currency='ARS')
        balance_btc  = AccountBalance(parent=user, account=user, currency='BTC')
        
        addr = generate_new_address()
        if not addr[0]:
          # TODO: Log!!
          return False

        btc_addr = BitcoinAddress(key_name    = addr[1],
                                  parent      = user,
                                  user        = user,
                                  address     = addr[1], 
                                  private_key = encrypt_private(addr[2],user.password))

        db.put([user, balance_curr, balance_btc, btc_addr])
        return True

      return False

    if _tx():
      self.set_ok(u'<strong>Su cuenta ha sido confirmada</strong>. Puede acceder ahora ingresando sus datos.')
      return self.redirect_to('account-login')

    self.set_error(u'<strong>Codigo de registro inválido</strong>')
    return self.redirect_to('account-signup')

  def login(self, **kwargs):

    if self.request.method == 'GET':
      return self.render_response('frontend/login.html')  
    
    email    = self.request.POST['email']
    password = self.request.POST['password']

    user = Account.all().filter('email =', email).get()
    if user and user.confirmed_at and check_password_hash(password, user.password, config['my']['secret_key']):
      self.do_login(user)
      return self.redirect_to('trade-new')

    if user:
      user.failed_attempts = user.failed_attempts + 1
      user.put()

    self.set_error(u'Usuario o contraseña inválidos')
    
    return self.redirect_to('account-login')

  def logout(self, **kwargs):
    self.do_logout()
    return self.redirect_to('trade-new')

  def forget(self, **kwargs):
    
    kwargs['form'] = self.forget_form

    if self.request.method == 'GET':
      return self.render_response('frontend/forget_password.html', **kwargs)

    # Proceso el form
    form_validated = self.forget_form.validate()
    if not form_validated:
      return self.render_response('frontend/forget_password.html', **kwargs)
    
    # Envio correo si existe el mail
    user = Account.all().filter('email =', self.forget_form.email.data).get()
    if user:
      user.reset_password_token = generate_random_string(length=40)
      user.put()

      deferred.defer(send_resetpassword_email, mail_contex_for('send_resetpassword_email',user))

    self.set_ok(u'Si su correo existe en nuestro sitio, recibirá un enlace para crear un nuevo password en su correo.')
    return self.redirect_to('account-login')

  def reset(self, **kwargs):

    kwargs['form'] = self.reset_form

    # Existe el token
    user = Account.all().filter('reset_password_token =', kwargs['token']).get()
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


  # DELETE
  def test_1(self):
    from electrum.bitcoin import *
    from decimal import Decimal

    seed = random_seed(128)
    #seed = 'd61a1a11fa622ec57b6047c1e203b5ceda522819ee59ffd2b2e9d4b32bf5556f'

    self.response.write(seed + '</br>')
    ss = int('0x%s' % seed,16)
    self.response.write( str(ss) + '</br>')
    pkey = EC_KEY(ss)

    private_key = GetPrivKey(pkey)
    public_key = GetPubKey(pkey.pubkey)
    address = public_key_to_bc_address(public_key)

    sec = PrivKeyToSecret(private_key)
    asec =  SecretToASecret(sec)

    self.response.write(address+ '</br>')
    self.response.write( str(is_valid(address)) + '</br>')

    addy = address_from_private_key(asec)
    self.response.write(str(address == addy) + '</br>')

    ##----
    src_add = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
    dst_add = '14UbWFC3aafN2CF1Pt4wutop3EfJR8XQRh'

    tx_hash = '5f5d7bdeab9ba19f1ce209d498e188b3b1f270da82b0b712f1a15c6ff3c2a235'

    hash_160 = bc_address_to_hash_160(src_add)[1]

    script = '76a9'                                      # op_dup, op_hash_160
    script += '14'                                       # push 0x14 bytes
    script += hash_160.encode('hex')
    script += '88ac'

    inputs  = [{'tx_hash':tx_hash, 'index':0,'raw_output_script':script, 'address': 0}]
    outputs = [(dst_add, int(Decimal('0.1')*Decimal(1e8)))]

    tx = Transaction.from_io(inputs, outputs)

    tx.sign(['L4J68a3t7EUKNfaKzyDBhUSeywFpUR6WMdsAGEzMdhgDKRkKws5q'])

    self.response.write( str(tx.as_dict()) + '</br>')




  def init_all(self):
    from models import Dummy
    parent=Dummy.get_or_insert('trade_orders')
    parent=Dummy.get_or_insert('operations')

    xchg = Account(key_name='xchg')
    xchg.email                 = self.signup_form.email.data
    xchg.password              = generate_password_hash('beto', method='sha256', pepper=config['my']['secret_key'])
    xchg.confirmation_token    = generate_random_string(length=40)
    xchg.confirmation_sent_at  = datetime.now()
    xchg.put()

    b_ars = AccountBalance(account=xchg, currency='ARS')
    b_ars.put()

    b_btc = AccountBalance(account=xchg, currency='BTC')
    b_btc.put()

    self.response.write('lito')
    

