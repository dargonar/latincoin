# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [

      PathPrefixRoute('/tasks', [ NamePrefixRoute('task-', [ HandlerPrefixRoute('apps.backend.tasks_controller', [
        Route('/import_block',              name='import-block',             handler='.TasksController:import_block'),
        Route('/process_block',             name='process-block',            handler='.TasksController:process_block'),
        Route('/forward_txs',               name='forward-txs',              handler='.TasksController:forward_txs'),
        Route('/update_btc_balance',        name='update-btc-balance',       handler='.TasksController:update_btc_balance'),
        Route('/match_orders',              name='match-orders',             handler='.TasksController:match_orders'),
        Route('/apply_operations',          name='apply-operations',         handler='.TasksController:apply_operations'),
        Route('/build_next_bar',            name='build-next-bar',           handler='.TasksController:build_next_bar'),
        Route('/send_mail',                 name='send-mail',                handler='.TasksController:send_mail'),
        Route('/build_1h_bar',              name='build-1h-bar',             handler='.TasksController:build_1h_bar'),
        Route('/notify_operations',         name='notify-operations',        handler='.TasksController:notify_operations'),
        Route('/remove_unconfirmed_users',  name='remove-unconfirmed-users', handler='.TasksController:remove_unconfirmed_users'),
      ]) ]) ]),
      
      Route('/a/backend',                   name='backend',         handler='apps.backend.backend_controller.BackendController:home'),
      
      #Route('/a/backend/generate_demo_data',  name='demo-data',     handler='apps.backend.demo_controller.GenerateTradeData:generate'),
      
      PathPrefixRoute('/a/backend', [ NamePrefixRoute('backend-', [ HandlerPrefixRoute('apps.backend.backend_controller', [
        Route('/login',                     name='login',             handler='.BackendController:login'),
        Route('/logout',                    name='logout',            handler='.BackendController:logout'),
        Route('/dashboard',                 name='dashboard',         handler='.BackendController:dashboard'),
      ]) ]) ]),
      
      PathPrefixRoute('/a/backend/user', [ NamePrefixRoute('backend-user-', [ HandlerPrefixRoute('apps.backend.user_controller', [
        Route('/list',                                                name='list',            handler='.UserController:list'),
        Route('/edit/<user>',                                         name='edit',            handler='.UserController:edit'),
        Route('/validate/<user>/<valid:(1|0)>',                       name='validate',        handler='.UserController:validate'),
        Route('/file/list/<user>',                                    name='list_files',      handler='.UserController:list_files'),
        Route('/file/validate/<file>/<valid:(1|0)>',                  name='validate_file',   handler='.UserController:validate_file'),
        Route('/file/validate/<file>/<valid:(1|0)>/<invalid_reason>', name='validate_file2',  handler='.UserController:validate_file'),
        
      ]) ]) ]),
      
      PathPrefixRoute('/a/backend/deposit', [ NamePrefixRoute('backend-deposit-', [ HandlerPrefixRoute('apps.backend.deposit_controller', [
        Route('/currency/<user>',             name='currency',    handler='.DepositController:currency'),
        Route('/list/currency',               name='list',        handler='.DepositController:list'),
      ]) ]) ]),
      
      PathPrefixRoute('/a/backend/withdraw', [ NamePrefixRoute('backend-withdraw-', [ HandlerPrefixRoute('apps.backend.withdraw_controller', [
        Route('/list',                          name='list',          handler='.WithdrawController:list'),
        Route('/list/<user>',                   name='list_for_user', handler='.WithdrawController:list_for_user'),
        Route('/edit/<key>/<state>',            name='edit',          handler='.WithdrawController:edit'),
        Route('/edit/<key>/<state>/<user_key>', name='edit_for_user', handler='.WithdrawController:edit'),
      ]) ]) ]),
      
    ]

    return rules
