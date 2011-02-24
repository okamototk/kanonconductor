from trac.core import *
from trac.web.api import IRequestFilter, IRequestHandler, ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, add_script, add_stylesheet
from trac.ticket.api import ITicketManipulator
from trac.config import Option, IntOption, BoolOption, ListOption

from genshi.builder import tag
from genshi.filters.transform import Transformer

import time
from traceback import format_exc
import re

class DateFieldModule(Component):
    """A module providing a JS date picker for custom fields."""
    
    date_format = Option('datefield', 'format', default='dmy',
        doc='The format to use for dates. Valid values are dmy, mdy, and ymd.')
    first_day = IntOption('datefield', 'first_day', default=0,
        doc='First day of the week. 0 == Sunday.')
    date_sep = Option('datefield', 'separator', default='/',
        doc='The separator character to use for dates.')
    show_week = BoolOption('datefield', 'weeknumbers', default='false',
        doc='Show ISO8601 week number in calendar?')
    show_panel = BoolOption('datefield', 'panel', default='false',
        doc='Show button panel at bottom? (Today, Done)')
    change_month = BoolOption('datefield', 'change_month', default='false',
        doc='Show a month dropdown in datepicker?')
    change_year = BoolOption('datefield', 'change_year', default='false',
        doc='Show a year dropdown in datepicker?')
    num_months = IntOption('datefield', 'months', default='1',
        doc='Number of months visible in datepicker')
    match_req = ListOption('datefield', 'match_request', default='',
        doc='Additional request paths to match (use input class="datepick")')
    use_milestone = BoolOption('datefield', 'milestone', default='false',
        doc="""Use datepicker for milestone due/completed fields? 
        If you turn this on, you must use MM/DD/YYYY for the date format.
        Set format to mdy and separator to / (default=Off)""")

    implements(IRequestFilter, IRequestHandler, ITemplateProvider, \
            ITicketManipulator, ITemplateStreamFilter)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/datefield')

    def process_request(self, req):
        # Use get to handle default format
        format = { 
            'dmy': 'dd%smm%syy',
            'mdy': 'mm%sdd%syy',
            'ymd': 'yy%smm%sdd' 
        }.get(self.date_format, 'dd%smm%syy')%(self.date_sep, self.date_sep)

        data = {}
        data['calendar'] = req.href.chrome('common', 'ics.png')
        data['format'] = format
        data['first_day'] = self.first_day
        data['show_week'] = self.show_week
        data['show_panel'] = self.show_panel
        data['change_month'] = self.change_month
        data['change_year'] = self.change_year
        data['num_months'] = self.num_months
        return 'datefield.html', {'data': data},'text/javascript' 

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        def attr_callback(name, event):
            attrs = event[1][1]
            return ' '.join(filter(None, (attrs.get('class'), 'datepick')))
        if filename == 'ticket.html':
            for field in list(self._date_fields()):
                stream = stream | Transformer(
                    '//input[@name="field_' + field + '"]'
                ).attr('class', attr_callback)
        elif self.use_milestone and filename in ('milestone_edit.html', 
                'admin_milestones.html'):
            for field in ('duedate', 'completeddate'):
                stream = stream | Transformer(
                    '//input[@name="' + field + '"]'
                ).attr('class', attr_callback)
        return stream
    
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
            
    def post_process_request(self, req, template, data, content_type):
        mine = ['/newticket', '/ticket', '/simpleticket']
        if self.use_milestone:
            mine.append('/milestone')
            mine.append('/admin/ticket/milestones')

        match = False
        for target in mine + self.match_req:
            if req.path_info.startswith(target):
                match = True
                break

        if match:
            add_script(req, 'datefield/js/jquery-ui.js')
            add_script(req, 'datefield/js/i18n/ui.datepicker-ja.js')
            # virtual script
            add_script(req, '/datefield/datefield.js')
            add_stylesheet(req, 'datefield/css/jquery-ui.css')
            add_stylesheet(req, 'datefield/css/ui.datepicker.css')
        return template, data, content_type
        
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('datefield', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
        
    # ITicketManipulator methods
    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket): # dmy mdy ymd
        for field in self._date_fields():
            try:
                val = (ticket[field] or u'').strip()
                
                if not val and self.config['ticket-custom'].getbool(field+'.date_empty', default=False):
                    continue
                if self.date_sep and len(self.date_sep.strip()) > 0:
                    if len(val.split(self.date_sep)) != 3:
                        raise Exception # Token exception to force failure
                else:
                    if re.match('.*[^\d].*', val.strip()):
                        raise Exception
                    
                format = self.date_sep.join(['%'+c for c in self.date_format])     
                try:
                    time.strptime(val, format)
                except ValueError:
                    time.strptime(val, format.replace('y', 'Y'))
            except Exception:
                self.log.warn('DateFieldModule: Got an exception, assuming it is a validation failure.\n'+format_exc())
                yield field, 'Field %s does not seem to look like a date. The correct format is %s.' % \
                             (field, self.date_sep.join([c.upper()*(c=='y' and 4 or 2) for c in self.date_format]))
                
                
        
    # Internal methods
    def _date_fields(self):
        # XXX: Will this work when there is no ticket-custom section? <NPK>
        for key, value in self.config['ticket-custom'].options():
            if key.endswith('.date'):
                yield key.split('.', 1)[0]
    


class CustomFieldAdminTweak(Component):
    implements(ITemplateStreamFilter, IRequestFilter)

    def pre_process_request(self, req, handler):
        if req.method == "POST" and req.href.endswith(u"/admin/ticket/customfields"):
            if req.args.get('type') == 'date':
                req.args['type'] = 'text'
                self.config.set('ticket-custom', '%s.date'%(req.args.get('name')), 'true')
                self.config.set('ticket-custom', '%s.date_empty'%(req.args.get('name')), req.args.get('date_empty', 'false'))
        return handler

    def post_process_request(self, template, content_type):
        return (template, content_type)

    def filter_stream(self, req, method, filename, stream, data):
        if filename == "customfieldadmin.html":
            add_script(req, 'datefield/js/customfield-admin.js')
            add_stylesheet(req, 'datefield/css/customfield-admin.css')
            stream = stream | Transformer('.//select[@id="type"]').append(
                tag.option('Date', value='date', id="date_type_option")
            )
            stream = stream | Transformer(
                './/form[@id="addcf"]/fieldset/div[@class="buttons"]'
            ).before(
                tag.div(
                    tag.input(
                        id="date_empty", 
                        type="checkbox", 
                        name="date_empty"
                    ), 
                    tag.label('空の日付を許可'), 
                    for_="date_empty", 
                    class_="field",
                    id="date_empty_option"
                )
            )
        return stream
