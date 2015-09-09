#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='TermFeed',
    summary='Minimal feed reader for terminal.',
    description='Browse, read, and open your favorite rss feed in the terminal (without curses).',
    author='Aziz Alto',
    url='https://github.com/iamaziz/TermFeed',
    download_url='https://github.com/iamaziz/TermFeed/archive/master.zip'
    author_email='iamaziz.alto@gmail.com',
    version='0.0.5',
    install_requires=['feedparser'],
    packages=['termfeed', 'termfeed.support'],
    scripts=[],
    keyword='terminal rss feed reader command line',
    entry_points={
        'console_scripts': [
            'feed = termfeed.feed:main'
        ]
    }
)
