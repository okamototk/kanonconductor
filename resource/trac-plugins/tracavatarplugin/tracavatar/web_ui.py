# -*- coding: utf-8 -*-
from trac.core import *
from trac.config import Option, BoolOption, Configuration
from trac.web.chrome import add_script,add_stylesheet,ITemplateProvider
from trac.web.main import IRequestHandler, IRequestFilter
from trac.web.api import ITemplateStreamFilter
from trac.util.html import Markup

from genshi.filters.transform import Transformer
from genshi.template import MarkupTemplate
import re
from json.encoder import JSONEncoder

class TracAvatarModule(Component):
    implements(IRequestHandler, IRequestFilter, ITemplateProvider, ITemplateStreamFilter)

    def filter_stream(self, req, method, filename, stream, data):
#        if re.match(r'^/(ticket|newticket|wiki|timeline)', req.path_info):
            script = "<script type='text/javascript'>\n"
            script = script + "   avatar_request_path = '"+req.base_path + "/tracavatar';"
            script = script+"</script>"
            return stream | Transformer('//div[@id="footer"]').before(MarkupTemplate(script).generate())
#        else:
#            return stream

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
        
    def post_process_request(self, req, template, content_type):
        return (template, content_type)

    def post_process_request(self, req, template, data, content_type):
#        if re.match(r'^/(ticket|newticket|wiki|timeline)', req.path_info):
        add_script(req, 'tracavatar/js/avatar.js')
        return (template, data, content_type)

    # IRequestHandler methods
    def match_request(self, req):
        if req.path_info in ('/login/tracavatar', '/tracavatar'):
            self.log.debug("%s matches %s" % (req.path_info, True))
            return True
        return False

    def process_request(self, req):
        id = req.args.get('id')
        username = req.args.get('username')
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM session_attribute WHERE sid='%s' AND name='picture_href'" % username)
        row = cursor.fetchone()
        if row:
            picture_href = row[0]
        else:
            picture_href = req.base_path + "/chrome/tracusermanager/img/no_picture.png"
        response = JSONEncoder().encode({"id":id, "username": username, "url": picture_href}).encode('utf-8')
        req.send_response(200)
        req.send_header('Content-Type', 'application/json; charset=utf-8')
        req.send_header('Content-Length', len(response.encode("utf-8")))

        req.end_headers()
        req.write(response)

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return []

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('tracavatar', resource_filename(__name__, 'htdocs'))]
