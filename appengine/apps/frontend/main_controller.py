# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import memcache

from utils import FrontendHandler
from models import TradeOrder, Operation

class MainController(FrontendHandler):
  
  def get_active_orders(self, max_orders=100):
    orders                  = {}
    bids                    = self.get_trade_orders('active','bid', '-')
    asks                    = self.get_trade_orders('active','ask','')
    orders['bids']          = bids
    orders['asks']          = asks
    orders['html_orders']   = self.render_template('frontend/market_orders.html', max_orders=max_orders, bids=orders['bids'],  asks=orders['asks'])
    return orders    
  
  def get_active_orders_html(self, max_orders=10, max_opers=10 ):
    data = memcache.get('orders-opers_html_tables')
    if data is None:
      index_html_tables = {}
      
      orders = self.get_active_orders(max_orders=max_orders)
      index_html_tables['orders']         = orders['html_orders']
      
      index_html_tables['operations']     = self.render_template('frontend/market_operations.html', max_opers =max_opers , opers = self.get_operations())
      
      data = index_html_tables
      memcache.add('orders-opers_html_tables', data, 60)
    return data
    
  def home(self, **kwargs):
    data = self.get_active_orders_html()
    return self.render_response('frontend/index.html', _tables=data)
  
  
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
    
    query = query.order(sort)
    return query
    
  def terms(self, **kwargs):
    return self.render_response('frontend/static/terms.html', **kwargs)
  
  def soon(self, **kwargs):
    return self.render_response('frontend/static/soon.html', **kwargs)
  
  def about_us(self, **kwargs):
    return self.render_response('frontend/static/about_us.html', **kwargs)
    
  def terms(self, **kwargs):
    return self.render_response('frontend/static/terms.html', **kwargs)
    
  def privacy(self, **kwargs):
    return self.render_response('frontend/static/privacy.html', **kwargs)
    
  def security(self, **kwargs):
    return self.render_response('frontend/static/security.html', **kwargs)
  
  def fees(self, **kwargs):
    return self.render_response('frontend/static/fees.html', **kwargs)
  
  def api(self, **kwargs):
    return self.render_response('frontend/static/api.html', **kwargs)
  
  def what_is_bitcoin(self, **kwargs):
    return self.render_response('frontend/static/what_is_bitcoin.html', **kwargs)
  
  def how_to_buy(self, **kwargs):
    return self.render_response('frontend/static/how_to_buy.html', **kwargs)
  
  def how_to_sell(self, **kwargs):
    return self.render_response('frontend/static/how_to_sell.html', **kwargs)
  
  def faq(self, **kwargs):
    return self.render_response('frontend/static/faq.html', **kwargs)
  
  def forum(self, **kwargs):
    return self.render_response('frontend/static/forum.html', **kwargs)
  
  def order_book(self, **kwargs):
    #from webapp2_extras import json
    orders_data = self.get_active_orders(max_orders=100)
    chart_data = self.get_order_book_data(bids=orders_data['bids'], asks=orders_data['asks'])
    return self.render_response('frontend/static/order_book.html', _orders_tables=orders_data['html_orders'], chart_data=chart_data, home=True)
  
  def order_book_data(self, **kwargs):
    return self.render_json_response(self.get_order_book_data())
  
  def get_order_book_data(self, bids=None, asks=None):  
    data = memcache.get('order_book_chart_data_array')
    if data is None:
      orders_data = self.get_active_orders(max_orders=100)
      if bids is None:
        bids = orders_data['bids']
      if asks is None:
        asks = orders_data['asks']
      
      # Bids processing: tengo un punto por cada precio de btc(ejeX). Sumo los btc para ppc iguales.
      _bids={}
      for bid in bids.run(limit=100):
        ppc = str('%.5f' % bid.ppc)
        if ppc in _bids:
          _bids[ppc]+=bid.amount
        else:
          _bids[ppc]=bid.amount
      
      bid_chart_data = []
      for key in sorted(_bids.iterkeys()): #, reverse=True
        value = _bids[key]
        bid_chart_data.append( [round(float(key),5), round(value,5)] )
        
      # Asks processing: tengo un punto por cada precio de btc(ejeX). Sumo los btc para ppc iguales.
      _asks={}
      for ask in asks.run(limit=100):
        ppc = str('%.5f' % ask.ppc)
        if ppc in _asks:
          _asks[ppc]+=ask.amount
        else:
          _asks[ppc]=ask.amount
      
      ask_chart_data = []
      for key in sorted(_asks.iterkeys()):
        value = _asks[key]
        ask_chart_data.append( [round(float(key),5), round(value,5)] )
        
      data={'bids':bid_chart_data, 'asks':ask_chart_data}
      # Descomentar
      memcache.add('order_book_chart_data_array', data, 60)
    return data    
      