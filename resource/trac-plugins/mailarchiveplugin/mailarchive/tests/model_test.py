# -*- coding: utf-8 -*-

import sys
import os
import re
import unittest

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = script_dir + os.sep + '../..'
if not base_dir in sys.path:
    sys.path.insert(0, base_dir)
    
from mailarchive.model import *

class ComponentManagerStub(object):
    components = {}

    def component_activated(self, dummy):
        pass

    def get_db_cnx(self):
        return DBStub()
    
class RequestStub(object):
    def __init__(self):
        self.href = HrefStub()
    
class HrefStub(object):
    def mailarchive(self, id):
        return 'mailarchive/%s' % id
  
class ConfigStub(object):
    def get(self, tag, key):
        pass

class DBStub(object):
    def __init__(self, row=None):
        self.row = row
    
    def cursor(self):
        print "cursor"
        return self
    
    def execute(self, sql , args):
        print "excecute"
        return self
    
    def fetchone(self):
        print "fetchone"
        return self.row 
    
    def commit(self):
        print "commit"
        
class ModelTest(unittest.TestCase):

    def setUp(self):
        self.env = ComponentManagerStub()
        self.req = RequestStub()
        self.db = DBStub()
    
    def test_populate(self):
        msg = {'message-id':'<28056cd5-24e1-4d94-941b-d25a01d35dcdtestmail@example.com>'}
        mail = Mail(self.env, db=self.db)
        mail.populate('test_author', msg, 'test-ML')


if __name__ == '__main__':
    unittest.main()

