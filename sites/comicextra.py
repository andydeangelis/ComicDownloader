from prettytable import PrettyTable
import re
import cloudscraper
import requests
from bs4 import BeautifulSoup
import os
import shutil
import sys
import logging
import glob
import json
import img2pdf
import math
import threading
from tqdm import tqdm
import sqlite3
import time
from zipfile import ZipFile

class ComicExtra:
    def comicSearchCE(searchData):
        try:
            print(searchData)
            sess = requests.session()
            sess = cloudscraper.create_scraper(sess, delay=10)

            headers = {
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'sec-fetch-mode': 'navigate',
                'secfetch-user': '?1'
            }

            searchData = searchData.replace(" ","+")

            page = sess.get('https://www.comicextra.com/comic-search?key='+searchData, headers=headers)
            time.sleep(5)

            soup = BeautifulSoup(page.text,"html5lib")

            table = soup.find("table")

            for i in range (1,2):
                try:
                    findLinks = table.find_all('a') 
                except EnvironmentError as e:
                    print(e)

            return findLinks
        except EnvironmentError as e:
            print(e)