# -*- coding: utf-8 -*-
from decimal import Decimal

from google.appengine.ext import db
from google.appengine.api import taskqueue

from webapp2 import cached_property, uri_for as url_for

import exchanger

from models import TradeOrder
from utils import FrontendHandler, need_auth, get_or_404
from forms.trade import BidForm, AskForm
from mail.mailer import enqueue_mail

class TradeController(FrontendHandler):
  
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

    # Es una market order?
    if form.market():
      trade = exchanger.add_market_trade(self.user, 'B' if bid_ask == 'bid' else 'A', 
                                    Decimal(form.amount()) )
    else:
      trade = exchanger.add_limit_trade(self.user, 'B' if bid_ask == 'bid' else 'A', 
                                    Decimal(form.amount()), Decimal(form.ppc()))

    # Verificamos si se pudo ingresar la orden
    if not trade[0]:
      self.set_error(trade[1])
      return self.render_response('frontend/trade.html', active_tab=bid_ask, **kwargs)
    
    self.set_ok(u'La orden fue %s con éxito. (#%d)' % ('ingresada' if form.market() else 'completada',trade[0].key().id()) )

    # Si fue una orden de mercado, mandamos el mail correspondiente
    # Lo hacemos aca por que no se si un encolamiento puede frenar una transaccion
    # Es mas importante que se realize el trade que mandar el mail, por eso lo hacemos afuera
    
    # NOTA: las funciones add_market_* add_limit_* sabemos que pudieron escribir bien en la "DB".
    # Y tambien sabemos que se van a escribir bien los indices, lo que no sabemos es cuando
    # por eso al mandar al toque el taskqueue.add puede ser que no encuentre la recien creada operacion
    # o el match_orders no encuentre la orden 

    order_key = str(trade[0].key())
    if form.market():
      enqueue_mail('completed_order', {'user_key':self.user, 'order_key':order_key})
      taskqueue.add(url=url_for('task-apply-operations'))    
    else:
      enqueue_mail('new_order', {'user_key':self.user, 'order_key':order_key})
      taskqueue.add(url=url_for('task-match-orders'))    

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

    result = exchanger.cancel_order(key)

    if result:
      self.set_ok(u'La orden (#%d) fue cancelada con éxito.' % order.key().id())
    else:
      self.set_error(u'La orden (#%d) no pudo ser cancelada.' % order.key().id())

    bid_ask = 'bid' if order.is_bid() else 'ask'
    
    # HACKU: separar esto en dos forms para hacer todo mas sencillo
    if 'history' in self.request.referer:
      return self.redirect(self.request.referer)

    # Notificamos por mail, mismo rationale que add_trade_order (ver mas arriba)
    enqueue_mail('cancel_order', {'user_key':self.user, 'order_key':key})

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
      row.append(order.created_at.strftime("%Y-%m-%d %H:%M:%S"))
      row.append('%s%s' % ( 'Compra' if order.bid_ask == TradeOrder.BID_ORDER else 'Venta', '' if order.order_type == TradeOrder.LIMIT_ORDER else ' (inmediata)' ))

      if order.order_type == TradeOrder.LIMIT_ORDER:
        temp = order.original_amount-order.amount
        if order.status==TradeOrder.ORDER_ACTIVE:
          row.append('%.2f<br/><small>(restan&nbsp;%.2f)</small>' % (order.original_amount, order.original_amount-temp))
        else:
          row.append('%.2f' % order.original_amount)
      else:
        temp = order.amount
        row.append('%.2f' % temp)

      row.append('%.2f' % order.ppc)
      #row.append('%.2f' % (order.ppc*temp) )
      row.append('%.2f' % (order.ppc*order.amount) )
      
      row.append(self.label_for_order(order))
      if order.status==TradeOrder.ORDER_ACTIVE:
        row.append('<a href="' + self.url_for('trade-cancel', key=str(order.key())) + '" class="btn mini red"><i class="icon-remove"></i>&nbsp;Cancelar</a>')
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
