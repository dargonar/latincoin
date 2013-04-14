# -*- coding: utf-8 -*-

import sys
sys.path[0:0] = ['../appengine/distlib', '../appengine', '../appengine/lib']

from aes import encryptData, decryptData
from hashlib import sha256
from config import config

from electrum.bitcoin import *
from bitcoin_helper import encrypt_private, decrypt_private, generate_new_address

priv = '13067dc1ab3d49f5cfaf84e787bcf1c98f740cce2a30a0fcb9af8a271dbc42188b0e41940edb63ce2cae633d5166b225c1d957107845b546a6213084c2dd2152a77d648dd0ed9e7fa2b444849558c21d'
print decrypt_private(priv)