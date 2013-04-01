# -*- coding: utf-8 -*-

from bitcoinrpc.authproxy import AuthServiceProxy
from mycrypto import AESCipher

# config
rpcuser = 'bitcoin-admin'
rpcpass = '5MLpeupM46'


access = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (rpcuser,rpcpass))
adds = access.listreceivedbyaddress(0,True)

#XRXqZeUbWHjISTO4bV6gNbNBqVecxIlj

batch_name = raw_input("Batch name: ")
encrypt_key = raw_input("Encrypt Key: ")

cipher = AESCipher(encrypt_key)

with open('%s.txt' % batch_name,'wb') as outfile:
  for add in adds:
    if add['account'] == batch_name:
      privkey = access.dumpprivkey(add['address'])
      outfile.write("%s %s\n" % (add['address'],cipher.encrypt(privkey)))