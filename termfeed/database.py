#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database operations.

dbop.py manipulate database add, update, delete
"""

import yaml, json
from os import path
from cached_property import cached_property

class DataBase:

    file = path.join(path.expanduser('~'), '.termfeed.json')

    def rebuild_library(self):

        with open(path.join(path.dirname(__file__), 'rss.yaml'), 'r') as f:
            rss = yaml.load(f)

        self.save_rss_on_fs(rss)
        print('created ".termfeed" in {}'.format(path.dirname(self.file)))

    def __init__(self):

        # instantiate db if it's not created yet
        if not (path.exists(self.file)):
            self.rebuild_library()

        with open(self.file, 'r') as f:
            self.rss = json.load(f)

    def save_rss_on_fs(self, rss):
        with open(self.file+'.json', 'w') as f:
            json.load(rss, f)

    @property
    def topics(self):
        return self.rss.keys()
        # return list(self.db.keys())

    def read(self, topic):
        if topic in self.topics:
            return self.rss[topic]
        else:
            return None

    def browse_links(self, topic):
        if topic in self.topics:
            links = self.rss[topic]
            print('{} resources:'.format(topic))
            for link in links:
                print('\t{}'.format(link))
        else:
            print('no category named {}'.format(topic))
            print(self)

    def __str__(self):
        out = 'available topics: \n\t' + '\n\t'.join(self.topics)
        return(out)

    def print_topics(self):
        print(self)

    def add_link(self, link, topic='General'):
        if topic in self.topics:
            if link not in self.rss[topic]:
                # to add a new url: copy, mutates, store back
                temp = self.rss[topic]
                temp.append(link)
                self.rss[topic] = temp
                self.save_rss_on_fs(rss)
                print('Updated .. {}'.format(topic))
            else:
                print('{} already exists in {}!!'.format(link, topic))
        else:
            print('Created new category .. {}'.format(topic))
            self.rss[topic] = [link]
            self.save_rss_on_fs(rss)


    def remove_link(self, link):
        done = False
        for topic in self.topics:
            if link in self.rss[topic]:
                self.rss[topic] = [l for l in self.rss[topic] if l != link]
                self.save_rss_on_fs(rss)
                print('removed: {}\nfrom: {}'.format(link, topic))
                done = True

        if not done:
            print('URL not found: {}'.format(link))


    def delete_topic(self, topic):
        if topic == 'General':
            print('Default topic "General" cannot be removed.')
            exit()
        try:
            del self.rss[topic]
            self.save_rss_on_fs(rss)
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
