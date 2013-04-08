# -*- coding: utf-8 -*-
from decimal import Decimal

from google.appengine.ext import db

from webapp2 import cached_property

from models import TradeOrder, BankAccount, UserBitcoinAddress
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
