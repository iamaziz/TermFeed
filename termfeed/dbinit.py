#!/usr/bin/env python

# This should be exectued once to initialize the db from urls.py

import shelve
from os import path

from termfeed.urls import rss

homedir = path.expanduser('~')

# initiate database datafile
d = shelve.open(path.join(homedir, '.termfeed.db'))


# dump urls.py into rss_shelf.db
for topic in rss:
	links = rss[topic]
	d[topic] = [link for link in links]

d.close()
