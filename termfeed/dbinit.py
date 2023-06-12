#!/usr/bin/env python

import os
import shelve
from termfeed.urls import rss

def initialize_database(database_path, rss_data):
    try:
        with shelve.open(database_path) as db:
            for topic, links in rss_data.items():
                db[topic] = links
    except Exception as e:
        print(f"Error while initializing the database: {e}")

def main():
    
    # Determine home directory and database file path
    home_dir = os.path.expanduser('~')
    database_file_path = os.path.join(home_dir, '.termfeed')

    # Initialize database with rss data from 'urls.py'
    initialize_database(database_file_path, rss)

if __name__ == "__main__":
    main()
