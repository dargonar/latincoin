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
      # Si esta activa significa que aún no se completó.
      # Eviamos mail "parcialmente completada"
      if oper.purchase_order.status == TradeOrder.ORDER_ACTIVE:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_partiallycompletedbid_email
                        , mail_contex_for('send_partiallycompletedbid_email'
                                        , oper.purchase_order.user
                                        , order=oper.purchase_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.purchase_order.purchases)))
      # Orden completada: eviamos mail "fully completada"
      elif oper.purchase_order.status == TradeOrder.ORDER_COMPLETED:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_completedbid_email
                        , mail_contex_for('send_completedbid_email'
                                        , oper.purchase_order.user
                                        , order=oper.purchase_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.purchase_order.purchases)))
      oper.buyer_was_notified = True
      
    # Envio mail al user de la sale_order
    if oper.seller_was_notified!= True:
      # Si esta activa significa que aún no se completó.
      # Eviamos mail "parcialmente completada"
      if oper.sale_order.status == TradeOrder.ORDER_ACTIVE:
        logging.info(' Mapper::enviando mail a %s', oper)
        deferred.defer(send_partiallycompletedask_email
                        , mail_contex_for('send_partiallycompletedask_email'
                                        , oper.sale_order.user
                                        , order=oper.sale_order
                                        , opers=filter(lambda x:x.traders_were_notified==False,oper.sale_order.sales)))
      # Orden completada: eviamos mail "fully completada"
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
