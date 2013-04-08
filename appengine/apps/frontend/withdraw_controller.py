# -*- coding: utf-8 -*-
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import cached_property

from models import TradeOrder, BankAccount, UserBitcoinAddress, AccountOperation
from utils import FrontendHandler, need_auth, get_or_404
from trader import Trader
from withdraw_forms import WithdrawBTCForm, WithdrawCurrencyForm

class WithdrawController(FrontendHandler):
  
  @need_auth()
  def new_btc(self, **kwargs):
    
    kwargs['html']    = 'withdraw'
    kwargs['tab']     = 'withdraw_bitcoins'
    form              = self.withdraw_btc_form
    kwargs['form']    = form
    
    btc_addresses = UserBitcoinAddress.all().filter('active =', True).filter('account =', db.Key(self.user))
      
    data_source = ''
    data_source_count = 0
    for btc_address in btc_addresses:
      data_source += '"'+btc_address.address+'",'
    if data_source.strip() != '':
      data_source = '[' + data_source + '""'+']'
    
    kwargs['data_source'] = data_source
    kwargs['data_source_count'] = str(data_source_count)
    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      return self.render_response('frontend/withdraw.html', **kwargs)

    # Proceso el form
    form_validated = form.validate()
    if not form_validated:
      return self.render_response('frontend/withdraw.html', **kwargs)

    trader    = Trader()
    account   = get_or_404(self.user)
    order     = trader.add_widthdraw_btc_order(str(self.user), form.amount(), form.address())
    
    # Verificamos si se pudo ingresar la orden
    if not order[0]:
      self.set_error(order[1])
      return self.render_response('frontend/withdraw.html', **kwargs)

    self.set_ok(u'El pedido de retiro realizado con éxito. (#%d)' % (order[0].key().id()) )

    return self.redirect(self.url_for('withdraw-bitcoins'))

  @cached_property
  def withdraw_btc_form(self):
    return WithdrawBTCForm(self.request.POST)

  @need_auth()
  def new_currency(self, **kwargs):
    
    kwargs['html']    = 'withdraw'
    kwargs['tab']     = 'withdraw_currency'
    form              = self.withdraw_currency_form
    kwargs['form']    = form
    
    # Si viene GET mostramos el FORM
    if self.request.method == 'GET':
      return self.render_response('frontend/withdraw.html', **kwargs)

    # Proceso el form
    form_validated = form.validate()
    if not form_validated:
      return self.render_response('frontend/withdraw.html', **kwargs)

    trader    = Trader()
    account   = get_or_404(self.user)
    
    # validamos que el cbu sea del fucking man
    bank_account = BankAccount.all().filter('cbu =', form.cbu()).filter('active =', True).filter('account =', db.Key(self.user)).get()
    
    if not bank_account:
      self.set_error(u'El CBU es inválido y/o no ha sido verificado que Ud. sea el propietario de la cuenta.')
      return self.render_response('frontend/withdraw.html', **kwargs)
      
    order     = trader.add_widthdraw_currency_order(str(self.user), form.amount(), str(bank_account.key()))
    
    # Verificamos si se pudo ingresar la orden
    if not order[0]:
      self.set_error(order[1])
      return self.render_response('frontend/withdraw.html', **kwargs)

    self.set_ok(u'El pedido de retiro realizado con éxito. (#%d)' % (order[0].key().id()) )

    return self.redirect(self.url_for('withdraw-currency', currency='ARS'))

  def get_bank_account_list(self):
    return BankAccount.all().filter('active =', True).filter('account =', db.Key(self.user)).order('created_at')
  
  @cached_property
  def withdraw_currency_form(self):
    currency_form = WithdrawCurrencyForm(self.request.POST)
    
    ba_list = self.get_bank_account_list()
    if ba_list is not None:
      cbus=[]
      for bank_account in ba_list:
        cbus.append((bank_account.cbu, bank_account.description + ' (' + bank_account.cbu+')'))
      currency_form.currency_cbu.choices = cbus
    return currency_form

  @need_auth()
  def cancel_account_operation(self, **kwargs):  
    oper = db.get(db.Key(kwargs['key']))
    referer = kwargs['referer']
    if str(oper.account.key()) != self.user:
      self.response.write(u'No tiene permitido realizar esta acción')
      self.response.set_status(500)
      return
    
    if oper.operation_type != Operation.MONEY_OUT:
      self.response.write(u'No tiene permitido realizar esta acción')
      self.response.set_status(500)
      return
      
    if oper.state != Operation.STATE_PENDING:
      self.response.write(u'No tiene permitido realizar esta acción')
      self.response.set_status(500)
      return
    
    trader    = Trader()
    ret = trader.cancel_widthdraw_order(str(oper.key()))
    
    #db.delete(btcaddress_or_bankacc)
    if ret[0] is not None:
      self.set_ok(u'El pedido de retiro fue cancelado.')
    else:
      self.set_error(ret[1])
    return self.redirect_to(referer)
    
    
  @need_auth()
  def account_operations(self, **kwargs):  
    
    type      = kwargs['type']
    state     = kwargs['state']
    currency  = kwargs['currency']
    
    opers = {'aaData':[]}
    #Hack: por lo pronto no handleamos operaciones de compra ni venta de BTC, ni deposito
    if type != AccountOperation.MONEY_OUT:
      return self.render_json_response(opers)
    
    query  = AccountOperation.all().filter('account =', db.Key(self.user))
    
    query = query.filter('currency =', currency.strip())
    
    # state                 = db.StringProperty(choices=[STATE_PENDING,STATE_ACCEPTED,STATE_CANCELED,STATE_DONE], required=True)
    if state != 'any':
      if state == AccountOperation.STATE_PENDING:
        query = query.filter('state =', AccountOperation.STATE_PENDING)
      if state == AccountOperation.STATE_ACCEPTED:
        query = query.filter('state =', AccountOperation.STATE_ACCEPTED)
      if state == AccountOperation.STATE_CANCELED:
        query = query.filter('state =', AccountOperation.STATE_CANCELED)
      if state == AccountOperation.STATE_DONE:
        query = query.filter('state =', AccountOperation.STATE_DONE)
        
    #operation_type        = db.StringProperty(choices=[BTC_BUY,BTC_SELL,MONEY_IN,MONEY_OUT,XCHG_FEE], required=True)
    if type != 'any':
      # if type == AccountOperation.BTC_BUY:
        # query = query.filter('operation_type !=', AccountOperation.BTC_BUY)
      # if type == AccountOperation.BTC_SELL:
        # query = query.filter('operation_type !=', AccountOperation.BTC_SELL)
      # if type == AccountOperation.MONEY_IN:
        # query = query.filter('operation_type !=', AccountOperation.MONEY_IN)
      if type == AccountOperation.MONEY_OUT:
        query = query.filter('operation_type =', AccountOperation.MONEY_OUT)
    # else:
      # query = query.filter('operation_type !=', AccountOperation.XCHG_FEE)
    
    query = query.order('created_at')
    
    for oper in query.run(limit=50):
      row = []
      row.append(str(oper.key().id()))
      row.append(oper.created_at.strftime("%Y-%m-%d %H:%M"))
      row.append('%s' % ( 'Retiro' if oper.operation_type == AccountOperation.MONEY_OUT else 'Deposito'))
      row.append('%s%.5f' % ( oper.currency, oper.amount))
      row.append('%s' % ( oper.bank_account if oper.bank_account else oper.address))
      
      if oper.state == AccountOperation.STATE_PENDING:
        referer = 'withdraw-new_currency' if oper.currency == 'ARS' else 'withdraw-new_btc'
        row.append('<a href="' + self.url_for('withdraw-cancel_account_operation', key=str(oper.key()), referer=referer ) + '">Cancelar&nbsp;retiro</a>')
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

