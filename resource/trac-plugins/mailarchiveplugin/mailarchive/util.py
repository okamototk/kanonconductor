# -*- coding: utf-8 -*-

import re
import sys

from trac.resource import ResourceNotFound
from trac.ticket.model import Ticket
from trac.util.compat import set
from trac.util.text import console_print
from trac.web.chrome import Chrome

from genshi.builder import tag
from genshi.template.markup import MarkupTemplate

def linkify_ids(env, req, ids):
    if len(ids) == 0 or ids[0] == '':
        return tag.span()
    
    from model import Mail
    data = []
    for id in sorted(ids, key=lambda x: int(x)):
        try:
            mail = Mail(env, id)
            data.append(tag.a('mail:%s'%mail.id,
                               href=req.href.mailarchive(mail.id),
                               class_='ticket',
                               title='%s %s %s' % (mail.get_fromtext(), mail.get_senddate(), mail.subject)))
        except ResourceNotFound:
            data.append('%s'%id)
        data.append(', ')
    if data:
        del data[-1] # Remove the last comma if needed
    return tag.span(*data)

def get_author(fromname, fromaddr):
    author = fromname
    if fromname == '':
        if re.match('(.+?)@', fromaddr):
            author = re.match('(.+?)@', fromaddr).group(1)
    if author == None or author.strip() == '':
        author = '--'
    return author

def get_related_tickets(env, req, db, id):
    # cached?
    if not hasattr(req, '_related_tikects'):
        cursor = db.cursor()
        
        sql = """SELECT ticket, value
        FROM ticket_custom
        WHERE name='mail_id' AND value <> ''"""
        
        cursor.execute(sql)
        related_tickets = [(ticket_id, [int(x) for x in mail_ids.split(',') if x != '']) for ticket_id, mail_ids in cursor]
        
        req._related_tikects = related_tickets
        
    related_tickets = req._related_tikects
    tickets = []
    for ticket_id, mail_ids in related_tickets:
        if int(id) in mail_ids:
            tickets.append(Ticket(env, ticket_id))
        
    return tickets

def show_thread(env, req, mail_ids):
    from model import Mail
    mails = [Mail(env, mail_id) for mail_id in mail_ids]
    
    template = MarkupTemplate("""
    <div xmlns:py="http://genshi.edgewall.org/">
 
    <script type="text/javascript" src="${req.chrome.htdocs_location}js/folding.js"></script>
    <script type="text/javascript">
      jQuery(document).ready(function($) {
        $("fieldset legend.foldable").enableFolding(false);
        /* Hide the filters for saved queries. */
        $(".options").toggleClass("collapsed");
      });
    </script>    
    
    <py:def function="show_thread(mail, cached_mails)">
    <li class="thread_li">
    <py:choose>
      <a py:when="mail.has_attachments(req)" class="thread_subject_clip"
        href="${req.href.mailarchive(mail.id)}">[$mail.id] ${mail.get_subject()}</a>
      <a py:otherwise=""
        href="${req.href.mailarchive(mail.id)}">[$mail.id] ${mail.get_subject()}</a>
      <py:with vars="related_tickets=mail.get_related_tickets(req);">
        <py:if test="len(related_tickets) > 0">
          <span class="related_tickets">
            --- (関連チケット: 
            <py:for each="ticket in related_tickets">
              <a href="${req.href.ticket(ticket.id)}">#${ticket.id}</a>&nbsp;
            </py:for>
            )
          </span>
        </py:if> 
      </py:with>
    </py:choose>
    <br />
    <span class="thread_from">${mail.get_fromtext()}</span>
    <span class="thread_senddate">${mail.get_senddate()}</span>

    <py:for each="child in mail.get_children(cached_mails=cached_mails)">
      <ul class="thread_ul">
        ${show_thread(child, cached_mails)}
      </ul>
    </py:for>
  </li>
  </py:def>

  <h2>関連メール</h2>
  <div id="mail_threads">
    <py:for each="mail in mails">
      <fieldset class="options">
        <legend class="foldable" style="! important">[${mail.id}] ${mail.subject}</legend>
        <span class="thread_from">${mail.get_fromtext()}</span>
        <span class="thread_senddate">${mail.get_senddate()}</span>
        <div id="mail_thread">
          <ul class="thread_ul">
            ${show_thread(mail.get_thread_root(), mail.get_thread_mails())}
          </ul>
        </div>
      </fieldset>
    </py:for>
  </div>
  </div>""")
    return template.generate(mails=mails, req=req)

def get_category_href(req, category):
    return req.href.mailarchive() + '?category=%s' % category

def get_item_per_page(env):
    return int(env.config.get('mailarchive', 'items_page','50'))

def get_num_shown_pages(env):
    return int(env.config.get('mailarchive', 'shown_pages','30'))

def month_add(year, month, add_month):
    month = month + add_month
    while month >12 or month <1:
        if month > 12:
            month = month - 12
            year = year + 1
        else :
            month = month + 12
            year = year - 1
        
def is_empty(str):
    return str == None or str.strip() == ''
    
def printout(*args):
    console_print(sys.stdout, *args)

def printerr(*args):
    console_print(sys.stderr, *args)
    
class Logger:
    
    def __init__(self, env):
        try:
            self.log = env.log
        except AttributeError:
            self.log = None
            
    def debug(self, *args):
        if self.log:
            self.log.debug(*args)
        else:
            printout(*args)
            
    def info(self, *args):
        if self.log:
            self.log.info(*args)
        else:
            printout(*args)
            
    def warn(self, *args):
        if self.log:
            self.log.warn(*args)
        else:
            printout(*args)
    
    def error(self, *args):
        if self.log:
            self.log.error(*args)
        else:
            printerr(*args)
        

