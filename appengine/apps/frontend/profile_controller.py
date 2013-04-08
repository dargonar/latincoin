# -*- coding: utf-8 -*-
from datetime import datetime

from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images, files
from google.appengine.api.images import get_serving_url

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import Account, AccountValidationFile, UserBitcoinAddress, BankAccount

from config import config
from utils import FrontendHandler, need_auth, get_or_404, abort, is_valid_bitcoin_address, is_valid_cbu

from profile_forms import ProfileForm, ChangePasswordForm

import json, re, urllib

from file_upload import UploadHandler

class ProfileController(FrontendHandler, UploadHandler):

  @need_auth()
  def otp(self, **kwargs):    
    kwargs['tab'] = 'otp';
    kwargs['html'] = 'profile'
    return self.render_response('frontend/profile.html', **kwargs)
  
  @need_auth()
  def personal_info(self, **kwargs):    
    account = get_or_404(self.user)
    kwargs['tab'] = 'personal_info';
    kwargs['html'] = 'profile'
    if self.request.method == 'GET':
      kwargs['form']              = ProfileForm(obj=account)
      return self.render_response('frontend/profile.html', **kwargs)
    
    
    is_valid = self.form.validate()
    if not is_valid:
      kwargs['form']         = self.form
      return self.render_response('frontend/profile.html', **kwargs)

    account          = self.form.update_object(account)
    account.save()
    
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
    return self.render_response('frontend/profile_validation_files.html', **kwargs)
    
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

      _tx()
      
      self.set_ok(u'La contraseña fue modificada con éxito.')
      return self.redirect_to('profile-change_password')

    # Solo guardamos si password viejo incorrecto (is_valid = True)
    # Pero mostramos el mismo mensaje en los dos casos, para no avivarlo que puso mal     
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
    account = get_or_404(self.user)
    
    kwargs['tab'] = 'bank_account';
    kwargs['html'] = 'profile'
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)
    
    cbu         = self.request.POST['bank_account_cbu'] 
    description = self.request.POST['bank_account_desc'] 
    if cbu is not None:
      cbu = cbu.strip()
    if is_valid_cbu(cbu)==False:
      self.response.write(u'El CBU no es válido.')
      self.response.set_status(500)
      #self.error(500)
      return
      
    key       = self.request.POST['key'] 
    bank_acc  = None
    
    if key is not None and key.strip()!='':
      old_bank_acc              = db.get(db.Key(key))
      old_bank_acc.active       = False
      old_bank_acc.put()
    
    bank_acc = BankAccount( account     = account,
                              cbu         = cbu,
                              description = description)
      
    bank_acc.put()
    self.response.out.write("It's done!")
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
      #row.append(str(addr.key()))
      row.append('<input type="hidden" name="key" value="'+str(bankacc.key())+'" />')
      row.append('<a href="' + self.url_for('profile-btc_address_delete', key=str(bankacc.key()), referer='profile-bank_account' ) + '">Borrar</a>')

      bankaccs['aaData'].append(row)

    return self.render_json_response(bankaccs)

  
  @need_auth()
  def btc_address(self, **kwargs):
    account = get_or_404(self.user)
    
    kwargs['tab'] = 'btc_address';
    kwargs['html'] = 'profile'
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)
    
    address     = self.request.POST['bitcoinaddr_address'] 
    description = self.request.POST['bitcoinaddr_desc'] 
    
    if address is not None:
      address = address.strip()
    if is_valid_bitcoin_address(address)==False:
      self.response.write(u'La dirección no es una dirección de Bitcoin válida.')
      self.response.set_status(500)
      #self.error(500)
      return
      
    key     = self.request.POST['key'] 
    btc_addr = None
    
    if key is not None and key.strip()!='':
      old_btc_addr = db.get(db.Key(key))
      old_btc_addr.active     = False
      old_btc_addr.put()
      
    btc_addr = UserBitcoinAddress(account     = account,
                              address     = address,
                              description = description)
      
    btc_addr.put()
    self.response.out.write("It's done!")
    return
      
  
  @need_auth()
  def btc_address_list(self, **kwargs):  
    addrs = {'aaData':[]}

    for addr in UserBitcoinAddress.all() \
              .filter('account =', db.Key(self.user)) \
              .filter('active =', True) \
              .order('-created_at'):

      row = []
      row.append(addr.address)
      row.append(addr.description)
      #row.append(str(addr.key()))
      row.append('<input type="hidden" name="key" value="'+str(addr.key())+'" />')
      row.append('<a href="' + self.url_for('profile-btc_address_delete', key=str(addr.key()), referer='profile-btc_address' ) + '">Borrar</a>')

      addrs['aaData'].append(row)

    return self.render_json_response(addrs)
  
  @need_auth()
  def btc_address_delete(self, **kwargs):  
    btcaddress_or_bankacc = db.get(db.Key(kwargs['key']))
    referer = kwargs['referer']
    if str(btcaddress_or_bankacc.account.key()) != self.user:
      abort(404)
    
    btcaddress_or_bankacc.active = False
    btcaddress_or_bankacc.put()
    
    #db.delete(btcaddress_or_bankacc)
    if referer=='profile-btc_address':
      self.set_ok(u'La dirección fue eliminada.')
    else:
      self.set_ok(u'El CBU fue eliminado.')
    return self.redirect_to(referer)
    
  