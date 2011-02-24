# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='TracXdocView',
    version='0.1',
    author='Kazuya Hirobe',
    author_email='',
    url='',
    description='',
    packages=['xdocview'],
    entry_points={
        'trac.plugins': 'TracXdocView = xdocview'
        },
    )

