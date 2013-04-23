# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import cached_property

import exchanger
from models import BankAccount, AccountOperation, Account
from utils import BackendHandler, get_or_404, need_admin_auth
from forms.deposit import DepositCurrencyForm

class DepositController(BackendHandler):
  user_key = ''
  
  @need_admin_auth()
  def list(self, **kwargs):
    return self.redirect_to('backend-user-list')
    
  @need_admin_auth()
  def currency(self, **kwargs):
    
    if 'user' not in kwargs:
      return self.redirect_to('backend-user-list')
      
    kwargs['html']        = 'deposits'
    logging.error(' ----------%s', kwargs['user'])
    self.user_key         = kwargs['user'].strip() 
    kwargs['user_key']    = self.user_key
    kwargs['account']     = Account.get(db.Key(self.user_key))
    
    form                  = self.deposit_currency_form
    kwargs['form']        = form
    
    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      return self.render_response('backend/deposit.html', **kwargs)

    # Proceso el form
    if not form.validate():
      
      return self.render_response('backend/deposit.html', **kwargs)
    
    # vemos si puso cuenta, no es requerida
    if form.bank_account.data and len(form.bank_account.data)>0:
      bank_account = db.get(form.bank_account.data)
    else:
      bank_account=None
      
    if bank_account and not bank_account.active:
      self.set_error(u'El CBU es inválido y/o no ha sido verificado.')
      return self.render_response('backend/deposit.html', **kwargs)
    
    #add_ars_balance(self.user, Decimal(form.amount.data), str(bank_account.key()))
    ret = exchanger.add_currency_balance(self.user_key, form.amount.data, bank_account)
    
    # Verificamos si se pudo ingresar la orden
    if not ret[0]:
      self.set_error(ret[1])
      return self.render_response('backend/deposit.html', **kwargs)

    self.set_ok(u'El depósito fue realizado con éxito. (#%d)' % (ret[0].key().id()) )

    return self.redirect(self.url_for('backend-deposit-currency', user=self.user_key))
  
  @cached_property
  def deposit_currency_form(self):
    currency_form = DepositCurrencyForm(self.request.POST, user=self.user_key) #self.request.POST['user']
    return currency_form

  