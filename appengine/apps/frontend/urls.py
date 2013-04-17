# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      #Route(r'/<bety:.*>', name='soon',        handler='apps.frontend.main_controller.MainController:soon'), # mover donde corresponda      
      
      # hacks
      Route('/init', name='a8', handler='apps.frontend.account_controller.AccountController:init_all'),
      Route('/test1', name='a9', handler='apps.frontend.account_controller.AccountController:test_1'),

      Route('/', name='home',         handler='apps.frontend.main_controller.MainController:home'),
      Route('/soon', name='soon',        handler='apps.frontend.main_controller.MainController:soon'), # mover donde corresponda
      Route('/terms', name='terms',        handler='apps.frontend.main_controller.MainController:terms'), # mover donde corresponda
      Route('/contact', name='contact',      handler='apps.frontend.main_controller.MainController:contact'), # mover donde corresponda
      
      PathPrefixRoute('/deposit', [ NamePrefixRoute('deposit-', [ HandlerPrefixRoute('apps.frontend.deposit_controller', [
        Route('/btc',                            name='btc',          handler='.DepositController:btc'),
        Route('/btc/qrcode',                     name='qrcode-img',   handler='.DepositController:qrcode'),
        Route('/currency',                       name='currency',     handler='.DepositController:currency'),
        Route('/list/<currency:(btc|currency)>', name='list',         handler='.DepositController:list'),
      ]) ]) ]),

      PathPrefixRoute('/withdraw', [ NamePrefixRoute('withdraw-', [ HandlerPrefixRoute('apps.frontend.withdraw_controller', [
        Route('/btc',                            name='btc',         handler='.WithdrawController:btc'),
        Route('/currency',                       name='currency',    handler='.WithdrawController:currency'),
        Route('/cancel/<key>',                   name='cancel',      handler='.WithdrawController:cancel'),
        Route('/list/<currency:(btc|currency)>', name='list',        handler='.WithdrawController:list'),
      ]) ]) ]),

      PathPrefixRoute('/account', [ NamePrefixRoute('account-', [ HandlerPrefixRoute('apps.frontend.account_controller', [
        Route('/signup',          name='signup',          handler='.AccountController:signup'),
        Route('/login',           name='login',           handler='.AccountController:login'),
        Route('/logout',          name='logout',          handler='.AccountController:logout'),
        Route('/confirm/<token>', name='confirm',         handler='.AccountController:confirm'),
        Route('/forget',          name='forget',          handler='.AccountController:forget'),
        Route('/reset/<token>',   name='reset',           handler='.AccountController:reset'),
        Route('/validate/<token>',name='validate',        handler='.AccountController:validate'),
      ]) ]) ]),
      
      PathPrefixRoute('/trade', [ NamePrefixRoute('trade-', [ HandlerPrefixRoute('apps.frontend.trade_controller', [
        Route('/new',             name='new',          handler='.TradeController:new'),
        Route('/orders/<mode:(active|inactive)>/<type:(bid|ask|any)>',  name='orders',  handler='.TradeController:list_orders'),
        Route('/history',         name='history',      handler='.TradeController:history'),
        Route('/cancel/<key>',    name='cancel',       handler='.TradeController:cancel_order'),
      ]) ]) ]),

      
      PathPrefixRoute('/profile', [ NamePrefixRoute('profile-', [ HandlerPrefixRoute('apps.frontend.profile_controller', [
        Route('/personal_info',               name='personal_info',                   handler='.ProfileController:personal_info'),
        Route('/identity_validation',         name='identity_validation',             handler='.ProfileController:identity_validation'),
        Route('/delete_file/<key>',           name='delete_file',                     handler='.ProfileController:delete_file'),
        Route('/identity_validation_files',   name='identity_validation_files',       handler='.ProfileController:identity_validation_files'),
        Route('/change_password',             name='change_password',                 handler='.ProfileController:change_password'),
        Route('/btc_address',                 name='btc_address',                     handler='.ProfileController:btc_address'),
        Route('/btc_address_delete/<key>',    name='btc_address_delete',              handler='.ProfileController:btc_address_delete'),
        Route('/btc_address_list',            name='btc_address_list',                handler='.ProfileController:btc_address_list'),
        Route('/bank_account',                name='bank_account',                    handler='.ProfileController:bank_account'),
        Route('/bank_account_delete/<key>',   name='bank_account_delete',             handler='.ProfileController:bank_account_delete'),
        Route('/bank_account_list',           name='bank_account_list',               handler='.ProfileController:bank_account_list'),
        Route('/otp',                         name='otp',                             handler='.ProfileController:otp'),
        Route('/otp/image/<url>',             name='otp-image',                       handler='.ProfileController:otp_image'),
        Route('/otp/verify',                  name='otp-verify',                      handler='.ProfileController:otp_verify'),
      ]) ]) ]),
      
    ]
    
    return rules
