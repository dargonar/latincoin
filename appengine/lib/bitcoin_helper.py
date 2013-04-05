# -*- coding: utf-8 -*-
from electrum.bitcoin import *
from aes import encryptData, decryptData
from config import config
from hashlib import sha256
from decimal import Decimal

from models import BitcoinAddress

def encrypt_all_keys(user, old_password):

  to_save = []
  for addy in BitcoinAddress.all().ancestor(user):
    addy.private_key = decrypt_private(addy.private_key, old_password)
    addy.private_key = encrypt_private(addy.private_key, user.password)
    to_save.append(addy)

  return to_save

def get_key_for_passwd(passwd):
  return sha256('%s%s' % (sha256(passwd).digest().encode('hex'), sha256(config['my']['secret_key_2']).digest().encode('hex'))).digest()

def decrypt_private(crypt_priv_key, user_password):
  return decryptData(get_key_for_passwd(user_password), crypt_priv_key.decode('hex'))

def encrypt_private(plain_priv_key, user_password):
  return encryptData(get_key_for_passwd(user_password), plain_priv_key).encode('hex')

def generate_new_address():

  seed = random_seed(128)
  int_seed = int('0x%s' % seed,16)
  
  pkey = EC_KEY(int_seed)

  private_key = GetPrivKey(pkey)
  public_key = GetPubKey(pkey.pubkey)
  address = public_key_to_bc_address(public_key)

  sec = PrivKeyToSecret(private_key)
  asec =  SecretToASecret(sec)

  tmp = address_from_private_key(asec)

  return { 'result': is_valid(address) and address==tmp, 'public': address, 'private': asec }


def generate_forward_transaction(src_add, src_priv, dst_add, tx_hash, amount, index, fee=Decimal('0.0005')):
  
  amount -= fee
  if abs(amount) < Decimal(1e-8):
    return [False, u'Couldnt set fee']

  hash_160 = bc_address_to_hash_160(src_add)[1]

  script = '76a9'                                      # op_dup, op_hash_160
  script += '14'                                       # push 0x14 bytes
  script += hash_160.encode('hex')
  script += '88ac'

  inputs  = [{'tx_hash':tx_hash, 'index':index,'raw_output_script':script, 'address': 0}]
  outputs = [(dst_add, int(amount*Decimal(1e8)))]

  tx = Transaction.from_io(inputs, outputs)

  tx.sign([src_priv])
  return [True, tx.as_dict()['hex']]
