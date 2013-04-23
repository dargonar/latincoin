# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache

from utils import FrontendHandler, need_auth
from models import Account, AccountOperation

from filters import do_label_for_acc_oper

class HistoryController(FrontendHandler):

  @need_auth()
  def account_ops(self, **kwargs):
    kwargs['html']     = 'history'
    kwargs['tab']      = 'history_%s' % kwargs['currency']

    return self.render_response('frontend/history_account_operations.html', **kwargs)
  
  @need_auth()
  def account_ops_list(self, **kwargs):
    currency = 'BTC' if kwargs['currency'] == 'btc' else 'ARS'

    descriptions = {AccountOperation.MONEY_IN   : 'Deposito de %s' % currency,
                    AccountOperation.MONEY_OUT  : 'Retiro de %s' % currency,
                    AccountOperation.BTC_SELL   : 'Venta de Bitcoin',
                    AccountOperation.BTC_BUY    : 'Compra de Bitcoin'}

    query = AccountOperation.all().filter('account =', db.Key(self.user))
    query = query.filter('currency =', currency)
    query = query.order('-created_at')
    
    deposits = {'aaData':[]}

    for aop in query:
      row = []
      row.append(aop.created_at.strftime("%Y-%m-%d %H:%M:%S"))
      row.append(descriptions[aop.operation_type])
      row.append('%.8f' % aop.amount )
      
      if aop.commission_rate is not None:
        row.append('%.3f' % aop.commission_rate )
      else:
        row.append('---')
      
      row.append( do_label_for_acc_oper(aop) )

      deposits['aaData'].append(row)

    return self.render_json_response(deposits)
    pass