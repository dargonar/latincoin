# -*- coding: utf-8 -*-

from utils import FrontendHandler, need_auth

class Trade(FrontendHandler):
  
  @need_auth()
  def buysell(self, **kwargs):
    kwargs['html'] = 'trade'
    return self.render_response('frontend/trade.html', **kwargs)

