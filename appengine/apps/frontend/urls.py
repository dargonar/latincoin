# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account', [
        Route('/signup',  name='signup',  handler='.Account:signup'),
        Route('/login',   name='login',   handler='.Account:login'),
        Route('/confirm', name='confirm', handler='.Account:confirm'),
      ]) ]) ]),
      
      PathPrefixRoute('/designer', [ NamePrefixRoute('designer-', [ HandlerPrefixRoute('apps.frontend.designer', [
        Route('/<html>',         name='html',         handler='.Designer:verHtmlTemplate'),
      ]) ]) ]),
    ]
    
    return rules
