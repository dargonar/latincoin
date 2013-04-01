# -*- coding: utf-8 -*-

import sys
sys.path[0:0] = ['../appengine/distlib']

from electrum.bitcoin import *

#seed = random_seed(128)
seed = 'd61a1a11fa622ec57b6047c1e203b5ceda522819ee59ffd2b2e9d4b32bf5556f'

print seed
ss = int('0x%s' % seed,16)
print ss
pkey = EC_KEY(ss)

private_key = GetPrivKey(pkey)
public_key = GetPubKey(pkey.pubkey)
address = public_key_to_bc_address(public_key)

sec = PrivKeyToSecret(private_key)
asec =  SecretToASecret(sec)

print address
print is_valid(address)

addy = address_from_private_key(asec)
print address == addy
