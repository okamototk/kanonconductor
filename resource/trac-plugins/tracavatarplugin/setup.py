#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='TracAvatarPlugin',
    version='0.3',
    zip_safe = True,
    packages=find_packages(exclude=['*.tests*']),

    author = "Takashi Okamoto",
    author_email='okamototk@user.sourceforge.jp',
    url="http://sourceforge.jp/projects/shibuya-trac/",
    description='Avatar Support for Trac',
    license = "New BSD",

    entry_points = {
        'trac.plugins': [
            'tracavatar.web_ui = tracavatar.web_ui',
        ]
    },
    package_data={'tracavatar': [
'htdocs/js/avatar.js']},
)
