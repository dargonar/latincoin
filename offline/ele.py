# -*- coding: utf-8 -*-
import sys

root_appe = '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine'

sys.path[0:0] = [
'../appengine/distlib', 
'../appengine', 
'../appengine/lib', 
root_appe, 
root_appe + '/lib/yaml/lib',
root_appe + '/lib/webapp2-2.5.2',
root_appe + '/lib/webob-1.2.3',
]

from decimal import Decimal
from electrum.bitcoin import *
from config import config

from bitcoinrpc.authproxy import AuthServiceProxy
from bitcoin_helper import generate_forward_transaction
from mycrypto import AESCipher



src_add  = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
src_priv = 'L4J68a3t7EUKNfaKzyDBhUSeywFpUR6WMdsAGEzMdhgDKRkKws5q'
dst_add  = '14UbWFC3aafN2CF1Pt4wutop3EfJR8XQRh'
tx_hash  = '5f5d7bdeab9ba19f1ce209d498e188b3b1f270da82b0b712f1a15c6ff3c2a235'
index    = 0
amount   = Decimal('0.1')

raw, tx = generate_forward_transaction(src_add, src_priv, dst_add, tx_hash, amount, index)
print tx.hash()

# access = get_ec2_access()
# print access.decoderawtransaction(raw[1])


# addy = address_from_private_key('L4J68a3t7EUKNfaKzyDBhUSeywFpUR6WMdsAGEzMdhgDKRkKws5q')
# print addy

# import sys
# sys.exit(0)

# xx = bc_address_to_hash_160('1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2')
# print xx[1].encode('hex')

# src_add = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
# dst_add = '14UbWFC3aafN2CF1Pt4wutop3EfJR8XQRh'

# tx_hash = '5f5d7bdeab9ba19f1ce209d498e188b3b1f270da82b0b712f1a15c6ff3c2a235'

# hash_160 = bc_address_to_hash_160(src_add)[1]

# script = '76a9'                                      # op_dup, op_hash_160
# script += '14'                                       # push 0x14 bytes
# script += hash_160.encode('hex')
# script += '88ac'

# # script  = 'OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG' % bc_address_to_hash_160(dst_add)[1].encode('hex')
# # print script

# inputs  = [{'tx_hash':tx_hash, 'index':0,'raw_output_script':script, 'address': 0}]
# outputs = [(dst_add, int(Decimal('0.1')*Decimal(1e8)))]

# tx = Transaction.from_io(inputs, outputs)
# # print tx.raw

# tx.sign(['L4J68a3t7EUKNfaKzyDBhUSeywFpUR6WMdsAGEzMdhgDKRkKws5q'])

# print
# print tx.as_dict()

# Transaction
# ss = tx.for_sig(-1)
# print ss


# tx.for


# xx = bc_address_to_hash_160('1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2')
# print xx

# config
# rpcuser = 'bitcoin-admin'
# rpcpass = '5MLpeupM46'

# encrypt_key='XRXqZeUbWHjISTO4bV6gNbNBqVecxIlj'

# txid    = '2276f8d6db4dade0d5923f7db9f6ca16a4f1d2f374fb0d4b0af15821f5f736fc'

# btcdest  = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
# enc_privkey = 'pN1DYKnq/yZwj+E380+p5zujblQkGP+ocz/ub2cC6QkfE4mLAdCBfJpBRxIpRpfn/EwAeBB/PTTlbTEfC6khJLMKPSFeBlN7/Esx/9ZZ92c='

# txinfo = [{'txid':txid, 'vout':0}]
# txdest = {btcdest:1.000}

# cipher = AESCipher(encrypt_key)
# privkey = cipher.decrypt(enc_privkey)

# access = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (rpcuser,rpcpass))

# rawtx = access.createrawtransaction(txinfo, txdest)

# print 'rawtx: ', rawtx

# #jsontx = access.decoderawtransaction(rawtx)
# print privkey
# txx = access.signrawtransaction(rawtx, [], [privkey])
# print 'sigtx: ', txx

# #adds = access.listreceivedbyaddress(0,True)


# #XRXqZeUbWHjISTO4bV6gNbNBqVecxIlj
# # batch_name = raw_input("Batch name: ")
# # encrypt_key = raw_input("Encrypt Key: ")

# # cipher = AESCipher(encrypt_key)



# # with open('%s.txt' % batch_name,'wb') as outfile:
# #   for add in adds:
# #     if add['account'] == batch_name:
# #       privkey = access.dumpprivkey(add['address'])
# #       outfile.write("%s %s\n" % (add['address'],cipher.encrypt(privkey)))