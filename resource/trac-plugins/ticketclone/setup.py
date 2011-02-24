#!/usr/bin/env python

from setuptools import setup, find_packages

PACKAGE = 'TicketClonePlugin'
VERSION = '0.1'

setup (
    name = PACKAGE,
    version = VERSION,
    description = 'Clone ticket from exsiting ticket.',
    license='BSD', 
    packages = ['.'],
    package_data = { },
    entry_points = {
        'trac.plugins': [
            'ticket_clone = ticket_clone',
        ]
    },
)
