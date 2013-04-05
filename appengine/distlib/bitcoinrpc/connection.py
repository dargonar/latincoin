# -*- coding: utf-8 -*-

import json
import httplib
import logging
import urllib

from decimal import Decimal

from config import config
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def get_proxy(remote_rpc):
  
  if remote_rpc == 'ec2':
    return EC2Proxy()

  if remote_rpc == 'blockchain':
    return BlockChainProxy()

  raise(BaseException('get_proxy no proxy configured'))


class EC2Proxy(AuthServiceProxy):
  
  def __init__(self):
    
    user   = config['my']['bd_user']
    passwd = config['my']['bd_pass']
    host   = config['my']['bd_host']
    port   = config['my']['bd_port']

    url    = "https://%s:%s@%s:%s" % (user,passwd,host,port)
    return AuthServiceProxy.__init__(self, url)

  def getblk(self, block):
    hash = self.getblockhash(block)
    return self.getblock(hash)

  def pushtx(self, rawtx):
    return self.sendrawtransaction(rawtx)

class BlockChainProxy():
  
  HTTP_TIMEOUT = 30

  def pushtx(self, rawtx):
    conn = httplib.HTTPConnection('blockchain.info', 80, False, self.HTTP_TIMEOUT)
    
    conn.request('POST', '/pushtx', urllib.urlencode({'tx': rawtx}), 
                 {'user-agent'  : 'Mozilla/5.0 (Windows NT 5.1; rv:5.0.1) Gecko/20100101 Firefox/5.0.1', 
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'Accept'      : 'application/json'})

    resp = conn.getresponse()
    
    if resp is None:
      raise JSONRPCException({'code' : -342, 'message' : 'missing HTTP response from server'})

    resp = resp.read()
    resp = resp.decode('utf8')

    if resp.startswith('Transaction Submitted'):
      raise JSONRPCException({'code' : 617, 'message' : 'unable to push tx: %s' % resp})

  def get_url(self, url):
    logging.info(url)

    conn = httplib.HTTPConnection('blockchain.info', 80, False, self.HTTP_TIMEOUT)
    conn.request('GET', url)
    resp = conn.getresponse()
    
    if resp is None:
      raise JSONRPCException({'code' : -342, 'message' : 'missing HTTP response from server'})

    resp = resp.read()
    resp = resp.decode('utf8')

    resp = json.loads(resp)
    return resp

  def getblockcount(self):
    resp = self.get_url('/latestblock?format=json')
    return int(resp['height'])

  def getblk(self, block):
    tmp = self.get_url('/block-height/%d?format=json'%block)

    txs = []    
    for bc_tx in tmp['blocks'][0]['tx']:

      outs = []
      for bc_out in bc_tx['out']:
        
        tmpaddr = {}
        if bc_out.has_key('addr'):
          tmpaddr = {'addresses':[bc_out['addr']]}

        outs.append({'n'            : bc_out['n'], 
                     'value'        : Decimal(bc_out['value'])/Decimal(1e8), 
                     'scriptPubKey' : tmpaddr }) 

      txs.append({'outs':outs, 'txid': bc_tx['hash']})

    return {'tx':txs, 'hash':tmp['blocks'][0]['hash']}

    #same format