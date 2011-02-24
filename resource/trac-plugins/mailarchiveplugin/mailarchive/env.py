# -*- coding: utf-8 -*-

import re

from trac.core import *
from trac.env import IEnvironmentSetupParticipant

class MailArchiveSetup(Component):
    implements(IEnvironmentSetupParticipant)
    
    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.found_db_version = 0
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        # check for our custom fields
        if 'mail_id' not in self.config['ticket-custom']:
            return True
        
        # check for database table
        cursor = db.cursor()
        try:
            cursor.execute("SELECT id FROM mailarc WHERE id='1'")
        except :
            db.rollback()
            return True
            
        # fall through
        return False

    def upgrade_environment(self, db):
        # create custom field
        custom = self.config['ticket-custom']
        if 'mail_id' not in custom:
            custom.set('mail_id', 'text')
            custom.set('mail_id.label', 'Mail ID')
            self.config.save()
            
        # create database tables
        sql = [
"""
CREATE TABLE mailarc (id integer, category text, messageid text,
 utcdate integer, zoneoffset integer, 
 subject text, fromname text, fromaddr text, header text, text text, 
 threadroot text, threadparent text);
""",
"""
CREATE TABLE mailarc_category ( category text, mlid text, yearmonth text, count integer);
""",
"""
CREATE UNIQUE INDEX mailarc_messageid_idx ON mailarc (messageid)
""",
"""
CREATE INDEX mailarc_id_idx ON mailarc (id)
""",
"""
CREATE INDEX mailarc_category_idx ON mailarc (category)
""",
"""
CREATE INDEX mailarc_utcdate_idx ON mailarc (utcdate)
""",
"""
CREATE UNIQUE INDEX mailarc_category_category_idx ON mailarc_category (category)
""",
        ]
        
        cursor = db.cursor()
        for s in sql:
            cursor.execute(s)
            self.log.debug('%s' % s)
