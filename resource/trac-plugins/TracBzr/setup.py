#!/usr/bin/python

from setuptools import setup

readme=file('README').read()
readme=readme[:readme.index('\n.. cut long_description here')]

# see http://docs.python.org/distutils/setupscript.html#meta-data
# and http://docs.python.org/distutils/apiref.html
# for a list of meta data to be included here.
setup(
    name='TracBzr',
    description='Bazaar plugin for Trac',
    keywords='trac vcs plugin bazaar bzr',
    version='0.4.2',
    url='http://launchpad.net/trac-bzr',
    license='GPL',
    author='Trac Bazaar Team',
    author_email='trac-bzr-team@lists.launchpad.net',
    long_description=readme,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Trac',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Version Control',
        # see http://pypi.python.org/pypi?:action=list_classifiers for more
    ],
    packages=['tracbzr'],
    entry_points={'trac.plugins': 'bzr = tracbzr.backend'},
#    install_requires=[
#        'Trac >=0.10, <0.13',
#        'bzr >= 2.0',
#    ],
)
