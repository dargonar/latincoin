# -*- coding: utf-8 -*-
from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app
from webapp2_extras import jinja2

from config import config
from utils import Jinja2Mixin

def send_resetpassword_email(user, host):
  
  context = {
    'reset_link' : url_for('account-reset', token=user.reset_password_token, _full=True),
  }
  
  send_user_email(user, 'reset_password', context, host)



def send_welcome_email(user, host):
  
  context = {
    'confirm_link' : url_for('account-confirm', token=user.confirmation_token, _full=True),
  }
  
  send_user_email(user, 'welcome', context, host)



def send_user_email(user, email_type, params, host):

  fullurl = 'http://%s' % host

  tmp =     { 'site_name'    : config['my']['site_name'],
              'domain_name'  : config['my']['domain_name'],
              'server_url'   : fullurl,        
              'support_url'  : fullurl }

  context = dict(params.items() + tmp.items())

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
                 to=user.email,
                 subject="%s - %s" % (context['site_name'], subject),
                 body=body,
                 html=html)
