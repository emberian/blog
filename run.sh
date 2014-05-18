#!/bin/sh
. ./bin/activate
./bin/pelican content -s pelicanconf.py -t themes/pelican-elegant-1.3
rsync -razvP output/ cmr@octayn.net:blog
