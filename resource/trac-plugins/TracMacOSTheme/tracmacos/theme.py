# Copyright (c) 2010 Olemis Lang. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from trac.core import *
from trac.config import Option, IntOption, ListOption
from trac.util.translation import _
from trac.web.chrome import add_script
from trac.web.api import IRequestFilter

from genshi.builder import Markup, Element, Fragment, tag
from genshi.input import XML
from genshi.util import striptags

from themeengine.api import ThemeBase

try :
  from trac.config import ChoiceOption, FloatOption
except ImportError :
  from trac.util.text import to_unicode
  
  def _to_utf8(basestr):
    return to_unicode(basestr).encode('utf-8')
  
  class FloatOption(Option):
    """Descriptor for float configuration options."""
    def accessor(self, section, name, default):
       value = section.get(name, default)
       if not value:
         return 0.0
       try:
         return float(value)
       except ValueError:
         raise ConfigurationError(
                 _('[%(section)s] %(entry)s: expected float, got %(value)s',
                   section=self.name, entry=name, value=repr(value)))
  
  class ChoiceOption(Option):
    """Descriptor for configuration options providing a choice among a list
    of items.
    
    The default value is the first choice in the list.
    """
    
    def __init__(self, section, name, choices, doc=''):
      Option.__init__(self, section, name, _to_utf8(choices[0]), doc)
      self.choices = set(_to_utf8(choice).strip() for choice in choices)
    
    def accessor(self, section, name, default):
      value = section.get(name, default)
      if value not in self.choices:
        raise ConfigurationError(
                      _('[%(section)s] %(entry)s: expected one of '
                        '(%(choices)s), got %(value)s',
                        section=section.name, entry=name, value=repr(value),
                        choices=', '.join('"%s"' % c
                                          for c in sorted(self.choices))))
      return value

class MappingOption(ListOption):
    """Descriptor for configuration options that contain multiple 
    key-value pairs separated by a specific character."""
    
    def __init__(self, section, name, default=None, sep=',', itemsep=':',
                 doc=''):
        Option.__init__(self, section, name, default, doc)
        self.sep = sep
        self.itemsep = itemsep
    
    def accessor(self, section, name, default):
        value = section.getlist(name, default, self.sep, False)
        return dict(filter(lambda itm: len(itm) == 2, 
                        (itm.split(self.itemsep, 1) for itm in value))) 

