#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prettytable import PrettyTable
import re
import time
import cloudscraper
import requests
from bs4 import BeautifulSoup
import os
from os import system
from os.path import exists
import subprocess
import shutil
import sys
import logging
import glob
import json
import threading
import math
import threading
from tqdm import tqdm
import sqlite3
import time
import getpass
from zipfile import ZipFile
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from termcolor import colored