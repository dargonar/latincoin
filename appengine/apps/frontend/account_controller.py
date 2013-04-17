# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal
from google.appengine.ext import deferred
from google.appengine.ext import db

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import Account, AccountBalance, BitcoinAddress

from utils import FrontendHandler
from forms.account import SignUpForm, ForgetPasswordForm, ResetPasswordForm

from mail.mailer import enqueue_mail 
from bitcoin_helper import generate_new_address, encrypt_private

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
    user = Account.new_user(self.signup_form.email.data, self.signup_form.password.data)
    user.put()

    # Mandamos email de confirmacion
    enqueue_mail('welcome', {'user_key':str(user.key())})

    return self.render_response('frontend/signup_success.html')

  def validate(self, **kwargs):
    token = kwargs['token']

    user = Account.all().filter('confirmation_token =', token).get()
    
    # No hay codigo de verificación
    if not user:
      self.set_error(u'<strong>Código inválido</strong>')
      return self.redirect_to('account-login')

    user.validate_email()
    user.put()

    self.update_user_info(user)

    self.set_ok(u'<strong>Su email fue verificado correctamente</strong>')
    return self.redirect_to('account-login')


  def confirm(self, **kwargs):
    token = kwargs['token']
    
    user = Account.all().filter('confirmation_token =', token).get()
    
    # No hay codigo o ya expiro el tiempo
    if not user or not user.can_confirm():
      self.set_error(u'<strong>Código de registro inválido o expirado</strong>')
      
      # Borramos al usuario si estaba expirado para que se puede volver a registrar.
      if user: 
        #logging.error('No va mas')
        user.delete()

      return self.redirect_to('account-signup')

    @db.transactional(xg=True)
    def _tx():

      user.confirm()

      balance_curr = AccountBalance(parent=user, account=user, currency='ARS')
      balance_btc  = AccountBalance(parent=user, account=user, currency='BTC')
        
      addr = generate_new_address()
      if not addr['result']:
        raise(BaseException('no se puede generar direccion btc'))

      btc_addr = BitcoinAddress(key_name    = addr['public'],
                                user        = user,
                                address     = addr['public'], 
                                private_key = encrypt_private(addr['private']))

      db.put([user, balance_curr, balance_btc, btc_addr])

    # do it
    _tx()

    self.set_ok(u'<strong>Su cuenta ha sido confirmada</strong>. Puede acceder ahora ingresando sus datos.')
    return self.redirect_to('account-login')

  def login(self, **kwargs):

    if self.request.method == 'GET':
      return self.render_response('frontend/login.html')  
    
    email    = self.request.POST['email']
    password = self.request.POST['password']

    # Traemos el usuario y nos fijamos que no este inhabilitado
    user = Account.all().filter('email =', email).get()
    if user and user.user_need_captcha():
      return self.redirect_to('account-login')

    # Usuario y password validos?
    if user and user.is_active() and user.has_password(password):
      
      user.login(self.request.remote_addr)
      user.put()

      self.do_login(user)
      return self.redirect_to('trade-new')

    # Usuario valido y password invalido?
    if user and user.is_active():
      user.failed_login(self.request.remote_addr)
      user.put()

    self.set_error(u'Usuario o contraseña inválido')
    
    return self.redirect_to('account-login')

  def logout(self, **kwargs):
    self.do_logout()
    return self.redirect_to('home')

  def forget(self, **kwargs):
    
    kwargs['form'] = self.forget_form

    # Si es GET mostramos el form para que ponga el mail
    if self.request.method == 'GET':
      return self.render_response('frontend/forget_password.html', **kwargs)

    # Proceso el form
    form_validated = self.forget_form.validate()
    if not form_validated:
      return self.render_response('frontend/forget_password.html', **kwargs)
    
    # Envio correo si existe el mail
    user = Account.all().filter('email =', self.forget_form.email.data).get()
    if user:
      user.create_reset_token()
      user.put()
      enqueue_mail('forgot_password', {'user_key':str(user.key())} )

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

    @db.transactional(xg=True)
    def _tx():
      to_save = user.change_password(self.reset_form.password.data, self.request.remote_addr, True)
      db.put(to_save)
      enqueue_mail('password_changed', {'user_key':str(user.key())})
    _tx()

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


  def test_1(self):
    from bitcoin_helper import encrypt_private, decrypt_private, generate_new_address
    from electrum.bitcoin import *

    addy = generate_new_address()
    if not addy['result']:
      raise(BaseException('no se puede generar direccion btc'))

    priv_enc = encrypt_private(addy['private'])
    self.response.write(priv_enc + '</br>' )
    asec = decrypt_private(priv_enc)
    self.response.write(asec + '</br>' )
    tmp = address_from_private_key(asec)
    self.response.write(tmp + '</br>' )
    self.response.write( str(tmp==addy['public']) + '</br>')


  # # DELETE
  # def test_1(self):
  #   from electrum.bitcoin import *
  #   from decimal import Decimal

  #   seed = random_seed(128)
  #   #seed = 'd61a1a11fa622ec57b6047c1e203b5ceda522819ee59ffd2b2e9d4b32bf5556f'

  #   self.response.write(seed + '</br>')
  #   ss = int('0x%s' % seed,16)
  #   self.response.write( str(ss) + '</br>')
  #   pkey = EC_KEY(ss)

  #   private_key = GetPrivKey(pkey)
  #   public_key = GetPubKey(pkey.pubkey)
  #   address = public_key_to_bc_address(public_key)

  #   sec = PrivKeyToSecret(private_key)
  #   asec =  SecretToASecret(sec)

  #   self.response.write(address+ '</br>')
  #   self.response.write( str(is_valid(address)) + '</br>')

  #   addy = address_from_private_key(asec)
  #   self.response.write(str(address == addy) + '</br>')

  #   ##----
  #   src_add = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
  #   dst_add = '14UbWFC3aafN2CF1Pt4wutop3EfJR8XQRh'

  #   tx_hash = '5f5d7bdeab9ba19f1ce209d498e188b3b1f270da82b0b712f1a15c6ff3c2a235'

  #   hash_160 = bc_address_to_hash_160(src_add)[1]

  #   script = '76a9'                                      # op_dup, op_hash_160
  #   script += '14'                                       # push 0x14 bytes
  #   script += hash_160.encode('hex')
  #   script += '88ac'

  #   inputs  = [{'tx_hash':tx_hash, 'index':0,'raw_output_script':script, 'address': 0}]
  #   outputs = [(dst_add, int(Decimal('0.1')*Decimal(1e8)))]

  #   tx = Transaction.from_io(inputs, outputs)

  #   tx.sign(['L4J68a3t7EUKNfaKzyDBhUSeywFpUR6WMdsAGEzMdhgDKRkKws5q'])

  #   self.response.write( str(tx.as_dict()) + '</br>')




  def init_all(self):
    from config import config
    from webapp2_extras.security import generate_random_string, check_password_hash
    
    from models import Dummy
    parent=Dummy.get_or_insert('trade_orders')
    parent=Dummy.get_or_insert('operations')

    xchg = Account.get_or_insert('xchg')
    xchg.email                 = self.signup_form.email.data
    xchg.password              = generate_password_hash('beto', method='sha256', pepper=config['my']['secret_key'])
    xchg.confirmation_token    = generate_random_string(length=40)
    xchg.confirmation_sent_at  = datetime.now()
    xchg.put()

    b_ars = AccountBalance.get_or_insert('xchg-ars',account=xchg, currency='ARS', parent=xchg)
    b_ars.put()

    b_btc = AccountBalance.get_or_insert('xchg-btc',account=xchg, currency='BTC', parent=xchg)
    b_btc.put()

    from models import SystemConfig
    s = SystemConfig.get_or_insert('system-config',
          remote_rpc        = 'blockchain', 
          confirmations     = '0',
          trade_enable      = 'Y', 
          import_delay      = '0',
          import_enable     = 'Y',
          forward_enable    = 'Y',
          min_btc_withdraw  = Decimal('0.01'),
          min_curr_deposit  = Decimal('0'),
          min_curr_withdraw = Decimal('50'),
    )

    s.put()

    from bitcoinrpc.connection import get_proxy
    
    #last_block = 231713
    #last_block = get_proxy(s.remote_rpc).getblockcount()

    #from models import Block
    #b = Block( key=db.Key.from_path('Block',last_block), processed='Y', number=last_block, hash='n/a', txs=0)
    #b.put()

    from models import PriceBar
    import time
    nowts = time.time()

    bar_time = int(nowts/PriceBar.H1)

    now = datetime.fromtimestamp(bar_time)

    from models import PriceBar
    dummy_bar = PriceBar.get_or_insert('dummy_bar',
                        open     = 0,
                        high     = 0,
                        low      = 0,
                        close    = 0,
                        volume   = 0, 
                        bar_time = bar_time,
                        bar_interval = PriceBar.H1,
                        year     = now.year,
                        month    = now.month,
                        day      = now.day)
    dummy_bar.put()
    
    from mail import init_mails
    init_mails()
    
    self.response.write('lito')
