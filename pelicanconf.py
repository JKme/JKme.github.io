#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'JKme'
#SITENAME = 'Follow My Heart'
SITENAME = 'Study The World'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
MENUITEMS = [
        ('Pentest', '/category/pentest.html'),
        ('Learning', '/category/learning.html'),
	('Python', '/category/python.html')
]
DISPLAY_CATEGORIES_ON_MENU = False
SUMMARY_MAX_LENGTH=20
#MARKDOWN = ['codehilite(css_class=highlight, guess_lang=False)', 'extra']
#MARKDOWN = ['codehilite(guess_lang=False)']
