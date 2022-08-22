#!/bin/sh
docker image rm dalthakar/comicdownloader:ubuntu-dev
time docker build -t dalthakar/comicdownloader:ubuntu-dev -f dockerfile-ubuntu .