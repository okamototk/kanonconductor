# -*- coding: utf-8 -*-

import cmd
import sys

import urllib
import time
import calendar
import re
import os
import tempfile
import email.Errors
import email.Utils
import mailbox
import mimetypes
import email
#from email.Parser  import Parser
from email.Header import decode_header
#from email.Utils import collapse_rfc2231_value
import traceback

#011
import pkg_resources

from genshi.builder import tag

from genshi.core import Stream, Markup as GenshiMarkup
from genshi.input import HTMLParser, ParseError, HTML

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
#from trac.Search import ISearchSource, search_to_sql, shorten_result
from trac.search import ISearchSource, search_to_sql, shorten_result

from trac.ticket.model import Ticket

from trac.web import IRequestHandler
from trac.util import NaivePopen
from trac.util.translation import _
from StringIO import StringIO

import poplib

from trac.wiki import wiki_to_html,wiki_to_oneliner, IWikiSyntaxProvider
from trac.wiki.api import WikiSystem
from trac.util.html import html, Markup #0.10

from trac.util.text import to_unicode, wrap, unicode_quote, unicode_unquote, \
                           print_table, console_print
                           
from trac.web.chrome import add_link, add_stylesheet, INavigationContributor, ITemplateProvider

#0.11 from trac.attachment import attachment_to_hdf, attachments_to_hdf, Attachment, AttachmentModule
from trac.attachment import Attachment,AttachmentModule

from trac.mimeview import *
#from trac.mimeview.api import Mimeview, IContentConverter #0.10


from trac.admin.console import TracAdmin

from api import IEmailHandler
from model import Mail
from util import printout, printerr


PLUGIN_VERSION = pkg_resources.get_distribution('TracMailArchive').version

