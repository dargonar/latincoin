# -*- coding: utf-8 -*-
import sys
sys.path[0:0] = ['../appengine/distlib', '../appengine/lib', '../appengine']

from bitcoinrpc.authproxy import AuthServiceProxy
from config import config

def get_blockchain_url():
  host   = 'blockchain.info'
  url    = "http://blockchain.info/%s"

  access = AuthServiceProxy(url)
  return access  

def get_ec2_access():
  user   = config['my']['bd_user']
  passwd = config['my']['bd_pass']
  host   = config['my']['bd_host']
  port   = config['my']['bd_port']

  url    = "https://%s:%s@%s:%s" % (user,passwd,host,port)

  access = AuthServiceProxy(url)
  return access


access = get_ec2_access()

tx='e54000456cf6963f763857adc0be722284e05d474ce5b8119ade798c76a52609'
xx = access.getrawtransaction(tx,1)

print xx