# -*- coding: utf-8 -*-

from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.util.text import to_unicode,unicode_quote
from trac.web.chrome import add_link,add_script, add_stylesheet, INavigationContributor, ITemplateProvider

import os
import pkg_resources
from datetime import tzinfo, timedelta, datetime

from trac.ticket.api import TicketSystem
from trac.ticket.query import Query, QuerySyntaxError
from trac.util.datefmt import parse_date,to_datetime,format_date,to_timestamp
from trac.util.translation import _

from genshi.builder import tag


class Macro(Component):
    implements(IWikiMacroProvider,ITemplateProvider)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [('querychart',
                 pkg_resources.resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]


    # IWikiMacroProvider methods

    def get_macros(self):
        yield 'QueryChart'

    def get_macro_description(self, name):
        return '''
Draw Chart from Query.
{{{

 {{{
[[QueryChart(args1,args2,...)]]
 }}}

args:

 * query: Search condition of ticket. The following three kinds of can be described.
   * [http://trac.edgewall.org/wiki/TracQuery#QueryLanguage Query language] notation of TicketQuery macro:[[BR]]
     Write the condition without applying ? to the head. 
     Refer to the [http://trac.edgewall.org/wiki/TracQuery#QueryLanguage Query language] for details.[[BR]]
     !query:status=new|assigned&version;^=1.0
   * Notation displayed in URL with custom query:[[BR]]
     Write conditions delimited by & applying ? (Without forgetting :) to the head as follows. It might be 
     good to put the part of URL specifying the condition on the screen of custom query.[[BR]]
     !query:?status=new&status;=assigned&version;=^1.0
   * Omitte:[[BR]]
     It is possible to omit it only when putting it on the column the explanation of the report made from 
     custom query (which displayed in address field of a browser). It becomes a search condition specified the 
     omission on the screen. Please omit this item (query:...) when omitting it.
 * col: Targeted item. Please describe by col=xxx, col=yyy, and switching off the comma district when you 
   specify the plural. The item name can specify both the field name (name of the field in Trac) and the label 
   (displayed item name).
 * per:(=day,week,free) Unit of total. Default is week.
 * start: Day in left end of graph. If it is unspecification, it is the most past day of the ticket. yyyy/mm/dd form
 * end: Day on right edge in graph. If it is unspecification, it is the most recent day of the ticket. yyyy/mm/dd form
 * width: Width in graph. It specifies it by the unit of px. If it is unspecification, it is 536px.
 * height: Height of graph. It specifies it by the unit of px. If it is unspecification,    [[BR]]it is 300px.
 * upper: The improvement chart is written (bug settling curve etc.). Down chart when not specifying it.
}}}
'''


    def _urlstring_to_reqarg(self,urlstr):
        args={}
        for uslarg in urlstr[1:].split('&'):
            uslarg_sp = uslarg.split('=')
            key = uslarg_sp[0]
            val = '='.join(uslarg_sp[1:])
            if len(val)>1 and val[0] in ['~','^','$','!']:
                if val[0] == '!':
                    args[key+'_mode']=val[:1]
                    val = val[2:]
                else:
                    args[key+'_mode']=val[0]
                    val = val[1:]
            if not args.get(key):
                args[key] = []
            args[key].append(val)
        return args
    
    def _get_constraints(self, args):
            
        constraints = {}
        ticket_fields = [f['name'] for f in
                         TicketSystem(self.env).get_ticket_fields()]
        ticket_fields.append('id')

        for field in [k for k in args.keys() if k in ticket_fields]:
            vals = args[field]
            if not isinstance(vals, (list, tuple)):
                vals = [vals]
            if vals:
                mode = args.get(field + '_mode')
                if mode:
                    vals = [mode + x for x in vals]
                constraints[field] = vals

        return constraints


    def _make_data(self,req,opts):
        arg_x_min = opts['start']
        arg_x_max = opts['end']
        per = opts['per']
        query_str = opts['query']
        fieldlist = opts['col']
        upper = opts['upper']
        
        if len(query_str)>1 and query_str[0]!='?':
            query_str = query_str + ''.join(['&col=%s'%field
                                             for field in fieldlist])
            query = Query.from_string(self.env, query_str)
        elif len(query_str)>1 and query_str[0]=='?':
            constraints = self._get_constraints(self._urlstring_to_reqarg(query_str))
            query = Query(self.env, constraints=constraints, cols=fieldlist)
        else:
            constraints = self._get_constraints(req.args)
            query = Query(self.env, constraints=constraints, cols=fieldlist)
                          
        self.log.debug(query.get_sql())
        result = query.execute(req, db=None, cached_ids=None)
        result_len = len(result)
        daylists = []
        edgedays = []
        for fieldname in fieldlist:
            daylist =[]
            dayids = {}
            for ticket in result:
                try:
                    dtin = ticket[fieldname]

                    # parse date
                    if isinstance(dtin, (str,unicode)):
                        dt = parse_date(dtin)
                    else:
                        dt = to_datetime(dtin)
                except:
                    continue

                d = datetime(dt.year,dt.month,dt.day,tzinfo=req.tz)
                daylist.append(d)


            daylists.append( (daylist,dayids) )

            if len(daylist)>0 :
                edgedays.append(min(daylist))
                edgedays.append(max(daylist))

        if len(edgedays)==0:
            return None#'''No data to output.'''

        x_min = arg_x_min or min(edgedays)
        x_max = arg_x_max or max(edgedays)
        x_min = datetime(x_min.year,x_min.month,x_min.day,tzinfo=x_min.tzinfo)
        x_max = datetime(x_max.year,x_max.month,x_max.day,tzinfo=x_max.tzinfo)

        if per=='week':
            x_axis = [x_min+timedelta(x)
                      for x in range(0,(x_max-x_min).days+7,7)]
            x_max = x_axis[-1] # As x_axis[-1] may be larger than x_max.
        else: #'day','free'
            x_axis = [x_min+timedelta(x)
                      for x in range(0,(x_max-x_min).days+1)]

        counts={}
        linenum = 0
        for daylist,dayids in daylists:
            for x in x_axis:
                
                count = len([1 for c in daylist if c <= x])
                #ids = [dayids[c] for c in daylist if c <= x and c>last_x ]
                #points.append(Point(x,count))
                if not upper:
                    count = result_len - count
                counts[(x,linenum)] = count
            linenum += 1


        return {'x_axis':x_axis,
                'counts':counts,
                'linenum':linenum,
                'x_min':x_min,
                'x_max':x_max,
                'fieldlist':fieldlist,
                'result_len':result_len}

        
    def expand_macro(self, formatter, name, content):
        req = formatter.req
        if not hasattr(req, '_querychart'):
            add_script(req, 'querychart/js/flot/excanvas.pack.js')
            add_script(req, 'querychart/js/flot/jquery.flot.pack.js')
            add_script(req, 'querychart/js/querychart.js')
            req._querychart = 0
        else:
            req._querychart = req._querychart+1

        #context = formatter.context
        opts = {
               'width':'536',
               'height':'300',
               'end':None,
               'start':None,
               'query':'',
               'col':[],
               'per':'week',
               'upper':False
               }
        collabel={}
        ticket_fields = TicketSystem(self.env).get_ticket_fields()

        for arg in content.split(','):
            colon_split = arg.split(':')
            key = colon_split[0]
            value = ''
            if len(colon_split)>1:
                value = ':'.join(colon_split[1:])
            else:
                value = True
            if key=='col':
                if value=='time':
                    opts[key].append('time')
                    collabel['time'] = _('Created')
                elif value=='changetime':
                    opts[key].append('changetime')
                    collabel['changetime'] = _('Modified')
                else:
                    for f in ticket_fields:
                        if f['name'] == value or f['label'] == value:
                            opts[key].append(f['name'])
                            collabel[f['name']] = f['label']
                            break

            elif key in ['start','end']:
                opts[key]= parse_date(value)
            else:
                opts[key] = value


        
        data = self._make_data(req,opts)
        if data==None:
            raise TracError('No data matched')
        fieldlist = data['fieldlist']
        x_axis = data['x_axis']
        counts = data['counts']
        linenum = data['linenum']
        result_len = data['result_len']


        table = tag.table(class_="listing reports",
                          id="querycharttable_%d"%(req._querychart),
                          style="display:none")
        tr = tag.tr(tag.th('Field'),
                    tag.th('Date'),
                    tag.th('Count'))
        #for field in fieldlist:
        #    tr.append(tag.th(field))
        table.append(tag.thead(tr))

        for i in range(0,linenum):
            for x in x_axis:
                tr = tag.tr(tag.td(collabel[fieldlist[i]]),
                            tag.td(format_date(x)),
                            tag.td(counts[(x,i)])
                            )
                table.append(tr)

        opttag = tag.div(id="querychartopt_%d"%(req._querychart),
                         style="display:none")

        for opt in opts:
            opttag.append(tag.span(opts[opt],class_=opt))

        div = tag.div(
                      tag.div(' ',
                              id="placeholder_%d"%(req._querychart),
                              style="width:%spx;height:%spx;"%
                              (opts["width"],opts["height"])),
                      opttag,
                      table,
                      class_="querychart",
                      id="querychart_%d"%(req._querychart)
                      )
        return div




