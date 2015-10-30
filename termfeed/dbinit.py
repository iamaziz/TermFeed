#!/usr/bin/env python

# This should be exectued once to initialize the db from urls.py

import shelve
from os import path

homedir = path.expanduser('~')

# initiate database datafile
d = shelve.open(path.join(homedir, '.termfeed'))
d.close()
