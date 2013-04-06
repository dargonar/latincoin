# -*- coding: utf-8 -*-

from utils import FrontendHandler

class MainController(FrontendHandler):
  def home(self, **kwargs):
    #kwargs[]
    return self.render_response('frontend/index.html', **kwargs)

  def terms(self, **kwargs):
    return self.render_response('frontend/terminos.html', **kwargs)

    
  def contact(self, **kwargs):
    return self.render_response('frontend/index.html', **kwargs)
  
  def deposito(self, **kwargs):
    return self.render_response('frontend/deposito.html', **kwargs)
    
  def retiro(self, **kwargs):
    return self.render_response('frontend/retiro.html', **kwargs)
