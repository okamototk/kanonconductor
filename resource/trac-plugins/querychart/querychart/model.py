# -*- coding: utf-8 -*-

from trac.core import *

from trac.util.datefmt import format_date,to_datetime
from trac.config import Option, ListOption

from trac.ticket.api import ITicketManipulator
from trac.ticket.model import Ticket


class TicketStatusLogModelProvider(Component):
    implements(ITicketManipulator)
    #sample:'assigned:last_assigned, accepted,reopened, closed:last_closed'
    ListOption('querychart', 'order', default='assigned, accepted,reopened, closed',
                       doc='status order')
    

    def validate_ticket(self,req, ticket):
        """If status changed, then set date to custom field."""
        status_dt = set_status_dt(self.env,ticket.id,ticket['status'],ticket['changetime'])
        if ticket._old.has_key('status'):
            for m in status_dt:
                ticket[m] = status_dt[m]
        
        return []


def set_status_dt(env,ticket_id,new_status=None,new_time=None,db=None):

    order_lst = env.config.getlist('querychart', 'order')
    order =[]
    custom_fields = {}
    for m in order_lst:
        ms = m.split(':')
        if len(ms) >= 2:
            order.append(ms[0])
            custom_fields[ms[0]] = ':'.join(ms[1:])
        else:
            order.append(m)

    if not db:
        db = env.get_db_cnx()

    cursor = db.cursor()
    cursor.execute("SELECT newvalue,time,ticket ,field from ticket_change where ticket=%s"
                   " and field=%s"
                   " order by time",(ticket_id,'status'))
    history=[(row[0],to_datetime(row[1])) for row in cursor]
    if new_status:
        history.append((new_status,new_time))
    
    result ={}
    for new_status,time in history:
        #set date by priority of 'order'
        #if status date (higher priority than next status) is none, set date to higher priority. 
        #and set none to lower priority status date.
        if not new_status in order:
            continue
        idx = order.index(new_status)
        formated_date = format_date(to_datetime(time))
        
        for m_idx in range(len(order)-1, -1, -1):
            if not order[m_idx] in custom_fields:
                continue

            m_field = custom_fields[order[m_idx]]
            if not m_field in result:
                result[m_field] = None

            if idx==m_idx:
                result[m_field]=formated_date
            elif idx<m_idx:
                result[m_field]=None
            else:
                if result[m_field]==None:
                    result[m_field]=formated_date
                else:
                    formated_date=result[m_field]
    return result


