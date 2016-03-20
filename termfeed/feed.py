#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""TermFeed 0.0.11

Usage:
    feed
    feed <rss-url>
    feed -b [<category>]
    feed -a <rss-url> [<category>]
    feed -d <rss-url>
    feed -t [<category>]
    feed -D <category>
    feed -R
    feed (-h | --help)
    feed --version

Options:
                  List feeds from the default category 'General' of your library.
    <URL>         List feeds from the provided url source.
    -b            Browse feed by category avaialble in the database file.
    -a URL        Add new url <rss-url> to database under [<category>] (or 'General' otherwise).
    -d URL        Delete <rss-url> from the database file.
    -t            See the stored categories in your library, or list the URLs stored under <category> in your library.
    -D TOPIC      Remove entire cateogry (and its urls) from your library.
    -R            Rebuild the library from the rss.yaml
    -h --help     Show this screen.

"""


from __future__ import print_function
import sys
import webbrowser
import feedparser
import re
import arrow
import dateutil.parser
from plumbum import colors as c

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

import termfeed.database

dbop = termfeed.database.DataBase()
def _connected():
    """check internet connect"""
    host = 'http://google.com'

    try:
        urlopen(host)
        return True
    except:
        return False

def open_page(url, title):
    with c.info:
        print('\topening ... {}\n'.format(title.encode('utf8')))
    # open page in browser
    webbrowser.open(url)

from tabulate import tabulate
def print_feed(zipped):
    #keys()
    #dict_keys(['id', 'links', 'summary', 'author', 'guidislink',
    #'author_detail', 'link', 'summary_detail', 'published', 'content',
    #'authors', 'published_parsed', 'title', 'title_detail'])

    def parse_time(post):
        try:
            return c.info | arrow.get(dateutil.parser.parse(post.published)).humanize()
        except:
            return c.info | arrow.get(dateutil.parser.parse(post.updated)).humanize()

    def parse_author(post):
        if post.author_detail.name:
            return post.author_detail.name
        else:
            return post.author_detail.email.split('@')[0]

    r = re.compile(r'(\w+)(?:/commits/\w+\.atom|\.git)')

    def repo(post):
        # print(post.keys())
        repos = r.findall(post.content[0].base)#summary_detail.base)
        if repos:
            return repos[0]
        else:
            return ''

    table = [[  c.green | '[{}]'.format(num),
                repo(post),
                parse_time(post),
                c.dark_gray | parse_author(post), post.title]
            for num, post in reversed(list(zipped.items()))]

    print(tabulate(table, tablefmt="plain"))#, tablefmt="plain"))


def print_desc(topic, txt):
    with c.info:
        try:
                print('\n\n{}:'.format(topic))
        except UnicodeEncodeError:
            pass
    with c.bold:
        print('\n\t{}'.format(txt))


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

        msg = """\nPress: Enter to continue, ... [NUM] for short description / open a page, ... or CTRL-C to exit: """
        with c.warn:
            print(msg, end='')
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

    feeds = []
    for i, url in enumerate(urls):

        feeds += [parse_feed(url)]

    #if d is None:
    #    continue  # to next url

    # feeds source
    l = len(urls) - 1

    for i, d in enumerate(feeds):
        title = url if d.feed.title else d.feed.title
        print(c.magenta | "     {}/{} SOURCE>> {}".format(i, l, d.feed.title) )

    # print out feeds

    zipped = []
    for d in feeds:
        zipped += d.entries

    # https://wiki.python.org/moin/HowTo/Sorting#The_Old_Way_Using_Decorate-Sort-Undecorate
    try:
        decorated = [(dateutil.parser.parse(post.published), i, post) for i, post in enumerate(zipped)]
    except:
        decorated = [(dateutil.parser.parse(post.updated), i, post) for i, post in enumerate(zipped)]

    decorated.sort(reverse=True)
    zipped = [post for time, i, post in decorated]               # undecorate

    zipped = dict(enumerate(zipped))

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
                with c.bold:
                    print('Invalid entry ... {} '.format(kb))
            # repeat with same feeds and listen to kb again
            recurse(zipped)

    recurse(zipped)


def topic_choice(browse, topic):

    if not topic in dbop.topics:
        if browse:

            tags = {}

            for i, tag in enumerate(dbop.topics):
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

# from .support.docopt import docopt
from docopt import docopt

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
        urls = topic_choice(browse, category)

    # if not listing feeds
    if add_link or delete or tags or rebuild or remove:
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
            print(dbop)

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