class MailArchiveAdmin(TracAdmin):
    intro = ''
    doc_header = 'Trac MailArchive Plugin Admin Console %(version)s\n' \
                 % {'version': PLUGIN_VERSION}
    
    ruler = ''
    prompt = "MailArchiveAdmin> "
    __env = None
    _date_format = '%Y-%m-%d'
    _datetime_format = '%Y-%m-%d %H:%M:%S'
    _date_format_hint = 'YYYY-MM-DD'

    ## Help
    _help_help = [('help', 'Show documentation')]

    def all_docs(cls):
        return (cls._help_help + cls._help_import + cls._help_pop3 + cls._help_updatedb)
    all_docs = classmethod(all_docs)

    def msgfactory(self,fp):
        try:
            return email.message_from_file(fp)
        except email.Errors.MessageParseError:
            # Don't return None since that will
	    # stop the mailbox iterator
	    return ''

    def import_message(self, msg, author, mlid, db):
        mail = Mail(self.env, db=db)
        mail.populate(author, msg, mlid)
        
        self.handleMail(mail)

    def handleMail(self, mail):
        # handle the message
        handlers = ExtensionPoint(IEmailHandler).extensions(self.env)
        
        handlers.sort(key=lambda x: x.order(), reverse=True)
        warnings = []
        for handler in handlers:
            try:
                message = handler.invoke(mail, warnings)
            except Exception, e:
                traceback.print_exc(e)
                printerr(_('Handler Error. Subject: %s\n\n%s' % (str(mail.subject), str(e))))
        
    def do_refresh_category(self,line):
        db = self.db_open()
        self.env = self.env_open()
        cursor = db.cursor()
        cursor.execute("DELETE FROM mailarc_category")
        cursor.execute("SELECT category, count(*) as cnt from mailarc GROUP BY category ")
        for category,cnt in cursor:
            cursor2 =  db.cursor()
            cursor2.execute("INSERT INTO mailarc_category (category,mlid,yearmonth,count) VALUES(%s,%s,%s,%s)",(category,category[:-6],category[-6:],cnt))
        db.commit()

    ## Help
    _help_import = [('import <mlname> <filepath>', 'import UnixMail')]

    def do_import(self, line):
        arg = self.arg_tokenize(line)
        if len(arg) < 2 :
            self.print_error(_('import MLname filepath'))
            return
        
        db = self.db_open()
        self.env = self.env_open()
        self._import_unixmailbox('cmd', db, arg[0], arg[1])

    ## Help
    _help_pop3 = [('pop3 <mlname>', 'import from pop3 server')]

    def do_pop3(self, line):
        arg = self.arg_tokenize(line)
        if len(arg) < 1 :
            printerr("pop3 MLname")
        db = self.db_open()
        self.env = self.env_open()
        self._import_from_pop3('cmd', db, arg[0])
        
    ## Help
    _help_updatedb = [('updatedb', 'update db for new version plugin.')]

    def do_updatedb(self, line):
        db = self.db_open()
        self.env = self.env_open()
        
        from model import MailFinder
        
        mails = MailFinder.find_not_root(self.env)
        
        cursor = db.cursor()
        for mail in mails:
            root_id = mail.get_thread_root().messageid
            sql = "UPDATE mailarc SET threadroot = %s WHERE messageid = %s" 
            printout(_('root_id=%s, messageid=%s' % (root_id, mail.messageid)))
            if root_id == mail.messageid:
                #自分が親(親メッセージIDのメールがDBに存在しない)場合、更新しない
                continue
            cursor.execute(sql, (root_id, mail.messageid))
            self.print_info('%s' % sql)
            
        db.commit()

    ## Help
    _help_help = [('help', 'Show documentation')]

    def do_help(self, line=None):
        arg = self.arg_tokenize(line)
        if arg[0]:
            try:
                doc = getattr(self, "_help_" + arg[0])
                self.print_doc (doc)
            except AttributeError:
                printerr(_("No documentation found for '%(cmd)s'", cmd=arg[0]))
        else:
            printout(_("mailarc-admin - The Trac MailArchivePlugin Administration Console "
                       "%(version)s", version=PLUGIN_VERSION))
            if not self.interactive:
                print
                printout(_("Usage: mailarc-admin </path/to/projenv> "
                           "[command [subcommand] [option ...]]\n")
                    )
            self.print_doc(self.all_docs())

    def print_info(self, line):
        printout(line)

    def print_debug(self, line):
        #print "[Debug] %s" % line
        pass

    def print_error(self, line):
        printout("[Error] %s" % line)

    def print_warning(self, line):
        printout("[Warning] %s" % line)
        
    def print_import_error(self, msg):
        self.print_error(_('Exception At Message-ID:%(messageid)s,\
                            Subject:%(subject)s', messageid=msg['message-id'],
                            subject=msg['Subject']))

    def _import_unixmailbox(self, author, db, mlid, msgfile_path):
        self.print_debug('import_mail')
        if not db:
            #db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False

        printout(_("%(time)s Start Importing %(file_path)s ...",
                   time=time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()),
                  file_path=msgfile_path))

        fp = open(msgfile_path,"rb")
        mbox = mailbox.UnixMailbox(fp, self.msgfactory)

        counter =1
        msg = mbox.next()
        while msg is not None:
            messageid = ''
            try:
                self.import_message(msg, author, mlid, db)
            except Exception, e:
                traceback.print_exc(e)
                exception_flag = True
                self.print_import_error(msg)

            if counter > 10000:
                break
            msg = mbox.next()
            counter = counter + 1

        fp.close()
        #if handle_ta:
        db.commit()
        printout(_("End Imporing %(file_path)s. ", file_path=msgfile_path))

    def _import_from_pop3(self, author, db, mlid):

        pop_server = self.env.config.get('mailarchive', 'pop3_server_' + mlid)
        if pop_server =='':
            pop_server = self.env.config.get('mailarchive', 'pop3_server')

        pop_user = self.env.config.get('mailarchive', 'pop3_user_' + mlid)
        if pop_user =='':
            pop_user = self.env.config.get('mailarchive', 'pop3_user')

        pop_password = self.env.config.get('mailarchive', 'pop3_password_' + mlid)
        if pop_password =='':
            pop_password = self.env.config.get('mailarchive', 'pop3_password')

        pop_delete = self.env.config.get('mailarchive', 'pop3_delete_' + mlid)
        if pop_delete =='':
            pop_delete = self.env.config.get('mailarchive', 'pop3_delete','none')
            
            
        #for POP SSL. Thanks! http://hidamarinonaka.jugem.cc/?eid=140
        pop_ssl = self.env.config.get('mailarchive', 'pop3_ssl_' + mlid)
        if pop_ssl == '':
            pop_ssl = self.env.config.get('mailarchive', 'pop3_ssl' + mlid, 'no')


        if pop_server =='':
            printerr(_('trac.ini mailarchive pop3_server is null!'))
        elif pop_user == '':
            printerr(_('trac.ini mailarchive pop3_user is null!'))
        elif pop_password == '':
            printerr(_('trac.ini mailarchive pop3_password is null!'))

        printout(_("%(time)s Start Connction pop3 %(server)s:%(user)s ...",
                    time=time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime()),
                    server=pop_server,
                    user=pop_user))

        pop = None
        if pop_ssl == 'yes':
            printout(_('POP3_SSL access...'))
            pop = poplib.POP3_SSL(pop_server)
        elif pop_ssl == 'no':
            printout(_('POP3 access...'))
            pop = poplib.POP3(pop_server)
        else:
            printerr(_('trac.ini mailarchive pop3_ssl isn\'t yes/no!'))

        pop.user(pop_user)
        pop.pass_(pop_password)
        num_messages = len(pop.list()[1])
        counter = 1
        for i in range(num_messages):
            #lines = ['',]
            #for j in pop.retr(i+1)[1]:
            #    lines.append(j + os.linesep)
            #mes_text = ''.join(lines)
            mes_text = ''.join(['%s\n' % line for line in  pop.retr(i+1)[1]])
            messageid = ''
            exception_flag = False
            msg = ''
            try:
                msg = email.message_from_string(mes_text)
                self.import_message(msg, author, mlid, db)
            except Exception, e:
                traceback.print_exc(e)
                exception_flag = True
                self.print_import_error(msg)

            # delete mail
            if pop_delete == 'all':
                pop.dele(i+1)
                printout(_("    Delete MailServer Message"))
            elif pop_delete == 'imported':
                if exception_flag == False:
                    pop.dele(i+1)
                    printout(_("    Delete MailServer Message"))
            else:
                pass

            if counter > 10000:
                break
            counter = counter + 1

        pop.quit()

        #if handle_ta:
        db.commit()
        printout(_("End Reciving."))

def run(args=None):
    """Main entry point."""
    if args is None:
        args = sys.argv[1:]
    admin = MailArchiveAdmin()
    if len(args) > 0:
        if args[0] in ('-h', '--help', 'help'):
            return admin.onecmd('help')
        elif args[0] in ('-v','--version'):
            print '%s %s' % (os.path.basename(args[0]), TRAC_VERSION)
        else:
            admin.env_set(os.path.abspath(args[0]))
            if len(args) > 1:
                s_args = ' '.join(["'%s'" % c for c in args[2:]])
                command = args[1] + ' ' +s_args
                print command
                return admin.onecmd(command)
            else:
                while True:
                    admin.run()
    else:
        return admin.onecmd("help")
    
if __name__ =='__main__':
    run()
