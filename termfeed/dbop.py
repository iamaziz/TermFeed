#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database operations.

dbop.py manipulate database add, update, delete
"""

import shelve
from os import path
from termfeed.urls import rss

homedir = path.expanduser('~')

# connect to db
d = shelve.open(path.join(homedir, '.termfeed'), 'w')

def rebuild_library():
    # dump urls.py into rss_shelf.db
    d.clear()
    for topic in rss:
        links = rss[topic]
        d[topic] = [link for link in links]


def topics():
    return d.keys()


def read(topic):
    if topic in d.keys():
        return d[topic]
    else:
        return None


def browse_links(topic):
    if topic in d.keys():
        links = d[topic]
        print('{} resources:'.format(topic))
        for link in links:
            print('\t{}'.format(link))
    else:
        print('no category named {}'.format(topic))
        print_topics()


def print_topics():
    print('available topics: ')
    for t in topics():
        print('\t{}'.format(t))


def add_link(link, topic='General'):

    if topic in d.keys():
        if link not in d[topic]:
            # to add a new url: copy, mutates, store back
            temp = d[topic]
            temp.append(link)
            d[topic] = temp
            print('Updated .. {}'.format(topic))
        else:
            print('{} already exists in {}!!'.format(link, topic))
    else:
        print('Created new category .. {}'.format(topic))
        d[topic] = [link]


def remove_link(link):

    done = False
    for topic in topics():
        if link in d[topic]:
            d[topic] = [l for l in d[topic] if l != link]
            print('removed: {}\nfrom: {}'.format(link, topic))
            done = True

    if not done:
        print('URL not found: {}'.format(link))


def delete_topic(topic):
    if topic == 'General':
        print('Default topic "General" cannot be removed.')
        d[topic] = []
        exit()
    try:
        del d[topic]
        print('Removed "{}" from your library.'.format(topic))
    except KeyError:
        print('"{}" is not in your library!'.format(topic))
        exit()


# if __name__ == '__main__':

#     for l in read('News'):
#         print(l)

#     remove_link('http://rt.com/rss/')

#     add_link('http://rt.com/rss/', 'News')

#     for l in read('News'):
#         print(l)
