#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'HudsonTracPlus',
    version = '0.4',
    author = "Itou Akihiro",
    author_email = "itou.akihiro@gmail.com",
    description = "An advanced trac plugin to cooperate with hudson. Forked from HudsonTrac Plugin (c) Ronald Tschalär. http://trac-hacks.org/wiki/HudsonTracPlugin",
    license = "BSD",
    keywords = "trac builds hudson",
    url = "http://sourceforge.jp/projects/shibuya-trac/wiki/HudsonTracPlusPlugin",

    packages = ['HudsonTracPlus'],
    package_data = {
        'HudsonTracPlus' : ['htdocs/*.css', 'htdocs/*.png', 'htdocs/*.gif']
    },
    entry_points = {
        'trac.plugins' : [ 'HudsonTracPlus = HudsonTracPlus.HudsonTracPlusPlugin' ]
    }
)
