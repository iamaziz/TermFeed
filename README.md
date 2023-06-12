# TermFeed

[![PyPI version](https://badge.fury.io/py/termfeed.svg)](http://badge.fury.io/py/termfeed)

**Term**inal **Feed** is a *minimal* feed **reader** for the terminal (without curses).

TermFeed is a minimal RSS reader for your terminal. You can read, preview, open, store, and delete your favorite RSS feeds directly from the command line.

## Why TermFeed?
TermFeed is perfect for terminal addicts who want to stay up-to-date with the world by quickly reading feed summaries WITHOUT leaving the terminal.


## Usage

`$ feed`

- browse latest feed from your favorite rss sources (links stored under the default category `General`).

`$ feed <RSS-LINK>`

- browse latest feed from the single link `<RSS-LINK>` provided.
- e.g. `$ feed https://news.ycombinator.com/rss`

`$ feed -b`

- browse latest feeds by category of your library.

`$ feed -t`

- list the topics stored in your library.

`$ feed -t <CATEGORY>`

- list the URLs stored under `<category>` in your library.

`$ feed -a <RSS-LINK>`

- add new link to your rss library.

`$ feed -a <RSS-LINK> <CATEGORY>`

- add new link to your rss library under `<category>`.

`$ feed -d <RSS-LINK>`

- delete a link from your rss library.

`$ feed -D <category>`
- Remove entire category (with its URLs) from library.

`$ feed -R`

- rebuild the library from `urls.py`


## Features (what you can do?)

- List feeds from different sources (stored in your library) with colorful text.
- Preview a short summary of a selected feed.
- Jump to (optionally) the source page of a feed in default browser.
- Store new (or delete) RSS URLs in (from) your library under a specific topic or under the default tag `General`.


## Help

Help
See `$ feed -h` for detailed usage.

```
TermFeed 0.0.8

Usage:
    feed
    feed <rss-url>
    feed -b
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
    -R            Rebuild the library from the url.py
    -h --help     Show this screen.
```


## Installation

1) from `PyPI` repository:

	$ pip install TermFeed


2) from the source distribution,

download and unpack the [zipped folder](https://github.com/iamaziz/TermFeed/archive/master.zip), then:

	$ cd TermFeed
	$ python setup.py install

## Uninstall


	$ pip uninstall TermFeed

I use a data file (`.termfeed.db`) as a mini-database to maintain the RSS URLs.
This file is created at the home directory (e.g. `$HOME/.termfeed.db`), delete it as well.


> Remember, you may need to run these commands as an admin e.g.
> 	`$ sudo ...`


### Dependencies

- [feedparser](https://pypi.python.org/pypi/feedparser)


### Miscellaneous

- Tested on OS X and Linux.
- Supports Python 2.7 and Python 3.4
- The URLs in `urls.py` are complementary. They will be added to your library at `$HOME/.termfeed.db` when you run TermFeed (`$ feed`) for the first time. You may delete them all and have your own list instead.
- [Instant RSS Search](http://ctrlq.org/rss) is a nice search engine for searching RSS feeds.


## Creator

- Aziz Alto

## Contributors
- Victor van Liederen
