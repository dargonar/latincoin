# -*- coding: utf-8 -*-

from utils import FrontendHandler

class Account(FrontendHandler):

  def signin(self, **kwargs):
    return self.render_response('frontend/signin.html')

  def login(self, **kwargs):
    return self.render_response('frontend/login.html')
