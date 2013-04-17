# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from google.appengine.ext import db

from utils import FrontendHandler, need_auth, get_or_404

from gaeqrcode.PyQRNative import QRErrorCorrectLevel
from gaeqrcode.PyQRNativeGAE import QRCode

from jinja2 import Environment, FunctionLoader, PackageLoader
from jinja2.environment import Template

from mail.mailer import get_template_key
from datastore_template import MyJinjaLoader, get_template
from models import JinjaTemplate, BitcoinAddress, Account, AccountOperation

class DepositController(FrontendHandler):

  @need_auth()
  def list(self, **kwargs):

    currency = 'BTC' if kwargs['currency'] == 'btc' else 'ARS'

    query = AccountOperation.all().filter('account =', db.Key(self.user))
    query = query.filter('operation_type =', AccountOperation.MONEY_IN)
    query = query.filter('currency =', currency)
    query = query.order('created_at')
    
    deposits = {'aaData':[]}

    for aop in query:
      row = []
      row.append('%d' % aop.key().id() )
      row.append(aop.created_at.strftime("%Y-%m-%d %H:%M:%S"))
      row.append('%.8f' % aop.amount )
      deposits['aaData'].append(row)

    return self.render_json_response(deposits)


  def get_current_btc_address(self):
    addy = Account.get(self.user).bitcoin_addresses.order('created_at').get()
    return addy.address

  @need_auth()
  def btc(self, **kwargs):
    kwargs['tab'] = 'btc';
    kwargs['html'] = 'deposito'

    kwargs['btc_address'] = self.get_current_btc_address()
    return self.render_response('frontend/deposit.html', **kwargs)
  
  @need_auth()
  def qrcode(self, **kwargs):
    
    url = "bitcoin:%s" % (self.get_current_btc_address())
    img = memcache.get(url)
    if not img:
      qr = QRCode(QRCode.get_type_for_string(url), QRErrorCorrectLevel.L)
      qr.addData(url)
      qr.make()
      img = qr.make_image()
      memcache.set(url, img)

    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(img)

  @need_auth()
  def currency(self, **kwargs):
    kwargs['tab'] = 'currency';
    kwargs['html'] = 'deposito'
    
    template_key    = get_template_key('account_information')
    jinja_template  = JinjaTemplate.get_by_key_name(template_key)
    kwargs['account_information'] = self.jinja2.environment.from_string(jinja_template.source).render()
    kwargs['account'] = get_or_404(self.user)
    return self.render_response('frontend/deposit.html', **kwargs)
