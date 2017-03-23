#!/usr/bin/env python
#-*- coding: utf-8 -*-

from .feed import _connected, main

if __name__ == '__main__':

    if not _connected():
        print('No Internet Connection!')
        exit()

    main()
