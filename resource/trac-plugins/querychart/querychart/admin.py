# -*- coding: utf-8 -*-

from trac.core import *
from trac.admin import IAdminPanelProvider
from trac.web.chrome import ITemplateProvider
from trac.util.translation import _
import re
import pkg_resources

from trac.web.chrome import add_notice, add_warning, Chrome, \
                            ITemplateProvider
from trac.resource import ResourceNotFound
                 
from model import *

from trac.ticket.model import Ticket
from trac.util.datefmt import format_date,to_datetime
                            
class AdminPanel(Component):
    implements(IAdminPanelProvider,ITemplateProvider)

    _type = 'querychart'
    _label = ( _('QueryChart'), _('QueryChart'))

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]
    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'TICKET_ADMIN' in req.perm:
            yield ('ticket', _('Ticket System'), self._type, self._label[1])

    def render_admin_panel(self, req, cat, page, querychart):
        req.perm.require('TICKET_ADMIN')
        # Detail view?
        data = {}
        if req.method == 'POST':
                
            if req.args.get('reset'):
                db = self.env.get_db_cnx()
                #rebuild_status_log(self.env,1,db)
                cursor = db.cursor()
                cursor.execute("SELECT id from ticket")
                ids = [id for id, in cursor]
                for id in ids:
                    #delete_status_log(env,ticket_id,db)
                    status_dt = set_status_dt(self.env,id,db=db)
                    ticket = Ticket(self.env,id,db=db)
                    for m in status_dt:
                        ticket[m] = status_dt[m]
                    ticket.save_changes(req.authname, None, when=None, db=db, cnum='')
                db.commit()
                
                add_notice(req, "Data has been reseted. ")
                
        return 'admin_querychart.html', data

