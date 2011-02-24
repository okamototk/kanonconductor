#!/usr/bin/python

from tracnav import __version__ as VERSION
from setuptools import setup

setup(
    name = 'TracNav',
    version = VERSION,
    packages = ['tracnav'],
    package_data = { 'tracnav': ['htdocs/css/*.css'] },
    author = 'Bernhard Haumacher',
    author_email = 'haui@haumacher.de',
    maintainer = 'Thomas Moschny',
    maintainer_email = 'thomas.moschny@gmx.de',
    url = 'http://svn.ipd.uka.de/trac/javaparty/wiki/TracNav',
    download_url = 'http://svn.ipd.uka.de/trac/javaparty/wiki/TracNav/DownloadAndInstall',
    description = 'The Navigation Bar for Trac',
    entry_points={'trac.plugins': ['TracNav = tracnav.tracnav']},
    keywords = 'trac toc plugin',
    license = 'GPLv2+',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Trac',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    )
