# -*- coding: utf-8 -*-
import logging

from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app, get_request
from webapp2_extras import jinja2

from config import config
from utils import Jinja2Mixin
from models import MailTemplate, JinjaTemplate
from my_jinja2_loader import MyJinjaLoader, get_template

from jinja2 import Environment, FunctionLoader, PackageLoader

import os
import sys

#sys.path.append(os.path.join(os.path.dirname(__file__), ''))
sys.path.append(os.path.join(os.path.abspath("."), "lib"))

def mail_contex_for(fnc, user, **kwargs):
  
  base_context = {}
  # if fnc == 'deposit_received_ars':
    # base_context['deposit_amount']  = kwargs['deposit_amount'] 
  # if fnc == 'deposit_received_btc': 
    # base_context['deposit_amount']  = kwargs['deposit_amount'] 
  # if fnc == 'withdraw_request_ars': 
    # base_context['withdraw_amount']  = kwargs['withdraw_amount'] 
    # base_context['withdraw_cbu']  = kwargs['withdraw_cbu'] 
  # if fnc == 'withdraw_request_btc': 
    # base_context['withdraw_amount']  = kwargs['withdraw_amount'] 
    # base_context['withdraw_address']  = kwargs['withdraw_address']   
  # if fnc == 'send_completedask_email' or fnc == 'send_completedbid_email' or fnc == 'send_newask_email' or fnc == 'send_newbid_email' or fnc == 'send_partiallycompletedask_email' or fnc == 'send_partiallycompletedbid_email' or fnc == 'send_cancelask_email' or fnc == 'send_cancelbid_email':
    # base_context['order']        = kwargs['order']
    # if fnc != 'send_newask_email' and fnc != 'send_newbid_email':
      # base_context['opers']        = kwargs['opers']

  if fnc == 'send_forgotpassword_email':
    base_context['reset_link']        = url_for('account-reset', token=user.reset_password_token, _full=True)
    base_context['cancel_reset_link'] = url_for('account-cancel_reset', token=user.reset_password_token, _full=True)
    
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

def send_withdrawrequestars_email(context):      
  send_user_email('withdraw_request_ars', context)

def send_withdrawrequestbtc_email(context):      
  send_user_email('withdraw_request_btc', context)

def send_depositreceivedbtc_email(context):      
  send_user_email('deposit_received_btc', context)
  
def send_depositreceivedars_email(context):      
  send_user_email('deposit_received_ars', context)
  
def send_cancelask_email(context):      
  send_user_email('cancel_ask', context)

def send_cancelbid_email(context):
  send_user_email('cancel_bid', context)

def send_partiallycompletedask_email(context):      
  send_user_email('partially_completed_ask', context)

def send_partiallycompletedbid_email(context):
  send_user_email('partially_completed_bid', context)

def send_completedask_email(context):      
  send_user_email('completed_ask', context)

def send_completedbid_email(context):
  send_user_email('completed_bid', context)

def send_newask_email(context):
  send_user_email('new_ask', context)

def send_newbid_email(context):
  send_user_email('new_bid', context)
  
def send_forgotpassword_email(context):
  send_user_email('forgot_password', context)

def send_passwordchanged_email(context):
  send_user_email('password_changed', context)

def send_welcome_email(context):
  send_user_email('welcome', context)

def get_mailtemplate_key(template, language='es'):
  return 'mail_%s_%s' % (template, language)

def get_jinjatemplate_key(template, language='es'):
  return '%s_%s' % (template, language)
  
def send_user_email(email_type, context):
  
  logging.info('os.path[%s]   sys.path[%s]', os.path.abspath("."), sys.path)
  
  template = email_type
  sender   = 'ptutino@gmail.com'
    
  template_key = get_mailtemplate_key(template)  
  mMailTemplate = MailTemplate.get_by_key_name(template_key)
  
  if mMailTemplate is None:
    raise Exception(u'Imposible obtener mail template [%s][%s].' % (template, template_key)) 
  
  subject  = mMailTemplate.subject 
  
  j2              = jinja2.get_jinja2(app=get_app())
  j2_environment  = Environment(  autoescape=True
                                , loader=FunctionLoader(get_template)) # my_jinja2_loader.
  
  # Armo el body en plain text.
  body_tpl = j2_environment.get_template(get_jinjatemplate_key(template))
                              #, **context)  
  body = body_tpl.render(**context)
  
  # Envío el correo.
  mail.send_mail(sender=sender, #"%s <%s@%s>" % (context['domain_name'], sender, context['site_name']), 
                 to=context['user_email'],
                 subject="%s - %s" % (context['site_name'], subject),
                 body=body)
