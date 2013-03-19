# -*- coding: utf-8 -*-
from decimal import Decimal

from webapp2 import cached_property

from utils import FrontendHandler, need_auth
from trader import Trader
from trade_forms import TradeForm

class TradeController(FrontendHandler):
  
  @need_auth()
  def new(self, **kwargs):
    
    kwargs['ask_form'] = self.ask_form
    kwargs['bid_form'] = self.bid_form

    if self.request.method == 'GET':
      return self.render_response('frontend/trade.html', **kwargs)

    bid_ask = self.request.POST['type']

    # Elegimos el form (de acuerdo al type)
    form = self.bid_form if bid_ask else self.ask_form

    # Proceso el form
    form_validated = form.validate()
    if not form_validated:
      return self.render_response('frontend/trade.html', **kwargs)

    trader = Trader()
    trade = trader.add_limit_trade(self.user, 'B' if bid_ask == 'bid' else 'A', 
                                    Decimal(form.amount.data), Decimal(form.ppc.data))

    # Verificamos si se pudo ingresar la orden
    if not trade[0]:
      self.set_error(trade[1])
      return self.render_response('frontend/trade.html', **kwargs)      

    self.set_ok(u'La orden fue ingresada con éxito. (#%d)' % trade[0].key().id())

    return self.redirect_to('trade-new')

  @cached_property
  def ask_form(self):
    return TradeForm(self.request.POST)

  @cached_property
  def bid_form(self):
    return TradeForm(self.request.POST)
