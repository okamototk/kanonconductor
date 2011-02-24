# -*- coding: utf-8 -*-
"""
= !TracNav: The Navigation Bar for Trac =

This macro implements a fully customizable navigation bar for the Trac
wiki engine. The contents of the navigation bar is a wiki page itself
and can be edited like any other wiki page through the web
interface. The navigation bar supports hierarchical ordering of
topics. The design of !TracNav mimics the design of the !TracGuideToc
that was originally supplied with Trac. The drawback of !TracGuideToc
is that it is not customizable without editing its source code and
that it does not support hierarchical ordering.

== Installation ==

See http://trac.edgewall.org/wiki/TracPlugins.

== Usage ==

To use !TracNav, create an index page for your site and call the
TracNav macro on each page, where the navigation bar should be
displayed. The index page is a regular wiki page. The page with the
table of contents must include an unordered list of links that should
be displayed in the navigation bar.

To display the navigation bar on a page, you must call the !TracNav
macro on that page an pass the name of your table of contents as
argument.

== Additional information and a life example ==

Please visit: http://svn.ipd.uka.de/trac/javaparty/wiki/TracNav.

== Author and License ==

 * Copyright 2005-2006, Bernhard Haumacher (haui at haumacher.de)
 * Copyright 2005-2008, Thomas Moschny (thomas.moschny at gmx.de)

{{{
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
}}}

"""
__id__        = '$Id: tracnav.py 3275 2008-11-09 12:44:09Z moschny $'
__revision__  = '$LastChangedRevision: 3275 $'

import re
from trac.core import Component, implements
from trac.wiki.api import WikiSystem, IWikiMacroProvider
from trac.web.chrome import ITemplateProvider, add_stylesheet
from trac.wiki.model import WikiPage
from trac.wiki.formatter import Formatter, OneLinerFormatter
from trac.util.html import Markup
from genshi.builder import tag
from StringIO import StringIO


TRACNAVHOME = "http://svn.ipd.uka.de/trac/javaparty/wiki/TracNav"
LISTRULE = re.compile(r"^(?P<indent>[ \t\v]+)\* +(?P<rest>.*)$", re.M)

# Python 2.4 compatibility
def _partition(s, c):
    i = s.find(c)
    if i >= 0:
        return s[:i], s[i+len(c):]
    else:
        return s, ''

class TocFormatter(OneLinerFormatter):
    """
    Basically the OneLinerFormatter, but additionally remembers the
    last wiki link.
    """
    def __init__(self, env, ctx, allowed_macros=[]):
        OneLinerFormatter.__init__(self, env, ctx)
        self.lastlink = None
        self.allowed_macros = allowed_macros

    def format_toc(self, wikitext):
        self.lastlink = None
        out = StringIO()
        OneLinerFormatter.format(self, wikitext, out)
        return out.getvalue(), self.lastlink

    def _make_link(self, namespace, target, *args):
        if namespace == 'wiki':
            self.lastlink = target
        return OneLinerFormatter._make_link(
            self, namespace, target, *args)

    def _macro_formatter(self, match, fullmatch):
        name = fullmatch.group('macroname')
        if name in self.allowed_macros:
            # leapfrog the OneLinerFormatter
            return Formatter._macro_formatter(self, match, fullmatch)
        else:
            # use the OneLinerFormatter
            return OneLinerFormatter._macro_formatter(self, match, fullmatch)

    # FIXME: what about _make_relative_link() ?
    # FIXME: CamelCase links are special and not handled by the Formatter...


