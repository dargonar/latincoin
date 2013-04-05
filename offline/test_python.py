# -*- coding: utf-8 -*-

import sys
sys.path[0:0] = ['../appengine/distlib', '../appengine', '../appengine/lib']


from bitcoinrpc.connection_helper import BlockChainProxy, EC2Proxy

b = BlockChainProxy()
print b.getblk(229755)

 
# from bitcoinrpc.authproxy import AuthServiceProxy
 
# access = AuthServiceProxy("https://bitcoinrpc:GveWduSEmAAsSBHWRYKkUsCcbm6HR4xbVRFKNmGmYChL@ec2-54-245-175-53.us-west-2.compute.amazonaws.com:52234")
# last_block = access.getblockcount()
# #print last_block

# last_block = 229712
# block_hash = access.getblockhash(last_block)
# block = access.getblock(block_hash)
# print block
