# -*- coding: utf-8 -*-
from pkg_resources import resource_filename
import re
import time
from datetime import datetime
import dbhelper
from usermanual import *
from trac.log import logger_factory
from trac.core import *
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.chrome import add_stylesheet, add_script, add_warning,\
     INavigationContributor, ITemplateProvider
from trac.web.href import Href
from reportmanager import CustomReportManager
from statuses import get_statuses
import trac.util.datefmt
import reports

class WorkTimeEntryPage(Component):
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    def __init__(self):
        pass

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        val = re.search('/worktime$', req.path_info)
        if val and val.start() == 0:
            return "worktime"
        else:
            return ""

    def get_navigation_items(self, req):
        url = req.href.worktime()
        if req.perm.has_permission("TICKET_MODIFY"):
            yield 'mainnav', "worktime", \
                  Markup('<a href="%s">%s</a>' % \
                         (req.href('worktime') , u'作業時間入力'))

    def process_request(self, req):
        db = self.env.get_db_cnx()
        cursor = db.cursor()

        errors = []
        if req.method == 'POST':
            params = {}
            for param in req.args.keys():
                try:
                    property, id = param.split('_')
                    p = None
                    try:
                        p = params[id]
                    except KeyError:
                        p = params[id] = {}
                    p[property]=req.args.get(param)
                    if p[property]=='':
                        continue
                    if property=='totalhours':
                        try:
                            p[property]=str(p[property])
                            float(p[property])
                        except ValueError:
                            errors.append({'id': id , 'name': 'totalhours', 'value': p[property]})
                            add_warning(req,"チケット#%sの合計時間%sが実数ではありません。" % (id, p[property]))
                    if property=='hours':
                        try:
                            p[property]=str(p[property])
                            float(p[property])
                        except ValueError:
                            errors.append({'id': id , 'name': 'hours', 'value': p[property]})
                            add_warning(req,"チケット#%sの作業時間%sが実数ではありません。" % (id ,p[property]))
                    if property=='remainedhours':
                        try:
                            p[property]=str(p[property])
                            float(p[property])
                        except ValueError:
                            errors.append({'id': id , 'name': 'remainedhours', 'value': p[property]})
                            add_warning(req,"チケット#%sの残り作業時間%sが実数ではありません。" % (id ,p[property]))
                except ValueError:
                    pass
            self.log.info(params)
            if len(errors)==0:
                self.update_tickets(req,cursor,db,params)
        user = req.authname
        def addMessage(s):
            messages.extend([s]);

        tickets = self.get_tickets(req, cursor)
        # replace error fields
        self.log.info(errors)
        self.log.info(tickets)
        for e in errors:
            id = int(e['id'])
            for ticket in tickets:
                if ticket['id']==id:
                    ticket[e['name']]=e['value']

        add_script(req, 'worktime/worktime.js')
        add_stylesheet(req, 'common/css/report.css')
        return 'entryworktime.html', {'tickets':tickets, 'req':req}, None

    def update_tickets(self, req, cursor, db, params):
        change_time = int(time.mktime(datetime.today().timetuple())*1e6)
        for ticket_id in params:
            props = params[ticket_id]
            cursor.execute("SELECT value FROM ticket_custom WHERE ticket=%s AND name='totalhours'" % (ticket_id))
            row = cursor.fetchone()
            totalhours = row[0]
            for field in props:
                value = str(props[field])
                if (value==''):
                    continue
                if (field=='totalhours') and (props[field]!=totalhours):
                    SQL = "UPDATE  ticket_custom SET value=%s WHERE ticket=%s AND name='%s'" % (str(props[field]) ,ticket_id, str(field))
                    cursor.execute(SQL)

                    SQL="""INSERT INTO ticket_change 
                      (ticket,time,author,field, oldvalue, newvalue)
                      VALUES(%s, %s, '%s', '%s', '%s', '%s')""" %  (ticket_id, change_time, req.authname, field, 0, props[field])
                    cursor.execute(SQL)
                    db.commit()
                elif field=='hours':
                    new_totalhours = float(totalhours) + float(props['hours'])
                    SQL = "UPDATE  ticket_custom SET value=%s WHERE ticket=%s AND name='totalhours'" % (new_totalhours ,ticket_id)
                    cursor.execute(SQL)
                    SQL="""INSERT INTO ticket_change 
                      (ticket,time,author,field, oldvalue, newvalue)
                       VALUES(%s, %s, '%s', '%s', '%s', '%s')""" % (ticket_id, change_time, req.authname, 'totalhours', totalhours, new_totalhours)
                    cursor.execute(SQL)
                    SQL="""INSERT INTO ticket_change 
                      (ticket,time,author,field, oldvalue, newvalue)
                       VALUES(%s, %s, '%s', '%s', '%s', '%s')""" % (ticket_id, change_time, req.authname, 'hours', 0, float(props['hours']))
                    cursor.execute(SQL)

                    db.commit()
                elif field=='remainedhours':
                    cursor.execute("""SELECT te.value, tt.value FROM ticket t"""
                                   """ JOIN ticket_custom te ON t.id = te.ticket AND te.name='estimatedhours' """ 
                                   """ JOIN ticket_custom tt ON t.id = tt.ticket AND tt.name='totalhours' """ 
                                   """WHERE t.id = %s""" % ticket_id)
                    estimatedhours, totalhours = cursor.fetchone()
                    remainedhours = float(props['remainedhours'])
                    updated_estimatedhours = remainedhours + float(totalhours);
                    if abs(float(estimatedhours) - updated_estimatedhours) > 1:
                        self.log.info("change estimatedhours: " + estimatedhours + "->" + str(updated_estimatedhours))
                        cursor.execute("UPDATE ticket_custom SET value='%s' WHERE ticket = %s AND name='estimatedhours'"  % (updated_estimatedhours,ticket_id))
                        db.commit()
                elif (field=='close') and (str(props[field])=='on'):
                    SQL = "UPDATE ticket SET status='closed' WHERE id=%s" % ticket_id;
                    cursor.execute(SQL)
                    db.commit()
                elif (field!='totalhours') and (field!='billable') and (field!='close'):
                    SQL = "UPDATE  ticket_custom SET value=%s WHERE ticket=%s AND name='%s'" % (str(props[field]) ,ticket_id, str(field))
                    cursor.execute(SQL)
                    SQL="""INSERT INTO ticket_change 
                      (ticket,time,author,field, oldvalue, newvalue)
                       VALUES(%s, %s, '%s', '%s', '%s', '%s')""" % (ticket_id, change_time, req.authname, field, 0, props[field])
                    cursor.execute(SQL)
                    db.commit()


    def get_tickets(self, req, cursor):
        sql = """SELECT t.id ,t.type ,t.owner, t.summary ,t.priority ,t.milestone ,cth.value ,cbil.value , cest.value FROM ticket t
              JOIN ticket_custom cth ON t.id=cth.ticket
              JOIN ticket_custom cbil ON t.id=cbil.ticket
              JOIN ticket_custom cest ON t.id=cest.ticket
              WHERE t.status <> 'closed' AND t.owner='%s' AND
              cth.name='totalhours' AND cbil.name='billable' AND cest.name='estimatedhours'
              ORDER BY t.milestone""" % req.authname
        cursor.execute(sql)
        tickets = []
        for id, type, owner, summary, priority, milestone, totalhours, billable, estimatedhours in cursor:
            billable = 'true' if billable=='1' else 'false'
            totalhours = totalhours if totalhours!='' else '0'
            estimatedhours = estimatedhours if totalhours!='' else '0'
            tickets.append({'id':id ,'type':type, 'owner': owner, 'summary':summary, 'priority': priority , 'milestone':milestone, 'totalhours': totalhours, 'billable': billable, 'estimatedhours': estimatedhours})

        t = datetime.today()
        t = datetime(t.year,t.month,t.day)
        start = int(time.mktime(t.timetuple())*1e6)
        end = int(time.mktime(t.timetuple())*1e6+24*60*60*1e6)

        for ticket in tickets:
            sql = "SELECT * from ticket_change WHERE ticket='%s' AND field='totalhours' AND time > %s  AND time < %s" % (ticket['id'], start, end)
            self.log.info(sql)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row:
                ticket['reported'] = True
            else:
                ticket['reported'] = False
        return  tickets

    # IRequestHandler methods
    def match_request(self, req):
        val = re.search('/worktime$', req.path_info)
        return val and val.start() == 0

    # ITemplateProvider
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('worktime', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        genshi templates.
        """
        rtn = [resource_filename(__name__, 'templates')]
        return rtn