class MacTheme(ThemeBase):
    """A theme for Trac based on Mac OS appearance."""
    implements(IRequestFilter)
    dock_images = MappingOption('docknav', 'images', 
                                'wiki:/chrome/theme/dk_wiki.png,'
                                'admin:/chrome/theme/galternatives.png,'
                                'search:/chrome/theme/dk_search.png,'
                                'browser:/chrome/theme/Documents.png,'
                                'timeline:/chrome/theme/dk_timeline.png,'
                                'pydoc:/chrome/theme/dk_pydoc.png,'
                                'newticket:/chrome/theme/emblem-draft.png,'
                                'tickets:/chrome/theme/gthumb.png,'
                                'downloader:/chrome/theme/dk_downl.png,'
                                'ticketcalendar:/chrome/theme/calendar.png,'
                                'ticketgantt:/chrome/theme/GantChart.png,'
                                'builds:/chrome/theme/hudmi.png,'
                                'burndown:/chrome/theme/burndown.png,'
                                'mailarchive:/chrome/theme/stock_mail-open.png,'
                                'Billing:/chrome/theme/text-spreadsheet.png,'
                                'worktime:/chrome/theme/text-spreadsheet.png,'
                                'importer:/chrome/theme/gnome-mime-application-vnd.ms-excel.png,'
                                'roadmap:/chrome/theme/gnome-mines.png',
                                doc="Images rendered in dock menu.")
    dock_default = Option('docknav', 'default', '/chrome/theme/dk_default.png',
                                doc="Catch-all image in dock menu.")
    dock_coefficient = FloatOption('docknav', 'coefficient', default=0.8,
                                doc="Attenuation coefficient. This controls "
                                    "the relationship between the distance "
                                    "from the cursor and the amount of "
                                    "expansion of any affected image within "
                                    "that distance. A coefficient of 1 makes "
                                    "the expansion linear with respect to "
                                    "distance from cursor; a larger "
                                    "coefficient gives a greater degree of "
                                    "expansion the closer to the cursor the "
                                    "affected image is (within distance).")
    dock_distance = IntOption('docknav', 'distance', default=40,
                                doc="Attenuation distance from cursor, ie "
                                    "the distance (in pixels) from the "
                                    "cursor that an image has to be within "
                                    "in order to have any expansion applied. "
                                    "Note that attenuation is always "
                                    "calculated as if the Dock was 'at rest'"
                                    " (no images expanded), even though "
                                    "there may be expanded images at "
                                    "the time.")
    dock_duration = IntOption('docknav', 'duration', default=300,
                                doc="The duration (in milliseconds) of the"
                                    " initial 'on-Dock' expansion, and the "
                                    "'off-Dock' shrinkage.")
    dock_fadeIn = IntOption('docknav', 'fadeIn', default=1000,
                                doc="The amount of time (in milliseconds) "
                                    "for the initial fade-in of the Dock "
                                    "after initialisation. By default this "
                                    "is set to 1000, which means that the "
                                    "Dock is displayed in full 1 second "
                                    "after it's initialized. Set this "
                                    "value to 0 (zero) to remove the effect.")
    dock_fadeLayer = ChoiceOption('docknav', 'fadeLayer', 
                                ('', 'wrap', 'dock'),
                                doc="By default the fade-in effect "
                                    "is applied to the original target menu "
                                    "element. By specifying either 'wrap' or "
                                    "'dock' here, the fade-in element can "
                                    "be switched to the child or "
                                    "grand-child of the original "
                                    "target menu element. This "
                                    "option only has any effect if "
                                    "fadeIn is set, and is really "
                                    "only useful for cases where, "
                                    "for example, background colours "
                                    "have been styled on the original "
                                    "menu element and you don't want "
                                    "them to be faded in.")
    dock_inactivity = IntOption('docknav', 'inactivity', default=4000,
                                doc="The period of time (in milliseconds)"
                                    " after which the Dock will shrink if "
                                    "there has been no movement of the mouse"
                                    " while it is over an expanded Dock. "
                                    "Set to 0 (zero) to disable the "
                                    "inactivity timeout .")
    dock_labels = ChoiceOption('docknav', 'labels', ('tl', 'tc', 'tr', '',
                                                     'ml', 'mc', 'mr', 
                                                     'bl', 'bc', 'br'),
                                doc="This enables/disables display of a "
                                    "label on the current image. Allowed "
                                    "string values are 2 characters in "
                                    "length: the first character indicates "
                                    "horizontal position (t=top, "
                                    "m=middle, b=bottom) and the second "
                                    "indicates vertical position (l=left, "
                                    "c=center, r=right). Default is 'tl' "
                                    "(i.e. labels shown in top-left corner). "
                                    "Please be aware that enabling this "
                                    "option with one of the middle/center "
                                    "label positions (eg. 'ml', 'bc', etc) "
                                    "may have a slight effect on the "
                                    "performance of the Dock, simply due "
                                    "to the additional processing required "
                                    "to position the label correctly. Hide "
                                    "labels by leaving this option empty.")
    dock_step = IntOption('docknav', 'step', default=50,
                                doc="The timer interval (in milliseconds) "
                                    "between each animation step of the "
                                    "'on-Dock' expansion, and the "
                                    "'off-Dock' shrinkage.")
    tb_count = IntOption('macos', 'tbcount', default=5,
                                doc="Number of fixed items in toolbar ")
    
    template = htdocs = css = screenshot = True
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        self._prepare_request(req)
        self._prepare_chrome_for_fail(req)
        return handler
    
    def post_process_request(self, req, template, data, content_type):
#        self._prepare_request(req)
        self._add_macos_scripts(req)
        return template, data, content_type
    
    # Internal methods
    def _add_macos_scripts(self, req):
        add_script(req, '/chrome/theme/jquery.jqDock.min.js')
        add_script(req, '/chrome/theme/animatedcollapse.js')
        add_script(req, '/chrome/theme/jquery.cookie.js')
        
    def _prepare_request(self, req):
        def to_text(fragment):
          if isinstance(fragment, (Element, Fragment, Markup)):
            return striptags(unicode(fragment))
          else:
            return unicode(fragment)
        def extract_href(fragment):
          if isinstance(fragment, (Element, Fragment)):
            stream = tag.body(fragment).generate()
          else :
            self.log.debug("Extracting href from %s", fragment)
            stream = XML('<body>%s</body>' % (unicode(fragment),))
          for x in stream.select('a[@href]') :
            if x[0] == 'START' :
               return x[1][1].get('href')
        
        req.macos = {
              'opts' : {
                  'coefficient' : self.dock_coefficient,
                  'distance' : self.dock_distance,
                  'duration' : self.dock_duration,
                  'fadeIn' : self.dock_fadeIn,
                  'fadeLayer' : "'" + self.dock_fadeLayer + "'",
                  'inactivity' : self.dock_inactivity,
                  'labels' : "'" + self.dock_labels + "'",
                  'step' : self.dock_step,
                  },
              'tb_count': self.tb_count,
              'util' : {
                  'striptags' : to_text,
                  'extract_href' : extract_href,
                  },
              'imgs' : {
                  'dock_default' : self.dock_default,
                  'dock' : self.dock_images,
                  },
            }
    
    def _prepare_chrome_for_fail(self, req):
        old_prepare_chrome = req.callbacks['chrome']
        
        def macos_prepare_request(_):
            req.chrome = value = old_prepare_chrome(req)
            self._add_macos_scripts(req)
            return value
            
        req.callbacks['chrome'] = macos_prepare_request
        
