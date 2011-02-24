# -*- coding: utf-8 -*-
"""
= Hudson Trac Plus Plugin =

== Description ==
A plugin to cooperate with [https://hudson.dev.java.net/ Hudson] - an excellent CI tool.

This plugin provides the following functions.

 * Add Hudson Build results into the Trac timeline
 * Provide a navbar menu to link to the Hudson dashboard
 * Add wiki macro to make an extra-link to the Hudson Build

This plugin are forked from [http://trac-hacks.org/wiki/HudsonTracPlugin HudsonTracPlugin]. 
Original HudsonTracPlugin uses rss to get build information,
but Hudson Trac Plus plugin uses [http://hudson.gotdns.com/wiki/display/HUDSON/Remote+access+API Hudson Remote API]. 

Much more detail information are [http://sourceforge.jp/projects/shibuya-trac/wiki/HudsonTracPlusPlugin HudsonTracPlus page on Shibuya.Trac]. Sorry this page is Japanese only.

== Dependencies ==
This plugin requires no extra library.
And works on Trac-0.10 and 0.11.

== Configuration ==
There are 2 options you must configure in your trac.ini under the section `[hudsonplus]`.

hudson_url
  The url of the Hudson top page.
  This plugin uses this to get information through Hudson Remote API.
  Example: `http://localhost/hudson/`
  By default, 'http://localhost:8010/hudson'. This is for TracLightning.
main_page
  The url of the Hudson page to link to from the trac mainnav; if empty, no entry is created in the mainnav. Example: /hudson/
  
And also, you can specify 5 extra options.

display_in_new_tab
  Set `true` if you want to show Hudson on other window.
jobs
  Jobs to display on timeline separated by comma. 
  If you don't specify this at all, show all jobs.
navigation_label
  The label string of navigation tab. Default is 'Hudson'.
username / password
  The username to access Hudson.
  HudsonTracPlus supports for Basic and Digest authentifications.
  And if you are also using iniAdminPlugin(r3915-),
  please add 'hudsonplus:password' into 'passwords' values on [iniadmin] section in trac.ini.

{{{
[iniadmin]
passwords = hudsonplus:password
}}}

  If you don't set this, the password is very very clear on the screen:)

== Bugs/Feature Requests ==
Existing bugs and feature requests for HudsonTracPlugin are [http://sourceforge.jp/projects/shibuya-trac/ticket/ here]. 

== Download and Source ==
Download the egg-file from [http://sourceforge.jp/projects/shibuya-trac/wiki/HudsonTracPlusPlugin project page].
And you can [http://svn.sourceforge.jp/view/plugins/hudsontracplus/?root=shibuya-trac browse the source] on Shibuya.Trac. 

== Author/Contributors ==
'''Author:''' akihirox(Itou Akihiro)

'''Contributors:'''
Color ball images in htdocs are from [https://hudson.dev.java.net/ Hudson].

== ChangeLog ==

 * What's new in 0.4 2009/08/11
  * + add Aborted build information on timeline.
  * - fix job_url handling when hudson_url includes 'localhost'

 * What's new in 0.3 2009/04/29
  * + add Basic/Digest authentification support.
  * - fix bugs.

 * What's new in 0.2 2009/01/29
  * - fix building build information on timeline probleml([http://sourceforge.jp/ticket/browse.php?group_id=3068&tid=14851 issue:14851).

 * What's new in 0.1 2009/01/28
  * + release

"""
import time
import calendar
import urllib2
import urlparse
from datetime import datetime
from trac.core import *
from trac.config import Option, BoolOption, ListOption
from trac.util import Markup, format_datetime
from trac.web.chrome import INavigationContributor, ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiMacroProvider
try:
    from trac.timeline.api import ITimelineEventProvider
except ImportError:
    from trac.Timeline import ITimelineEventProvider

# build-kind -> build-message
BUILD_MESSAGES = {'build-no-status': 'No build status(Maybe now building)',
                  'build-success': 'Build finished successfully',
                  'build-unstable': 'Build failed',
                  'build-aborted': 'Build aborted',
                  'build-failure': 'Build failed'}

