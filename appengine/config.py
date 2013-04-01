# -*- coding: utf-8 -*-
config = {}

config['webapp2'] = {
    'apps_installed': [
        'apps.backend',
        'apps.frontend',
    ],
}

config['webapp2_extras.sessions'] = {
  'secret_key'  : '@ 4 OSCAR VICTOR PAPA VICTOR ECHO # [ @ ~ kilo alpha / delta',
  'cookie_name' : 'btc-xchange',
}

config['webapp2_extras.jinja2'] = {
  'template_path' :  'templates',
  'compiled_path' :  None,
  'force_compiled':  False,

  'environment_args': {
    'autoescape': False,
  }
}

config['my'] = {
  'site_name'   : 'BTC-XChange',
  'domain_name' : 'www.btc-xchange.com.ar',
  'secret_key'  : 'x-ray X-RAY ] % # ~ * QUEBEC kilo . bravo $ [ whiskey # ! whiskey " @ / 1 $ = + 8',
  'secret_key_2': '% 4 [space] 1 $ > _ . } ] 8 ] ROMEO | ECHO ^ 6 tango 5 ZULU $ 0 % _ 1 1 8 3 { 4',
  'mail': {
    'welcome':        {'sender':'noreply', 'subject': 'Bienvenido', 'template':'email/welcome'},
    'reset_password': {'sender':'noreply', 'subject': 'Recuperación de contraseña', 'template':'email/reset_password'},
  },

}