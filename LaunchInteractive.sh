#!/bin/sh
docker run -ti --rm --name comicdownloader --volume=/home/andy/docker/comicdownloader/data:/data --volume=/mnt/books/comics2:/comics dalthakar/comicdownloader:andy-dev