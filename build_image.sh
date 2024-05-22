#!/bin/sh
docker image rm dalthakar/comicdownloader:ubuntu-dev
time docker build -t dalthakar/comicdownloader:andy-dev -f dockerfile-ubuntu .