# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account', [
        Route('/signup',          name='signup',          handler='.Account:signup'),
        Route('/login',           name='login',           handler='.Account:login'),
        Route('/logout',          name='logout',          handler='.Account:logout'),
        Route('/confirm/<token>', name='confirm',         handler='.Account:confirm'),
        Route('/forget',          name='forget',          handler='.Account:forget'),
        Route('/reset/<token>',   name='reset',           handler='.Account:reset'),
      ]) ]) ]),
      
      PathPrefixRoute('/trade', [ NamePrefixRoute('trade-', [ HandlerPrefixRoute('apps.frontend.trade', [
        Route('/buysell',         name='buysell',          handler='.Trade:buysell'),
      ]) ]) ]),
      
      PathPrefixRoute('/designer', [ NamePrefixRoute('designer-', [ HandlerPrefixRoute('apps.frontend.designer', [
        Route('/<html>',         name='html',         handler='.Designer:verHtmlTemplate'),
      ]) ]) ]),
    ]
    
    return rules
