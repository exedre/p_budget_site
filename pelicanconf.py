#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

LOAD_CONTENT_CACHE = False
# CACHE_MODIFIED_METHOD = 'md5'

EVENT_TIME = '2020/10/2 09:30'

HOME_LINK = '/'

def split(string):
    return [x.strip() for x in string.strip().split(',')]

JINJA_FILTERS = {'split': split}

AUTHOR = u'reporter'
SITENAME = u'Reporter'
SITEURL = ''
PATH = 'content'

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = u'it'

USE_FOLDER_AS_CATEGORY = True

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DIRECT_TEMPLATES = ['index', 'archives']

DELETE_OUTPUT_DIRECTORY = True

THIS_TITLE = ""

DEFAULT_PAGINATION = 1

STATIC_PATHS = ['json','images', 'pdfs', 'audio', '.htaccess', 'pp-it.json']

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = 'themes/pirates'

DATE_FORMATS = {
    'en': '%a, %d %b %Y',
    'jp': '%Y-%m-%d(%a)',
    'it': '%d/%m/%Y',
}

LOCALE = ('it_IT', )
