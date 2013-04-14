# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from urllib import quote_plus,unquote_plus

from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import deferred

from google.appengine.api import images, files
from google.appengine.api.images import get_serving_url

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash, LOWERCASE_ALPHA

from models import Account, AccountValidationFile, UserBitcoinAddress, BankAccount

from config import config
from utils import FrontendHandler, need_auth, get_or_404, abort, is_valid_bitcoin_address, is_valid_cbu

from forms.profile import ProfileForm, ChangePasswordForm, BankAccountForm, UserBitcoinAddressForm

import json, re, urllib

from appengine.file_upload import UploadHandler

from mailer import send_passwordchanged_email, mail_contex_for

from onetimepass import *
from gaeqrcode.PyQRNative import QRErrorCorrectLevel
from gaeqrcode.PyQRNativeGAE import QRCode
import base64

class ProfileController(FrontendHandler, UploadHandler):

  @need_auth()
  def otp_verify(self, **kwargs):

    try:
      code   = int(self.request.POST['code'])
      secret = self.request.POST['secret'] 
    except:
      self.set_error('Código inválido #1.')
      return self.redirect_to('profile-otp')

    if valid_hotp(code, secret):
      self.set_ok('Código valido.')
    else:
      self.set_error('Código inválido #2.')
    
    return self.redirect_to('profile-otp')

  @need_auth()
  def otp(self, **kwargs):    
    kwargs['tab'] = 'otp';
    
    secret = base64.b32encode( generate_random_string(10, pool=LOWERCASE_ALPHA) )

    name = self.user_name
    if '@' in name:
      name = name[0:name.find('@')]

    name = '%s@LatinCoin' % name

    kwargs['secret']  = secret
    kwargs['name']    = name
    
    url = 'otpauth://totp/%s?secret=%s' % (name,secret)
    kwargs['url'] = url

    kwargs['img_url'] = quote_plus(url)

    kwargs['html'] = 'profile'
    return self.render_response('frontend/profile.html', **kwargs)
  
  @need_auth()
  def otp_image(self, **kwargs):
    url = unquote_plus(kwargs['url'])

    qr = QRCode(QRCode.get_type_for_string(url), QRErrorCorrectLevel.L)
    qr.addData(url)
    qr.make()
    img = qr.make_image()

    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(img)

  @need_auth()
  def personal_info(self, **kwargs):    
    
    account = Account.get(db.Key(self.user))

    kwargs['tab'] = 'personal_info';
    kwargs['html'] = 'profile'

    if self.request.method == 'GET':
      kwargs['form'] = ProfileForm(obj=account)
      return self.render_response('frontend/profile.html', **kwargs)
    
    if self.form.validate():
      kwargs['form'] = self.form
      return self.render_response('frontend/profile.html', **kwargs)

    # Si cambio el email, lo marcamos como no verificado
    old_email = account.email
    account = self.form.update_object(account)
    new_email = account.email

    if old_email != new_email:
      account.email_verified = False

      account.confirmation_token = generate_random_string(length=40)
      account.confirmation_sent_at = datetime.now()

      #TODO: taskqueue, mandar email
      logging.error('TOKEN: %s' % account.confirmation_token)

    account.save()

    self.update_user_info(account)
    
    self.set_ok('Perfil guardado satisfactoriamente.')
    return self.redirect_to('profile-personal_info')
  
  @cached_property
  def form(self):
    my_form = ProfileForm(self.request.POST)
    my_form.user_key = self.user
    return my_form
  
  
  @need_auth()
  def identity_validation_files(self, **kwargs):
    account_key = db.Key(self.user)
    
    myfiles = AccountValidationFile.all() \
            .filter('account =', account_key) \
            .order('created_at')
            
    kwargs['files'] = myfiles
    return self.render_response('frontend/profile_form_verification_files.html', **kwargs)
    
  @need_auth()
  def identity_validation(self, **kwargs):
    
    kwargs['tab'] = 'identity_validation';
    kwargs['html'] = 'profile'
    account_key = db.Key(self.user)
    
    if self.request.method == 'GET':
      myfiles = AccountValidationFile.all() \
              .filter('account =', account_key) \
              .order('created_at')
              
      kwargs['files'] = myfiles
      return self.render_response('frontend/profile.html', **kwargs)
    
    results = self.handle_upload()
    for result in results:
      if result['is_valid']==False:
        continue
      #blob_key = files.blobstore.get_blob_key(result['blob_key'])
      blob_key = result['blob_key']
      valid_file = AccountValidationFile(validation_type   = AccountValidationFile.VALIDATION_UNDEFINED,
                                                  file                = blob_key,
                                                  filename            = result['name'],
                                                  account             = db.get(account_key),
                                                  serving_url         = get_serving_url(blob_key),
                                                  filetype            = result['type'],
                                                  filesize            = '%.2f' % result['size'],
                                                  not_valid_reason    = '')
      valid_file.save()
      result['blob_key']=''
            
    data = {'files': results}
    return self.render_json_response(data)
  
  
  
  @need_auth()
  def delete_file(self, **kwargs):
    
    validation_file = self.mine_or_404(kwargs['key'])
    
    file_was_valid  = validation_file.is_valid
    file_type       = validation_file.filetype
    blob            = validation_file.file.key()
    db.delete(validation_file)
    blobstore.delete([blob])
    
    # Veo si el archivo era el que validaba al usuario
    if file_was_valid==True:
      # Traigo los restantes archivos validos
      user_files = AccountValidationFile.all(keys_only=True) \
                .filter('user =', db.Key(self.user)) \
                .filter('is_valid =', True) \
                .filter('type =', file_type) \
                .get()
                
      # Pregunto si habia mas arcihvos del tipo
      if user_files is None:
        #self.response.write('ok')
      
        # No habia, por ende invalido al usuario
        account = db.Get(db.Key(self.user))
        if account.isIdentityType(file_type):
          account.identity_is_validated = False
        else:
          account.address_is_validated = False
        account.put()
    
    self.set_ok('Archivo eliminado satisfactoriamente')
    return self.redirect_to('profile-identity_validation')
    
  @need_auth()
  def change_password(self, **kwargs):    
    
    kwargs['tab'] = 'change_password';
    kwargs['html'] = 'profile'
    kwargs['form'] = self.password_form

    if self.request.method == 'GET':      
      return self.render_response('frontend/profile.html', **kwargs)
    
    user = Account.get(db.Key(self.user))

    new_password  = self.password_form.new_password.data
    password      = self.password_form.password.data
    
    is_valid = self.password_form.validate() # valido que el nuevo password este confirmado.

    # repitio correctamente? el password viejo es correcto?
    if is_valid and user.has_password(password):
      @db.transactional(xg=True)
      def _tx():
        to_save = user.change_password(new_password, self.request.remote_addr)
        db.put(to_save)
        # Mandamos email de aviso de cambio de clave
        deferred.defer(send_passwordchanged_email, mail_contex_for('send_passwordchanged_email', user))
      _tx()
      
      self.set_ok(u'La contraseña fue modificada con éxito.')
      return self.redirect_to('profile-change_password')

    # Solo guardamos si password viejo incorrecto (is_valid = True)
    # Pero mostramos el mismo mensaje en los dos casos, 
    # para no avivarlo que fue lo que puso mal     
    if is_valid:
      user.fail_change_pass(self.request.remote_addr)
      user.put()

    kwargs['flash'] = self.build_error(u'Verifique los datos ingresados.')
    return self.render_response('frontend/profile.html', **kwargs)
  
  @cached_property
  def password_form(self):
    my_pwd_form = ChangePasswordForm(self.request.POST)
    my_pwd_form.user_key = self.user
    return my_pwd_form
  
  @need_auth()
  def bank_account(self, **kwargs):
    
    kwargs['html'] = 'profile'
    kwargs['tab']  = 'bank_account';
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)
    
    # Cuando viene el post, lo validamos dentro de un form
    # Si hay error, mandamos el primer error
    form = BankAccountForm(self.request.POST)
    if not form.validate():
      self.response.write(form.errors[form.errors.keys()[0]][0])
      self.response.set_status(500)
      return

    # Es uno nuevo o un edit?
    # Si es edit, traemos con mine_or_404 (code=500)
    key = form.key.data
    if key and len(key):
      bank_acc = self.mine_or_404(key, code=500)
      bank_acc.cbu         = form.cbu.data
      bank_acc.description = form.description.data
    else:
      bank_acc = BankAccount(account     = db.Key(self.user),
                             cbu         = form.cbu.data, 
                             description = form.description.data)

    bank_acc.put()
    self.response.out.write("ok")
    return
      
  
  @need_auth()
  def bank_account_list(self, **kwargs):
    bankaccs = {'aaData':[]}

    for bankacc in BankAccount.all() \
              .filter('account =', db.Key(self.user)) \
              .filter('active =', True) \
              .order('-created_at'):

      row = []
      row.append(bankacc.cbu)
      row.append(bankacc.description)
      
      edit_link   = '<a href="#" key="%s" class="edit btn mini purple"><i class="icon-edit"></i>&nbsp;Editar</a>' % str(bankacc.key())
      remove_link = '<a href="%s" class="delete btn mini black"><i class="icon-trash"></i>&nbsp;Borrar</a>' % self.url_for( 'profile-bank_account_delete', key=str(bankacc.key()) )
      row.append( '%s&nbsp;%s' % (edit_link,remove_link))

      bankaccs['aaData'].append(row)

    return self.render_json_response(bankaccs)

  
  @need_auth()
  def btc_address(self, **kwargs):
    account = get_or_404(self.user)
    
    kwargs['tab'] = 'btc_address';
    kwargs['html'] = 'profile'
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)

    # Cuando viene el post, lo validamos dentro de un form
    # Si hay error, mandamos el primer error
    form = UserBitcoinAddressForm(self.request.POST)
    if not form.validate():
      self.response.write(form.errors[form.errors.keys()[0]][0])
      self.response.set_status(500)
      return

    # Es uno nuevo o un edit?
    # Si es edit, traemos con mine_or_404 (code=500)
    key = form.key.data
    if key and len(key):

      user_addy = self.mine_or_404(key, code=500)
      user_addy.address = form.address.data
      user_addy.description = form.description.data

    else:
      user_addy = UserBitcoinAddress(account     = db.Key(self.user),
                                     address     = form.address.data, 
                                     description = form.description.data)
    user_addy.put()
    self.response.out.write("ok")
    return
  
  @need_auth()
  def btc_address_list(self, **kwargs):  
    addrs = {'aaData':[]}

    for addr in UserBitcoinAddress.all() \
              .filter('account =', db.Key(self.user)) \
              .filter('active =', True) \
              .order('-created_at'):

      row = []
      
      row = []
      row.append(addr.address)
      row.append(addr.description)
      
      edit_link   = '<a href="#" key="%s" class="edit btn mini purple"><i class="icon-edit"></i>&nbsp;Editar</a>' % str(addr.key())
      remove_link = '<a href="%s" class="delete btn mini black"><i class="icon-trash"></i>&nbsp;Borrar</a>' % self.url_for( 'profile-btc_address_delete', key=str(addr.key()) )
      row.append( '%s&nbsp;%s' % (edit_link,remove_link))

      addrs['aaData'].append(row)

    return self.render_json_response(addrs)
  
  @need_auth()
  def btc_address_delete(self, **kwargs):  
    
    btc_address = self.mine_or_404(kwargs['key'])
    btc_address.active = False
    btc_address.put()
    
    self.set_ok(u'La dirección fue eliminada correctamente.')
    return self.redirect(self.request.referer)

  @need_auth()
  def bank_account_delete(self, **kwargs):  
    
    bank_account = self.mine_or_404(kwargs['key'])
    bank_account.active = False
    bank_account.put()
    
    self.set_ok(u'La cuenta bancaria fue eliminada correctamente.')
    return self.redirect(self.request.referer)
  
