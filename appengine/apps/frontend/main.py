# -*- coding: utf-8 -*-

from utils import FrontendHandler

class Main(FrontendHandler):
  def home(self):
    return self.render_response('frontend/index.html')
