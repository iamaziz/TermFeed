#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database operations.

dbop.py manipulate database add, update, delete
"""

import yaml, json, re
from plumbum import local
from os import path
from cached_property import cached_property
from pathlib import Path



class DataBase:

    file = local.env.home / '.termfeed.json'

    debug_flag = False

    def debug(self, *args, **kwargs):
        if self.debug_flag:
            print(*args, **kwargs)

    def rebuild_library(self, file = None):
        # force type local.path
        file = local.path(file) if file else local.path(__file__).dirname / 'rss.yaml'
        if not file.exists():
            raise FileNotFoundError(file)
        with open(file, 'r') as f:
            self.rss = yaml.load(f)

        print('created ".termfeed" in {}'.format(file.dirname))

    @property
    def as_yaml(self):
        return yaml.dump(self.rss, default_flow_style=False)

    @property
    def as_yaml_v2(self):
        import collections
        data = collections.defaultdict(dict)
        for topic in self.rss:
            for link in self.rss[topic]:
                data[link].setdefault('label', []).append(topic)

        r = re.compile(r'(\w+)(?:/commits/\w+\.atom|\.git)')

        for link in data:
            if 'git' in link:
                data[link].setdefault('flag', []).append('git')

                # ToDo: catch exeption
                title, = r.findall(link)#summary_detail.base)
                data[link]['title'] = title

        return yaml.dump(dict(data))

    #def __init__(self):
    #    print(self.rss == self.rss)

    def save_on_fs_if_changed(self):
        if not self.__rss == self.rss:
            print('Backup changed library in {}.'.format(self.file))
            with open(self.file, 'w') as f:
                json.dump(self.__rss, f)

    __rss = None

    @cached_property
    def rss(self):
        # The following will only called once
        self.debug('Load library')
        if not self.__rss:
            if not self.file.exists():
                try:
                    file = local.path(file) if file else local.path(__file__).dirname / 'rss.yaml'
                except UnboundLocalError:
                    file = local.path(self.file) \
                        if self.file else local.path(__file__).dirname / 'rss.yaml'

                if not file.exists():
                    raise FileNotFoundError(file)
                with open(file, 'r') as f:
                    return yaml.load(f)
            else:
                with open(self.file, 'r') as f:
                    self.__rss = json.load(f)
        return self.__rss.copy() # ensure copy, for comp in __del__

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
                #temp = self.rss[topic]
                #temp.append(link)
                #self.rss[topic] = temp
                self.rss.append(link)
                print('Updated .. {}'.format(topic))
            else:
                print('{} already exists in {}!!'.format(link, topic))
        else:
            print('Created new category .. {}'.format(topic))
            self.rss[topic] = [link]

    def remove_link(self, link):
        done = False
        for topic in self.topics:
            if link in self.rss[topic]:
                self.rss[topic] = [l for l in self.rss[topic] if l != link]
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
