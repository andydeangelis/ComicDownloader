#!/usr/bin/env python
# -*- coding: utf-8 -*-

from genericpath import isfile
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
        if config_file.is_file():
            with open(config_file) as f_in:
                current_root_path = (json.load(f_in))['comic_dir']

        api_file = Path("/data/comicvine_api_key.json")
        if api_file.is_file():
            with open(api_file) as f_in:
                current_api_key = (json.load(f_in))['comic_api_key']

        if current_root_path is not None and current_ap_key is not None:
            GlobalFunctions.mainMenu()
        else:
            GlobalFunctions.modifySettingsMenu()                