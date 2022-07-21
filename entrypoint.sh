#!/bin/bash
set -e
SOURCE_DIR=/repos/ComicDownloader/config
TARGET_DIR=/data
if [ $(find $TARGET_DIR -maxdepth 0 -type d -empty) 2>/dev/null) ]; then
   cp -r --preserve-all $SOURCE_DIR/* $TARGET_DIR/
fi

# continue Docker container initialization, execute CMD
exec $@
