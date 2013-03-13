# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account', [
        Route('/signin', name='signin', handler='.Account:signin'),
        Route('/login',  name='login',  handler='.Account:login'),
      ]) ]) ]),
    ]
    
    return rules
