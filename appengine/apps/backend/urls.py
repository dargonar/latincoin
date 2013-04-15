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
        Route('/send_mail/<action>',        name='send-mail',           handler='.TasksController:send_mail'),
      ]) ]) ]),

    ]

    return rules
