# -*- coding: utf-8 -*-
from bitcoinrpc.authproxy import AuthServiceProxy
from mycrypto import AESCipher

# config
rpcuser = 'bitcoin-admin'
rpcpass = '5MLpeupM46'

encrypt_key='XRXqZeUbWHjISTO4bV6gNbNBqVecxIlj'

txid    = '2276f8d6db4dade0d5923f7db9f6ca16a4f1d2f374fb0d4b0af15821f5f736fc'

btcdest  = '1CC63cRz5qQMEYB4SiQRugnhs5VHzEMuM2'
enc_privkey = 'pN1DYKnq/yZwj+E380+p5zujblQkGP+ocz/ub2cC6QkfE4mLAdCBfJpBRxIpRpfn/EwAeBB/PTTlbTEfC6khJLMKPSFeBlN7/Esx/9ZZ92c='

txinfo = [{'txid':txid, 'vout':0}]
txdest = {btcdest:1.000}

cipher = AESCipher(encrypt_key)
privkey = cipher.decrypt(enc_privkey)

access = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (rpcuser,rpcpass))

rawtx = access.createrawtransaction(txinfo, txdest)

print 'rawtx: ', rawtx

#jsontx = access.decoderawtransaction(rawtx)
print privkey
txx = access.signrawtransaction(rawtx, [], [privkey])
print 'sigtx: ', txx

#adds = access.listreceivedbyaddress(0,True)


#XRXqZeUbWHjISTO4bV6gNbNBqVecxIlj
# batch_name = raw_input("Batch name: ")
# encrypt_key = raw_input("Encrypt Key: ")

# cipher = AESCipher(encrypt_key)



# with open('%s.txt' % batch_name,'wb') as outfile:
#   for add in adds:
#     if add['account'] == batch_name:
#       privkey = access.dumpprivkey(add['address'])
#       outfile.write("%s %s\n" % (add['address'],cipher.encrypt(privkey)))