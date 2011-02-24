from trac.core import *

from themeengine.api import ThemeBase

class LightningTheme(ThemeBase):
    """A theme for TracLightning."""

    template = htdocs = css = screenshot = True
    
