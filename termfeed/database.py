#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database operations.

dbop.py manipulate database add, update, delete
"""

import shelve, yaml
from os import path

class DataBase:

    def rebuild_library(self):
        # import termfeed.dbinit
        if not path.exists('rss.yaml'):
            from termfeed.urls import rss
            with open('rss.yaml', 'w') as f:
                f.write(yaml.dump(rss, default_flow_style=False))

        with open('rss.yaml', 'r') as f:
            rss = yaml.load(f)

        with shelve.open(self.file) as d:
            for topic in rss:
                links = rss[topic]
                d[topic] = [link for link in links]

            print('created ".termfeed" in {}'.format(path.dirname(self.file)))

    def __init__(self):
        homedir = path.expanduser('~')

        self.file = path.join(homedir, '.termfeed')

        # instantiate db if it's not created yet
        if not (path.exists(self.file + '.dir')
                or path.exists(self.file + '.dat')):
            self.rebuild_library()

        # connect to db
        self.db = shelve.open(self.file, 'w')


    def __del__(self):
        self.db.close()

    @property
    def topics(self):
        return list(self.db.keys())


    def read(self, topic):
        if topic in self.topics:
            return self.db[topic]
        else:
            return None

    def browse_links(self, topic):
        if topic in self.topics:
            links = self.db[topic]
            print('{} resources:'.format(topic))
            for link in links:
                print('\t{}'.format(link))
        else:
            print('no category named {}'.format(topic))
            print_topics(d)

    def __repr__(self):
        out = 'available topics: \n\t' + '\n\t'.join(self.topics)
        return(out)

    def print_topics(self, d = None):
        print(self)

    def add_link(self, link, topic='General'):
        if topic in self.topics:
            if link not in d[topic]:
                # to add a new url: copy, mutates, store back
                temp = d[topic]
                temp.append(link)
                self.db[topic] = temp
                print('Updated .. {}'.format(topic))
            else:
                print('{} already exists in {}!!'.format(link, topic))
        else:
            print('Created new category .. {}'.format(topic))
            self.db[topic] = [link]


    def remove_link(self, link):
        done = False
        for topic in self.topics:
            if link in self.db[topic]:
                self.db[topic] = [l for l in self.db[topic] if l != link]
                print('removed: {}\nfrom: {}'.format(link, topic))
                done = True

        if not done:
            print('URL not found: {}'.format(link))


    def delete_topic(self, topic):
        if topic == 'General':
            print('Default topic "General" cannot be removed.')
            exit()
        try:
            del self.db[topic]
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
