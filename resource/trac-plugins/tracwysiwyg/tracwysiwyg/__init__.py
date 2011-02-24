# -*- coding: utf-8 -*-

import re

from trac.core import Component, implements
from trac.config import ListOption
from trac.ticket.web_ui import TicketModule
from trac.web.api import IRequestFilter
from trac.web.chrome import ITemplateProvider, add_link, add_stylesheet, add_script, add_script_data
from trac.web.href import Href


__all__ = ['WysiwygModule']


class WysiwygModule(Component):
    implements(ITemplateProvider, IRequestFilter)

    wysiwyg_stylesheets = ListOption('tracwysiwyg', 'wysiwyg_stylesheets',
            doc="""Add stylesheets to the WYSIWYG editor""")

    # ITemplateProvider#get_htdocs_dirs
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('tracwysiwyg', resource_filename(__name__, 'htdocs'))]

    # ITemplateProvider#get_templates_dirs
    def get_templates_dirs(self):
        return []

    # IRequestFilter#pre_process_request
    def pre_process_request(self, req, handler):
        return handler

    # IRequestFilter#post_process_request
    def post_process_request(self, req, template, data, content_type):
        if not (req.args.get('action', None)=="edit" or req.path_info.startswith(r'/newticket') or req.path_info.startswith(r'/ticket/')):
            return (template, data, content_type)
        options = {}
        options['escapeNewlines'] = False
        if template == 'ticket.html':
            options['escapeNewlines'] = TicketModule(self.env).must_preserve_newlines

        if options:
            add_script_data(req, { '_tracwysiwyg': options })

        add_link(req, 'tracwysiwyg.base', req.href() or '/')
        stylesheets = ['chrome/common/css/trac.css', 'chrome/tracwysiwyg/editor.css']
        stylesheets += self.wysiwyg_stylesheets
        for stylesheet in stylesheets:
            add_link(req, 'tracwysiwyg.stylesheet', _expand_filename(req, stylesheet))
        add_stylesheet(req, 'tracwysiwyg/wysiwyg.css')
        add_script(req, 'tracwysiwyg/wysiwyg.js')
        add_script(req, 'tracwysiwyg/wysiwyg-load.js')

        return (template, data, content_type)


def _expand_filename(req, filename):
    if filename.startswith('chrome/common/') and 'htdocs_location' in req.chrome:
        href = Href(req.chrome['htdocs_location'])
        return href(filename[14:])
    if filename.startswith('/') or re.match(r'https?://', filename):
        href = Href(filename)
        return href()
    return req.href(filename)


