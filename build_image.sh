#!/bin/sh
docker image rm dalthakar/comicdownloader:andy-dev
time docker build -t dalthakar/comicdownloader:andy-dev -f dockerfile-ubuntu .