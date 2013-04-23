# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import cached_property

import exchanger
from models import BankAccount, AccountOperation, Account
from utils import BackendHandler, get_or_404, need_admin_auth

class WithdrawController(BackendHandler):
  user_key = ''
  
  @need_admin_auth()
  def edit(self, **kwargs):
    
    oper  = get_or_404(kwargs['key'])
    state = kwargs['state'].strip()
    ret = []
    
    if state == AccountOperation.STATE_ACCEPTED:
      ret = exchanger.accept_withdraw_order(str(oper.key()))
    if state == AccountOperation.STATE_CANCELED:
      ret = exchanger.cancel_withdraw_order(str(oper.key()))
    if state == AccountOperation.STATE_DONE:
      ret = exchanger.done_withdraw_order(str(oper.key()))
    
    if state != AccountOperation.STATE_PENDING and len(state)>0 and ret and len(ret)>1:
      if ret[0]:
        self.set_ok(u'La orden de retiro fue modificada satisfactoriemnte.')
      else:
        self.set_error(ret[1])
    
    if 'user_key' in kwargs:
      return self.redirect_to('backend-withdraw-list_for_user',user=kwargs['user_key'])
    return self.redirect_to('backend-withdraw-list')
    
    
  @need_admin_auth()
  def list(self, **kwargs):
    query  = AccountOperation.all().filter('operation_type =', AccountOperation.MONEY_OUT)
    query  = query.filter('operation_type !=', AccountOperation.STATE_CANCELED)
    query  = query.order('operation_type')
    
    kwargs['opers']=query
    kwargs['html']='withdrawals'
    return self.render_response('backend/withdraw.html', **kwargs)
    
  @need_admin_auth()
  def list_for_user(self, **kwargs):
    kwargs['html']      = 'withdrawals'
    self.user_key       = kwargs['user']
    account_key         = db.Key(kwargs['user'])
    
    kwargs['user_key']  = kwargs['user']
    kwargs['account']   = get_or_404(account_key)
    
    query  = AccountOperation.all().filter('account =', db.Key(self.user_key))    
    query = query.filter('operation_type =', AccountOperation.MONEY_OUT)
    #query = query.filter('currency =', 'BTC' if currency == 'btc' else 'ARS')
                
    query = query.order('created_at')
    
    kwargs['opers'] = query
    return self.render_response('backend/withdraw.html', **kwargs)
  