#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
TermFeed 0.0.11: Command Line RSS Feed Manager

Commands:
    feed                 - Lists feeds from 'General' category.
    feed <rss-url>       - Lists feeds from provided RSS URL.
    feed -b              - Browses feeds by category.
    feed -a <url> [cat]  - Adds new RSS URL to [cat] (default: 'General').
    feed -d <rss-url>    - Deletes specified RSS URL from database.
    feed -t [cat]        - Shows categories or URLs under a category.
    feed -D <cat>        - Deletes a category and its URLs.
    feed -R              - Rebuilds library from url.py.
    feed (-h | --help)   - Displays help screen.
    feed --version       - Shows TermFeed version.
"""


from __future__ import print_function
import sys
import webbrowser
import feedparser
import re

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

import termfeed.dbop as dbop


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except:
        return False


def open_page(url, title):
    print(bcolors.WARNING +
          '\topening ... {}\n'.format(title.encode('utf8')) + bcolors.ENDC)
    # open page in browser
    webbrowser.open(url)


def print_feed(zipped):

    for num, post in zipped.items():
        print(bcolors.OKGREEN + '[{}] '.format(num) + bcolors.ENDC, end='')
        print('{}'.format(post.title.encode('utf8')))


def print_desc(topic, txt):
    try:
        print(bcolors.WARNING + '\n\n{}:'.format(topic) + bcolors.ENDC)
    except UnicodeEncodeError:
        pass
    print(bcolors.BOLD + '\n\t{}'.format(txt.encode('utf8')) + bcolors.ENDC)


def open_it():
    try:
        txt = '\n\n\t Open it in browser ? [y/n] '
        try:
            q = raw_input(txt)  # python 2
        except NameError:
            q = input(txt)  # python 3

        print('\n')
        if q == 'y':
            return True
    except KeyboardInterrupt:
        print('\n')
        return False

def clean_txt(txt):
    """clean txt from e.g. html tags"""
    cleaned = re.sub(r'<.*?>', '', txt) # remove html
    cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>') # retain html code tags
    cleaned = cleaned.replace('&quot;', '"')
    cleaned = cleaned.replace('&rsquo;', "'")
    cleaned = cleaned.replace('&nbsp;', ' ') # italized text
    return cleaned

def _continue():
    try:

        msg = """\n\nPress: Enter to continue, ... [NUM] for short description / open a page, ... or CTRL-C to exit: """
        print(bcolors.FAIL + msg + bcolors.ENDC, end='')
        # kb is the pressed keyboard key
        try:
            kb = raw_input()
        except NameError:
            kb = input()
        return kb

    except KeyboardInterrupt:
        # return False
        exit()


def parse_feed(url):

    d = feedparser.parse(url)

    # validate rss URL
    if d.entries:
        return d
    else:
        print("INVALID URL feed: {}".format(url))
        return None


def fetch_feeds(urls):

    for i, url in enumerate(urls):

        d = parse_feed(url)

        if d is None:
            continue  # to next url

        # feeds source
        l = len(urls) - 1
        print(
            bcolors.HEADER + "\n     {}/{} SOURCE>> {}\n".format(i, l, url) + bcolors.ENDC)

        # print out feeds
        zipped = dict(enumerate(d.entries))

        def recurse(zipped):

            print_feed(zipped)

            kb = _continue()  # keystroke listener

            if kb:
                user_selected = kb is not '' and kb in str(zipped.keys())
                if user_selected:
                    # to open page in browser
                    link = zipped[int(kb)].link
                    title = zipped[int(kb)].title
                    try:
                        desc = zipped[int(kb)].description
                        desc = clean_txt(desc)
                        print_desc(title, desc)
                    except AttributeError:
                        print('\n\tNo description available!!')

                    if open_it():
                        open_page(link, title)
                else:
                    print(
                        bcolors.BOLD + 'Invalid entry ... {} '.format(kb) + bcolors.ENDC)
                # repeat with same feeds and listen to kb again
                recurse(zipped)

        recurse(zipped)


def topic_choice(browse):

    if browse:
        topics = dbop.topics()

        tags = {}

        for i, tag in enumerate(topics):
            tags[i] = tag
            print("{}) {}".format(i, tags[i]))

        try:
            m = '\nChoose the topic (number)? : '
            try: # python 2
                uin = raw_input(m) 
            except NameError: # python 3
                uin = input(m)
            uin = int(uin)
            topic = tags[uin]
        except: # catch all exceptions
            print('\nInvalid choice!')
            topic = 'General'

    else:
        topic = 'General'
    urls = dbop.read(topic)

    return urls


def validate_feed(url):
    if parse_feed(url):
        return url
    else:
        exit()

from .support.docopt import docopt


def main():
    args = docopt(
        __doc__, version="TermFeed 0.0.11 (with pleasure by: Aziz Alto)")

    # parse args
    browse = args['-b']
    external = args['<rss-url>']
    add_link = args['-a']
    category = args['<category>']
    delete = args['-d']
    remove = args['-D']
    tags = args['-t']
    rebuild = args['-R']

    fetch = True

    # get rss urls
    if external:
        urls = [validate_feed(external)]
    else:
        urls = topic_choice(browse)

    # if not listing feeds
    if add_link or delete or category or tags or rebuild or remove:
        fetch = False

    # updating URLs library
    if add_link:
        url = validate_feed(add_link)
        if category:
            dbop.add_link(url, category)
        else:
            dbop.add_link(url)
    if delete:
        dbop.remove_link(delete)

    if remove:
        dbop.delete_topic(remove)
    # display resource contents
    if tags:
        if category:
            dbop.browse_links(category)
        else:
            dbop.print_topics()

    if rebuild:
        dbop.rebuild_library()

    if fetch:
        fetch_feeds(urls)

# start
if __name__ == '__main__':

    if not _connected():
        print('No Internet Connection!')
        exit()

    main()
