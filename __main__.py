#!/usr/bin/env python
# -*- coding: utf-8 -*-

from genericpath import isfile
import os
import sys
from GlobalFunctions import GlobalFunctions
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--silent", required=False, help="Process the currently tracked list of comics and downloads new issues.", action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    if args.silent:
        GlobalFunctions.comicDownload()
    else:
        if os.path.isfile('/data/comicDatabase.db'):
            GlobalFunctions.mainMenu()
        else:
            GlobalFunctions.createNewDatabase()
            GlobalFunctions.mainMenu()