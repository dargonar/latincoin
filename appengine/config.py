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
  'compiled_path' :  'templates_compiled',
  'force_compiled':  False,

  'environment_args': {
    'autoescape': False,
  }
}

config['btc-xchange'] = {
}