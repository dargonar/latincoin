# -*- coding: utf-8 -*-

from utils import FrontendHandler

class DesignerController(FrontendHandler):

  def verHtmlTemplate(self, **kwargs):
    #return self.render_response('frontend/signin.html')
    return self.render_response('frontend/'+kwargs['html']+'.html', **kwargs)
  