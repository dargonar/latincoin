# -*- coding: utf-8 -*-
from datetime import datetime

from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images, files
from google.appengine.api.images import get_serving_url

from webapp2 import cached_property
from webapp2_extras.security import generate_password_hash, generate_random_string, check_password_hash

from models import Account, AccountValidationFile, BitcoinAddress, BankAccount

from config import config
from utils import FrontendHandler, need_auth, get_or_404, abort, is_valid_bitcoin_address, is_valid_cbu

from profile_forms import ProfileForm, ChangePasswordForm

import json, re, urllib

from file_upload import UploadHandler

class ProfileController(FrontendHandler, UploadHandler):

  @need_auth()
  def otp(self, **kwargs):    
    kwargs['tab'] = 'otp';
    return self.render_response('frontend/profile.html', **kwargs)
  
  @need_auth()
  def personal_info(self, **kwargs):    
    
    account = get_or_404(self.user)
    kwargs['tab'] = 'personal_info';
    if self.request.method == 'GET':
      kwargs['form']              = ProfileForm(obj=account)
      return self.render_response('frontend/profile.html', **kwargs)
    
    self.request.charset  = 'utf-8'
    
    is_valid = self.form.validate()
    if not is_valid:
      kwargs['form']         = self.form
      if self.form.errors:
        kwargs['flash']      = self.build_error('Verifique los datos ingresados:')
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
    validation_file = db.get(db.Key(kwargs['key']))
    if str(validation_file.account.key()) != self.user:
      abort(404)
    
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
    account = get_or_404(self.user)
    
    if self.request.method == 'GET':
      kwargs['form']              = ChangePasswordForm(obj=account)
      return self.render_response('frontend/profile.html', **kwargs)
    
    self.request.charset  = 'utf-8'
    
    new_password  = self.password_form.new_password.data
    password      = self.password_form.password.data
    
    is_valid = self.password_form.validate() # valido que el nuevo password este confirmado.
    
    # repitio correctamente? el password viejo es correcto?
    if not is_valid or check_password_hash(password, account.password, config['my']['secret_key'])==False:
      account.last_password_change_ip     = self.request.remote_addr
      account.last_password_change_date   = datetime.now()
      kwargs['form']         = self.password_form
      if self.password_form.errors:
        kwargs['flash']      = self.build_error(u'Verifique los datos ingresados:')
      else:
        kwargs['flash']      = self.build_error(u'El password ingresado no es válido.')
      return self.render_response('frontend/profile.html', **kwargs)

    account.last_password_change_date   = datetime.now()
    account.last_password_change_ip     = self.request.remote_addr
    account.password = generate_password_hash(self.password_form.new_password.data, method='sha256', pepper=config['my']['secret_key'])
    account.save()
    
    self.set_ok(u'La contraseña fue modificada con éxito.')
    return self.redirect_to('profile-change_password')
  
  @cached_property
  def password_form(self):
    my_pwd_form = ChangePasswordForm(self.request.POST)
    my_pwd_form.user_key = self.user
    return my_pwd_form
  
  @need_auth()
  def bank_account(self, **kwargs):
    kwargs['tab'] = 'bank_account';
    account = get_or_404(self.user)
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)
    self.request.charset  = 'utf-8'
    
    cbu         = self.request.POST['bank_account_cbu'] 
    description = self.request.POST['bank_account_desc'] 
    
    if is_valid_cbu(cbu)==False:
      self.response.write(u'El CBU no es válido.')
      self.response.set_status(500)
      #self.error(500)
      return
      
    key       = self.request.POST['key'] 
    bank_acc  = None
    
    if key is None or key.strip()=='':
      bank_acc = BankAccount( account     = account,
                              cbu         = cbu,
                              description = description)
    else:
      bank_acc = db.get(db.Key(key))
      bank_acc.cbu          = cbu
      bank_acc.description  = description
      
    bank_acc.put()
    self.response.out.write("It's done!")
    return
      
  
  @need_auth()
  def bank_account_list(self, **kwargs):
    bankaccs = {'aaData':[]}

    for bankacc in BankAccount.all() \
              .filter('account =', db.Key(self.user)) \
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
    
    kwargs['tab'] = 'btc_address';
    account = get_or_404(self.user)
    
    if self.request.method == 'GET':
      return self.render_response('frontend/profile.html', **kwargs)
    self.request.charset  = 'utf-8'
    
    address     = self.request.POST['bitcoinaddr_address'] 
    description = self.request.POST['bitcoinaddr_desc'] 
    
    if is_valid_bitcoin_address(address)==False:
      self.response.write(u'La dirección no es una dirección de Bitcoin válida.')
      self.response.set_status(500)
      #self.error(500)
      return
      
    key     = self.request.POST['key'] 
    btc_addr = None
    
    if key is None or key.strip()=='':
      btc_addr = BitcoinAddress(account     = account,
                              address     = address,
                              description = description)
    else:
      btc_addr = db.get(db.Key(key))
      btc_addr.address     = address
      btc_addr.description = description
      
    btc_addr.put()
    self.response.out.write("It's done!")
    return
      
  
  @need_auth()
  def btc_address_delete(self, **kwargs):  
    btcaddress_or_bankacc = db.get(db.Key(kwargs['key']))
    referer = kwargs['referer']
    if str(btcaddress_or_bankacc.account.key()) != self.user:
      abort(404)
    
    db.delete(btcaddress_or_bankacc)
    if referer=='profile-btc_address':
      self.set_ok(u'La dirección fue eliminada.')
    else:
      self.set_ok(u'El CBU fue eliminado.')
    return self.redirect_to(referer)
    
  @need_auth()
  
  def btc_address_list(self, **kwargs):  
    addrs = {'aaData':[]}

    for addr in BitcoinAddress.all() \
              .filter('account =', db.Key(self.user)) \
              .order('-created_at'):

      row = []
      row.append(addr.address)
      row.append(addr.description)
      #row.append(str(addr.key()))
      row.append('<input type="hidden" name="key" value="'+str(addr.key())+'" />')
      row.append('<a href="' + self.url_for('profile-btc_address_delete', key=str(addr.key()), referer='profile-btc_address' ) + '">Borrar</a>')

      addrs['aaData'].append(row)

    return self.render_json_response(addrs)
