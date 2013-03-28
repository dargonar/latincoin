# -*- coding: utf-8 -*-

from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images, files
from google.appengine.api.images import get_serving_url

from webapp2 import cached_property

from models import Account, AccountValidationFile
from utils import FrontendHandler, need_auth, get_or_404, abort

from profile_forms import ProfileForm, ChangePasswordForm

import json, re, urllib

from file_upload import UploadHandler

class ProfileController(FrontendHandler, UploadHandler):

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
      #result['delete_type']
      #result['delete_url']
      #result['blob_key']
            
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
    
    is_valid = self.password_form.validate()
    if not is_valid:
      kwargs['form']         = self.password_form
      if self.password_form.errors:
        kwargs['flash']      = self.build_error(u'Verifique los datos ingresados:')
      return self.render_response('frontend/profile.html', **kwargs)

    account          = self.password_form.update_object(account)
    account.save()
    
    self.set_ok(u'Contraseña modificada satisfactoriamente.')
    return self.redirect_to('profile-change_password')
  
  @cached_property
  def password_form(self):
    my_pwd_form = ChangePasswordForm(self.request.POST)
    my_pwd_form.user_key = self.user
    return my_pwd_form
  