# -*- coding: utf-8 -*-
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import cached_property

from models import TradeOrder
from utils import FrontendHandler, need_auth
from trader import Trader
from trade_forms import BidForm, AskForm

class TradeController(FrontendHandler):
  
  def apply_operation(self, **kwargs):
    trader = Trader()
    tmp = trader.apply_operation(kwargs['key'])

    self.response.write(tmp)

  def match_orders(self, **kwargs):
    trader = Trader()
    tmp = trader.match_orders()

    self.response.write(tmp)

  @need_auth()
  def new(self, **kwargs):
    kwargs['html']     = 'trade'
    kwargs['ask_form'] = self.ask_form
    kwargs['bid_form'] = self.bid_form

    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      kwargs['active_tab'] = 'bid' if not 'active_tab' in self.request.GET else self.request.GET['active_tab']
      return self.render_response('frontend/trade.html', **kwargs)

    # Viene POST validamos el FORM
    bid_ask = self.request.POST['type']
    
    # Elegimos el form (de acuerdo al type)
    form = self.bid_form if bid_ask == 'bid' else self.ask_form

    # Proceso el form
    form_validated = form.validate()
    if not form_validated:
      return self.render_response('frontend/trade.html', active_tab=bid_ask, **kwargs)

    trader = Trader()

    # Es una market order?
    if form.market():
      trade = trader.add_market_trade(self.user, 'B' if bid_ask == 'bid' else 'A', 
                                    Decimal(form.amount()) )
    else:
      trade = trader.add_limit_trade(self.user, 'B' if bid_ask == 'bid' else 'A', 
                                    Decimal(form.amount()), Decimal(form.ppc()))

    # Verificamos si se pudo ingresar la orden
    if not trade[0]:
      self.set_error(trade[1])
      return self.render_response('frontend/trade.html', active_tab=bid_ask, **kwargs)

    self.set_ok(u'La orden fue %s con éxito. (#%d)' % ('ingresada' if form.market() else 'completada',trade[0].key().id()) )

    return self.redirect(self.url_for('trade-new') + ('?active_tab=%s' % bid_ask))

  @cached_property
  def ask_form(self):
    return AskForm(self.request.POST)

  @cached_property
  def bid_form(self):
    return BidForm(self.request.POST)

  @need_auth()
  def cancel_order(self, **kwargs):

    key = kwargs['key']
    
    # Verificamos que la orden sea del usuario que esta logueado
    order = self.mine_or_404(key)

    trader = Trader()
    result = trader.cancel_order(key)

    if result:
      self.set_ok(u'La orden (#%d) fue cancelada con éxito.' % order.key().id())
    else:
      self.set_error(u'La orden (#%d) no pudo ser cancelada.' % order.key().id())

    bid_ask = 'bid' if order.is_bid() else 'ask'
    return self.redirect(self.url_for('trade-new') + ('?active_tab=%s' % bid_ask))

  @need_auth()
  def list_orders(self, **kwargs):

    type  = kwargs['type']
    mode  = kwargs['mode']

    orders = {'aaData':[]}

    query  = TradeOrder.all().filter('user =', db.Key(self.user))

    if mode == 'active':
      query = query.filter('status =', TradeOrder.ORDER_ACTIVE)
      query = query.order('created_at')
    else:
      query = query.filter('status !=', TradeOrder.ORDER_ACTIVE)
    
    if type != 'any':
      query = query.filter('bid_ask =', TradeOrder.BID_ORDER if type =='bid' else TradeOrder.ASK_ORDER)
      query = query.filter('order_type =', TradeOrder.LIMIT_ORDER)

    for order in query:

      row = []
      row.append('#%d' % order.key().id())
      row.append(order.created_at.strftime("%Y-%m-%d %H:%M"))
      row.append('%s%s' % ( 'Compra' if order.bid_ask == TradeOrder.BID_ORDER else 'Venta', '' if order.order_type == TradeOrder.LIMIT_ORDER else ' (inmediata)' ))

      if order.order_type == TradeOrder.LIMIT_ORDER:
        temp = order.original_amount-order.amount
        row.append('%.2f&nbsp;de&nbsp;%.2f' % (temp,order.original_amount))
      else:
        temp = order.amount
        row.append('%.2f' % temp)

      row.append('%.2f' % order.ppc)
      row.append('%.2f' % (order.ppc*temp) )
      
      
      row.append(self.label_for_order(order))
      if order.status==TradeOrder.ORDER_ACTIVE:
        row.append('<a href="' + self.url_for('trade-cancel', key=str(order.key())) + '">Cancelar</a>')
      else:
        row.append('')

      orders['aaData'].append(row)

    return self.render_json_response(orders)

  def label_for_order(self, order):
    
    tmp = '<span class="label %s" style="padding: 0;width:100%%;"><span class="label label-success" style="float: left; width: %d%%; padding: 2px 0 2px 0;">%s</span></span>'
    percent = int(Decimal('100')*(Decimal('1') - order.amount/order.original_amount))

    if order.status == TradeOrder.ORDER_ACTIVE:
      return tmp % ('', percent, 'Activa')
    elif order.status == TradeOrder.ORDER_COMPLETED:
      return tmp % ('label-success', 100, 'Completada')
    elif order.status == TradeOrder.ORDER_CANCELED:
      return tmp % ('label-inverse', percent, 'Cancelada')

  @need_auth()
  def history(self, **kwargs):
    kwargs['html'] = 'history'
    return self.render_response('frontend/operations.html', **kwargs)
