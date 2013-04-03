# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db

from webapp2 import RequestHandler
from bitcoinrpc.authproxy import AuthServiceProxy
from config import config
from models import ImportInfo

class TasksController(RequestHandler):
  def import_block(self, **kwargs):
    user   = config['my']['bd_user']
    passwd = config['my']['bd_pass']
    host   = config['my']['bd_host']
    port   = config['my']['bd_port']

    url    = "https://%s:%s@%s:%s" % (user,passwd,host,port)

    info = ImportInfo.get_or_insert('import_info')

    access = AuthServiceProxy(url)
    
    block_hash = access.getblockhash(info.last_block+1)
    block_info = access.getblock(block_hash)

    keys = []

    for tx in block_info['tx']:
      for out in tx['outs']:
        db.Key.from_path('BitcoinAddress', out['scriptPubKey']['addresses'][0])

    info.last_block = info.last_block+1
    info.put()


