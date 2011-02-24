# -*- coding: utf-8 -*-
from pkg_resources import resource_filename
import re
import time
import datetime
import dbhelper
from usermanual import *
from trac.log import logger_factory
from trac.core import *
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.chrome import add_stylesheet, add_script, \
     INavigationContributor, ITemplateProvider
from trac.web.href import Href
from reportmanager import CustomReportManager
from statuses import get_statuses
import trac.util.datefmt
import reports

#get_statuses = api.get_statuses

class TimingEstimationAndBillingPage(Component):
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    def __init__(self):
        pass

    def set_bill_date(self, username="Timing and Estimation Plugin",  when=0):
        now = trac.util.datefmt.to_datetime(None)#get now
        if not when:
            when = now

        strwhen = "%s-%s-%s %#02d:%#02d:%#02d" % \
                (when.year, when.month, when.day, when.hour,when.minute, when.second)
        sql = """
        INSERT INTO bill_date (time, set_when, str_value)
        VALUES (%s, %s, %s)
        """
        dbhelper.execute_non_query(self.env, sql, trac.util.datefmt.to_timestamp(when),
                                   trac.util.datefmt.to_timestamp(now), strwhen)


    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        val = re.search('/Billing$', req.path_info)
        if val and val.start() == 0:
            return "Billing"
        else:
            return ""

    def get_navigation_items(self, req):
        url = req.href.Billing()
        if req.perm.has_permission("REPORT_VIEW"):
            yield 'mainnav', "Billing", \
                  Markup('<a href="%s">%s</a>' % \
                         (url , u'作業時間管理'))

    # IRequestHandler methods
    def set_request_billing_dates(self, data):
        billing_dates = []
        billing_time_sql = """
        SELECT DISTINCT time as value, str_value as text
        FROM bill_date
        ORDER BY time DESC
        """
        rs = dbhelper.get_result_set(self.env, billing_time_sql)
        if rs:
            for (value, text) in rs.rows:
                billing_info = {'text':text , 'value':value*1000*1000}
                billing_dates.extend([billing_info])
        #self.log.debug("bill-dates: %s"%billing_dates)
        data['billing_info']["billdates"] = billing_dates

    def match_request(self, req):
        val = re.search('/Billing$', req.path_info)
        return val and val.start() == 0

    def process_request(self, req):
        messages = []

        def addMessage(s):
            messages.extend([s]);

        if req.method == 'POST':
            if req.args.has_key('setbillingtime'):
                self.set_bill_date(req.authname)
                addMessage("All tickets last bill date updated")

        mgr = CustomReportManager(self.env, self.log)
        data = {};
        data["statuses"] = get_statuses(self.env)
        data["reports"] = mgr.get_reports_by_group(CustomReportManager.TimingAndEstimationKey);
        # Handle pulling in report_descriptions
        # Could be added to custom report stuff, but that requires 
        # coordinating with too many people for me to care right now
        report_descriptions = {}
        for h in reports.all_reports:
            report_descriptions[h["title"]] = h["description"]
        for key in data["reports"]:
            if report_descriptions.has_key(key):
                data["reports"][key]["description"] = report_descriptions[key]
        #self.log.debug("DEBUG got %s, %s" % (data["reports"], type(data["reports"])));
        data["billing_info"] = {"messages":         messages,
                                "href":             req.href.Billing(),
                                "report_base_href": req.href.report(),
                                "usermanual_href":  req.href.wiki(user_manual_wiki_title),
                                "usermanual_title": user_manual_title }

        self.set_request_billing_dates(data)

        add_stylesheet(req, "Billing/billingplugin.css")
        add_script(req, "Billing/date.js")
        add_script(req, "Billing/linkifyer.js")
        return 'billing.html', data, None


    # ITemplateProvider
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('Billing', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        genshi templates.
        """
        rtn = [resource_filename(__name__, 'templates')]
        return rtn

