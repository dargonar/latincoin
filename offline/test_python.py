# -*- coding: utf-8 -*-
 
from bitcoinrpc.authproxy import AuthServiceProxy
 
access = AuthServiceProxy("https://bitcoinrpc:GveWduSEmAAsSBHWRYKkUsCcbm6HR4xbVRFKNmGmYChL@ec2-54-245-175-53.us-west-2.compute.amazonaws.com:52234")
last_block = access.getblockcount()
#print last_block

block_hash = access.getblockhash(last_block)
#print block_hash

block = access.getblock(block_hash)
#print block
for tx in block['tx']:
  print tx['txid']
  for o in tx['outs']:
    print o['scriptPubKey']['addresses'][0], '=>', ('%.8f' % o['value'])
