from appengine.mapper import Mapper

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
    