class Invocation(object):

    def __init__(self, formatter, args):

        # shortcuts
        self.env = formatter.env
        self.req = formatter.req
        self.ctx = formatter.context

        # needed several times
        self.preview = self.req.args.get('preview', '')
        self.curpage = self.req.args.get('page', 'WikiStart')
        self.modify = self.req.perm.has_permission('WIKI_MODIFY')

        # parse arguments
        self.names = []
        self.collapse = True
        self.reorder = True
        self.allowed_macros = 'Image'
        if args:
            for arg, values in map(lambda s: _partition(s, '='), args.split('|')):
                arg = arg.strip()
                if arg == 'nocollapse':
                    self.collapse = False
                elif arg == 'noedit':
                    self.modify = False
                elif arg == 'noreorder':
                    self.reorder = False
                elif arg == 'allowed_macros':
                    self.allowed_macros = map(lambda s: s.strip(), values.split(','))
                else:
                    self.names.append(arg)

    def get_toc(self, name):
        """
        Fetch the wiki page containing the toc, if available.
        """
        if self.preview and name == self.curpage:
            return self.req.args.get('text', '')
        elif WikiSystem(self.env).has_page(name):
            return WikiPage(self.env, name).text
        else:
            return ''

    def get_toc_entry(self, toc_text):
        """
        Parse and format the entries in toc_text.
        """
        formatter = TocFormatter(self.env, self.ctx, self.allowed_macros)
        for match in LISTRULE.finditer(toc_text):
            indent = len(match.group('indent'))
            label, link = formatter.format_toc(match.group('rest'))
            yield indent, link, label

    def get_toc_entry_and_indent(self, gen):
        """
        Filter for get_toc_entry().  The first call to next() returns the
        indentation level of the next entry (or -1 if there are no more
        entries) and the second call returns the entry itself.
        """
        while True:
            try:
                indent, link, label = gen.next()
            except StopIteration:
                yield -1
                return
            yield indent
            yield link, label

    def _parse_toc(self, gen, next_indent, level = 0):
        """
        Construct the toc tree at the given level.
        """
        toclist = []
        if next_indent > level:
            sublist, next_indent = self._parse_toc(gen, next_indent, level + 1)
            if next_indent < level: # level is empty
                return sublist, next_indent
            else:                   # broken indentation structure
                toclist.append((None, None, sublist))
        while True:
            if next_indent == level:
                (link, label), next_indent = gen.next(), gen.next()
                if next_indent > level:
                    sublist, next_indent = self._parse_toc(gen, next_indent, level + 1)
                    toclist.append((link, label, sublist))
                else:
                    toclist.append((link, label, None))
            else:
                assert next_indent < level
                return toclist, next_indent

    def parse_toc(self, toc_text):
        """
        Recursively construct the toc tree using _parse_toc().
        """
        gen = self.get_toc_entry_and_indent(self.get_toc_entry(toc_text))
        toc, _ = self._parse_toc(gen, gen.next())
        return toc

    def run(self):
        """
        Main routine of the wiki macro.
        """
        out = tag.div(class_="wiki-toc trac-nav")

        # header
        out.append(tag.h2(tag.a("TracNav", href=TRACNAVHOME)))

        # add TOCs
        for name in (self.names or ["TOC"]):
            toc = self.parse_toc(self.get_toc(name))
            if not toc:
                toc = self.parse_toc(' * TOC "%s" is empty!' % name)
            found, filtered = self.filter_toc(toc)
            if (not self.collapse) or (not found):
                self.display_all(name, toc, out)
            else:
                self.display_all(name, filtered, out)

        # add our stylesheet
        add_stylesheet(self.req, 'tracnav/css/tracnav.css')

        # done
        return out

    def filter_toc(self, toc, level = 0, found = False):
        result = []
        for name, title, sub in toc:
            foundhere = name == self.curpage
            if sub is not None:
                foundhere, sub = self.filter_toc(sub, level + 1, foundhere)
                if not (foundhere or name is None):
                    sub = []
            if self.reorder and level is 0 and foundhere:
                result.insert(0, (name, title, sub))
            else:
                result.append((name, title, sub))
            found |= foundhere
        return found, result

    def display_all(self, name, toc, out):
        if (not self.preview) and self.modify:
            out.append(tag.div(
                    tag.a("edit", href="%s?action=edit" % self.req.href.wiki(name)),
                    class_="edit"))
        out.append(self.display(toc, tag.ul()))

    def display(self, toc, ul):
        for name, title, sub in toc:
            if sub == None:
                ul.append(tag.li(
                        Markup(title),
                        class_= (name == self.curpage) and "active" or None))
            else:
                show_dots = not (name == None or sub)
                ul.append(tag.li(
                        tag.h4(Markup(title), show_dots and "..." or None)))
                if len(sub) > 0:
                    ul.append(self.display(sub, tag.ul()))
        return ul


class TracNav(Component):

    implements(IWikiMacroProvider, ITemplateProvider)

    def get_macros(self):
        yield 'TracNav'
        yield 'JPNav' # legacy

    def expand_macro(self, formatter, name, args):
        return Invocation(formatter, args).run()

    def get_macro_description(self, name):
        from inspect import getdoc, getmodule
        return getdoc(getmodule(self))

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('tracnav', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [] # we don't provide templates
