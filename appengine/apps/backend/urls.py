# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [

      PathPrefixRoute('/tasks', [ NamePrefixRoute('task-', [ HandlerPrefixRoute('apps.backend.tasks_controller', [
        Route('/import_block',              name='import-block',        handler='.TasksController:import_block'),
        Route('/process_block',             name='process-block',       handler='.TasksController:process_block'),
        Route('/forward_txs',               name='forward-txs',         handler='.TasksController:forward_txs'),
        Route('/update_btc_balance',        name='update-btc-balance',  handler='.TasksController:update_btc_balance'),
        Route('/match_orders',              name='match-orders',        handler='.TasksController:match_orders'),
        Route('/apply_operations',          name='apply-operations',    handler='.TasksController:apply_operations'),
        Route('/build_next_bar',            name='build-next-bar',      handler='.TasksController:build_next_bar'),
        Route('/send_mail',                 name='send-mail',           handler='.TasksController:send_mail'),
        Route('/build_1h_bar',              name='build-1h-bar',        handler='.TasksController:build_1h_bar'),
        Route('/notify_operations',         name='notify-operations',   handler='.TasksController:notify_operations'),
      ]) ]) ]),
      
      Route('/a/backend',                   name='backend',         handler='apps.backend.backend_controller.BackendController:home'),
      
      PathPrefixRoute('/a/backend', [ NamePrefixRoute('backend-', [ HandlerPrefixRoute('apps.backend.backend_controller', [
        Route('/login',                     name='login',             handler='.BackendController:login'),
        Route('/logout',                    name='logout',            handler='.BackendController:logout'),
        Route('/dashboard',                 name='dashboard',         handler='.BackendController:dashboard'),
        
        Route('/users',                                     name='users',               handler='.BackendController:users'),
        Route('/validate_user/<user>/<valid:(1|0)>',        name='validate_user',       handler='.BackendController:validate_user'),
        Route('/list_user_files/<user>',                    name='list_user_files',     handler='.BackendController:list_user_files'),
        Route('/validate_user_file/<file>/<valid:(1|0)>',   name='validate_user_file',  handler='.BackendController:validate_user_file'),
        Route('/validate_user_file/<file>/<valid:(1|0)>/<invalid_reason>',   name='validate_user_file2',  handler='.BackendController:validate_user_file'),
        
        Route('/withdrawals',               name='withdrawals',       handler='.BackendController:withdrawals'),
        
      ]) ]) ]),
      
      PathPrefixRoute('/a/backend', [ NamePrefixRoute('backend-deposit-', [ HandlerPrefixRoute('apps.backend.deposit_controller', [
        Route('/deposit/currency/<user>', name='currency',handler='.DepositController:currency'),
        Route('/deposit/currency/list',   name='list',handler='.DepositController:list'),
      ]) ]) ]),
      
    ]

    return rules
