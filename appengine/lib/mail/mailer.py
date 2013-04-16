# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app, get_request
from webapp2_extras import jinja2

from config import config

from datastore_template import MyJinjaLoader, get_template
from models import MailTemplate, JinjaTemplate

from jinja2 import Environment, FunctionLoader, PackageLoader

import os
import sys

#sys.path.append(os.path.join(os.path.dirname(__file__), ''))
sys.path.append(os.path.join(os.path.abspath("."), "lib"))

def enqueue_mail(mail, kwargs):
  taskqueue.add(url=url_for('task-send-mail', mail=mail), params=dict({'mail':mail}, **kwargs))

def enqueue_mail_tx(mail, kwargs):
  taskqueue.add(url=url_for('task-send-mail', mail=mail), params=dict({'mail':mail}, **kwargs), transactional=True)
  
def send_mail(mail, params):
  mailo = Mailo()
  ctx = mailo.mail_contex_for(mail, params)
  return getattr(mailo, mail)(ctx)
    
class Mailo(object):
  def mail_contex_for(self, fnc, kwargs):
    
    base_context = {}
    user = db.get(db.Key(kwargs['user_key']))
    
    if fnc in ('btc_address_deleted', 'btc_address_added'):
      base_context['user_btc_address'] = db.get(db.Key(kwargs['user_btc_address_key']))
    
    if fnc in ('bank_account_not_validated', 'bank_account_validated', 'bank_account_added', 'bank_account_deleted'):
      base_context['bank_account'] = db.get(db.Key(kwargs['bank_account_key']))
      
    if fnc in ('send_newbid_email', 'send_newask_email', 'send_donewithdrawrequestbtc_email', 'send_donewithdrawrequestars_email'):
      base_context['order'] = db.get(db.Key(kwargs['order_key']))
    
    if fnc in ('send_acceptwithdrawrequestbtc_email','send_acceptwithdrawrequestars_email'):
      base_context['account_operation'] = db.get(db.Key(kwargs['account_operation_key']))
    
    if fnc == 'send_forgotpassword_email':
      base_context['reset_link'] = url_for('account-reset', token=user.reset_password_token, _full=True)
      
    if fnc == 'send_welcome_email':
      base_context['confirm_link'] = url_for('account-confirm', token=user.confirmation_token, _full=True)

    # Add global 
    base_context['site_name']   = config['my']['site_name']
    base_context['domain_name'] = config['my']['domain_name']
    base_context['server_url']  = 'http://%s' % get_request().host
    base_context['support_url'] = 'http://%s' % get_request().host
    base_context['user_email']  = user.email
    
    base_context = dict(base_context, **kwargs)
    return base_context

  def send_btcaddressdeleted_email(self, context):      # **
    self.send_user_email('btc_address_deleted', context)

  def send_btcaddressadded_email(self, context):      # **
    self.send_user_email('btc_address_added', context)
    
  def send_bankaccountdeleted_email(self, context):      # **
    self.send_user_email('bank_account_deleted', context)

  def send_bankaccountnotvalidated_email(self, context):      # **
    self.send_user_email('bank_account_not_validated', context)

  def send_bankaccountvalidated_email(self, context):      # **
    self.send_user_email('bank_account_validated', context)

  def send_bankaccountadded_email(self, context):      # **
    self.send_user_email('bank_account_added', context)
    
  def send_identitynotvalidated_email(self, context):      # **
    self.send_user_email('identity_not_validated', context)

  def send_identityvalidated_email(self, context):      # **
    self.send_user_email('identity_validated', context)
    
  def send_validationfileuploaded_email(self, context):
    self.send_user_email('validation_file_uploaded', context)

  def send_personalinfochanged_email(self, context):      
    self.send_user_email('personal_info_changed', context)
    
  def send_donewithdrawrequestars_email(self, context):      
    self.send_user_email('done_withdraw_request_ars', context)

  def send_donewithdrawrequestbtc_email(self, context):      
    self.send_user_email('done_withdraw_request_btc', context)
    
  def send_acceptwithdrawrequestars_email(self, context):      
    self.send_user_email('accept_withdraw_request_ars', context)

  def send_acceptwithdrawrequestbtc_email(self, context):      
    self.send_user_email('accept_withdraw_request_btc', context)
    
  def send_cancelwithdrawrequestars_email(self, context):      
    self.send_user_email('cancel_withdraw_request_ars', context)

  def send_cancelwithdrawrequestbtc_email(self, context):      
    self.send_user_email('cancel_withdraw_request_btc', context)
    
  def send_withdrawrequestars_email(self, context):      
    self.send_user_email('withdraw_request_ars', context)

  def send_withdrawrequestbtc_email(self, context):      
    self.send_user_email('withdraw_request_btc', context)

  def send_depositreceivedbtc_email(self, context):      
    self.send_user_email('deposit_received_btc', context)
    
  def send_depositreceivedars_email(self, context):      
    self.send_user_email('deposit_received_ars', context)
    
  def send_cancelask_email(self, context):      
    self.send_user_email('cancel_ask', context)

  def send_cancelbid_email(self, context):
    self.send_user_email('cancel_bid', context)

  def send_partiallycompletedask_email(self, context):      
    self.send_user_email('partially_completed_ask', context)

  def send_partiallycompletedbid_email(self, context):
    self.send_user_email('partially_completed_bid', context)

  def send_completedask_email(self, context):      
    self.send_user_email('completed_ask', context)

  def send_completedbid_email(self, context):
    self.send_user_email('completed_bid', context)

  def send_newask_email(self, context):
    self.send_user_email('new_ask', context)

  def send_newbid_email(self, context):
    self.send_user_email('new_bid', context)
    
  def send_forgotpassword_email(self, context):
    self.send_user_email('forgot_password', context)

  def send_passwordchanged_email(self, context):
    self.send_user_email('password_changed', context)

  def send_welcome_email(self, context):
    self.send_user_email('welcome', context)

  def get_mailtemplate_key(self, template, language='es'):
    return 'mail_%s_%s' % (template, language)

  def get_jinjatemplate_key(self, template, language='es'):
    return '%s_%s' % (template, language)
    
  def send_user_email(self, email_type, context):
    
    logging.info('os.path[%s]   sys.path[%s]', os.path.abspath("."), sys.path)
    
    template = email_type
    sender   = 'admin@latincoin.com'
      
    template_key = self.get_mailtemplate_key(template)  
    mMailTemplate = MailTemplate.get_by_key_name(template_key)
    
    if mMailTemplate is None:
      raise Exception(u'Imposible obtener mail template [%s][%s].' % (template, template_key)) 
    
    subject  = mMailTemplate.subject 
    
    j2              = jinja2.get_jinja2(app=get_app())
    j2_environment  = Environment(  autoescape=True
                                  , loader=FunctionLoader(get_template)) # my_jinja2_loader.
    
    # Armo el body en plain text.
    body_tpl = j2_environment.get_template(self.get_jinjatemplate_key(template))
                                #, **context)  
    body = body_tpl.render(**context)
    
    # Envío el correo.
    mail.send_mail(sender=sender, #"%s <%s@%s>" % (context['domain_name'], sender, context['site_name']), 
                   to=context['user_email'],
                   subject="%s - %s" % (context['site_name'], subject),
                   body=body)