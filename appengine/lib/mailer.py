# -*- coding: utf-8 -*-
from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app, get_request
from webapp2_extras import jinja2

from config import config
from utils import Jinja2Mixin

def mail_contex_for(fnc, user):
  
  base_context = {}

  if fnc == 'send_resetpassword_email':
    base_context['reset_link'] = url_for('account-reset', token=user.reset_password_token, _full=True)

  if fnc == 'send_welcome_email':
    base_context['confirm_link'] = url_for('account-confirm', token=user.confirmation_token, _full=True)

  # Add global 
  base_context['site_name']   = config['my']['site_name']
  base_context['domain_name'] = config['my']['domain_name']
  base_context['server_url']  = 'http://%s' % get_request().host
  base_context['support_url'] = 'http://%s' % get_request().host
  base_context['user_email']  = user.email

  return base_context

def send_resetpassword_email(context):
  send_user_email('reset_password', context)

def send_welcome_email(context):
  send_user_email('welcome', context)

def send_user_email(email_type, context):

  template = config['my']['mail'][email_type]['template']
  sender   = config['my']['mail'][email_type]['sender']
  subject  = config['my']['mail'][email_type]['subject']

  j2 = jinja2.get_jinja2(app=get_app())
  
  # Armo el body en plain text.
  body = j2.render_template(template+'.txt', **context)  

  # Armo el body en HTML.
  html = j2.render_template(template+'.html', **context)  

  # Envío el correo.
  mail.send_mail(sender="%s <%s@%s>" % (context['domain_name'], sender, context['site_name']), 
                 to=context['user_email'],
                 subject="%s - %s" % (context['site_name'], subject),
                 body=body,
                 html=html)
