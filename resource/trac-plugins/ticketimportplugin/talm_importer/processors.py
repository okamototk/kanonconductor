# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2008 by nexB, Inc. http://www.nexb.com/ - All rights reserved.
# Author: Francois Granade - fg at nexb dot com
# Licensed under the same license as Trac - http://trac.edgewall.org/wiki/TracLicense
#

import time

from trac.ticket import Ticket, model
from trac.util import get_reporter_id
from trac.util.datefmt import format_datetime
from trac.util.html import Markup
from trac.wiki import wiki_to_html


class ImportProcessor(object):
    def __init__(self, env, req, filename, tickettime):
        self.env = env
        self.req = req
        self.filename = filename
        self.modifiedcount = 0
        self.notmodifiedcount = 0
        self.added = 0
        self.parent_tid = 0

        # TODO: check that the tickets haven't changed since preview
        self.tickettime = tickettime
        
        # Keep the db to commit it all at once at the end
        self.db = self.env.get_db_cnx()
        self.missingemptyfields = None
        self.missingdefaultedfields = None
        self.computedfields = None
        self.importedfields = None

    def start(self, importedfields, reconciliate_by_owner_also, has_comments):
        self.lowercaseimportedfields = [f.lower() for f in importedfields]

    def process_missing_fields(self, missingfields, missingemptyfields, missingdefaultedfields, computedfields):
        self.missingemptyfields = missingemptyfields
        self.missingdefaultedfields = missingdefaultedfields
        self.computedfields = computedfields

    def process_notimported_fields(self, notimportedfields):
        pass

    def process_comment_field(self, comment):
        pass

    def start_process_row(self, row_idx, ticket_id):
        from ticket import PatchedTicket
        if ticket_id > 0:
            # existing ticket
            self.ticket = PatchedTicket(self.env, tkt_id=ticket_id, db=self.db)

            # 'Ticket.time_changed' is a datetime in 0.11, and an int in 0.10.
            # if we have trac.util.datefmt.to_datetime, we're likely with 0.11
            try:
                from trac.util.datefmt import to_timestamp
                time_changed = to_timestamp(self.ticket.time_changed)
            except ImportError:
                time_changed = int(self.ticket.time_changed)
                
            if time_changed > self.tickettime:
                # just in case, verify if it wouldn't be a ticket that has been modified in the future
                # (of course, it shouldn't happen... but who know). If it's the case, don't report it as an error
                if time_changed < int(time.time()):
                    # TODO: this is not working yet...
                    #
                    #raise TracError("Sorry, can not execute the import. "
                    #"The ticket #" + str(ticket_id) + " has been modified by someone else "
                    #"since preview. You must re-upload and preview your file to avoid overwriting the other changes.")
                    pass

        else:
            self.ticket = PatchedTicket(self.env, db=self.db)
        self.comment = ''

    def process_cell(self, column, cell):
        cell = unicode(cell)
        # this will ensure that the changes are logged, see model.py Ticket.__setitem__
        self.ticket[column.lower()] = cell

    def process_comment(self, comment):
        self.comment = comment

    def end_process_row(self, indent):
        try:
            # 'when' is a datetime in 0.11, and an int in 0.10.
            # if we have trac.util.datefmt.to_datetime, we're likely with 0.11
            from trac.util.datefmt import to_datetime
            tickettime = to_datetime(self.tickettime)
        except ImportError:
            tickettime = self.tickettime
                
        if self.ticket.id == None:
            for f in self.missingemptyfields:
                if self.ticket.values.has_key(f) and self.ticket[f] == None:
                    self.ticket[f] = ''

            if self.comment:
                self.ticket['description'] = self.ticket['description'] + "\n[[BR]][[BR]]\n''Batch insert from file " + self.filename + ":''\n" + self.comment

            for f in self.computedfields:
                if f not in self.lowercaseimportedfields and self.computedfields[f] != None and self.computedfields[f]['set']:
                    self.ticket[f] = self.computedfields[f]['value']

            if (indent!=0) and (self.parent_tid!=0) and ('parents' in self.env.config['ticket-custom']):
                self.ticket['parents'] = str(self.parent_tid)

            self.added += 1
            self.ticket.insert(when=tickettime, db=self.db)
            if indent==0:
                 self.parent_tid = self.ticket.id

        else:
            if self.comment:
                message = "''Batch update from file " + self.filename + ":'' " + self.comment
            else:
                message = "''Batch update from file " + self.filename + "''"
            if self.ticket.is_modified() or self.comment:
                self.modifiedcount += 1
                self.ticket.save_changes(get_reporter_id(self.req), message, when=tickettime, db=self.db) # TODO: handle cnum, cnum = ticket.values['cnum'] + 1)
            else:
                self.notmodifiedcount += 1

        self.ticket = None

    def process_new_lookups(self, newvalues):
        for field, names in newvalues.iteritems():
            if field == 'status':
                continue
            
            if field == 'component':
                class CurrentLookupEnum(model.Component):
                    pass
            elif field == 'milestone':
                class CurrentLookupEnum(model.Milestone):
                    pass
            elif field == 'version':
                class CurrentLookupEnum(model.Version):
                    pass
            elif field == 'type':
                class CurrentLookupEnum(model.Type):
                    pass
            else:
                class CurrentLookupEnum(model.AbstractEnum):
                    # here, you shouldn't put 'self.' before the class field.
                    type = field

            for name in names:
                lookup = CurrentLookupEnum(self.env, db=self.db)
                lookup.name = name
                lookup.insert()

    def process_new_users(self, newusers):
        pass
            
    def end_process(self, numrows):
        self.db.commit()

        data = {}
        data['title'] = 'Import completed'
        #data['report.title'] = data['title'].lower()

        message = 'インポートに成功しました。 ' + str(numrows) + ' tickets (' + str(self.added) + ' 追加, ' + str(self.modifiedcount) + ' 更新, ' + str(self.notmodifiedcount) + ' 未更新).'

        data['message'] = Markup("<style type=\"text/css\">#report-notfound { display:none; }</style>\n") + wiki_to_html(message, self.env, self.req)

        return 'import_preview.html', data, None
    