class HudsonTracPlusPlugin(Component):
    '''
    This class implements 4 interfaces:

    - INavigationContributor
    - ITimelineEventProvider
    - ITemplate Provider
    - IWkikiMacroProvider

    INavigationContributor is for making navbar menu.

    ITimelineEventProverder is for displaying build results on timeline.

    ITemplateProvider is for using custom css/images.

    IWikiMacroProvider is for defining a custom macro.
    '''
    implements(INavigationContributor, ITimelineEventProvider, ITemplateProvider, IWikiMacroProvider)

    hudson_url = Option('hudsonplus', 'hudson_url', 'http://localhost:8010/hudson/',
                        'The url of the hudson top page. This must be an ' +
                        'absolute url. This plugin uses this to get information ' +
                        'through Hudson Remote API.')

    nav_url  = Option('hudsonplus', 'main_page', '/hudson/',
                      'The url of the hudson main page to which the trac nav ' +
                      'entry should link; if empty, no entry is created in ' +
                      'the nav bar/timeline/wikimacro. This may be a relative url.')
    jobs = ListOption('hudsonplus', 'jobs', '', sep=',' , 
                      doc='Jobs to display on timeline separated by comma. ' +
                      'If you don\'t specify this at all, show all jobs.')
    disp_tab = BoolOption('hudsonplus', 'display_in_new_tab', 'false',
                          'Open hudson page in new tab/window')
    navi_label = Option('hudsonplus', 'navigation_label', 'Hudson',
                        'The label of navigation tab.')
    username = Option('hudsonplus', 'username', '',
                      'The username to use to access hudson')
    password = Option('hudsonplus', 'password', '',
                      'The password to use to access hudson')

    def __init__(self):
        pwdMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        base_url = urlparse.urlsplit(self.hudson_url)[1]
        pwdMgr.add_password(None, base_url, self.username, self.password)

        bAuth = urllib2.HTTPBasicAuthHandler(pwdMgr)
        dAuth = urllib2.HTTPDigestAuthHandler(pwdMgr)

        self.url_opener = urllib2.build_opener(bAuth, dAuth)
        self.env.log.debug("registered auth-handler for '%s', username='%s'" %
                           (base_url, self.username))

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'builds'

    def get_navigation_items(self, req):
        if self.nav_url:
            markup = get_navi_markup(self.disp_tab, self.nav_url, self.navi_label)
            yield 'mainnav', 'builds', markup

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [self.env.get_templates_dir(),
                self.config.get('trac', 'templates_dir')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('HudsonTracPlus', resource_filename(__name__, 'htdocs'))]

    # ITimelineEventProvider methods
    def get_timeline_filters(self, req):
        if req.perm.has_permission('CHANGESET_VIEW'):
            yield ('build', 'Hudson Builds')

    def get_timeline_events(self, req, start, stop, filters):
        if isinstance(start, datetime): # Trac>=0.11
            from trac.util.datefmt import to_timestamp
            start = to_timestamp(start)
            stop = to_timestamp(stop)

        if 'build' in filters:
            add_stylesheet(req, 'HudsonTracPlus/hudsontracplus.css')
            
            hudson_api_url = self.hudson_url + 'api/python'
            try:
                hudson_json = eval(self.url_opener.open(hudson_api_url).readline())
            except:
                self.env.log.debug("hudson_api_url='%s'" % (hudson_api_url))
                return
            
            for job in hudson_json['jobs']:
                if len(self.jobs) > 0 and not job['name'] in self.jobs:
                    continue

                job_api_url = get_job_url(job['url'] + 'api/python?depth=2', self.hudson_url)
                try:
                    json = eval(self.url_opener.open(job_api_url).readline())
                except:
                    self.env.log.debug("job_api_url='%s'" % (job_api_url))
                    raise

                for build in json['builds']:
                    # check time range
                    completed = build['timestamp'] / 1000
                    if completed > stop:
                        continue
                    if completed < start:
                        break

                    # create timeline entry
                    kind = get_build_kind(build)
                    href = get_build_href(build, self.hudson_url, self.nav_url)
                    title = Markup(get_build_title_markup(job, build))
                    comment = get_build_comment(build, format_datetime(completed))

                    yield kind, href, title, completed, None, comment

    # IWikiMacroProvider method
    def get_macros(self):
        """RefHudsonBuild"""
        yield 'RefHudsonBuild'

    def get_macro_description(self, name):
        return '''Make an extra-link to hudson build'''

    def render_macro(self, req, name, content):
            return self.expand_macro(None, name, content)

    def expand_macro(self, formatter, name, content):
        if name == 'RefHudsonBuild':
            if self.nav_url:
                return get_build_ref_markup(self.nav_url, self.jobs, content)

