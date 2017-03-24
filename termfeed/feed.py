#!/usr/bin/env python

import logging
import os
import re
import webbrowser

import arrow
import click
import dateutil.parser
import feedparser
import yaml
yaml.add_representer(tuple, yaml.representer.SafeRepresenter.represent_list)
yaml.add_representer(feedparser.FeedParserDict,
                     yaml.representer.SafeRepresenter.represent_dict)

from bs4 import BeautifulSoup
from plumbum import colors as c
from tabulate import tabulate
from urllib.request import urlopen
import termfeed.database

logger = logging.getLogger(__name__)

log_info = logger.info
log_debug = logger.debug

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


def print_feed(zipped):
    # keys()
    # dict_keys(['id', 'links', 'summary', 'author', 'guidislink',
    # 'author_detail', 'link', 'summary_detail', 'published', 'content',
    # 'authors', 'published_parsed', 'title', 'title_detail'])

    def parse_time(post):
        try:
            return c.info | arrow.get(dateutil.parser.parse(post.published)).humanize()
        except:
            return c.info | arrow.get(dateutil.parser.parse(post.updated)).humanize()

    def parse_author(post):
        try:
            if post.author_detail.name:
                return post.author_detail.name
            else:
                return post.author_detail.email.split('@')[0]
        except AttributeError:
            return 'unknown'
        except BaseException as e:
            print(c.red | yaml.dump(post))
            import sys
            raise e

    # r = re.compile(r'(\w+)(?:/commits/\w+\.atom|\.git)')

    def repo(post):
        try:
            return dbop.data[post.title_detail.base]['title']
        except:
            print('Keys: ', dbop.data.keys())
            raise

    # try:
    table = [[c.green | '[{}]'.format(num),
              repo(post),
              parse_time(post),
              c.dark_gray | parse_author(post),
              post.title,
              ] for num, post in reversed(list(zipped.items()))]
    # except AttributeError as e:
    #     print('Bug:', post.keys())
    #     print(post.published)
    #     print(c.magenta | yaml.dump(post))
    #     print(post.title)
    #     print(post.title_detail)
    #     raise e
    # else:
    #     print('Bug:', dir(post), post.keys())

    print(tabulate(table, tablefmt="plain"))  # , tablefmt="plain"))


def print_desc(topic, txt, post):
    with c.info:
        try:

            print('\n\nTitle : {}:'.format(topic))

        except UnicodeEncodeError:
            pass
    with c.dark_gray:
        yaml.add_representer(
            tuple, yaml.representer.SafeRepresenter.represent_list)
        yaml.add_representer(feedparser.FeedParserDict,
                             yaml.representer.SafeRepresenter.represent_dict)

        import copy
        post_copy = copy.deepcopy(post)

        # post_copy = post.copy()
        for key in list(post_copy.keys()):
            if '_parsed' in key \
                    or '_detail' in key \
                    or key in ('guidislink', 'link', 'links', 'id', 'summary', 'authors', 'title'):
                del post_copy[key]
            if 'content' is key:
                for i in range(len(post_copy[key])):
                    post_copy[key][i] = clean_txt(post_copy[key][i]['value'])
        print(yaml.dump(post_copy))


def open_it():
    if os.environ.get('DISPLAY'):
        return click.confirm('\n\n\t Open it in browser ?')

    elif click.confirm('No display aviable, do you want to continue?', default=True, show_default=False):
        log_info('Confirm True')
        return False

    else:
        log_info('Confirm False')
        exit()
        return False


def clean_txt(txt):
    """clean txt from e.g. html tags"""
    clean_text = BeautifulSoup(txt, "html.parser").text
    return clean_text


def _continue():
    try:

        msg = """\nPress: Enter to continue, ... [NUM] for short description / open a page, ... or CTRL-C to exit"""
        with c.warn:
            return click.prompt(msg, type=str, default='', show_default=False)
            # click.confirm('No display aviaable, do you want to continue?',
            # default=True, show_default=False):

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
        # exit()
        return None


def fetch_feeds(urls):
    # feeds source
    l = len(urls) - 1

    feeds = [parse_feed(url) for url in urls]
    for f, u in zip(feeds, urls):
        if not f:
            print(c.warn | 'ERROR with {}'.format(u))
            feeds.remove(f)

    zipped = []
    for i, d in enumerate(feeds):
        # title = url if d.feed.title else d.feed.title
        print(c.magenta | "     {}/{} SOURCE>> {}".format(i, l, d.feed.title))
        zipped += d.entries

    # https://wiki.python.org/moin/HowTo/Sorting#The_Old_Way_Using_Decorate-Sort-Undecorate
    try:
        decorated = [(dateutil.parser.parse(post.published), i, post)
                     for i, post in enumerate(zipped)]
    except:
        decorated = [(dateutil.parser.parse(post.updated), i, post)
                     for i, post in enumerate(zipped)]
    decorated.sort(reverse=True)
    zipped = [post for time, i, post in decorated]  # undecorate

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
                    print_desc(title, desc, zipped[int(kb)])
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


