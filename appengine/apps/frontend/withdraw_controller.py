# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from google.appengine.ext import db
from google.appengine.ext import deferred

from webapp2 import cached_property

from models import TradeOrder, BankAccount, UserBitcoinAddress, AccountOperation
from utils import FrontendHandler, need_auth, get_or_404
from trader import Trader
from withdraw_forms import WithdrawBTCForm, WithdrawCurrencyForm

from mailer import send_withdrawrequestbtc_email, send_withdrawrequestars_email, send_cancelwithdrawrequestbtc_email, send_cancelwithdrawrequestars_email, mail_contex_for

class WithdrawController(FrontendHandler):
  
  @need_auth()
  def btc(self, **kwargs):
    
    kwargs['html']    = 'withdraw'
    kwargs['tab']     = 'withdraw_bitcoins'
    form              = self.withdraw_btc_form
    kwargs['form']    = form
    
    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      return self.render_response('frontend/withdraw.html', **kwargs)

    # Proceso el form
    if not form.validate():
      return self.render_response('frontend/withdraw.html', **kwargs)

    trader = Trader()
    order = trader.add_withdraw_btc_order(str(self.user), Decimal(form.amount.data), form.btc_address.data)
    
    # Verificamos si se pudo ingresar la orden
    if not order[0]:
      self.set_error(order[1])
      return self.render_response('frontend/withdraw.html', **kwargs)
    
    deferred.defer(send_withdrawrequestbtc_email
                        , mail_contex_for('send_withdrawrequestbtc_email'
                                        , get_or_404(self.user)
                                        , account_operation   =  order[0]))
      
    self.set_ok(u'El pedido de retiro fue realizado con éxito. (#%d)' % (order[0].key().id()) )

    return self.redirect(self.url_for('withdraw-btc'))

  @cached_property
  def withdraw_btc_form(self):
    return WithdrawBTCForm(self.request.POST, user=self.user)

  @need_auth()
  def currency(self, **kwargs):
    
    kwargs['html']    = 'withdraw'
    kwargs['tab']     = 'withdraw_currency'
    form              = self.withdraw_currency_form
    kwargs['form']    = form
    
    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      return self.render_response('frontend/withdraw.html', **kwargs)

    # Proceso el form
    if not form.validate():
      return self.render_response('frontend/withdraw.html', **kwargs)
    
    # validamos que la cuenta sea del fucking man
    bank_account = self.mine_or_404(form.bank_account.data)

    if not bank_account.active:
      self.set_error(u'El CBU es inválido y/o no ha sido verificado que Ud. sea el propietario de la cuenta.')
      return self.render_response('frontend/withdraw.html', **kwargs)
    
    trader = Trader()  
    ret    = trader.add_withdraw_currency_order(self.user, Decimal(form.amount.data), str(bank_account.key()))
    
    # Verificamos si se pudo ingresar la orden
    if not ret[0]:
      self.set_error(ret[1])
      return self.render_response('frontend/withdraw.html', **kwargs)

    if ret[0].currency.lower() == 'ars':
      deferred.defer( send_withdrawrequestars_email
                        , mail_contex_for('send_withdrawrequestars_email'
                                        , get_or_404(self.user)
                                        , account_operation   =  ret[0]))
                                        
    self.set_ok(u'El pedido de retiro fue realizado con éxito. (#%d)' % (ret[0].key().id()) )

    return self.redirect(self.url_for('withdraw-currency'))
  
  @cached_property
  def withdraw_currency_form(self):
    currency_form = WithdrawCurrencyForm(self.request.POST, user=self.user)
    return currency_form

  @need_auth()
  def cancel(self, **kwargs):  
    
    oper = self.mine_or_404(kwargs['key'], code=500, msg=u'Operación inválida')

    trader = Trader()
    ret = trader.cancel_withdraw_order(str(oper.key()))
    
    if ret[0]:
      self.set_ok(u'El pedido de retiro fue cancelado.')
      if ret[0].is_btc():
        deferred.defer( send_cancelwithdrawrequestbtc_email
                          , mail_contex_for('send_cancelwithdrawrequestbtc_email'
                                          , get_or_404(self.user)
                                          , account_operation   =  ret[0]))
      else:
        deferred.defer( send_cancelwithdrawrequestars_email
                          , mail_contex_for('send_cancelwithdrawrequestars_email'
                                          , get_or_404(self.user)
                                          , account_operation   =  ret[0]))
    else:
      self.set_error(ret[1])
    
    return self.redirect(self.request.referer)
    
  @need_auth()
  def list(self, **kwargs):  
    
    currency  = kwargs['currency']
    
    query  = AccountOperation.all().filter('account =', db.Key(self.user))    
    query = query.filter('operation_type =', AccountOperation.MONEY_OUT)
    query = query.filter('currency =', 'BTC' if currency == 'btc' else 'ARS')
                
    query = query.order('created_at')
    
    opers = {'aaData':[]}
    for oper in query.run(limit=50):
      row = []
      row.append(str(oper.key().id()))
      row.append(oper.created_at.strftime("%Y-%m-%d %H:%M:%S"))
      row.append('%s' % ( 'Retiro' if oper.operation_type == AccountOperation.MONEY_OUT else 'Deposito'))
      
      if oper.is_btc():
        row.append( '%.8f' % abs(oper.amount) )
      else:
        row.append( '%.2f' % abs(oper.amount) )

      row.append('%s' % ( oper.bank_account if oper.bank_account else oper.address))
      
      if oper.state == AccountOperation.STATE_PENDING:
        row.append('<a href="' + self.url_for('withdraw-cancel', key=str(oper.key()) ) + '">Cancelar</a>')
      else:
        row.append(self.label_for_oper(oper))
        
      opers['aaData'].append(row)

    return self.render_json_response(opers)
    
  def label_for_oper(self, oper):
    tmp = '<span class="label %s">%s</span>'
    
    if oper.state == AccountOperation.STATE_DONE:
      return tmp % ('label-success', 'Completada')
    elif oper.state == AccountOperation.STATE_ACCEPTED:
      return tmp % ('label-info', 'Aceptada')
    elif oper.state == AccountOperation.STATE_CANCELED:
      return tmp % ('label-important', 'Cancelada')

