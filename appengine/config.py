# -*- coding: utf-8 -*-
config = {}

config['webapp2'] = {
    'apps_installed': [
        'apps.backend',
        'apps.frontend',
    ],
}

config['webapp2_extras.sessions'] = {
  'cookie_name'         : 'latincoin',
  'cookie_name_backend' : 'latincoin_backend',
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
  'site_name'      : 'LatinCoin',
  'domain_name'    : 'www.latincin.com',
  'secret_key'     : 'x-ray X-RAY ] % # ~ * QUEBEC kilo . bravo $ [ whiskey # ! whiskey " @ / 1 $ = + 8',
  'secret_key_2'   : '% 4 [space] 1 $ > _ . } ] 8 ] ROMEO | ECHO ^ 6 tango 5 ZULU $ 0 % _ 1 1 8 3 { 4',
  'cold_wallet'    : '19eE72sBA5WUNvcXWpH5pn3Cg8mfUj3wQS',
  'recaptcha_pub'  : '6LfYP98SAAAAALlOdUQF1BmgAHAWreZzzn822mMj',
  'mail': {
    'welcome':        {'sender':'noreply', 'subject': 'Bienvenido', 'template':'email/welcome'},
    'reset_password': {'sender':'noreply', 'subject': 'Recuperación de contraseña', 'template':'email/reset_password'},
  },
}


# --------------------------------------------------
# ADD SECURE SECTION
# --------------------------------------------------
from secure_config import add_secure_config
config = add_secure_config(config)
# --------------------------------------------------
