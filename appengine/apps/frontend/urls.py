# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      # hacks
      Route('/init', name='a8', handler='apps.frontend.account_controller.AccountController:init_all'),


      Route('/', name='home', handler='apps.frontend.main_controller.MainController:home'),

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
        Route('/active/<type:(bid|ask)>',  name='active-orders',  handler='.TradeController:active_orders'),
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
      ]) ]) ]),
      
      PathPrefixRoute('/designer', [ NamePrefixRoute('designer-', [ HandlerPrefixRoute('apps.frontend.designer_controller', [
        Route('/<html>',         name='html',         handler='.DesignerController:verHtmlTemplate'),
      ]) ]) ]),
    ]
    
    return rules
