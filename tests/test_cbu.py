# -*- coding: utf-8 -*-
import unittest

from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from utils import is_valid_cbu

class TestCBU(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()

  def tearDown(self):
    self.testbed.deactivate()

  def test_CBU(self):
    self.assertTrue( is_valid_cbu('0150804601000112908741') )
    self.assertFalse( is_valid_cbu('0150804601000112508741') )