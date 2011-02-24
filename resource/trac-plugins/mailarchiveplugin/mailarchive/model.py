# -*- coding: utf-8 -*-

import calendar
import email
import os
import re
import time
import traceback

from datetime import datetime

from trac.attachment import Attachment, AttachmentModule
from trac.core import *
from trac.mimeview.api import Context
from trac.resource import Resource, ResourceNotFound
from trac.ticket.model import Ticket
from trac.util import NaivePopen, Markup
from trac.util.compat import set, sorted
from trac.util.datefmt import utc, to_timestamp
from trac.wiki.formatter import Formatter, WikiProcessor

from api import IEmailHandler
from attachment import MailArchiveAttachment
from util import Logger, get_author, is_empty, get_category_href, get_item_per_page, get_num_shown_pages, get_related_tickets

OUTPUT_ENCODING = 'utf-8'
SELECT_FROM_MAILARC = "SELECT id, messageid, utcdate, zoneoffset, subject, fromname, fromaddr, header, text, threadroot, threadparent FROM mailarc "

class Mail(object):
    """model for the Mail."""
    
    id_is_valid = staticmethod(lambda num: 0 < int(num) <= 1L << 31)
    
    def __init__(self, env, id=None, db=None, messageid=None, row=None):
        self.env = env
        self.db = db
        self.log = Logger(env)
        
        if id is not None:
            self.resource = Resource('mailarchive', str(id), None)
            self._fetch_mail(id)
        elif messageid is not None:
            self._fetch_mail_by_messageid(messageid)
            self.resource = Resource('mailarchive', self.id, None)
        elif row is not None:
            self._fetch_mail_by_row(row)
            self.resource = Resource('mailarchive', self.id, None)
        else:
            self.messageid = ''
            self.subject = ''
            self.utcdate = 0
            self.localdate = ''
            self.zoneoffset = 0
            self.body = ''
        
    def __eq__(self, other):
        if isinstance(other, Mail):
            return self.messageid == other.messageid
        return super.__eq__(other)
        
    def _get_db(self):
        if self.db:
            return self.db
        else:
            return self.env.get_db_cnx()

    def _get_db_for_write(self):
        if self.db:
            return (self.db, False)
        else:
            return (self.env.get_db_cnx(), True)
        
    def get_sanitized_fromaddr(self):
        return self.fromaddr.replace('@',
                                     self.env.config.get('mailarchive',
                                                         'replaceat', '@'))
        
    def get_fromtext(self):
        return get_author(self.fromname, self.fromaddr) 
        
    def get_category(self):
        yearmonth = time.strftime("%Y%m", time.gmtime(self.utcdate))
        category = self.mlid + yearmonth
        return category.encode('utf-8')
        
    def get_plain_body(self):
        return self._sanitize(self.env, self.body)
    
    def get_html_body(self, req):
        
        # for HTML Mail
        if self.body.lstrip().startswith('<'):
            return Markup(self.body)
        
        contentlines = self.body.splitlines()
        htmllines = ['',]
        
        #customize!
        #http://d.hatena.ne.jp/ohgui/20090604/1244114483
        wikimode = req.args.get('wikimode', 'on')
        for line in contentlines:
            if self.env.config.get('mailarchive', 'wikiview',' enabled') == 'enabled' and wikimode == 'on':
                htmllines.append(wiki_to_oneliner(line, self.env, self.db, False, False, req))
            else:
                htmllines.append(Markup(Markup().escape(line).replace(' ','&nbsp;')))
            
        content = Markup('<br/>').join(htmllines)
        return content
        
    def _sanitize(self, env, text):
        return text.replace('@', env.config.get('mailarchive', 'replaceat','_at_') )
    
    def _fetch_mail(self, id):
        row = None
        if self.id_is_valid(id):
            db = self._get_db()
            cursor = db.cursor()
            cursor.execute(SELECT_FROM_MAILARC + " WHERE id=%s", (id,))

            row = cursor.fetchone()
        if not row:
            raise ResourceNotFound('Mail %s does not exist.' % id,
                                   'Invalid Mail Number')

        self._fetch_mail_by_row(row)
    
    def _fetch_mail_by_messageid(self, messageid):
        row = None

        db = self._get_db()
        cursor = db.cursor()
        cursor.execute(SELECT_FROM_MAILARC + " WHERE messageid=%s",
                        (messageid,))

        row = cursor.fetchone()
        if not row:
            raise ResourceNotFound('Mail messageid %s does not exist.' % messageid,
                                   'Invalid Mail messageid Number')

        self._fetch_mail_by_row(row)
        
    def _fetch_mail_by_row(self, row):
        self.id = row[0]
        self.messageid = row[1]
        self.utcdate = row[2]
        self.zoneoffset = row[3]
        self.subject = row[4]
        self.fromname = row[5]
        self.fromaddr = row[6]
        self.header =row[7]
        self.body = row[8]
        self.thread_root = row[9]
        self.thread_parent = row[10]
        
        self.zone = self._to_zone(self.zoneoffset)
        self.localdate = self._to_localdate(self.utcdate, self.zoneoffset)
        
    def _to_localdate(self, utcdate, zoneoffset):
        return time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(utcdate + zoneoffset))

    def _to_zone(self, zoneoffset):
        #zone and date
        zone = ''
        if zoneoffset == '':
            zoneoffset = 0
        if zoneoffset > 0:
            zone = ' +' + time.strftime('%H%M', time.gmtime(zoneoffset))
        elif zoneoffset < 0:
            zone = ' -' + time.strftime('%H%M', time.gmtime(-1 * zoneoffset))
        return zone
                
    def get_href(self, req):
        return req.href.mailarchive(self.id)
    
    def get_subject(self):
        if is_empty(self.subject):
            return '(no subject)'
        else:
            return self.subject
    
    def get_senddate(self):
        return self.localdate + self.zone
    
    def get_thread_root(self):
        if self.thread_root == '':
            return self
        try:
            root_mail = Mail(self.env, messageid=self.thread_root)
        except ResourceNotFound:
            return self
        
        #self.thread_rootはオリジナル版だと親のメールになってしまっている。
        #互換性維持のため、ルートではない場合は自力で探しにいくロジックを走らす
        if root_mail.thread_root == '':
            return root_mail
        else:
            if self.thread_parent != '':
                root_id = MailFinder.find_root_id(self.env, self.messageid)
                return Mail(self.env, messageid=root_id)
    
    def get_thread_parent_id(self):
        if self.thread_parent != '':
            return self.thread_parent.split(' ')[0]
        return None
    
    def get_thread_parent(self):
        if self.thread_parent != '':
            return Mail(self.env, db=self.db, messageid=self.get_thread_parent_id())
        return self
    
    def get_children(self, desc=False, cached_mails=None):
        if cached_mails:
            self.log.debug("[%s] mail's threads is cached." % self.id)
            return [x for x in cached_mails if x.get_thread_parent_id() == self.messageid]
            
        db = self._get_db()
        cursor = db.cursor()
        sql = SELECT_FROM_MAILARC + " WHERE threadparent LIKE %s ORDER BY utcdate"
        
        if desc:
            sql += " DESC"
        
        cursor.execute(sql, ('%s %%' % self.messageid,))
        
        children = []
        
        for row in cursor:
            child_mail = Mail(self.env, row=row, db=self.db)
            children.append(child_mail)
        return children
    
    def get_thread_mails(self, desc=False):
        root = self.get_thread_root()
        
        db = self._get_db()
        cursor = db.cursor()
        sql = SELECT_FROM_MAILARC + " WHERE threadroot = %s ORDER BY utcdate"
        
        if desc:
            sql += " DESC"
        
        cursor.execute(sql, (root.messageid,))
        mails = []
        for row in cursor:
            mails.append(Mail(self.env, row=row, db=self.db))
        return mails
    
    def has_children(self, cached_mails=None):
        rtn = len(self.get_children(cached_mails=cached_mails)) > 0
        return rtn 

    def get_related_tickets(self, req):
        db = self._get_db()
        return get_related_tickets(self.env, req, db, self.id)
    
    def has_attachments(self, req):
        attachment = MailArchiveAttachment(self.env, self.id)
        return attachment.has_attachments(req)

    def populate(self, author, msg, mlid):
        """Populate the mail with 'suitable' values from a message"""
        
        if 'message-id' not in msg:
            raise 'Illegal Format Mail!'
        
        self.is_new_mail = False
        self.mlid = mlid

        self._parse_messageid(msg)
        self._parse_date(msg)
        self._parse_subject(msg)
        
        if msg.is_multipart():
            self._parse_multipart(author, msg)
        else:
            self._parse_body(msg)

        ref_messageid = self._parse_reference(msg)
        self._make_thread(ref_messageid)
        
    def update_or_save(self):
        if self.messageid is None or self.messageid == '':
            raise "Can't save mail to database."
        
        db, has_tran = self._get_db_for_write()
        cursor = db.cursor()

        yearmonth = time.strftime("%Y%m", time.gmtime(self.utcdate))
        category = self.mlid + yearmonth
        cursor.execute("SELECT category, mlid, yearmonth, count FROM mailarc_category WHERE category=%s",
                        (category.encode('utf-8'),))
        row = cursor.fetchone()
        count = 0
        if row:
            count = row[3]
            pass
        else:
            cursor.execute("INSERT INTO mailarc_category (category, mlid, yearmonth, count) VALUES(%s, %s, %s, %s)",
                            (category.encode('utf-8'),
                             self.mlid.encode('utf-8'),
                             yearmonth,
                             0))
        if self.is_new_mail:
            count = count + 1
        cursor.execute("UPDATE mailarc_category SET count=%s WHERE category=%s",
            (count, category.encode('utf-8')))

        # insert or update mailarc

        #self.log.debug(
        #    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" %(str(id),
        #    category.encode('utf-8'),
        #    messageid,
        #     utcdate,
        #      zoneoffset,
        #     subject.encode('utf-8'), fromname.encode('utf-8'),
        #     fromaddr.encode('utf-8'),'','',
        #     thread_root,thread_parent))
        cursor.execute("DELETE FROM mailarc where messageid=%s",
                       (self.messageid,))

        cursor.execute("INSERT INTO mailarc ("
            "id, category, messageid, utcdate, zoneoffset, subject,"
            "fromname, fromaddr, header, text, threadroot, threadparent) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (str(self.id),
            category.encode('utf-8'),
            self.messageid,
            self.utcdate,
            self.zoneoffset,
            self.subject.encode('utf-8'), self.fromname.encode('utf-8'),
            self.fromaddr.encode('utf-8'), '', self.body.encode('utf-8'),
            self.thread_root, self.thread_parent))

        if has_tran:
            db.commit()

    def _parse_messageid(self, msg):
        self.messageid = msg['message-id'].strip('<>')

        #check messageid is unique
        self.log.debug("Creating new mailarc '%s'" % 'mailarc')
        
        db = self._get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id from mailarc WHERE messageid=%s", (self.messageid,))
        row = cursor.fetchone()
        id = None
        if row:
            id = row[0]
            
        if id == None or id == "":
            # why? get_last_id return 0 at first.
            #id = db.get_last_id(cursor, 'mailarc')
            self.is_new_mail = True
            cursor.execute("SELECT Max(id)+1 as id from mailarc")
            row = cursor.fetchone()
            if row and row[0] != None:
                id = row[0]
            else:
                id = 1
        self.id = int(id) # Because id might be 'n.0', int() is called.

    def _parse_date(self, msg):
        if 'date' in msg:
            datetuple_tz = email.Utils.parsedate_tz(msg['date'])
            localdate = calendar.timegm(datetuple_tz[:9]) #toDB
            zoneoffset = datetuple_tz[9] # toDB
            utcdate = localdate - zoneoffset # toDB
            #make zone ( +HHMM or -HHMM
            zone = ''
            if zoneoffset > 0:
                zone = '+' + time.strftime('%H%M', time.gmtime(zoneoffset))
            elif zoneoffset < 0:
                zone = '-' + time.strftime('%H%M', time.gmtime(-1 * zoneoffset))
            #self.log.debug( time.strftime("%y/%m/%d %H:%M:%S %z",datetuple_tz[:9]))
            
            self.log.debug(time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(utcdate)))
            self.log.debug(time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(localdate)))
            self.log.debug(zone)
        
        fromname, fromaddr = email.Utils.parseaddr(msg['from'])
        
        self.fromname = self._decode_to_unicode(fromname)
        self.fromaddr = self._decode_to_unicode(fromaddr)
        self.zone = zone
        self.utcdate = utcdate
        self.zoneoffset = zoneoffset
        self.localdate = self._to_localdate(utcdate, zoneoffset)
        
        self.log.info('  ' + self.localdate + ' ' + zone +' '+ fromaddr)
        
    def _parse_subject(self, msg):
        if 'subject' in msg:
            self.subject = self._decode_to_unicode(msg['subject'])
            
    def _parse_reference(self, msg):
        # make thread infomations
        ref_messageid = ''
        if 'in-reply-to' in msg:
            ref_messageid = ref_messageid + msg['In-Reply-To'] + ' '
            self.log.debug('In-Reply-To:%s' % ref_messageid )

        if 'references' in msg:
            ref_messageid = ref_messageid + msg['References'] + ' '

        m = re.findall(r'<(.+?)>', ref_messageid)
        ref_messageid = ''
        for text in m:
            ref_messageid = ref_messageid + "'%s'," % text
            
        ref_messageid = ref_messageid.strip(',')
        
        self.log.debug('RefMessage-ID:%s' % ref_messageid)
        
        return ref_messageid

    def _parse_multipart(self, author, msg):
        body = ''
        # delete all attachement at message-id
        Attachment.delete_all(self.env, 'mailarchive', self.id, self.db)

        for part in msg.walk():
            content_type = part.get_content_type()
            self.log.debug('Content-Type:' + content_type)
            file_counter = 1

            if content_type == 'multipart/mixed':
                pass
            
            elif content_type == 'text/html' and self._is_file(part) == False:
                if body != '':
                    body += "\n------------------------------\n\n"
                    
                body = part.get_payload(decode=True)
                charset = part.get_content_charset()
                
                self.log.debug('charset:' + str(charset))
                # Todo:need try
                if charset != None:
                    body = self._to_unicode(body, charset)
                
            elif content_type == 'text/plain' and self._is_file(part) == False:
                #body = part.get_payload(decode=True)
                if body != '':
                    body += "\n------------------------------\n\n"
                    
                current_body = part.get_payload(decode=True)
                charset = part.get_content_charset()
                
                self.log.debug('charset:' + str(charset))
                # Todo:need try
                if charset != None:
                    #body = self._to_unicode(body, charset)
                    body += self._to_unicode(current_body, charset)
                else:
                    body += current_body
                
            elif part.get_payload(decode=True) == None:
                pass
            
            # file attachment
            else:
                self.log.debug(part.get_content_type())
                # get filename
                # Applications should really sanitize the given filename so that an
                # email message can't be used to overwrite important files
                
                filename = self._get_filename(part)
                if not filename:
                    import mimetypes
                    
                    ext = mimetypes.guess_extension(part.get_content_type())
                    if not ext:
                        # Use a generic bag-of-bits extension
                        ext = '.bin'
                    filename = 'part-%03d%s' % (file_counter, ext)
                    file_counter += 1

                self.log.debug("filename:" + filename.encode(OUTPUT_ENCODING))

                # make attachment
                tmp = os.tmpfile()
                tempsize = len(part.get_payload(decode=True))
                tmp.write(part.get_payload(decode=True))

                tmp.flush()
                tmp.seek(0,0)

                attachment = Attachment(self.env, 'mailarchive', self.id)

                attachment.description = '' # req.args.get('description', '')
                attachment.author = author #req.args.get('author', '')
                attachment.ipnr = '127.0.0.1'

                try:
                    attachment.insert(filename,
                            tmp, tempsize, None, self.db)
                except Exception, e:
                    try:
                        ext = filename.split('.')[-1]
                        if ext == filename:
                            ext = '.bin'
                        else:
                            ext = '.' + ext
                        filename = 'part-%03d%s' % (file_counter, ext)
                        file_counter += 1
                        attachment.description += ', Original FileName: %s' % filename
                        attachment.insert(filename,
                                tmp, tempsize, None, self.db)
                        self.log.warn('As name is too long, the attached file is renamed : ' + filename)

                    except Exception, e:
                        self.log.error('Exception at attach file of Message-ID:' + self.messageid)
                        traceback.print_exc(e)

                tmp.close()
        
        self.body = body
                
    def _parse_body(self, msg):
        content_type = msg.get_content_type()
        self.log.debug('Content-Type:' + content_type)
        
        if content_type == 'text/html':
            body = msg.get_payload(decode=True)
            charset = msg.get_content_charset()
 
            # need try:
            if charset != None:
                self.log.debug("charset:"+charset)
                body = self._to_unicode(body, charset)

            body = unicode(body)
            
            from stripogram import html2text, html2safehtml
            body = html2text(body)

        else:
            #body
            #self.log.debug(msg.get_content_type())
            body = msg.get_payload(decode=1)
            charset = msg.get_content_charset()

            # need try:
            if charset != None:
                self.log.debug("charset:"+charset)
                body = self._to_unicode(body,charset)
        self.body = body

    def _make_thread(self, ref_messageid):
        #body = body.replace(os.linesep,'\n')
        self.log.debug('Thread')

        thread_parent = ref_messageid.replace("'", '').replace(',',' ')
        thread_root = ''
        if thread_parent !='':
        # search first parent id
            self.log.debug("SearchThread;" + thread_parent)
            
            db = self._get_db()
            cursor = db.cursor()
            sql = "SELECT threadroot, messageid, utcdate FROM mailarc where messageid in (%s)" \
                  " ORDER BY utcdate DESC" % ref_messageid
            
            self.log.debug(sql)
            
            cursor.execute(sql)

            row = cursor.fetchone()
            if row:
                print row[0], row[1]
                #親スレッドがルートの場合
                if row[0] == '':
                    #ルートに親を設定
                    thread_root = thread_parent.split(' ').pop()
                    self.log.debug("NewThread;" + thread_root)
                else:
                    #親スレッドはルートではい場合、親スレッドのルートを設定する
                    thread_root = row[0]
                    self.log.debug("AddToThread;" + thread_root)
            else:
                    self.log.debug("NoThread;" + thread_parent)
                    
        self.thread_root = thread_root.strip()
        self.thread_parent = thread_parent

    def _is_file(self, part):
        """Return True:filename associated with the payload if present.
        """
        missing = object()
        filename = part.get_param('filename', missing, 'content-disposition')
        if filename is missing:
            filename = part.get_param('name', missing, 'content-disposition')
        if filename is missing:
            return False
        return True
    
    def _get_filename(self, part, failobj=None):
        """Return the filename associated with the payload if present.

        The filename is extracted from the Content-Disposition header's
        `filename' parameter, and it is unquoted.  If that header is missing
        the `filename' parameter, this method falls back to looking for the
        `name' parameter.
        """
        missing = object()
        filename = part.get_param('filename', missing, 'content-disposition')
        if filename is missing:
            filename = part.get_param('name', missing, 'content-disposition')
        if filename is missing:
            return failobj

        errors='replace'
        fallback_charset='us-ascii'
        if isinstance(filename, tuple):
            rawval = email.Utils.unquote(filename[2])
            charset = filename[0] or 'us-ascii'
            try:
                return self._to_unicode(rawval, charset)
            except LookupError:
                # XXX charset is unknown to Python.
                return unicode(rawval, fallback_charset, errors)
        else:
            return self._decode_to_unicode(email.Utils.unquote(filename))
        
    def _decode_to_unicode(self, basestr):
        # http://www.python.jp/pipermail/python-ml-jp/2004-June/002932.html
        # Make mail header string to unicode string

        decodefrag = email.Header.decode_header(basestr)
        subj_fragments = ['',]
        for frag, enc in decodefrag:
            if enc:
                frag = self._to_unicode(frag, enc)
            subj_fragments.append(frag)
        return ''.join(subj_fragments)

    def _to_unicode(self, text, charset):
        if text=='':
            return ''

        default_charset = self.env.config.get('mailarchive', 'default_charset', None)
        if default_charset:
            chaerset = default_charset

        # to unicode with codecaliases
        # codecaliases change mail charset to python charset
        charset = charset.lower( )
        aliases = {}
        aliases_text = self.env.config.get('mailarchive', 'codecaliases')
        for alias in aliases_text.split(','):
            alias_s = alias.split(':')
            if len(alias_s) >=2:
                if alias_s[1] == 'cmd':
                    aliases[alias_s[0].lower()] = ('cmd', alias_s[2])
                else:
                    aliases[alias_s[0].lower()] = ('codec', alias_s[1])

        if aliases.has_key(charset):
            (type, alias) = aliases[charset]
            if type == 'codec':
                text = unicode(text, alias)
            elif type == 'cmd':
                np = NaivePopen(alias, text, capturestderr=1)
                if np.errorlevel or np.err:
                    err = 'Running (%s) failed: %s, %s.' % (alias, np.errorlevel,
                                                            np.err)
                    print err
                    raise Exception, err
                text = unicode(np.out, 'utf-8')
        else:
            text = unicode(text, charset)
        return text

