# -*- coding: utf-8 -*-
import fix_path

from decimal import Decimal
from datetime import datetime 
import logging

from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.ext import deferred

from taskqueue import Mapper
from webapp2 import abort, cached_property, RequestHandler, Response, HTTPException, uri_for as url_for, get_app

from models import Ticker, Operation, TradeOrder
from mailer import send_partiallycompletedbid_email, send_completedbid_email, send_partiallycompletedask_email, send_completedask_email, mail_contex_for

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
                            high            = Decimal('0.0'),
                            low             = Decimal('1000000000.0'),
                            volume                = Decimal('0.0'),  
                            last_price_slope      = 0,
                            avg_price_slope       = 0,
                            high_slope      = 0,
                            low_slope       = 0,
                            volume_slope          = 0,
                            open                  = Decimal('0.0'),  
                            close                 = Decimal('0.0'))
    self.ticker.put()
    super(TickerMapper, self).__init__()
    # self.to_put = []
    # self.to_delete = []
  
  def get_query(self):
    """Returns a query over the specified kind, with any appropriate filters applied."""
    
    logging.info(' get_query mapper sys.path[%s]', sys.path)
    
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
    
    self.ticker.high            = oper.ppc if oper.ppc>self.ticker.high else self.ticker.high
    self.ticker.low             = oper.ppc if oper.ppc<self.ticker.low else self.ticker.low
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
    self.ticker.high_slope      = 1 if self.last_ticker.high>self.ticker.high else (-1 if self.last_ticker.high<self.ticker.high else 0)
    self.ticker.low_slope       = 1 if self.last_ticker.low>self.ticker.low else (-1 if self.last_ticker.low<self.ticker.low else 0)
    self.ticker.volume_slope          = 1 if self.last_ticker.volume>self.ticker.volume else (-1 if self.last_ticker.volume<self.ticker.volume else 0)
    self.ticker.status                = Ticker.DONE
    
    self.ticker.put()
    
class OperationNotificationMapper(Mapper):
  KIND        = Operation
  FILTERS     = []
  
  def __init__(self, **kwargs): 
    self.FILTERS          = [ ('traders_were_notified', '=', False)]
    super(OperationNotificationMapper, self).__init__()
  
  def get_query(self):
    """Returns a query over the specified kind, with any appropriate filters applied."""
    q = self.KIND.all()
    for prop, operator, value in self.FILTERS:
      q.filter("%s %s" % (prop, operator), value)
    q.order("__key__")
    
    return q

  def map(self, oper):
    
    
    
    logging.info(' Operation MAPPER begin')
    
    if oper.buyer_was_notified!= True:
      # envio mail al user de la purchase_order
      if oper.purchase_order.status == TradeOrder.ORDER_ACTIVE:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_partiallycompletedbid_email
                        , mail_contex_for('send_partiallycompletedbid_email'
                                        , oper.purchase_order.user
                                        , order=oper.purchase_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.purchase_order.purchases)))
      elif oper.purchase_order.status == TradeOrder.ORDER_COMPLETED:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_completedbid_email
                        , mail_contex_for('send_completedbid_email'
                                        , oper.purchase_order.user
                                        , order=oper.purchase_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.purchase_order.purchases)))
      oper.buyer_was_notified = True
      
    if oper.seller_was_notified!= True:
      # envio mail al user de la sale_order
      if oper.sale_order.status == TradeOrder.ORDER_ACTIVE:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_partiallycompletedask_email
                        , mail_contex_for('send_partiallycompletedask_email'
                                        , oper.sale_order.user
                                        , order=oper.sale_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.sale_order.sales)))
      elif oper.sale_order.status == TradeOrder.ORDER_COMPLETED:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_completedask_email
                        , mail_contex_for('send_completedask_email'
                                        , oper.sale_order.user
                                        , order=oper.sale_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.sale_order.sales)))
      oper.seller_was_notified = True
    
    oper.traders_were_notified = (oper.seller_was_notified and oper.buyer_was_notified)
    #oper.last_notification = datetime.now()
    return ([oper],[])
  
  
  def finish(self):
    pass
    
    
    # if bid_ask == 'bid':
      # deferred.defer(send_newbid_email, mail_contex_for('send_newbid_email', user, order=trade[0]))
      # if form.market()!=True:
        # deferred.defer(send_completedbid_email, mail_contex_for('send_completedbid_email', user, order=trade[0], opers=trade[0].purchases))
    # else:
      # deferred.defer(send_newask_email, mail_contex_for('send_newask_email', user, order=trade[0]))
      # if form.market()!=True:
        # deferred.defer(send_completedask_email, mail_contex_for('send_completedask_email', user, order=trade[0], opers=trade[0].sales))
    