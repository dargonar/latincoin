# -*- coding: utf-8 -*-

import sys
sys.path[0:0] = ['../appengine/distlib', '../appengine', '../appengine/lib']

from aes import encryptData, decryptData
from hashlib import sha256
from config import config

from electrum.bitcoin import *

def get_key_for_passwd(passwd):
  return sha256('%s%s' % (sha256(passwd).digest().encode('hex'), sha256(config['my']['secret_key_2']).digest().encode('hex'))).digest()

def decrypt_private(crypt_priv_key, user_password):
  return decryptData(get_key_for_passwd(user_password), crypt_priv_key.decode('hex'))

def encrypt_private(plain_priv_key, user_password):
  return encryptData(get_key_for_passwd(user_password), plain_priv_key).encode('hex')


passwd = '00487002c09f308f8dc22ac4bef0b46fbe9cd5d3025f85a8df74a343e32e053b'
privk  = '5HpHagT65TZzG1PH3CSu63k9NmovqAZNQs8s8VAXLZFRbhnEhZU'
k = encrypt_private(privk, passwd)
dec = decrypt_private(k,passwd)
pub = address_from_private_key(dec)

print privk
print k
print pub

# texto_a_encriptar = 'A Jadri no le gusta el pollo'

# elpass = 'este el el password'

# llavemaestra = get_key_for_passwd(elpass)

# print 'llave maestra: %s' % llavemaestra.encode('hex')

# xxx = encrypt_private(texto_a_encriptar, elpass)
# print 'Encriptado: %s' % xxx

# yyy = decrypt_private(xxx, elpass)
# print yyy 