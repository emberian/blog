#!/bin/sh
set -e
. ./bin/activate
if [ ! -e bin/pelican ]; then
    pip install -r requirements.txt
fi
./bin/pelican content -s pelicanconf.py -t themes/pelican-elegant-1.3
if [ "$REALLY_DEPLOY" = "1" ]; then
    rsync -razvP output/ cmr@octayn.net:blog
fi