def get_job_url(job_url, hudson_url):
    """Return the job url to use api access.

    This method is mainly designed for the Hudson working as service on TracLightning.
    Hudson Service may return job_url which doesn't depend on API url.

    ex,
    Query API: http://localhost:8010/hudson/api/python
    returnd job url: http://foo/hudson/job/bar/

    foo is host name of the localhost.
    So that this plugin fails to get build informations.

    For this problem, hudson trac plus plugin converts job url if necessary.
    >>> get_job_url('http://foo/hudson/job/bar/api/python?depth=2', 'http://localhost:8010/hudson')
    'http://localhost:8010/hudson/job/bar/api/python?depth=2'
    
    hudson trac plus plugin converts job url only if hudson url includes 'localhost'.
    >>> get_job_url('http://foo/hudson/job/bar/api/python?depth=2', 'http://hoge/hudson')
    'http://foo/hudson/job/bar/api/python?depth=2'

    >>> get_job_url('http://localhost/hudson/job/bar/api/python?depth=2', 'http://localhost:8010/hudson')
    'http://localhost:8010/hudson/job/bar/api/python?depth=2'

    """
    if not 'localhost' in hudson_url:
        return job_url
    
    p1 = urlparse.urlsplit(job_url)
    p2 = urlparse.urlsplit(hudson_url)
    
    return urlparse.urlunsplit((p1.scheme, p2.netloc, p1.path, p1.query, p1.fragment))


def get_navi_markup(disp, url, label):
    """Return the navigation element markup.

    If nav_url is true, make an element to open other window.
    >>> str(get_navi_markup(True, 'url', 'label'))
    '<a class="ext-link" href="url" target="hudson"><span class="icon"></span>label</a>'

    If nav_url is false, make an element to link only.
    >>> str(get_navi_markup(False, 'url', 'label'))
    '<a class="ext-link" href="url" ><span class="icon"></span>label</a>'

    Also, _markup functions must be charcter-escaped.
    >>> str(get_navi_markup(False, '"<>', 'label'))
    '<a class="ext-link" href="&#34;&lt;&gt;" ><span class="icon"></span>label</a>'
    >>> str(get_navi_markup(False, 'url', '"<>'))
    '<a class="ext-link" href="url" ><span class="icon"></span>&#34;&lt;&gt;</a>'
    """
    FORMAT = '<a class="ext-link" href="%s" %s><span class="icon"></span>%s</a>'
    escaped_url = Markup.escape(url)
    escaped_label = Markup.escape(label)

    if disp:
        target = 'target="hudson"'
    else:
        target = ''

    return Markup(FORMAT % (escaped_url, target, escaped_label))

def get_build_kind(build):
    '''Return build kind.

    build must be a dictionary and have a key 'result'.
    When build['result'] is None(maybe in building), returns no-status
    >>> get_build_kind({'result': None})
    'build-no-status'

    SUCCESS/UNSTABLE is build-success/build-unstable/buidl-aborted.
    >>> get_build_kind({'result': 'SUCCESS'})
    'build-success'
    >>> get_build_kind({'result': 'UNSTABLE'})
    'build-unstable'
    >>> get_build_kind({'result': 'ABORTED'})
    'build-aborted'

    Other status are all build-fail.
    >>> get_build_kind({'result': 'FAILED'})
    'build-failure'
    >>> get_build_kind({'result': 'SPAM'})
    'build-failure'

    '''
    if build['result'] is None:
        return 'build-no-status'
    elif build['result'].find('SUCCESS') >= 0:
        return 'build-success'
    elif build['result'].find('UNSTABLE') >= 0:
        return 'build-unstable'
    elif build['result'].find('ABORTED') >= 0:
        return 'build-aborted'
    else:
        return 'build-failure'

