#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database operations.

database.py manipulate database add, update, delete
"""

import yaml, json, re
from plumbum import local
from plumbum import colors as c
from os import path
from cached_property import cached_property
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

log_info = logger.info
log_debug = logger.debug


class DataBase:

    file = local.env.home / '.termfeed.json'
    __data = None
    dry_run = False

    @cached_property
    def data(self):
        # The following will only called once
        log_info('Load library')
        if not self.__data:
            if not self.file.exists():
                file = local.path(__file__).dirname / 'db.yaml'
                if not file.exists():
                    raise FileNotFoundError(file)
                with open(file, 'r') as f:
                    log_info('Open yaml')
                    return yaml.load(f)
            else:
                with open(self.file, 'r') as f:
                    log_info('Open json')
                    self.__data = json.load(f)
        return self.__data.copy()  # ensure copy, for comp in __del__

    # def set_data(self, data):
    #     verify_data(data)
    #     self.__data = data
    #     del self.data
    #     with self:
    #         pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # type, value, traceback
        verify_data(self.data)
        if not self.dry_run:
            print('Backup changed library in {}.'.format(self.file))
            with open(self.file, 'w') as f:
                json.dump(self.data, f)
                log_info('Write to json')
                log_debug(json.dumps(self.data))
                log_debug(self.as_yaml)
        else:
            print('Normaly would write the following to file {}: '.format(self.file))
            print(c.highlight | c.black | json.dumps(self.data))

    debug_flag = False

    @property
    def labels(self):
        labels = set()
        for _, val in self.data.items():
            labels |= set(val['label'])
        return labels

    @property
    def as_yaml(self):
        return yaml.dump(self.data)  # , default_flow_style=False

    def link_for_label(self, *labels):
        return [link for link, val in self.data.items() if any(True for l in labels if l in val['label'])]

    @property
    def links(self):
        return self.data.keys()

    def browse_links(self, label):
        if label in self.labels:
            links = self(label)
            print('{} resources:'.format(label))
            for link in links:
                print('\t{}'.format(link))
        else:
            print('no category named {}'.format(label))
            print(self)

    def __str__(self):
        out = 'available lables: \n\t' + '\n\t'.join(self.labels)
        return(out)

    def print_labels(self):
        print(self)

    def link_as_yaml(self, link):
        return yaml.dump({link:self.data[link]})

    def add_link(self, link, *labels, flag = None, title=''):
        if link not in self.data:
            if not flag:
                flag = []
            template = dict(title=title, flag=flag, label=list(labels))
            self.data[link] = verify_entry(template, link)
            print('Added:')
            print(self.link_as_yaml(link))
            if logger.level <= logging.INFO:
                print(self.as_yaml)
        elif not title == '' or not title == self.data[link]['title']:
            self.data[link]['label'] = list(set(self.data[link]['label']) | set(labels))
            self.data[link]['title'] = title
            log_info('Title has changed')
            print(self.as_yaml)

        elif set(labels) | set(self.data[link]['label']) == set(self.data[link]['label']):
            print('{} already exists and has all labels: {}!!'.format(link, labels))
            print(self.as_yaml)
        else:
            self.data[link]['label'] = list(set(self.data[link]['label']) | set(labels))
            # print('Created new category .. {}'.format(topic))
            print(self.link_as_yaml(link))
            if logger.level <= logging.INFO:
                print(self.as_yaml)

    def remove_link(self, link):
        done = False
        if link in self.data:
            del self.data[link]
            print('removed: {}'.format(link))
        else:
            print('URL not found: {}'.format(link))

    def delete_topic(self, label):
        if label == '':
            print('Default topic "General" cannot be removed.')
            exit()
        try:
            for link in self.data:
                if label in self.data[link]['label']:
                    self.data[link]['label'] = list(set(self.data[link]['label']) - set(label))
            print('Removed "{}" from your library.'.format(label))
        except KeyError:
            print('"{}" is not in your library!'.format(label))
            exit()


def verify_entry(entry, link):
    allowed_keys = {'label', 'flag', 'title'}
    if not entry:
        entry = dict()
    if not (entry.keys() | allowed_keys) == allowed_keys:
        print('The url {} has invalid keys: '.format(link), entry)
        exit()
    if not isinstance(entry.setdefault('title', ''), str):
        print('The url {} has invalid title member: {}'.format(link, entry['title']))
        exit()
    if not isinstance(entry.setdefault('flag', []), list):
        print('The url {} has invalid flag type: {}'.format(link, entry['flag']))
        exit()
    if not all([isinstance(f, str) for f in entry['flag']]):
        print('The url {} has invalid flag member: {}'.format(link, entry['flag']))
        exit()
    if not isinstance(entry.setdefault('label', []), list):
        print('The url {} has invalid flag type: {}'.format(link, entry['label']))
        exit()
    if not all([isinstance(l, str) for l in entry['label']]):
        print('The url {} has invalid flag member: {}'.format(link, entry['label']))
        exit()
    return entry


def verify_data(data):
    for link in data:
        data[link] = verify_entry(data[link], link)

# if __name__ == '__main__':

#     for l in read('News'):
#         print(l)

#     remove_link('http://rt.com/rss/')

#     add_link('http://rt.com/rss/', 'News')

#     for l in read('News'):
#         print(l)
