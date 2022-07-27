#!/bin/sh
docker run -ti --rm --name comicdownloader --volume=/home/andy/Documents/docker/config:/data --volume=/home/andy/Documents/docker/comics:/comics comicdownloader "--silent"