#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'LightningTheme',
    version = '1.0',
    packages = ['lightningtheme'],
    package_data = { 'lightningtheme': ['templates/*.html', 'htdocs/*.png', 'htdocs/*.css', 'htdocs/img/*.png', 'htdocs/img/*.jpg' ] },

    author = 'Takashi Okamoto',
    author_email = 'okamototk@nospam.sf.jp',
    description = 'A theme for TracLightning.',
    license = 'BSD',
    keywords = 'trac plugin theme',
    url = 'http://sourceforge.jp/projects/shibuya-trac/wiki/FrontPage',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['Trac', 'TracThemeEngine>=2.0'],

    entry_points = {
        'trac.plugins': [
            'lightningtheme.theme = lightningtheme.theme',
        ]
    },
)
