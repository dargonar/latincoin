# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app, get_request
from webapp2_extras import jinja2

from config import config

from datastore_template import MyJinjaLoader, get_template
from models import MailTemplate, JinjaTemplate, UserBitcoinAddress, BankAccount, TradeOrder, AccountOperation, AccountValidationFile

from jinja2 import Environment, FunctionLoader, PackageLoader
from jinja2.environment import Template

def enqueue_mail(mail, kwargs, tx=False):
  taskqueue.add(url=url_for('task-send-mail'), params=dict({'mail':mail}, **kwargs), transactional=tx)

def send_mail(mail, params):
  mailo = Mailo()
  mailo.send_user_email(mail, mailo.mail_contex_for(mail, params) )

class Mailo(object):
  def mail_contex_for(self, fnc, kwargs):
    
    base_context = {}
    user = db.get(db.Key(kwargs['user_key']))

    if fnc == 'identity_validated':
      base_context['user'] = user
    
    if fnc =='validation_file_validated':
      base_context['file'] = AccountValidationFile.get(db.Key(kwargs['file_key']))
      
    if fnc == 'welcome':
      base_context['confirm_link'] = url_for('account-confirm', token=user.confirmation_token, _full=True)
    
    if fnc == 'forgot_password':
      base_context['reset_link'] = url_for('account-reset', token=user.reset_password_token, _full=True)
    
    if fnc in ('btc_address_deleted', 'btc_address_added'):
      base_context['user_btc_address'] = UserBitcoinAddress.get(db.Key(kwargs['btc_address_key']))
    
    if fnc in ('bank_account_not_validated', 'bank_account_validated', 'bank_account_added', 'bank_account_deleted'):
      base_context['bank_account'] = BankAccount.get(db.Key(kwargs['bank_account_key']))
      
    if fnc in ('new_order', 'cancel_order', 'completed_order'):
      base_context['order'] = TradeOrder.get(db.Key(kwargs['order_key']))
    
    if fnc in ('deposit_received', 'withdraw_request', 'accept_withdraw_request', 'cancel_withdraw_request', 'done_withdraw_request'):
      base_context['account_operation'] = AccountOperation.get(db.Key(kwargs['ao_key']))

    # Add global 
    base_context['site_name']   = config['my']['site_name']
    base_context['domain_name'] = config['my']['domain_name']
    base_context['server_url']  = 'http://%s' % get_request().host
    base_context['support_url'] = 'http://%s' % get_request().host
    base_context['user_name']   = user.name if user.name and len(user.name) else user.email
    base_context['user_email']  = user.email

    base_context = dict(base_context, **kwargs)
    return base_context

  def send_user_email(self, email_type, context):
    
    #logging.info('os.path[%s]   sys.path[%s]', os.path.abspath("."), sys.path)
    
    template = email_type
    sender   = 'admin@latincoin.com'
      
    template_key = get_template_key(template)  
    mail_template = MailTemplate.get_by_key_name(template_key)
    
    if mail_template is None:
      raise Exception(u'Imposible obtener mail template [%s].' % template_key)

    j2              = jinja2.get_jinja2(app=get_app())
    j2_environment  = Environment(  autoescape=True
                                  , loader=FunctionLoader(get_template)) # my_jinja2_loader.
    
    subject = j2_environment.from_string(mail_template.subject).render(**context)

    # Armo el body en plain text.
    body_txt = j2_environment.from_string(mail_template.body_txt).render(**context)
    
    # Envío el correo.
    mail.send_mail(sender=sender, #"%s <%s@%s>" % (context['domain_name'], sender, context['site_name']), 
                   to=context['user_email'],
                   subject=subject,
                   body=body_txt)

def get_template_key(template, language='es'):
    return '%s_%s' % (template, language)