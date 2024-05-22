#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import os
import sys
from GlobalFunctions_New import GlobalFunctions
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--silent", required=False, help="Process the currently tracked list of comics and downloads new issues.", action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    if args.silent:
        GlobalFunctions.comicDownload()
    else:
        
        config_file = Path("/data/comic_path_config.json")
        api_file = Path("/data/comicvine_api_key.json")

        if config_file.is_file() and api_file.is_file():
            GlobalFunctions.mainMenu()
        else:
            GlobalFunctions.modifySettingsMenu()                