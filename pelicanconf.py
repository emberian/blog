#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

PLUGIN_PATHS = ["pelican-plugins"]
PLUGINS = ["render_math"]
AUTHOR = u'Corey Richardson'
SITENAME = u"Corey's Local Search"
SITEURL = 'http://blog.octayn.net'

THEME = 'pelican-octopress-theme'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'atom.xml'
CATEGORY_FEED_ATOM = 'categories/%s/atom.xml'

DEFAULT_PAGINATION = 10

ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

ARCHIVES_SAVE_AS = 'blog/archives/index.html'

CATEGORY_URL = 'categories/{slug}/'
CATEGORY_SAVE_AS = 'categories/{slug}/index.html'

LANDING_PAGE_ABOUT = {
        "title": "Just some person, you know?",
        "details": """
My name is Corey Richardson and I'm searching for happiness.
"""
}
