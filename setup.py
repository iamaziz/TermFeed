#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='TermFeed',
    description=('Browse, read, and open your favorite rss feed in the terminal (without curses).'),
    author='Aziz Alto',
    url='https://github.com/iamaziz/TermFeed',
    download_url='https://github.com/iamaziz/TermFeed/archive/master.zip',
    license = "MIT",
    author_email='iamaziz.alto@gmail.com',
    version='0.0.9',
    install_requires=['feedparser'],
    packages=['termfeed', 'termfeed.support'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'feed = termfeed.feed:main'
        ]
    }
)
