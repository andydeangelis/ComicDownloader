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

class ReadComicOnline:
    def comicSearchRCO(searchData):
        try:
            print(searchData)
            sess = requests.session()
            sess = cloudscraper.create_scraper(sess, delay=10)

            headers = {
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9',
            'cache-control':'max-age=0',
            'content-length':'14',
            'content-type':'application/x-www-form-urlencoded',
            'cookie':'__cfduid=dc1f7b5c6d3dc6c09877ec8c1db8825bb1579376561; cf_clearance=e05005f85cead71365de805fe48b6a04e7cce3b3-1579376568-0-150',
            'origin':'https://readcomiconline.to',
            'referer':'https://readcomiconline.to/?__cf_chl_jschl_tk__=f435b3d2677af519c8db9a0cbf4069b3bba9b945-1579376564-0-AdV7lFWCg777vJQrgIIqmNJoP9mCURkfhAhA89qi19zQDJgHV5UiYotxKLM3LESw3gzh0rnvUts0SpJD9AnWfqyTIOb8FdI25IPvOv8JGQILVJvE-1KTpQDpCvVyvAXZEyoHh_DvyUM3q7bl6DZEuSLH6D9ulhUmfeJGsa1VewRwduUiBeXWvFT8MHC89otn2Lcvt-xx1fPUeCd9_jc9MwLO3TjusjrOH7kNv7MhfoTv9ghLATdjm7SuVXRJhiOF9ih7Rh_D0UyQNJWeaTNVbCk',
            'sec-fetch-mode':'navigate',
            'sec-fetch-site':'same-origin',
            'sec-fetch-user':'?1',
            'upgrade-insecure-requests':'1',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
            }

            data = {
                'keyword': "'"+searchData+"'"
            }

            page = sess.get('https://readcomiconline.to/Search/Comic', data=data, headers=headers)
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