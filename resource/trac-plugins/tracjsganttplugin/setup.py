#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'Trac-jsGantt',
    author = 'Chris Nelson',
    author_email = 'Chris.Nelson@SIXNET.com',
    description = 'Trac plugin displaying jsGantt charts in Trac',
    version = '0.2.0-ja',
    url = 'http://trac-hacks.org/wiki/TracJsGanttPlugin',
    license='BSD',
    packages=['tracjsgantt'],
    package_data = { 'tracjsgantt': ['htdocs/*.js', 'htdocs/*.css'] },
    entry_points = {
        'trac.plugins': [
            'tracjsgantt = tracjsgantt'
        ]
    }
)