def get_build_href(build, relative_url, absolute_url):
    '''Return build href address.

    build['url'] must be replaced by absolute url(nav_url)
    because build infomation is from hudson_url(maybe relative url).

    >>> get_build_href({'url': '/hudson/jobname/1/api'}, '/hudson/', 'http://example.com/hudson/')
    'http://example.com/hudson/jobname/1/api'
    '''
    return build['url'].replace(relative_url, absolute_url, 1)

def get_build_title_markup(job, build):
    '''Return build title for timeline.

    >>> str(get_build_title_markup({'name': 'jobname'}, {'number':1, 'result':'SUCCESS'}))
    '<img src="chrome/common/extlink.gif">jobname #1 - build-success</a>'

    Also, _markup functions must be charcter-escaped.
    >>> str(get_build_title_markup({'name': 'jobname'}, {'number':'><"', 'result':'SUCCESS'}))
    '<img src="chrome/common/extlink.gif">jobname #&gt;&lt;&#34; - build-success</a>'
    >>> str(get_build_title_markup({'name': '><"'}, {'number':1, 'result':'SUCCESS'}))
    '<img src="chrome/common/extlink.gif">&gt;&lt;&#34; #1 - build-success</a>'
    '''
    FORMAT = '<img src="chrome/common/extlink.gif">%s #%s - %s</a>'
    build_number = Markup.escape(str(build['number']))
    job_name = Markup.escape(job['name'])
    return Markup(FORMAT % (job_name, build_number, get_build_kind(build)))

def get_build_comment(build, formated_build_time):
    '''Return build comment for timeline.

    Add build message when exists.
    >>> str(get_build_comment({'result': 'SUCCESS', 'description': 'MSG'}, 'TIME'))
    'MSG at TIME'

    But if no build comment, only add simple build message.
    >>> str(get_build_comment({'result': 'SUCCESS', 'description': None}, 'TIME'))
    'Build finished successfully at TIME'

    '''
    kind = get_build_kind(build)
    message = BUILD_MESSAGES[kind]

    if build['description'] is None:
        return message + ' at ' + formated_build_time
    else:
        return unicode(build['description'], 'utf-8') + ' at ' + formated_build_time

def get_build_ref_markup(nav_url, jobs, content):
    '''Return build reference markup expanded by RefHudsonBuild macro.

    ex1. [[RefHudsonBuild(j3, 1)]
    >>> str(get_build_ref_markup('http://example.com/hudson/', ['j1','j2'], 'j3,1'))
    '<a class="ext-link" href="http://example.com/hudson/job/j3/1/"><span class="icon"></span>Hudson: j3#1</a>'
    
    ex2. [[RefHudsonBuild(1)] ; jobs = [j1, j2]
    >>> str(get_build_ref_markup('http://example.com/hudson/', ['j1','j2'], '1'))
    '<a class="ext-link" href="http://example.com/hudson/job/j1/1/"><span class="icon"></span>Hudson: j1#1</a>'

    Also, _markup functions must be charcter-escaped.
    >>> str(get_build_ref_markup('spam/', ['j1','j2'], '><",1'))
    '<a class="ext-link" href="spam/job/&gt;&lt;&#34;/1/"><span class="icon"></span>Hudson: &gt;&lt;&#34;#1</a>'
    >>> str(get_build_ref_markup('spam/', ['><"','j2'], '1'))
    '<a class="ext-link" href="spam/job/&gt;&lt;&#34;/1/"><span class="icon"></span>Hudson: &gt;&lt;&#34;#1</a>'

    '''
    FORMAT = '<a class="ext-link" href="%sjob/%s/%s/"><span class="icon"></span>Hudson: %s#%s</a>'
    args = map(lambda x: x.strip(), str(content).split(','))
    if len(args) == 1:
        if len(jobs) == 0:
            return ''
        job_name = Markup.escape(jobs[0].strip())
        job_no = Markup.escape(args[0])
    else:
        job_name = Markup.escape(args[0])
        job_no = Markup.escape(args[1])

    return Markup(FORMAT % (nav_url, job_name, job_no, job_name, job_no))