def topic_choice(browse, *labels):
    log_info(labels)

    labels = set(labels) & dbop.labels

    log_info(labels)

    if not labels:
        if browse:

            tags = {}

            for i, tag in enumerate(dbop.labels | {'all'}):
                tags[i] = tag
                print("{}) {}".format(i, tags[i]))

            uin = click.prompt('\nChoose the topic (number)? ', type=int)
            try:
                labels = tags[uin]
            except:  # catch all exceptions
                print('\nInvalid choice!')
                labels = []

        else:
            labels = []
    if labels == 'all':
        urls = dbop.links
    else:
        urls = dbop.link_for_label(labels)

    return urls


def validate_feed(url):
    if parse_feed(url):
        return True
    else:
        return False

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option('-l', '--label', multiple=True)
@click.option('-n', '--dry-run', is_flag=True)
# @click.option('--debug/--no-debug', default=False)
@click.option('-v', '--verbose', count=True, help='Levels: -v:INFO, -vvv:DEBUG')
def cli(ctx, verbose, label, dry_run):
    logging.basicConfig(format=(c.dark_gray | logging.BASIC_FORMAT))

    logger_pkg = logging.getLogger(__package__)
    if verbose >= 3:
        logger_pkg.setLevel(logging.DEBUG)
    elif verbose >= 1:
        logger_pkg.setLevel(logging.INFO)

    if dry_run:
        dbop.dry_run = True

    if ctx.invoked_subcommand is None:
        log_info('I was invoked without subcommand')
        if not label:
            fetch_feeds(dbop.links)
        else:
            fetch_feeds(dbop.link_for_label(*label))
    else:
        log_info('I am about to invoke %s' % ctx.invoked_subcommand)


@cli.command()
@click.argument('url', nargs=1)
@click.argument('label', nargs=-1)  # , help='One or more labels for this url.'
@click.option('--title', default='')
@click.option('-f', '--flag', multiple=True)
def add(url, label, title, flag):

    regex = re.compile(
        r'(https://github\.com/|git@github\.com:)(\w+)/([\w-]+)\.git')
    if regex.match(url):
        (r_prefix, r_user, r_name), = regex.findall(url)

        url_offer = 'https://github.com/' + r_user + \
            '/' + r_name + '/commits/master.atom'

        with c.info:
            if click.confirm('''
        It seams, that you try to add a github repo.
        But the url seams to be wrong.
        Do you mean {}?'''.format(url_offer), default=True):
                url = url_offer
                flag = list(set(flag) | {'github', 'git'})
            elif 'git' in url and click.confirm('''
        It seams, that your url is a git url, add Flag?
        '''.format(url_offer), default=True):
                flag = list(set(flag) | set('git'))
            if title == '':
                title = r_name

    if validate_feed(url):
        with dbop as db:
            db.add_link(url, *label, title=title, flag=flag)
        print("Add URL feed: {}".format(url))


@cli.command()
@click.argument('name')  # , help='namme must be a url or a label'
@click.argument('url', nargs=1)
def remove(url):
    if url in dbop.links:
        # with dbop as dbop:
        dbop.remove_link(url)
        print("Removed URL feed: {}".format(url))
    else:
        print("Could not find URL feed: {}".format(url))


@cli.command()
@click.option('--label/--no-label', default=False)
def show(label):
    if label:
        print('Labels: ', dbop.labels)
    print(dbop.as_yaml)


@cli.command()
@click.argument('label', nargs=-1)  # , help='One or more labels for this url.'
def browse(label):
    urls = topic_choice(browse, *label)
    fetch_feeds(urls)


@cli.command()
@click.pass_context
def edit(ctx):
    import tempfile
    from contextlib import suppress
    from subprocess import call

    EDITOR = os.environ.get('EDITOR', 'dav')  # that easy!
    #EDITOR = 'dav'
    if EDITOR == 'suplemon':
        os.environ['TERM'] = 'xterm-256color'

    initial_message = dbop.as_yaml
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode='w+') as tf:
        tf.write(initial_message)
        tf.flush()
        with suppress(KeyboardInterrupt):
            call([EDITOR, tf.name])

        # do the parsing with `tf` using regular File operations.
        # for instance:
        if False:
            tf.seek(0)
            edited_message = tf.read()
            print(edited_message)
        ctx.invoke(load, file=tf.name)


@cli.command()
@click.argument('file', type=click.File('r'))
def load(file):
    with open(file) as f:
        data = yaml.load(f.read())
    print('Loaded: ', file, os.path.exists(file))
    print(yaml.dump(data))
    #log_debug('data keys: ', data.keys())
    #log_debug('data keys: ', data)

    verification = [validate_feed(link) for link in data]
    if not all(verification):
        for link in data:
            if not validate_feed(link):
                print("INVALID URL feed: {}".format(link))
        exit()

    with dbop as db:
        db.data = data

    print(yaml.dump(data))


def main():
    if not _connected():
        print('No Internet Connection!')
        exit()

    cli()

# start
if __name__ == '__main__':
    main()