class MailFinder(object):
    
    @staticmethod
    def get_categories(req, db, target_category=''):
        cursor = db.cursor()
        sql = """SELECT category, mlid, yearmonth, count 
                   FROM mailarc_category
                   ORDER BY mlid, yearmonth DESC"""
        cursor.execute(sql)

        mls = []
        pre_mlid = ''
        for category, mlid, yearmonth, count in cursor:
            if target_category == '':
                target_category = category 

            category_item = {
                'id': mlid + yearmonth,
                'name': mlid,
                'year': yearmonth[:4],
                'month': yearmonth[4:],
                'count': str(count),
                'href': get_category_href(req, category)
            }
            if category == target_category:
                name = mlid
                year = yearmonth[:4]
                month = yearmonth[4:]
                category_item['href'] = ""

            if pre_mlid != mlid:
                mls.append({'name':mlid,'yearmonths':[]})
                pre_mlid = mlid
            mls[-1]['yearmonths'].append(category_item)      
        return mls, name, year, month, target_category
    
    @staticmethod
    def find_root_id(env, messageid):
        #self.thread_rootはオリジナル版では親のメールなので注意
        #互換性維持のため自力で探しにいく
        db = env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT id, threadparent FROM mailarc WHERE messageid = %s",
                       (messageid, ))
        row = cursor.fetchone()
        if row:
            #見つかったが親が無い場合
            if row[1] == '':
                return messageid
            else:
                root_id = MailFinder.find_root_id(env, row[1].split(' ')[0])
                if root_id:
                    return root_id
                else:
                    return messageid
        else:
            #親メールが見つからない場合
            return None
    
    @staticmethod
    def find_by_category(env, category, desc=True, limit=None):
        
        db = env.get_db_cnx()
        cursor = db.cursor()
        
        sql = SELECT_FROM_MAILARC + " WHERE category = %s ORDER BY utcdate"
        if not desc:
            sql += " ASC"
            
        if limit is None:
            limit = get_item_per_page(env) * get_num_shown_pages(env)
        sql += " LIMIT %d" % limit
        
        cursor.execute(sql, (category.encode('utf-8'),))
        
        mails = [Mail(env, row=row, db=db) for row in cursor]
        
        return mails
    
    @staticmethod
    def find_not_root(env):
        db = env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute(SELECT_FROM_MAILARC + " WHERE threadroot <> ''")
        mails = [Mail(env, row=row, db=db) for row in cursor]
        return mails
    
    @staticmethod
    def find_thread_mails(env, root_messageids):
        db = env.get_db_cnx()
        cursor = db.cursor()
        sql = SELECT_FROM_MAILARC + " WHERE threadroot IN (%s)" % ','.join(['%s' for x in root_messageids])
        
        env.log.debug('MailFinder.find_thread_mails: %s' % sql)
        
        cursor.execute(sql, root_messageids)
        thread_mails = [Mail(env, row=row, db=db) for row in cursor]
        return thread_mails

class MailImportHandler(Component):
    """create a ticket from an email"""

    implements(IEmailHandler)
    
    def match(self, mail):
        return true

    def invoke(self, mail, warnings):
        t ="""
        print "invoke"
        print mail.id
        print mail.messageid
        print mail.body
        print mail.mlid
        print mail.subject
        print mail.zone
        print mail.zoneoffset
        print mail.localdate
        print mail.utcdate
        print mail.fromname
        print mail.fromaddr
        print mail.thread_root
        print mail.thread_parent
        """    
        
        mail.update_or_save()

    def order(self):
        return None