from google.appengine.ext import db

from webapp2 import cached_property

from models import Account
from utils import FrontendHandler, need_auth, get_or_404

from profile_forms import ProfileForm

class ProfileController(FrontendHandler):

  @need_auth()
  def personal_info(self, **kwargs):    
    
    kwargs['tab'] = 'personal_info';
    if self.request.method == 'GET':
      account = get_or_404(self.user)
      kwargs['form']              = ProfileForm(obj=account)
      return self.render_response('frontend/profile.html', **kwargs)
    
    self.request.charset  = 'utf-8'
    
    account = get_or_404(self.user)
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
  def identity_validation(self, **kwargs):    
    kwargs['tab'] = 'identity_validation';
    return self.render_response('frontend/profile.html', **kwargs)