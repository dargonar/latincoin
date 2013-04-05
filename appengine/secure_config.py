# -*- coding: utf-8 -*-

def add_secure_config(config):

  # Clave para cookies (asi no hijackean sessiones)
  config['webapp2_extras.sessions']['secret_key']  = '@ 4 OSCAR VICTOR PAPA VICTOR ECHO # [ @ ~ kilo alpha / delta'
  
  # Clave para guardar los password de usuarios
  config['my']['secret_key']     = 'x-ray X-RAY ] % # ~ * QUEBEC kilo . bravo $ [ whiskey # ! whiskey " @ / 1 $ = + 8'
  
  # Clave para encriptar las privadas de bitcoin
  config['my']['secret_key_2']   = '% 4 [space] 1 $ > _ . } ] 8 ] ROMEO | ECHO ^ 6 tango 5 ZULU $ 0 % _ 1 1 8 3 { 4'
  
  # Clave para captcha
  config['my']['recaptcha_priv'] = '6LfYP98SAAAAALlOdUQF1BmgAHAWreZzzn822mMj'

  # Datos para acceder al bitcoind remoto
  config['my']['bd_host'] = 'ec2-54-245-175-53.us-west-2.compute.amazonaws.com'
  config['my']['bd_port'] = '52234'
  config['my']['bd_user'] = 'bitcoinrpc'
  config['my']['bd_pass'] = 'GveWduSEmAAsSBHWRYKkUsCcbm6HR4xbVRFKNmGmYChL'


  return config