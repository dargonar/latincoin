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

from bitcoinrpc.authproxy import AuthServiceProxy
from config import config
from models import SystemConfig

from bitcoinrpc import connection
access = connection.get_proxy( 'blockchain' )


tx='6279ec2fc1e075d73e17d8c8bc8f72949e3358da19931932178dee553528326d'
xx = access.getrawtransaction(tx,1)

print xx