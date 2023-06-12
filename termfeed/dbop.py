#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Database operations module (dbop.py) to manipulate a database:
add, update, delete.
"""

import os
import shelve
import termfeed.dbinit

HOME_DIR = os.path.expanduser('~')
DB_PATH = os.path.join(HOME_DIR, '.termfeed.db')

def rebuild_library():
    """Rebuild the library by calling the dbinit module."""
    termfeed.dbinit.main()
    print(f'Created ".termfeed.db" in {HOME_DIR}')

# Instantiate db if it's not created yet
if not os.path.exists(DB_PATH):
    rebuild_library()

def open_db():
    """Open the database and return the connection."""
    return shelve.open(DB_PATH, 'w')

def topics():
    """Get the list of topics in the database."""
    with open_db() as db:
        return list(db.keys())

def read(topic):
    """Read a topic from the database."""
    with open_db() as db:
        return db.get(topic, None)

def browse_links(topic):
    """Print the links for a given topic."""
    with open_db() as db:
        links = db.get(topic)
        if links:
            print(f'{topic} resources:')
            for link in links:
                print(f'\t{link}')
        else:
            print(f'No category named {topic}')
            print_topics()

def print_topics():
    """Print available topics."""
    print('Available topics: ')
    for t in topics():
        print(f'\t{t}')

def add_link(link, topic='General'):
    """Add a link to a topic. If the topic does not exist, create it."""
    with open_db() as db:
        links = db.get(topic, [])
        if link not in links:
            links.append(link)
            db[topic] = links
            print(f'Updated .. {topic}')
        else:
            print(f'{link} already exists in {topic}!!')

def remove_link(link):
    """Remove a link from all topics."""
    with open_db() as db:
        for topic in topics():
            links = db.get(topic, [])
            if link in links:
                links.remove(link)
                db[topic] = links
                print(f'Removed: {link}\nFrom: {topic}')
                return
        print(f'URL not found: {link}')

def delete_topic(topic):
    """Delete a topic."""
    if topic == 'General':
        print('Default topic "General" cannot be removed.')
        return

    with open_db() as db:
        if topic in db:
            del db[topic]
            print(f'Removed "{topic}" from your library.')
        else:
            print(f'"{topic}" is not in your library!')


# if __name__ == '__main__':

#     for l in read('News'):
#         print(l)

#     remove_link('http://rt.com/rss/')

#     add_link('http://rt.com/rss/', 'News')

#     for l in read('News'):
#         print(l)
