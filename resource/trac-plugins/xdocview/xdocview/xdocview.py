# -*- coding: utf-8 -*-
# XdocView plugin

from genshi.core import Markup
from genshi.builder import tag

from trac.config import Option, ListOption
from trac.core import *
from trac.mimeview.api import IHTMLPreviewRenderer, Mimeview
from trac.util import NaivePopen
from trac.util.html import escape, Deuglifier
import tempfile
import os

__all__ = ['XdocRenderer']

types = {
    'application/msword':       ('msword', 2),
    'application/rtf':          ('rtf',2),
    'application/vnd.ms-excel': ('msexcel',2),
    'application/vnd.ms-powerpoint':    ('msppt',2),
    'application/pdf':          ('pdf',2),
    'application/x-js-taro':    ('xjstaro',2),
    'application/vnd.fujitsu.oasys':    ('oasys',2),
    'application/vnd.fujitsu.oasys2':   ('oasys2',2),
    'application/vnd.fujitsu.oasys3':   ('oasys3',2),
    'application/lotus-123':    ('lotus123',2),
}






class XdocRenderer(Component):
    implements(IHTMLPreviewRenderer)

    #when expand_tabs is True, content is forced to unicode
    #expand_tabs = True
    returns_source = True

    path = Option('mimeviewer', 'xdoc2txt_path', 'xdoc2txt',
        u"""path to xdoc2txt""")

    # IHTMLPreviewRenderer methods

    def get_quality_ratio(self, mimetype):
        # Extend default MIME type to mode mappings with configured ones
        self.log.debug(types.get(mimetype, (None, 0))[1])
        return types.get(mimetype, (None, 0))[1]


    def render(self, context, mimetype, content, filename=None, rev=None):
        cmdline = self.path
        suffix = filename[filename.rfind('.'):]

        infilepath = tempfile.mktemp(suffix)
        tmp = open(str(infilepath), 'wb')
        tmp.write(content.read())
        tmp.close()

        cmdline = '%s \"%s\"' % (cmdline, infilepath)
        self.log.debug('XdocView-Plugin %s : %s' % (cmdline,suffix))
        np = NaivePopen(cmdline)


        #np = NaivePopen(cmdline, content.encode('utf-8'), capturestderr=1)
        if np.errorlevel or np.err:
            err = 'Running (%s) failed: %s, %s.' % (cmdline, np.errorlevel,
                                                    np.err)
            raise Exception, err
        odata = np.out
        if os.path.isfile(infilepath):
            os.remove(infilepath)

        data =  unicode(odata,'mbcs')

        return data


