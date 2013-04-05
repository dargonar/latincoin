# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [

      PathPrefixRoute('/tasks', [ NamePrefixRoute('task-', [ HandlerPrefixRoute('apps.backend.tasks_controller', [
        Route('/import_block',   name='import-block',     handler='.TasksController:import_block'),
        
      ]) ]) ]),
      
      PathPrefixRoute('/map', [ NamePrefixRoute('task-', [ HandlerPrefixRoute('apps.backend.ticker_mapper_runner', [
        Route('/ticker_mapper',  name='ticker-mapper',    handler='.RunTickerMapper:build_ticker'),
        
      ]) ]) ]),

    ]

    return rules
