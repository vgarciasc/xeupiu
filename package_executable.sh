#!/bin/sh

pyinstaller run.py --noconfirm --icon="data/resources/icon.ico" --name xeupiu
mkdir -p dist/xeupiu/data
mkdir -p dist/xeupiu/data/tmp
mkdir -p dist/xeupiu/data/log
cp -r data/characters dist/xeupiu/data/characters
cp -r data/backgrounds dist/xeupiu/data/backgrounds
cp -r data/resources dist/xeupiu/data/resources
cp -r data/texts dist/xeupiu/data/texts
cp config_generic.json dist/xeupiu/config.json
