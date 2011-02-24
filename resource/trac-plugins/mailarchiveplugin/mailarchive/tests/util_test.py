# -*- coding: utf-8 -*-

import sys
import os
import re
import unittest

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = script_dir + os.sep + '../..'
if not base_dir in sys.path:
    sys.path.insert(0, base_dir)

from mailarchive.util import *

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
        
class UtilTest(unittest.TestCase):

    def setUp(self):
        self.env = ComponentManagerStub()
        self.req = RequestStub()
    
    def test_linkify_ids(self):
        ids = [1, 2, 3]
        tag = linkify_ids(self.env, self.req, ids)
        self.assertEquals(
"""<span><a class="ticket" href="mailarchive/1" title="test">mail:1</a>, <a class="ticket" href="mailarchive/2" title="test">mail:2</a>, <a class="ticket" href="mailarchive/3" title="test">mail:3</a></span>"""
            , str(tag))
        
        ids = [1]
        tag = linkify_ids(self.env, self.req, ids)
        self.assertEquals(
"""<span><a class="ticket" href="mailarchive/1" title="test">mail:1</a></span>"""
            , str(tag))
        
        ids = []
        tag = linkify_ids(self.env, self.req, ids)
        self.assertEquals(
"""<span/>"""
            , str(tag))
    
    def test_get_author(self):
        author = get_author('foo', 'bar@example.com')
        self.assertEquals('foo', author)
        
        author = get_author('', 'bar@example.com')
        self.assertEquals('bar', author)
        
        author = get_author(None, 'bar@example.com')
        self.assertEquals('--', author)
        
        author = get_author(None, None)
        self.assertEquals('--', author)
        
        author = get_author(None, '')
        self.assertEquals('--', author)
        
        author = get_author('', 'bar')
        self.assertEquals('--', author)
        
        author = get_author('', 'bar@')
        self.assertEquals('bar', author)
        
        author = get_author('', 'bar@for@')
        self.assertEquals('bar', author)

if __name__ == '__main__':
    unittest.main()

