# -*- coding: utf-8 -*-
from electrum.bitcoin import *
from aes import encryptData, decryptData
from config import config
from hashlib import sha256
from decimal import Decimal

from models import BitcoinAddress

ONE_SATOSHI = Decimal(1e-8)
ONE_PIP     = Decimal(1e-10)


def format_satoshis(x, is_diff=False, num_zeros = 0):
  s = Decimal(x)
  sign, digits, exp = s.as_tuple()
  digits = map(str, digits)
  while len(digits) < 9:
      digits.insert(0,'0')
  digits.insert(-8,'.')
  s = ''.join(digits).rstrip('0')
  if sign: 
      s = '-' + s
  elif is_diff:
      s = "+" + s

  p = s.find('.')
  s += "0"*( 1 + num_zeros - ( len(s) - p ))
  s += " "*( 9 - ( len(s) - p ))
  s = " "*( 5 - ( p )) + s
  return s

def zero_btc(value):
  return value < ONE_SATOSHI

def zero_cur(value):
  return value < ONE_PIP

def get_secure_key():
  return sha256(config['my']['secret_key_2']).digest().encode('hex')[0:32]

def decrypt_private(crypt_priv_key):
  return decryptData(get_secure_key(), crypt_priv_key.decode('hex'))

def encrypt_private(plain_priv_key):
  return encryptData(get_secure_key(), plain_priv_key).encode('hex')

def generate_new_address():

  seed = random_seed(256)
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
  if zero_btc(amount):
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
  return [True, tx]
