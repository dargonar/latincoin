# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      # hacks
      Route('/init', name='a8', handler='apps.frontend.account_controller.AccountController:init_all'),
      Route('/test1', name='a9', handler='apps.frontend.account_controller.AccountController:test_1'),


      Route('/', name='home',         handler='apps.frontend.main_controller.MainController:home'),
      Route('/', name='terms',        handler='apps.frontend.main_controller.MainController:terms'), # mover donde corresponda
      Route('/', name='contact',      handler='apps.frontend.main_controller.MainController:contact'), # mover donde corresponda
      Route('/', name='deposito',     handler='apps.frontend.main_controller.MainController:deposito'), # mover donde corresponda
      Route('/', name='retiro',       handler='apps.frontend.main_controller.MainController:retiro'), # mover donde corresponda
      
      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account_controller', [
        Route('/signup',          name='signup',          handler='.AccountController:signup'),
        Route('/login',           name='login',           handler='.AccountController:login'),
        Route('/logout',          name='logout',          handler='.AccountController:logout'),
        Route('/confirm/<token>', name='confirm',         handler='.AccountController:confirm'),
        Route('/forget',          name='forget',          handler='.AccountController:forget'),
        Route('/reset/<token>',   name='reset',           handler='.AccountController:reset'),
      ]) ]) ]),
      
      PathPrefixRoute('/trade', [ NamePrefixRoute('trade-', [ HandlerPrefixRoute('apps.frontend.trade_controller', [
        Route('/new',             name='new',          handler='.TradeController:new'),
        Route('/orders/<mode:(active|inactive)>/<type:(bid|ask|any)>/<owner:(user|any)>',  name='orders',  handler='.TradeController:list_orders'),
        Route('/history',         name='history',      handler='.TradeController:history'),
        Route('/cancel/<key>',    name='cancel',       handler='.TradeController:cancel_order'),

        Route('/match',           name='match',        handler='.TradeController:match_orders'),
        Route('/apply/<key>',     name='apply',        handler='.TradeController:apply_operation'),

      ]) ]) ]),

      
      PathPrefixRoute('/profile', [ NamePrefixRoute('profile-', [ HandlerPrefixRoute('apps.frontend.profile_controller', [
        Route('/personal_info',               name='personal_info',                   handler='.ProfileController:personal_info'),
        Route('/identity_validation',         name='identity_validation',             handler='.ProfileController:identity_validation'),
        Route('/delete_file/<key>',           name='delete_file',                     handler='.ProfileController:delete_file'),
        Route('/identity_validation_files',   name='identity_validation_files',       handler='.ProfileController:identity_validation_files'),
        Route('/change_password',             name='change_password',                 handler='.ProfileController:change_password'),
        Route('/btc_address',                 name='btc_address',                     handler='.ProfileController:btc_address'),
        Route('/btc_address_delete/<key>/<referer>',    name='btc_address_delete',              handler='.ProfileController:btc_address_delete'),
        Route('/btc_address_list',            name='btc_address_list',                handler='.ProfileController:btc_address_list'),
        Route('/bank_account',                name='bank_account',                    handler='.ProfileController:bank_account'),
        Route('/bank_account_list',           name='bank_account_list',               handler='.ProfileController:bank_account_list'),
        Route('/otp',                         name='otp',                             handler='.ProfileController:otp'),
      ]) ]) ]),
      
    ]
    
    return rules
