# -*- coding: utf-8 -*-

import calendar
import os
import pkg_resources
import re
import time

from datetime import datetime

from trac.core import *
from trac.perm import IPermissionRequestor
from trac.resource import IResourceManager, Resource
from trac.search import ISearchSource, search_to_sql, shorten_result
from trac.ticket import Ticket
from trac.timeline import ITimelineEventProvider
from trac.util.datefmt import to_timestamp, utc
from trac.util.presentation import Paginator
from trac.util.translation import _
from trac.web.api import IRequestHandler, IRequestFilter, ITemplateStreamFilter
from trac.web.chrome import add_link, add_stylesheet, add_ctxtnav, prevnext_nav, \
                        INavigationContributor, ITemplateProvider
from trac.wiki import wiki_to_oneliner

from genshi.filters.transform import Transformer
from genshi.template import MarkupTemplate

from attachment import MailArchiveAttachment
from util import *

class MailArchiveModule(Component):
    
    implements(ITemplateProvider, IRequestFilter, ITemplateStreamFilter,
        INavigationContributor, IPermissionRequestor, IResourceManager,
        IRequestHandler)

    FIELD_XPATH = 'div[@id="ticket"]/table[@class="properties"]/td[@headers="h_%s"]/text()'
             
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('mailarchive',pkg_resources.resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
        
    def post_process_request(self, req, template, data, content_type):
        #チケット表示画面時はfilter_streamで加工できるように
        #dataに追加しておく
        if req.path_info.startswith('/ticket/'):
            ticket = data['ticket']
            if not isinstance(ticket, Ticket):
                ticket = Ticket(self.env, ticket)
            mail_id_plain = ticket['mail_id']
            mail_ids = []
            if mail_id_plain is None:
                mail_ids = []
            else:
                for mail_id in mail_id_plain.split(','):
                    try:
                        id = int(mail_id.strip())
                        mail_ids.append(id)
                    except ValueError:
                        continue
                    
            if len(mail_ids) > 0:
                data['mailarchive'] = {
                    'mail_ids': mail_ids,
                    'link': linkify_ids(self.env, req, mail_ids),
                }
        return template, data, content_type

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        if 'mailarchive' in data:
            #cssを追加
            add_stylesheet(req, 'common/css/report.css')
            add_stylesheet(req, 'mailarchive/css/mailarchive.css')
            
            #mail_idをハイパーリンクに置き換える
            link =  data['mailarchive']['link']
            stream |= Transformer(self.FIELD_XPATH % 'mail_id').replace(link)
            
            #関連メールのスレッド表示を追加する
            thread_stream = show_thread(self.env, req, data['mailarchive']['mail_ids'])
            THREAD_PATH = '//div[@id="ticket"]'
            stream |= Transformer(THREAD_PATH).after(thread_stream)
            
        return stream

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'mailarchive'

    def get_navigation_items(self, req):
        if 'MAILARCHIVE_VIEW' in req.perm('mailarchive'):
            yield ('mainnav', 'mailarchive',
                   tag.a(_('MailArchive'), href=req.href.mailarchive()))

    # IResourceManager methods
    def get_resource_realms(self):
        yield 'mailarchive'

    def get_resource_url(self, resource, href, **kwargs):
        return href.mailarchive(resource.id)
        
    def get_resource_description(self, resource, format=None, context=None,
                                 **kwargs):
        if context:
            return tag.a('mail:'+resource.id, href=context.href.mailarchive(resource.id))
        else:
            return 'mail:'+resource.id

    # IPermissionRequestor method
    def get_permission_actions(self):
        return ['MAILARCHIVE_VIEW',
                ('MAILARCHIVE_ADMIN', ['MAILARCHIVE_VIEW']),
                ]

    # IRequestHandler methods
    def match_request(self, req):
        match = re.match(r'^/mailarchive(?:/(.*))?', req.path_info)
        if match:
            if match.group(1):
                req.args['messageid'] = match.group(1)
            return 1

    def process_request(self, req):
        req.perm.assert_permission('MAILARCHIVE_VIEW')
        db = self.env.get_db_cnx()

        messageid = req.args.get('messageid', '')

        #id = req.args.get('id','')
        action = req.args.get('action', 'list')
        flatmode = (req.args.get('flatmode', 'off') == 'on')
        
        if action == 'import':
            # before import lock db , in order to avoid import twice
            self.import_unixmails(req.remote_addr,db)
            # after import unlock db
            return self._render_list(req, db, flatmode, False)
        
        elif messageid != '':
            return self._render_view(req, db, messageid)
        else:
            # did the user ask for any special report?
            return self._render_list(req, db, flatmode, False)

    def _render_view(self, req, db, id):
        data = {}
        data['action'] = 'view'

        from model import Mail
        mail = Mail(self.env, id, db=db)

        target_threadroot = mail.thread_root

        # Todo:Raise error when messsageid is wrong.

        if 'mailarc_mails' in req.session:
            self.log.debug(req.session['mailarc_mails'])
            mails = req.session['mailarc_mails'].split()
            if str(id) in mails:
                idx = mails.index(str(id))
                if idx > 0:
                    #add_ctxtnav(req, _('first'), req.href.mailarchive(mails[0]))
                    add_link(req, _('prev'), req.href.mailarchive(mails[idx - 1]))
                if idx < len(mails) - 1:
                    add_link(req, _('next'), req.href.mailarchive(mails[idx + 1]))
                    #add_ctxtnav(req, _('last'), req.href.mailarchive(mails[-1]))
                add_link(req, _('up'), req.session['mailarc_category_href'])
                prevnext_nav(req, u'メール', u'リストに戻る')

        #if target_threadroot == '':
        #    target_threadroot = messageid
        
        data['mail'] = mail
        data['related_tickets'] = get_related_tickets(self.env, req, db, mail.id)
        data['attachment'] = MailArchiveAttachment(self.env, mail.id) 
        
        return 'maildetail.html', data, None

   # Internal methods
    def _render_list(self, req, db, flatmode, month):
        target_category = req.args.get('category', '')

        data = {}

        from model import MailFinder
        data['mls'], data['name'], data['year'], data['month'], target_category \
             = MailFinder.get_categories(req, db, target_category)
        
        results = MailFinder.find_by_category(self.env, target_category.encode('utf-8'))
        
        #pagelize
        pagelized = self._pagelize_list(req, results, data)

        #Thanks http://d.hatena.ne.jp/ohgui/20090806/1249579406
        data['reversemode'] = reversemode = (req.args.get('reversemode', 'off') == 'on')
        data['flatmode'] = flatmode

        mails_per_page, cached_mails = self._get_mails_per_page(pagelized, reversemode, flatmode)

        idstext = self._collect_ids(pagelized.items, flatmode)
        
        self.log.debug("Idtext: %s" % idstext)
        
        req.session['mailarc_mails'] = idstext
        req.session['mailarc_category_href'] = get_category_href(req, target_category)

        data['mails'] = mails_per_page
        data['cached_mails'] = cached_mails

        return 'mailarchive.html', data, None
    
    def _collect_ids(self, mails, flatmode):
        if True:
            return ''.join(['%s ' % mail.id for mail in mails])
        #TODO: ツリー表示の場合に別処理を行うか？
    
    def _get_mails_per_page(self, pagelized, reversemode, flatmode):
        mails_per_page = []
        
        if flatmode:
            mails_per_page = [mail for mail in pagelized.items]
            if reversemode:
                mails_per_page.reverse()
            return mails_per_page, []
            
        else:
            #ツリー表示のため、rootだけを集める
            root_mails = []
            for mail in pagelized.items:
                root_mail = mail.get_thread_root()
                
                if root_mail in mails_per_page:
                    #ルートの場合最後に登録し直すため一度削除する
                    mails_per_page.remove(root_mail)
                mails_per_page.append(root_mail)
                
                if root_mail not in root_mails:
                    root_mails.append(root_mail)
                    
            #ルートから関連メールを全てキャッシュする
            root_messageids = [x.messageid for x in root_mails]
            from model import MailFinder
            cached_mails = MailFinder.find_thread_mails(self.env, root_messageids)
    
            if reversemode:
                mails_per_page.reverse()
            return mails_per_page, cached_mails
            
    def _pagelize_list(self, req, results, data):
        # get page from req(default page = max_page)
        page = int(req.args.get('page', '-1'))
        num_item_per_page = int(self.env.config.get('mailarchive', 'items_page','50'))
        num_shown_pages = int(self.env.config.get('mailarchive', 'shown_pages','30'))
        if page == -1:
            results_temp = Paginator(results, 0, num_item_per_page)
            page = results_temp.num_pages 

        results = Paginator(results, page - 1, num_item_per_page)
        
        pagedata = []    
        data['page_results'] = results
        shown_pages = results.get_shown_pages(num_shown_pages)
        for shown_page in shown_pages:
            page_href = req.href.mailarchive(category=req.args.get('category',None),
                                        page=shown_page, noquickjump=1)
            pagedata.append([page_href, None, str(shown_page),
                             'page ' + str(shown_page)])

        fields = ['href', 'class', 'string', 'title']
        results.shown_pages = [dict(zip(fields, p)) for p in pagedata]
        
        results.current_page = {'href': None, 'class': 'current',
                                'string': str(results.page + 1),
                                'title':None}

        if results.has_next_page:
            next_href = req.href.mailarchive(category=req.args.get('category',None),
                                        page=page + 1)
            add_link(req, 'next', next_href, _('Next Page'))

        if results.has_previous_page:
            prev_href = req.href.mailarchive(category=req.args.get('category',None),
                                        page=page - 1)
            add_link(req, 'prev', prev_href, _('Previous Page'))

        data['page_href'] = req.href.mailarchive(category=req.args.get('category',None))
        return results 
    
class Timeline(Component):
    
    implements(ITimelineEventProvider)

    # ITimelineEventProvider methods
    def get_timeline_filters(self, req):
        if 'MAILARCHIVE_VIEW' in req.perm:
            yield ('mailarchive', _(self.env.config.get('mailarchive', 'title', 'MailArchive')))

    def get_timeline_events(self, req, start, stop, filters):
        if 'mailarchive' in filters:
            add_stylesheet(req, 'mailarchive/css/mailarchive.css')

            db = self.env.get_db_cnx()
            mailarchive_realm = Resource('mailarchive')
            cursor = db.cursor()

            cursor.execute("SELECT id,category as mlname,utcdate as localdate,"
                           "fromname,fromaddr , subject  FROM mailarc "
                           "WHERE utcdate>=%s AND utcdate<=%s ",
                           (to_timestamp(start), to_timestamp(stop)))
            for id,category,localdate, fromname, fromaddr,subject in cursor:
                #if 'WIKI_VIEW' not in req.perm('wiki', name):
                #    continue
                author = get_author(fromname,fromaddr)
                #ctx = context('mailarchive', id)
                
                resource = mailarchive_realm(id=id,version=None)
                if 'MAILARCHIVE_VIEW' not in req.perm(resource):
                    continue
                yield ('mailarchive',
                       datetime.fromtimestamp(localdate, utc),
                       author or '--',
                       (resource,(category,author,subject)))


    def render_timeline_event(self, context, field, event):
        mailarchive_page,(category,author,subject) = event[3]
        if field == 'url':
            return context.href.mailarchive(mailarchive_page.id, version=mailarchive_page.version)
        elif field == 'title':
            markup = tag(u'メールが ',category,u'に送信されました')
            return markup
        elif field == 'description':
            markup = tag(subject)
            return markup
    
class SearchProvider(Component):
    
    implements(ISearchSource)

    # ISearchProvider methods
    def get_search_filters(self, req):
        if 'MAILARCHIVE_VIEW' in req.perm:
            yield ('mailarchive', self.env.config.get('mailarchive', 'title', 'MailArchive'))

    def get_search_results(self, req, terms, filters):
        if 'mailarchive' in filters:
            db = self.env.get_db_cnx()
            sql_query, args = search_to_sql(db,
                                             ['m1.messageid', 'm1.subject', 'm1.fromname', 'm1.fromaddr', 'm1.text'],
                                             terms)
            cursor = db.cursor()
            cursor.execute("SELECT m1.id, m1.subject, m1.fromname, m1.fromaddr, m1.text, m1.utcdate as localdate "
                           "FROM mailarc m1 "
                           "WHERE "
                           "" + sql_query, args)
            mailarchive_realm = Resource('mailarchive')

            for id,subject,fromname,fromaddr, text,localdate in cursor:
                resource = mailarchive_realm(id=id,version=None)
                if 'MAILARCHIVE_VIEW' not in req.perm(resource):
                    continue

                yield (req.href.mailarchive(id),
                       subject,
                       datetime.fromtimestamp(localdate, utc),
                       get_author(fromname,fromaddr),
                       shorten_result(text, terms))