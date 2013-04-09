# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import memcache

from utils import FrontendHandler
from models import TradeOrder, Operation

class MainController(FrontendHandler):
  def home(self, **kwargs):
    #kwargs[]
    data = memcache.get('index_html_tables')
    if data is None:
      index_html_tables = {}
      index_html_tables['orders']         = self.render_template('frontend/market_orders.html', bids=self.get_trade_orders('active','bid', '-'),  asks=self.get_trade_orders('active','ask',''))
      index_html_tables['operations']     = self.render_template('frontend/market_operations.html', opers = self.get_operations())
      data = index_html_tables
      memcache.add('index_html_tables', data, 60)
    
    return self.render_response('frontend/index.html', _tables=data, home=True)
  
  
  def get_operations(self):
    #return Operation.all().order('-updated_at')
    return Operation.all().filter('status =', Operation.OPERATION_DONE).order('-created_at')
    
  def get_trade_orders(self, mode, type, sort):

    # type  = kwargs['type']
    # mode  = kwargs['mode']
    sort = '%sppc' % sort
    query  = TradeOrder.all() 

    if mode == 'active':
      query = query.filter('status =', TradeOrder.ORDER_ACTIVE)
    else:
      query = query.filter('status !=', TradeOrder.ORDER_ACTIVE)
    
    if type != 'any':
      query = query.filter('bid_ask =', TradeOrder.BID_ORDER if type =='bid' else TradeOrder.ASK_ORDER)
      query = query.filter('order_type =', TradeOrder.LIMIT_ORDER)
    
    #query = query.order('-created_at')
    query = query.order(sort)
    return query
    
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
      row.append('<a href="' + self.url_for('trade-cancel', key=str(order.key())) + '">Cancelar</a>')

      orders['aaData'].append(row)

    return self.render_json_response(orders)

  
  def terms(self, **kwargs):
    return self.render_response('frontend/terminos.html', **kwargs)

    
  def contact(self, **kwargs):
    return self.render_response('frontend/index.html', **kwargs)
  
  def deposito(self, **kwargs):
    return self.render_response('frontend/deposito.html', **kwargs)
    
  def withdraw(self, **kwargs):
    return self.render_response('frontend/retiro.html', **kwargs)
