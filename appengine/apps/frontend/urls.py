# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      Route('/', name='home', handler='apps.frontend.main.Main:home'),

      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account_controller', [
        Route('/signup',          name='signup',          handler='.AccountController:signup'),
        Route('/login',           name='login',           handler='.AccountController:login'),
        Route('/logout',          name='logout',          handler='.AccountController:logout'),
        Route('/confirm/<token>', name='confirm',         handler='.AccountController:confirm'),
        Route('/forget',          name='forget',          handler='.AccountController:forget'),
        Route('/reset/<token>',   name='reset',           handler='.AccountController:reset'),

        Route('/init',          name='a8',          handler='.Account:init_all'),

      ]) ]) ]),
      
      PathPrefixRoute('/trade', [ NamePrefixRoute('trade-', [ HandlerPrefixRoute('apps.frontend.trade_controller', [
        Route('/new',         name='new',          handler='.TradeController:new'),
      ]) ]) ]),
      
      PathPrefixRoute('/designer', [ NamePrefixRoute('designer-', [ HandlerPrefixRoute('apps.frontend.designer', [
        Route('/<html>',         name='html',         handler='.Designer:verHtmlTemplate'),
      ]) ]) ]),
    ]
    
    return rules
