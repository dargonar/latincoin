# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [

      # PathPrefixRoute('/tasks', [ NamePrefixRoute('task-', [ HandlerPrefixRoute('apps.backend.tasks_controller', [
      #   Route('/import_block',       name='import-block',        handler='.TasksController:import_block'),
      #   Route('/process_block',      name='process-block',       handler='.TasksController:process_block'),
      #   Route('/forward_txs',        name='forward-txs',         handler='.TasksController:forward_txs'),
      #   Route('/update_btc_balance', name='update-btc-balance',  handler='.TasksController:update_btc_balance'),
      #   Route('/match_orders',       name='match-orders',        handler='.TasksController:match_orders'),
      #   Route('/apply_operations',   name='apply-operations',    handler='.TasksController:apply_operations'),

      # ]) ]) ]),
      
      # PathPrefixRoute('/map', [ NamePrefixRoute('mapper-', [ HandlerPrefixRoute('apps.backend.mapper_controller', [
      #   Route('/ticker',              name='ticker',                    handler='.RunTickerMapper:build'),
      #   Route('/oper_notification',   name='operation-notification',    handler='.RunOperationNotificationMapper:run'),
      # ]) ]) ]),

    ]

    return rules
