# -*- coding: utf-8 -*-

from utils import FrontendHandler

class Designer(FrontendHandler):

  def verHtmlTemplate(self, **kwargs):
    #return self.render_response('frontend/signin.html')
    return self.render_response('frontend/'+kwargs['html']+'.html')
  