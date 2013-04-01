# -*- coding: utf-8 -*-

from electrum.bitcoin import *
from config import config

def decrypt_private(key, passwd):
  #config['my']['secret_key_2']
  return key

def encrypt_private(key, passwd):
  #config['my']['secret_key_2']
  return key

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

  return [ is_valid(address) and address==tmp, address, asec]
