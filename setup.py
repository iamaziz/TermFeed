#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='TermFeed',
    description=(
        'Browse, read, and open your favorite rss feed in the terminal (without curses).'),
    author='Aziz Alto',
    url='https://github.com/iamaziz/TermFeed',
    download_url='https://github.com/iamaziz/TermFeed/archive/master.zip',
    license="MIT",
    author_email='iamaziz.alto@gmail.com',
    version='0.0.12',
    install_requires=[
        'feedparser',
        'pyyaml',
        'docopt',
        'plumbum',
        'arrow',
        'cached-property>=1.3.0',
    ],
    packages=['termfeed'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'feed = termfeed.feed:main'
        ]
    }
)
