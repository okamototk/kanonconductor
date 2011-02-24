# -*- coding: utf-8 -*-

from trac import util
from trac.core import *
from trac.wiki import IWikiSyntaxProvider

class WikiSyntaxMail(Component):
    
    implements(IWikiSyntaxProvider)

    # IWikiSyntaxProvider
    def get_link_resolvers(self):
        return [('mail', self._format_link)]

    def get_wiki_syntax(self):
        yield (r"!?\mail:([0-9]+)", # mail:123
               lambda x, y, z: self._format_link(x, 'mail', y[5:], y))

    def _format_link(self, formatter, ns, target, label):
        cursor = formatter.db.cursor()
        cursor.execute("SELECT subject,id FROM mailarc WHERE id = %s" , (target,))
        row = cursor.fetchone()
        if row:
            subject = util.escape(util.shorten_line(row[0]))
            return '<a href="%s" title="%s">%s</a>' \
                   % (formatter.href.mailarchive(row[1]), subject, label)
        else:
            return label

class WikiSyntaxMl(Component):
    
    implements(IWikiSyntaxProvider)

    # IWikiSyntaxProvider
    def get_link_resolvers(self):
        return [('ml', self._format_link)]

    def get_wiki_syntax(self):
        yield (r"!?\[(.+?)[ :]([0-9]+)\]", # [xxx 123] or [aaa:123]
               lambda x, y, z: self._format_link(x, 'ml', y[1:1], y))

    def _format_link(self, formatter, ns, target, label):
        cursor = formatter.db.cursor()
        cursor.execute("SELECT subject,id FROM mailarc WHERE subject like '%s%%'" % label)
        row = cursor.fetchone()
        if row:
            subject = util.escape(util.shorten_line(row[0]))
            return '<a href="%s" title="%s">%s</a>' \
                   % (formatter.href.mailarchive(row[1]), subject, label)
        else:
            return label

class WikiSyntaxMessageId(Component):
    
    implements(IWikiSyntaxProvider)

    # IWikiSyntaxProvider
    def get_link_resolvers(self):
        return [('messageid', self._format_link)]

    def get_wiki_syntax(self):
        yield (r"!?Message-ID:<(.+?)>", # Message-ID:<aaa>
               lambda x, y, z: self._format_link(x, 'messageid' ,y[12:-1],y))

    def _format_link(self, formatter, ns, target, label):
        cursor = formatter.db.cursor()
        cursor.execute("SELECT subject,id FROM mailarc WHERE messageid = %s" , (target,))
        row = cursor.fetchone()
        if row:
            subject = util.escape(util.shorten_line(row[0]))
            return '<a href="%s" title="%s">%s</a>' \
                   % (formatter.href.mailarchive(row[1]), subject, label)
        else:
            return label

