from setuptools import find_packages, setup

setup(
    name='TracMailArchive',
    author='wadahiro',
    author_email='wadahiro@gmail.com',
    version='0.1.4-SNAPSHOT',
    license = "New BSD",
    packages=find_packages(exclude=['*.tests*']),
    package_data={'mailarchive': ['templates/*.html',
                                 'htdocs/css/*.css',
                                 'htdocs/png/*']},
    entry_points = {
        'trac.plugins': [
            'mailarchive.web_ui = mailarchive.web_ui',
            'mailarchive.env = mailarchive.env',
            'mailarchive.wikisyntax = mailarchive.wikisyntax',
        ],
        'console_scripts': [
            'TracMailArchive-admin = mailarchive:run'
        ]
    }
)
