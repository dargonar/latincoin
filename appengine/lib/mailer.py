# -*- coding: utf-8 -*-
from google.appengine.api import mail

from webapp2 import uri_for as url_for, get_app
from webapp2_extras import jinja2

from config import config
from utils import Jinja2Mixin

def send_welcome_email(user, host):

  # Mando Correo de bienvenida y validación de eMail.
  # Armo el contexto dado que lo utilizo para mail plano y mail HTML.
  fullurl = 'http://%s' % host

  context = { 'site_name'    : config['my']['site_name'],
              'domain_name'  : config['my']['domain_name'],
              'server_url'   : fullurl        
             ,'confirm_link' : url_for('account-confirm', token=user.confirmation_token, _full=True) 
             ,'support_url'  : fullurl }

  template = config['my']['mail']['welcome']['template']
  sender   = config['my']['mail']['welcome']['sender']
  subject  = config['my']['mail']['welcome']['subject']

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
