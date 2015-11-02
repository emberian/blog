#!/bin/sh
set -e
. ./bin/activate
if [ ! -e pelican-plugins/LICENSE ] || [ "$UPDATE_PLUGINS" = 1 ]; then
    git submodule update --init --recursive
    git submodule sync
fi
if [ ! -e bin/pelican ] || [ "$UPDATE_PIP" = 1 ]; then
    pip install -r requirements.txt --upgrade
fi
./bin/pelican content -s pelicanconf.py -t themes/pelican-elegant-1.3
if [ "$REALLY_DEPLOY" = "1" ]; then
    rsync -razvP output/ cmr@octayn.net:blog
fi