class PreviewProcessor(object):
    
    def __init__(self, env, req):
        self.env = env
        self.req = req
        self.data = {'rows': []}
        self.ticket = None
        self.modified = False
        self.styles = ''
        self.duplicatessumaries = []
        self.modifiedcount = 0
        self.notmodifiedcount = 0
        self.added = 0

    def start(self, importedfields, reconciliate_by_owner_also, has_comments):
        self.data['title'] = 'Preview Import'

        self.message = ''

        if 'ticket' in [f.lower() for f in importedfields]:
            self.message += ' * \'\'\'ticket\'\'\' カラムが見つかりました： 既存のチケットは、新しい値に更新されます。 変更される値は、下記のプレビューにイタリックで表示されます。\n' 
        elif 'id' in [f.lower() for f in importedfields]:
            self.message += ' * \'\'\'id\'\'\' カラムが見つかりました： 既存のチケットは、新しい値に更新されます。 変更される値は、下記のプレビューにイタリックで表示されます。\n' 
        else:
            self.message += ' * \'\'\'ticket\'\'\' カラムが見つかりません： summary' + (reconciliate_by_owner_also and ' と owner' or '') + ' カラムで調整します。 同一の summary' + (reconciliate_by_owner_also and ' と owner' or '') + ' を持ったチケットが見つかれば、変更点が下記のプレビューにイタリックで表示されます。 もし同一の summary ' + (reconciliate_by_owner_also and ' と同一の owner' or '') + ' のチケットが無ければ、 すべてイタリックで表示され、新しいチケットとして追加されます。\n' 
                                
        self.data['headers'] = [{ 'col': 'ticket', 'title': 'ticket' }]
        # we use one more color to set a style for all fields in a row... the CS templates happens 'color' + color + '-odd'
        self.styles = "<style type=\"text/css\">\n.ticket-imported, .modified-ticket-imported { width: 40px; }\n"
        self.styles += ".color-new-odd td, .color-new-even td, .modified-ticket-imported"
        columns = importedfields[:]
        if has_comments:
            columns.append('comment')

        for col in columns:
            if col.lower() != 'ticket' and col.lower() != 'id':
                title=col.capitalize()
                self.data['headers'].append({ 'col': col, 'title': title })
                self.styles += ", .modified-%s" % col
        self.styles += " { font-style: italic; }\n"
        self.styles += "</style>\n"

    # This could be simplified...
    def process_missing_fields(self, missingfields, missingemptyfields, missingdefaultedfields, computedfields):
        self.message += ' * 次のフィールドインポートするファイルに見つかりませんでした。デフォルト値として次の値を設定します:\n\n'
        self.message += "   ||'''field'''||'''Default value'''||\n"
        if missingemptyfields != []:
            self.message += '   ||' + ', '.join([x.capitalize() for x in missingemptyfields]) + '||' + "''(Empty value)''" + '||\n'
            
        if missingdefaultedfields != []:
            for f in missingdefaultedfields:
                self.message += '   ||' + f.capitalize() + '||' + str(computedfields[f]['value']) + '||\n'

        self.message += '(あなたが管理者の場合、管理モジュールからこれらのデフォルト値を変更できます。もしくは、当該のカラムを追加して再アップロードする事も可能です。)\n'

    def process_notimported_fields(self, notimportedfields):
        self.message += ' * 次のフィールドはTracに存在しないため、インポートされません: ' + ', '.join([x and x or "''(empty name)''" for x in notimportedfields])  + '.\n'

    def process_comment_field(self, comment):
        self.message += ' * フィールド "%s" はチケットを変更したときにコメントとして利用します。新しいチケットには詳細として利用します。' % comment

    def start_process_row(self, row_idx, ticket_id):
        from ticket import PatchedTicket
        self.ticket = None
        self.cells = []
        self.modified = False
        if ticket_id > 0:
            # existing ticket. Load the ticket, to see which fields will be modified
            self.ticket = PatchedTicket(self.env, ticket_id)
            

    def process_cell(self, column, cell):
        if self.ticket and not (self.ticket.values.has_key(column.lower()) and self.ticket[column.lower()] == cell):
            self.cells.append( { 'col': column, 'value': cell, 'style': 'modified-' + column })
            self.modified = True
        else:
            self.cells.append( { 'col': column, 'value': cell, 'style': column })

    def process_comment(self, comment):
        column = 'comment'
        self.cells.append( { 'col': column, 'value': comment, 'style': column })

    def end_process_row(self, indent):
        odd = len(self.data['rows']) % 2
        if self.ticket:
            if self.modified:
                self.modifiedcount += 1
                style = ''
                ticket = self.ticket.id
            else:
                self.notmodifiedcount += 1
                style = ''
                ticket = self.ticket.id
        else: 
            self.added += 1
            style = odd and 'color-new-odd' or 'color-new-even'
            ticket = '(new)'
            
        self.data['rows'].append({ 'style': style, 'cells': [{ 'col': 'ticket', 'value': ticket, 'style': '' }] + self.cells })

            
    def process_new_lookups(self, newvalues):
        if 'status' in newvalues:
            if len(newvalues['status']) > 1:
                msg = ' * いくつかのチケットの"Status"フィールドは空欄のままです。: %s. それらはインポートされますが、不正なステータスになります。\n\n'
            else:
                msg = ' * いくつかのチケットの"Status"フィールドは空欄のままです。: %s. それらはインポートされますが、不正なステータスになります。\n\n'
                
            self.message += (msg % ','.join(newvalues['status']))
            del newvalues['status']
            
        if newvalues:
            self.message += ' * いくつかの値は見つかりませんでした。それらは、リストに追加されるでしょう。:\n\n'
            self.message += "   ||'''field'''||'''New values'''||\n"
            for field, values in newvalues.iteritems():                
                self.message += "   ||" + field.capitalize() + "||" + ', '.join(values) + "||\n"
            

    def process_new_users(self, newusers):
        self.message += ' * いくつかのユーザ名は、システムに存在しません: ' + ', '.join(newusers) + '。 正しいユーザ名を入力してください\n'
            
    def end_process(self, numrows):
        self.message = 'インポートされるチケットのプレビューです。データが正しければ、\'\'\'インポート実行\'\'\' を選択してください。\n' + ' * ' + str(numrows) + 'つのチケットがインポートされます (追加:' + str(self.added) + ', 変更:' + str(self.modifiedcount) + ', 未変更:' + str(self.notmodifiedcount) + ').\n' + self.message
        self.data['message'] = Markup(self.styles) + wiki_to_html(self.message, self.env, self.req) + Markup('<br/>')

        return 'import_preview.html', self.data, None

