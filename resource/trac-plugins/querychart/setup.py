# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='TracQueryChart',
    version='0.2.2',
    author='Kazuya Hirobe',
    author_email = "k.hirobe@gmail.com",
    description = "Provides macro to draw ticket chart.",
    license = "New BSD",
    keywords = "trac plugin chart ticket query",
    url='',
    zip_safe=True,
    packages=['querychart'],
    package_data={
        'querychart': ['templates/*.html','htdocs/js/*.js','htdocs/js/flot/*.js']
        },
    entry_points={
        'trac.plugins': 'TracQueryChart = querychart'
        },
    )
