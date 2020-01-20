#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from GlobalFunctions import GlobalFunctions
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--silent", help="Process the currently tracked list of comics and downloads new issues.", action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    if args.silent:
        GlobalFunctions.comicDownload()
    elif not args.silent:
        GlobalFunctions.mainMenu()