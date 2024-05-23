#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import Global
from prettytable import PrettyTable
from pathlib import Path
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
import csv
import threading
import math
import threading
from tqdm import tqdm
#import sqlite3
#from sqlite3 import Error
import time
import getpass
from zipfile import ZipFile
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from termcolor import colored

class GlobalFunctions:
    def cls():
        os.system('cls' if os.name=='nt' else 'clear')

    def set_comic_config():
        GlobalFunctions.cls()

        comic_path_config = "/data/comic_path_config.json"

        try:
            comicPath = input("Enter the path to your comic directory: ")
            comic_root_dir_json = {
                "comic_dir": comicPath
            }
            with open(comic_path_config, 'w', encoding='utf-8') as f:
                json.dump(comic_root_dir_json, f, ensure_ascii=False, indent=4)

            GlobalFunctions.modifySettingsMenu()
        except EnvironmentError:
            GlobalFunctions.modifySettingsMenu()

    def set_api_key():
        GlobalFunctions.cls()

        comic_api_file = "/data/comicvine_api_key.json"

        try:            
            comicApiKey = input("Enter your ComicVine API key: ")
            comic_api_key_json = {
                "comic_api_key": comicApiKey
            }
            with open(comic_api_file, 'w', encoding='utf-8') as f:
                json.dump(comic_api_key_json, f, ensure_ascii=False, indent=4)

            GlobalFunctions.modifySettingsMenu()
        except EnvironmentError:
            GlobalFunctions.modifySettingsMenu()

    def comicSearch():
        try:
            GlobalFunctions.cls()

            userSearchInput = input('What are you searching for (Leave blank to return to main menu)? ')

            if not bool(userSearchInput):
                GlobalFunctions.mainMenu()

            sess = requests.session()
            
            retries = Retry(total=5, backoff_factor=1)
            sess.mount('http://', HTTPAdapter(max_retries=retries))
            headers = {
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'sec-fetch-mode': 'navigate',
                'secfetch-user': '?1'
            }
            page = sess.get("https://readcomicsonline.ru/search", headers=headers)
            soup = BeautifulSoup(page.text,"html5lib")
            searchData = (json.loads(soup.body.text))['suggestions']

            i = 0
            searchMatch = []
            for item in searchData:
                if userSearchInput.lower() in (searchData[i]['value']).lower():
                    searchMatch.append(searchData[i])
                i = i + 1

            resultCounter = 1
            for match in searchMatch:
                listNum = str(resultCounter)
                print(listNum + ". " + match['value'])
                resultCounter = resultCounter + 1 

            searchSelectNum = input("Input the number of the series you want to add (Leave blank to return to main menu): ")

            if bool(searchSelectNum):
                tmpNum = int(searchSelectNum)
                searchSelectData = searchMatch[tmpNum - 1]['data']
                searchSelectValue = searchMatch[tmpNum - 1]['value']
                #comicURL = 'https://readcomicsonline.ru/comic/' + searchSelectData
                GlobalFunctions.add_new_comic(searchSelectData,searchSelectValue)
            else:
                GlobalFunctions.mainMenu()            

        except EnvironmentError as e:
            print(e)

    def add_new_comic(searchSelectData,searchSelectValue):
        try:
            GlobalFunctions.cls()

            trackerJsonFile = '/data/comic_tracker.json'
            
            configExists = Path(trackerJsonFile)

            if configExists.is_file():

                comicFolder = searchSelectData.replace("-"," ")
                if comicFolder[comicFolder.__len__() -1] == ' ':
                    comicFolder = comicFolder[:-1]

                newComicData = {
                    "comicUrl": 'https://readcomicsonline.ru/comic/' + searchSelectData,
                    "value": searchSelectValue,
                    "folder": comicFolder
                }

                with open (trackerJsonFile, 'r+') as file:
                    file_content = json.load(file)
                    value_exists = False
                    for val in file_content["trackedComics"]:
                        if val["value"] == newComicData["value"]:
                            value_exists = True
                    if value_exists == True:
                        print("Comic already exists in tracked list.")
                        input("Press any key to return to the main menu.")
                        GlobalFunctions.mainMenu()                            
                    else:
                        file_content["trackedComics"].append(newComicData)
                        file.seek(0)
                        json.dump(file_content, file, ensure_ascii=False, indent=4)
            else:
                comicFolder = searchSelectData.replace("-"," ")
                if comicFolder[comicFolder.__len__() -1] == ' ':
                    comicFolder = comicFolder[:-1]

                newComicData = {
                    "trackedComics":[
                        {
                            "comicUrl": 'https://readcomicsonline.ru/comic/' + searchSelectData,
                            "value": searchSelectValue,
                            "folder": comicFolder
                        }
                    ]
                }
                with open(trackerJsonFile,'w') as file:
                    json.dump(newComicData, file, ensure_ascii=False, indent=4)
            
            GlobalFunctions.mainMenu()

        except EnvironmentError as e:
            print(e)
    
    def batchComicDownload():
        GlobalFunctions.cls()
        
        trackerJsonFile = '/data/comic_tracker.json'
        comic_path_config = "/data/comic_path_config.json"
        comic_api_file = "/data/comicvine_api_key.json"

        #Get root directory
        with open(comic_path_config, 'r') as rootPath:
            comic_root_path = (json.load(rootPath))['comic_dir']

        #Get ComicVine API key
        with open(comic_api_file, 'r') as apiKey:
            comicvine_api_key = (json.load(apiKey))['comic_api_key']

        #Get the current list of comics
        with open (trackerJsonFile, 'r') as file:
            allComics = (json.load(file)  )['trackedComics']

        for comic in tqdm(allComics):
            print(comic['comicUrl'])
            GlobalFunctions.pullComic(comic,comic_root_path,comicvine_api_key)

        print("Sleeping for 20 seconds to finish metadata lookup.")
        time.sleep(20)

    def pullComic(comic,rootPath,apiKey):

        value = comic['value']
        url = comic['comicUrl']
        folder = comic['folder']

        print("\n" + value)
        
        sess = requests.session()
        retries = Retry(total=5, backoff_factor=1)
        sess.mount('http://', HTTPAdapter(max_retries=retries))
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'secfetch-user': '?1'
        }
        page = sess.get(url, headers=headers)
        time.sleep(2)
        title = folder
        
        print("Checking for new issues of "+title)
        
        soup = BeautifulSoup(page.text,"html5lib")
        links = soup.findAll('a')

        findLinks = []

        for link in links:
            try:
                if "/comic/" in link.get('href'):
                    findLinks.append(link)
            except EnvironmentError as e:
                print(e)

        # Get the list of already downloaded issues from file system. 
        #existingComics = os.listdir(rootPath + "/" + folder)
        
        for link in findLinks:
            try:
                # Create the URL to the issue from the relative link on the page. the '&readType=1' 
                # option specifies to show the full comic on one page.
                comicLink = (link.get('href')).replace(" ","") 
                
                # Set the name for the CBZ file.
                cbz_name = (link.string).replace(":","").replace(" / ","").replace("/"," ").replace("-)",")").replace("%","")
                fileExists = Path(rootPath + "/" + folder + "/" + cbz_name + ".cbz")
                fileExists2 = Path(rootPath + "/" + folder + "/" + link.string + ".cbz")
                
                # If the link exists, continue to the next issue. If not, download the issue.
                if not fileExists.is_file() and not fileExists2.is_file():
                    
                    # Create our sesion to the issue and get the encoded html.               
                    comicChapterPage = sess.get(comicLink, headers=headers)
                    page_source = BeautifulSoup(comicChapterPage.text.encode("utf-8"), "html.parser")

                    # Find each image link from the encoded html.
                    img_list = page_source.findAll('img')

                    # Generate the issue name.
                        # Generate the issue name.
                    file_issue_name = comicLink.split("/")
                    file_issue_name = file_issue_name[-1]
                    file_issue_name = file_issue_name.split("?")
                    file_issue_name = file_issue_name[0]
                    file_issue_name = file_issue_name.replace("-"," ").replace("%","") 

                    if len(file_issue_name) == 1:
                       file_issue_name = "00" + file_issue_name
                    elif len(file_issue_name) == 2:
                       file_issue_name = "0" + file_issue_name

                    # Set the name for the CBZ file.
                    cbz_name = (link.string).replace(":","").replace(" / ","").replace("/"," ").replace("-)",")").replace("%","")
                    
                    # Specify the paths. The 'tmpPath' is the issue sub-directory in the comic directory
                    # where the jpegs for the issue will be stored. The 'comicPath' is the top level folder
                    # where the resulting CBZ file will be stored.
                    tmpPath = rootPath + "/" + folder + "/" + file_issue_name     
                    comic_path = rootPath + "/" + folder + "/"    

                    # Check if the directory exists. If not, create it.
                    if os.path.isdir(tmpPath):
                        continue
                    else:
                        os.makedirs(tmpPath)
                    
                    # Take the list of image links that we have in img_list, change the '=s1600' value 
                    # to '=s0' value to ensure high quality images are pulled, then add the new links to 
                    # the links[] list.  
                    imgLinks = []

                    for img in img_list:
                        hdImgLink = img.get('data-src')
                        if hdImgLink is not None:
                            imgLinks.append(hdImgLink.replace(" ",""))
                    
                    total_images = len(links)
                    
                    print("Downloading images for "+cbz_name)
                    #This downloads all the images for the comic as jpgs in a folder named for the issue.
                    for imgLink in tqdm(imgLinks):
                        # Ensures that a zero is prepended to ensure proper page order.
                        max_digits = int(math.log10(int(total_images))) + 1
                        current_chapter_value = imgLinks.index(imgLink)
                        file_name = str(current_chapter_value).zfill(max_digits) + ".jpg"
                        r = (sess.get(imgLink)).content
                        #time.sleep(1)
                        f = open(tmpPath + "/" + file_name, 'wb')
                        f.write(r)
                        f.close()   
                    
                    print("Creating comic file "+cbz_name+".cbz...")
                    # Create the CBZ file from the downloaded images, then delete the image files.
                    zipObj = ZipFile(comic_path + cbz_name + ".cbz", 'w')
                    for issuePage in os.listdir(tmpPath):
                        zipObj.write(tmpPath + "/" + issuePage)
                        os.remove(tmpPath + "/" + issuePage)
                    zipObj.close()
                    # Remove the temp directory housing the downloaded jpeg files.
                    os.rmdir(tmpPath)

                    fullComicPath = comic_path + cbz_name + ".cbz"
                    
                    # Set the permissions on the file, otherwise it can't be modified outside the container.
                    os.chmod(fullComicPath, 0o0777)
                    
                    GlobalFunctions.generateMetadata(fullComicPath,apiKey)
    
            except EnvironmentError as e:
                print(e)

    def generateMetadata(comicFile,apiKey):
        process = subprocess.Popen([r'comictagger','--comicvine-key', apiKey, '-f', comicFile, '-o', '-s', '-q', '--no-summary', '-t', 'CR', '--type-modify', 'CR', '--no-gui'], cwd=os.getcwd())
        process.wait()

    def remove_comic():

        trackerJsonFile = '/data/comic_tracker.json'
        
        #Get the current list of comics
        with open (trackerJsonFile, 'r') as file:
            comicList = (json.load(file)  )['trackedComics']
        
        i = 1

        for row in comicList:
            listNum = str(i)
            print(listNum + ". " + row['value'])
            i = i+1

        try:
            comicToRemove = (int(input ("Enter number of comic to remove from tracker: ")))
            selectedComic = comicList[(comicToRemove - 1)]

            os.remove(trackerJsonFile)
            
            for comic in comicList:
                configExists = Path(trackerJsonFile)
                if comic["comicUrl"] != selectedComic["comicUrl"]:

                    if configExists.is_file():

                        newComicData = {
                            "comicUrl": comic["comicUrl"],
                            "value": comic["value"],
                            "folder": comic["folder"]
                        }

                        with open (trackerJsonFile, 'r+') as file:
                            file_content = json.load(file)
                            value_exists = False
                            for val in file_content["trackedComics"]:
                                if val["value"] == newComicData["value"]:
                                    value_exists = True
                            if value_exists == True:
                                print("Comic already exists in tracked list.")
                                input("Press any key to return to the main menu.")
                                GlobalFunctions.mainMenu()                            
                            else:
                                file_content["trackedComics"].append(newComicData)
                                file.seek(0)
                                json.dump(file_content, file, ensure_ascii=False, indent=4)
                else:
                    newComicData = {
                        "trackedComics":[
                            {
                                "comicUrl": comic["comicUrl"],
                                "value": comic["value"],
                                "folder": comic["folder"]
                            }
                        ]
                    }
                    with open(trackerJsonFile,'w') as file:
                        json.dump(newComicData, file, ensure_ascii=False, indent=4)

            GlobalFunctions.cls()

            print(selectedComic["comicUrl"])
            print("Comic " + selectedComic["value"] + " successfully removed!")
            input("Press any key to return to the main menu...")

            GlobalFunctions.mainMenu()

        except ValueError:
            GlobalFunctions.addRemoveComicMenu()
            
           
    def single_comic_download():
        GlobalFunctions.cls()

        trackerJsonFile = '/data/comic_tracker.json'
        comic_path_config = "/data/comic_path_config.json"
        comic_api_file = "/data/comicvine_api_key.json"

        #Get root directory
        with open(comic_path_config, 'r') as rootPath:
            comic_root_path = (json.load(rootPath))['comic_dir']

        #Get ComicVine API key
        with open(comic_api_file, 'r') as apiKey:
            comicvine_api_key = (json.load(apiKey))['comic_api_key']
        
        #Get the current list of comics
        with open (trackerJsonFile, 'r') as file:
            comicList = (json.load(file)  )['trackedComics']
        
        i = 1

        for row in comicList:
            listNum = str(i)
            print(listNum + ". " + row['value'])
            i = i+1

        try:
            comicToCheck = (int(input ("Enter number of comic to check for updates: ")))
            checkComic = comicList[(comicToCheck - 1)]
                            
            GlobalFunctions.pullComic(checkComic,comic_root_path,comicvine_api_key)
            #GlobalFunctions.single_comic_download()

        except ValueError:
            GlobalFunctions.addRemoveComicMenu()

        GlobalFunctions.mainMenu()
        
    def scanComicMetadata():
        GlobalFunctions.cls()

        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        F: Find a comic in current tracked list

        Q: Quit

        M: Main Menu

        Please enter your choice: """)
        
        if choice == "F" or choice =="f":
            search = input("Enter search criteria: ")
            search = search.replace(" ","%")
                            
            conn = sqlite3.connect("/data/comicDatabase.db")
            cur = conn.cursor()

            #Get the current list of comics
            comicListQuery = 'SELECT * from _comicURLs WHERE tracked == 1 and name like' + "'%" + search + "%' COLLATE NOCASE"
            cur.execute(comicListQuery)
            comicList = cur.fetchall()

            i = 1

            for row in comicList:
                listNum = str(i)
                print(listNum + ". " + row[2])
                i = i+1

            try:
                comicToCheck = (int(input ("Enter number of comic to check for updates: ")))
                checkComic = comicList[(comicToCheck - 1)]
                                
                root_path_query = "SELECT * FROM _config"
                cur.execute(root_path_query)
                root_path = cur.fetchall()

                for rootRow in root_path:
                    rootPath = rootRow[0]
                    apiKey = rootRow[1]

                path = rootPath + "/" + checkComic[2]
                                                
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if(file.endswith(".cbz")):
                            comicFile = os.path.join(root,file)
                            print(comicFile)
                            zip_file = ZipFile(comicFile,'r')
                            if 'ComicInfo.xml' not in zip_file.namelist():
                                print("Attempting to gather metadata for " + comicFile + " ...")
                                GlobalFunctions.generateMetadata(comicFile,apiKey)
                                time.sleep(10)
                            else:
                                print("Updating metadata for " + comicFile + " ...")
                                GlobalFunctions.generateMetadata(comicFile,apiKey)
                                time.sleep(10)

            except ValueError:
                GlobalFunctions.addRemoveComicMenu()

        elif choice=="Q" or choice=="q":
            GlobalFunctions.cls()
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must only select a valid entry.")
            print("Please try again")
            GlobalFunctions.mainMenu()
        
        #GlobalFunctions.mainMenu()

    def configureDownloader():
        
        # Create _comicURLs file
        
        # Create _config file
        
        # Create the default root path config
        comicPath = '/comics'
        cvApiKey = input ("""Enter your ComicVine API key): """)
        if cvApiKey == "":
            print("No API Key entered. ComicDownloader will not be able to auto-tag downloaded comics.")
            input ("Press Enter to continue...")

    def addRemoveComicMenu():
        GlobalFunctions.cls()
        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        1: Search for Comic to Add
        2: Remove Comic from tracker
        
        Q: Quit

        M: Main Menu

        Please enter your choice: """)

        if choice == "1":
            GlobalFunctions.comicSearch()
        elif choice == "2":
            GlobalFunctions.remove_comic()
        elif choice=="Q" or choice=="q":
            GlobalFunctions.cls()
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must select a valid entry.")
            input("Press any key to return to the previous menu.")
            GlobalFunctions.addRemoveComicMenu()

    def modifySettingsMenu():
        GlobalFunctions.cls()

        config_file = Path("/data/comic_path_config.json")
        if config_file.is_file():
            with open(config_file) as f_in:
                current_root_path = (json.load(f_in))['comic_dir']
        else:
            current_root_path = "ROOT PATH NOT SET"

        api_file = Path("/data/comicvine_api_key.json")
        if api_file.is_file():
            with open(api_file) as f_in:
                current_api_key = (json.load(f_in))['comic_api_key']
        else:
            current_api_key = "API KEY NOT SET"
        
        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        1: Set path to save Comics (Current: """ + current_root_path + """)
        2: Set ComicVine API key (Current: """ + current_api_key + """)

        Q: Quit

        M: Main Menu

        Please enter your choice: """)

        if choice == "1":
            GlobalFunctions.set_comic_config()
        elif choice == '2':
            GlobalFunctions.set_api_key()
        elif choice=="Q" or choice=="q":
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must only select a valid entry.")
            print("Please try again")
            GlobalFunctions.modifySettingsMenu()

    def mainMenu():
        try:
            GlobalFunctions.cls()
     
            choice = input("""
            ***PLEASE MAKE YOUR SELECTION***

            1: Run batch downloader
            2: Add/Remove Comics
            3. Check single comic from existing list

            M: Update all comic Metadata
            
            Q: Quit

            S: Modify Settings

            Please enter your choice: """)

            if choice == "1":
                GlobalFunctions.batchComicDownload()
            elif choice == "2":
                GlobalFunctions.addRemoveComicMenu()
            elif choice == "3":
                GlobalFunctions.single_comic_download()
            elif choice == "M" or choice =="m":
                GlobalFunctions.scanComicMetadata()
            elif choice=="Q" or choice=="q":
                GlobalFunctions.cls()
                sys.exit
            elif choice == "S" or choice == "s":
                GlobalFunctions.modifySettingsMenu()
            else:
                print("You must only select a valid entry.")
                print("Please try again")
                GlobalFunctions.mainMenu()
        except EnvironmentError as e:
            print(e)
        