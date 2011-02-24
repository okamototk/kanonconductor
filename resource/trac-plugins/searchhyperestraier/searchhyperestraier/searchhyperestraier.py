# -*- coding: utf-8 -*-
# SearchRepositoryWithHyperestraier plugin

from trac.core import *
#from trac.Search import ISearchSource
from trac.search.api import ISearchSource # for Trac0.11
from trac.util import NaivePopen
from StringIO import StringIO
import urllib
import time
from xml.dom.minidom import parseString
import datetime
from trac.util.datefmt import to_datetime, utc # for Trac0.11
from trac.util.text import to_unicode # for Trac0.11

class SearchHyperEstraierModule(Component):
    implements(ISearchSource)
    
    # ISearchProvider methods
    def get_search_filters(self, req):
        if req.perm.has_permission('BROWSER_VIEW'):
             yield ('repositoryhyperest', u'リポジトリ')

    def get_search_results(self, req, terms, filters):
        if not 'repositoryhyperest' in filters:
            return

        #estcmd.exeのパス
        estcmd_path = self.env.config.get('searchhyperestraier', 'estcmd_path','estcmd') 
        #estcmd.exeの引数
        estcmd_arg = self.env.config.get('searchhyperestraier', 'estcmd_arg','search -vx -sf -ic Shift_JIS') 
        #インデックスのパス
        index_path = self.env.config.get('searchhyperestraier', 'index_path','') 
        #コマンド実行時のエンコード(Pythonでの形式)
        #estcmd_argと一致(?)させる必要有り。
        estcmd_encode = self.env.config.get('searchhyperestraier', 'estcmd_encode','mbcs') 

        #検索結果のパスの頭で削る文字列
        replace_left = self.env.config.get('searchhyperestraier', 'replace_left','')
        #URLを生成する際に頭につける文字列
        #browse_trac=enabledの場合は/がリポジトリのルートになるように
        url_left = self.env.config.get('searchhyperestraier', 'url_left','')

        #Tracのブラウザへのリンクを作るか否か。
        #enabled:Tracのブラウザへのリンクを作る
        #上記以外:replace_left,url_leftで指定したURLへのリンクを作る
        browse_trac = self.env.config.get('searchhyperestraier', 'browse_trac','enabled')

        #cmdline = "%s %s %s %s" % (estcmd_path,estcmd_arg,index_path,unicode(query,'utf-8').encode('CP932'))
        qline = ' '.join(terms)
        cmdline = "%s %s %s %s" % (estcmd_path,estcmd_arg,index_path,qline)
        self.log.debug('SearchHyperEstraier:%s' % cmdline)
        cmdline = unicode(cmdline).encode(estcmd_encode)
        np = NaivePopen(cmdline)
        #self.log.debug('Result:%s' % unicode(np.out,'utf-8').encode('mbcs'))
        #self.log.debug('Result:%s' % np.out)
        if np.errorlevel or np.err:
            err = 'Running (%s) failed: %s, %s.' % (cmdline, np.errorlevel,
                                                    np.err)
            raise Exception, err
        
        dom = parseString(np.out)
        root = dom.documentElement
        #estresult_node = root.getElementsByTagName("document")[0]
        element_array = root.getElementsByTagName("document")
        for element in element_array:
            #self.log.debug('Result:%s' % 'hoge')
            url = ""
            title = ""
            date = 0
            detail = ""
            author = "不明"

            #detailを生成
            elem_array =  element.getElementsByTagName("snippet")
            detail = self._get_innerText("",elem_array)

            #その他の属性を生成
            attrelem_array = element.getElementsByTagName("attribute")
            for attrelem in attrelem_array:
                attr_name = attrelem.getAttribute("name")
                attr_value = unicode(attrelem.getAttribute("value"))
                #URLとタイトルを生成
                if attr_name == "_lreal":
                    attr_value=attr_value[len(replace_left):].replace("\\","/")
                    if browse_trac == "enabled":
                        url = self.env.href.browser(url_left + attr_value)
                        title = "source:"+ url_left + attr_value
                    else:
                        url = url_left + attr_value
                        title = url_left + attr_value
                #更新日時を生成
                elif attr_name =="@mdate":
                    date = time.strptime(attr_value,"%Y-%m-%dT%H:%M:%SZ")
                    self.log.debug('date:%s' % attr_value)
                    date = to_datetime(datetime.datetime(date[0],date[1],date[2],date[3],date[4],date[5],0,utc)) # for Trac0.11
            yield(url,title,date,to_unicode(author,'utf-8'),to_unicode(detail,'utf-8'))

    #XMLのElementを再帰的に探してテキストを生成
    def _get_innerText(self,text,node_array):
        for node in node_array:
            if node.nodeType == node.TEXT_NODE:
                text = text + unicode(node.data).encode('utf-8')
            else:
                text = self._get_innerText(text,node.childNodes)
        return text
