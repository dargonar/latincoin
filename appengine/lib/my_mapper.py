# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

from decimal import Decimal

import logging

from google.appengine.ext import db
from google.appengine.api import taskqueue
from taskqueue import Mapper
from webapp2 import abort, cached_property, RequestHandler, Response, HTTPException, uri_for as url_for, get_app

from models import Ticker, Operation

class TickerMapper(Mapper):
  KIND        = Operation
  FILTERS     = []
  
  def __init__(self, last_ticker_key, **kwargs): 
    
    last_ticker           = db.get(db.Key(last_ticker_key))
    logging.info(' init mapper date[%s] sys.path[%s]', str(last_ticker.updated_at), sys.path)
    self.FILTERS          = [ ('created_at', '>', last_ticker.updated_at), ('status', '=', Operation.OPERATION_DONE) ]
    self.last_ticker      = last_ticker
    
    self.prices_sum       = 0
    self.oper_count       = 0
    
    # el nuevo ticker
    self.ticker = Ticker(   status                = Ticker.IN_PROGRESS,
                            last_price            = Decimal('0.0'),
                            avg_price             = Decimal('0.0'),
                            high_price            = Decimal('0.0'),
                            low_price             = Decimal('1000000000.0'),
                            volume                = Decimal('0.0'),  
                            last_price_slope      = 0,
                            avg_price_slope       = 0,
                            high_price_slope      = 0,
                            low_price_slope       = 0,
                            volume_slope          = 0,
                            open                  = Decimal('0.0'),  
                            close                 = Decimal('0.0'))
    self.ticker.put()
    super(TickerMapper, self).__init__()
    # self.to_put = []
    # self.to_delete = []
  
  def get_query(self):
    """Returns a query over the specified kind, with any appropriate filters applied."""
    
    q = self.KIND.all()
    for prop, operator, value in self.FILTERS:
      q.filter("%s %s" % (prop, operator), value)
    q.order("__key__")
    
    logging.info(' MAPPER get_query')
    
    return q

  def map(self, oper):
    
    logging.info(' MAPPER map begin')
    self.prices_sum       += oper.ppc
    self.oper_count       += 1
    
    self.ticker.high_price            = oper.ppc if oper.ppc>self.ticker.high_price else self.ticker.high_price
    self.ticker.low_price             = oper.ppc if oper.ppc<self.ticker.low_price else self.ticker.low_price
    self.ticker.volume                += oper.traded_btc 
    if self.ticker.open == Decimal('0.0'):
      self.ticker.open                = oper.ppc
    self.ticker.close                 = oper.ppc
    self.ticker.last_price            = oper.ppc
    
    logging.info(' MAPPER map finish')
    return ([],[])
  
  def finish(self):
    logging.info('MAPPER se fini')
    if self.oper_count==0:
      logging.info('MAPPER NO HAGO NADA oper count=%s', str(self.oper_count))
      # copio todo
      return
    
    logging.info('MAPPER oper count=%s', str(self.oper_count))
    self.ticker.avg_price             = self.prices_sum / self.oper_count
    
    self.ticker.last_price_slope      = 1 if self.last_ticker.last_price>self.ticker.last_price else (-1 if self.last_ticker.last_price<self.ticker.last_price else 0)
    self.ticker.avg_price_slope       = 1 if self.last_ticker.avg_price>self.ticker.avg_price else (-1 if self.last_ticker.avg_price<self.ticker.avg_price else 0)
    self.ticker.high_price_slope      = 1 if self.last_ticker.high_price>self.ticker.high_price else (-1 if self.last_ticker.high_price<self.ticker.high_price else 0)
    self.ticker.low_price_slope       = 1 if self.last_ticker.low_price>self.ticker.low_price else (-1 if self.last_ticker.low_price<self.ticker.low_price else 0)
    self.ticker.volume_slope          = 1 if self.last_ticker.volume>self.ticker.volume else (-1 if self.last_ticker.volume<self.ticker.volume else 0)
    self.ticker.status                = Ticker.DONE
    
    self.ticker.put()
    