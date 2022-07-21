#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import Global
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
from sqlite3 import Error
import time
import getpass
from zipfile import ZipFile
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from termcolor import colored

class GlobalFunctions:
    def cls():
        os.system('cls' if os.name=='nt' else 'clear')
    
    def mainMenu():
        try:
            GlobalFunctions.cls()

            conn = sqlite3.connect("/data/comicDatabase.db")
            cur = conn.cursor()
            rootQuerySQL = "SELECT * FROM _config"
            cur.execute(rootQuerySQL)
            rootRows = cur.fetchall()

            for row in rootRows:
                if row is not None:
                    continue
                else:
                    GlobalFunctions.set_comic_config()

            choice = input("""
            ***PLEASE MAKE YOUR SELECTION***

            1: Run batch downloader
            2: Add/Remove Comics
            
            0: Quit

            S: Modify Settings

            Please enter your choice: """)

            if choice == "1":
                GlobalFunctions.comicDownload()
            elif choice == "2":
                GlobalFunctions.addRemoveComicMenu()
            elif choice=="0":
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

    def add_new_comic(track):
        try:
            GlobalFunctions.cls()
            #Create connections to database
            conn = sqlite3.connect("/data/comicDatabase.db")
            cur = conn.cursor()

            #Get the current list of comics

            selectAllComicsQuery = 'SELECT * FROM _comicURLs WHERE tracked = 1'
            cur.execute(selectAllComicsQuery)
            allComics = cur.fetchall()

            # Let's create our table
            comicTable = PrettyTable()

            comicTable.field_names = ["Comic Folder/Name", "Comic URL"]

            for row in allComics:
                comicTable.add_row ([row[2],row[1]])
                
            print(comicTable)    

            newComic = input ("""Enter URL for new comic (Leave blank and press Enter to return to menu): """)
            
            if newComic:
                if track == 'true':
                    checkExistsQuery = "SELECT * from _comicURLs where link is " + "'" + newComic + "'"
                    cur.execute(checkExistsQuery)
                    exists = cur.fetchall()
                    if exists:
                        print("Comic already exists in pull list!")
                        GlobalFunctions.addRemoveComicMenu()
            else:
                GlobalFunctions.addRemoveComicMenu()
            
            title = (newComic.split("/"))
            title = title[-1]
            
            comicFolder = title.replace("-"," ")
            if comicFolder[comicFolder.__len__() -1] == ' ':
                comicFolder = comicFolder[:-1]

            title = title.replace("-","")
            
            if track == 'true':
                insertComic = "INSERT INTO _comicURLs (name, link, folder, tracked) VALUES (%s,%s,%s,%s)" % ("'"+title+"'","'"+newComic+"'","'"+comicFolder+"'",'true')
            else:
                insertComic = "INSERT INTO _comicURLs (name, link, folder, tracked) VALUES (%s,%s,%s,%s)" % ("'"+title+"'","'"+newComic+"'","'"+comicFolder+"'",'false')
                GlobalFunctions.single_comic_download(newComic)

            cur.execute(insertComic)
            conn.commit()
            conn.close()

            GlobalFunctions.addRemoveComicMenu()
        except EnvironmentError:
            print(EnvironmentError)

    def remove_comic():
        GlobalFunctions.cls()

        #Create connections to database
        conn = sqlite3.connect("/data/comicDatabase.db")
        cur = conn.cursor()

        #Get the current list of comics
        comicListQuery = 'SELECT * from _comicURLs WHERE tracked = 1'
        cur.execute(comicListQuery)
        comicList = cur.fetchall()

        i = 1

        for row in comicList:
            listNum = str(i)
            print(listNum + ". " + row[2])
            i = i+1
        
        try:
            comicToRemove = (int(input ("Enter number of comic to remove from queue (this will not remove history): ")))
            removeComic = comicList[(comicToRemove - 1)][1]
            dropComicSql = "UPDATE _comicURLs SET tracked = 'false' WHERE link is " + "'" + removeComic + "'"
            cur.execute(dropComicSql)
            conn.commit()
            GlobalFunctions.addRemoveComicMenu()
        except ValueError:
            GlobalFunctions.addRemoveComicMenu()
              
        conn.close()

    def addRemoveComicMenu():
        GlobalFunctions.cls()
        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        1: Add New Comic to tracker
        2: Remove Comic from tracker
        3: Download Single Comic or Series without tracking
        4: Search for Comics

        0: Quit

        M: Main Menu

        Please enter your choice: """)

        if choice == "1":
            track = 'true'
            GlobalFunctions.add_new_comic(track)
        elif choice == "2":
            GlobalFunctions.remove_comic()
        elif choice == "3":
            track = 'false'
            GlobalFunctions.add_new_comic(track)
        elif choice == "4":
            GlobalFunctions.comicSearch()
        elif choice=="0":
            GlobalFunctions.cls()
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must only select a valid entry.")
            print("Please try again")
            GlobalFunctions.addRemoveComicMenu()

    def comicDownload():
        GlobalFunctions.cls()
        #Create connections to database
        conn = sqlite3.connect("/data/comicDatabase.db")
        cur = conn.cursor()

        #Get the current list of comics

        selectAllComicsQuery = "SELECT * FROM _comicURLs"
        cur.execute(selectAllComicsQuery)
        allComics = cur.fetchall()

        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        conn.close()

        for rootRow in root_path:
            rootPath = rootRow[0]

        for row in tqdm(allComics):
            GlobalFunctions.pullComic(row,rootPath)
           
    def single_comic_download(link):
        conn = sqlite3.connect("/data/comicDatabase.db")
        cur = conn.cursor()
        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        conn.close()

        for rootRow in root_path:
            rootPath = rootRow[0]            

        try:
            newComic = link             
        except:
            GlobalFunctions.addRemoveComicMenu()
        
        sess = requests.session()
        retries = Retry(total=5, backoff_factor=1)
        sess.mount('http://', HTTPAdapter(max_retries=retries))
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'secfetch-user': '?1'
        }

        title = (newComic.split("/"))
        if title[4] == title[-1]:
            newComic = "https://readcomicsonline.ru/comic/" + title[4]
            print(newComic)
        else:
            newComic = "https://readcomicsonline.ru/comic/" + title[4]
            print(newComic)
        
        page = sess.get(newComic, headers=headers)
        time.sleep(5)
        
        soup = BeautifulSoup(page.text,"html5lib")
        links = soup.findAll('a')
        
        comicFolder = title[4].replace("-"," ")
        
        findLinks = []

        for link in links:
            try:
                if "/comic/" in link.get('href'):
                    findLinks.append(link)
            except EnvironmentError as e:
                print(e)
        
        for link in findLinks:
            try:
                # Create the URL to the issue from the relative link on the page. the '&readType=1' 
                # option specifies to show the full comic on one page.  
                print(link)
                comicLink = (link.get('href')).replace(" ","")
                print(comicLink)
                # Create our sesion to the issue and get the encoded html. 
                comicChapterPage = sess.get(comicLink)
                time.sleep(5)
                page_source = BeautifulSoup(comicChapterPage.text.encode("utf-8"), "html.parser")
                
                # Find each image link from the encoded html.
                img_list = page_source.findAll('img')
                
                # Generate the issue name.
                file_issue_name = comicLink.split("/")
                file_issue_name = file_issue_name[-1]
                file_issue_name = file_issue_name.split("?")
                file_issue_name = file_issue_name[0]
                file_issue_name = file_issue_name.replace("-"," ").replace("%","")  

                # Set the name for the CBZ file.
                # cbz_name = comicLink.replace("https://readcomicsonline.ru/comic/","").split("/")
                # cbz_name = cbz_name[0].replace("-"," ")
                # cbz_name = cbz_name + " - Ch " + file_issue_name            
                cbz_name = (link.string).replace(":","").replace(" / ","").replace("/"," ").replace("-)",")").replace("%","")
                
                # Specify the paths. The 'tmpPath' is the issue sub-directory in the comic directory
                # where the jpegs for the issue will be stored. The 'comicPath' is the top level folder
                # where the resulting CBZ file will be stored.
                tmpPath = rootPath + "/" + comicFolder + "/" + file_issue_name     
                comic_path = rootPath + "/" + comicFolder + "/"

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

                total_images = len(imgLinks)
                
                print("Downloading images for "+cbz_name)

                #This downloads all the images for the comic as jpgs in a folder named for the issue.
                for imgLink in tqdm(imgLinks):
                    # Ensures that a zero is prepended to ensure proper page order.
                    max_digits = int(math.log10(int(total_images))) + 1
                    current_chapter_value = imgLinks.index(imgLink)
                    file_name = str(current_chapter_value).zfill(max_digits) + ".jpg"
                    file_name = imgLink.split("/")
                    file_name = file_name[-1]
                    r = (sess.get(imgLink)).content
                    f = open(tmpPath + "/" + file_name, 'wb')
                    f.write(r)
                    f.close()

                print("Creating comic file "+cbz_name+".cbz...")
                # Create the CBZ file from the downloaded images, then delete the image files.
                zipObj = ZipFile(comic_path + cbz_name + ".cbz", 'w')
                for issuePage in tqdm(os.listdir(tmpPath)):
                    zipObj.write(tmpPath + "/" + issuePage)
                    os.remove(tmpPath + "/" + issuePage)
                zipObj.close()    
                os.rmdir(tmpPath)

                fullComicPath = comic_path + cbz_name + ".cbz"
                GlobalFunctions.generateMetadata(fullComicPath)
            except EnvironmentError as e:
                print(e)
        
    def modifySettingsMenu():
        GlobalFunctions.cls()

        conn = sqlite3.connect("/data/comicDatabase.db")
        cur = conn.cursor()
        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        conn.close()
        
        if not root_path:
            rootPath = 'ROOT PATH NOT SET'
            APIKey = 'API KEY NOT SET'
        else:
            rootPath = root_path[0][0]
            APIKey = root_path[0][1]            

        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        1: Set path to save Comics (Current: """ + rootPath + """)
        2: Set ComicVine API key (Current: """ + APIKey + """)

        0: Quit

        M: Main Menu

        Please enter your choice: """)

        if choice == "1":
            GlobalFunctions.set_comic_config()
        elif choice == '2':
            GlobalFunctions.set_api_key()
        elif choice=="0":
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must only select a valid entry.")
            print("Please try again")
            GlobalFunctions.modifySettingsMenu()

    def set_comic_config():
        GlobalFunctions.cls()

        try:
            conn = sqlite3.connect("/data/comicDatabase.db")
            cur = conn.cursor()
            cur.execute ("SELECT * FROM _config")
            pathConfig = cur.fetchall()
            
            if pathConfig:
                print("Entry for already exists!")
                for rootRow in pathConfig:
                    rootPath = rootRow[0]
                update = input("Would you like to update your comic root path (" + rootPath + ")? (Y/N): ")
                if update == "Y" or update == "y":
                    comicPath = input("Enter the path to your comic directory: ")
                    while not comicPath:
                        print("No path selected.")
                        comicPath = input("Enter the path to your comic directory: ")
                    comicPath = comicPath.replace("\\","/")
                    updateRootPathProvider = "UPDATE _config SET comicFolder = '" + comicPath + "'"
                    cur.execute(updateRootPathProvider)
                    conn.commit()

            conn.commit()
            conn.close()

            GlobalFunctions.modifySettingsMenu()
        except EnvironmentError:
            GlobalFunctions.modifySettingsMenu()

    def set_api_key():
        GlobalFunctions.cls()

        try:
            conn = sqlite3.connect("/data/comicDatabase.db")
            cur = conn.cursor()
            cur.execute ("SELECT * FROM _config")
            pathConfig = cur.fetchall()
            
            if pathConfig:
                print("Entry for already exists!")
                for rootRow in pathConfig:
                    rootPath = rootRow[0][1]
                update = input("Would you like to update your ComicVine API Key (" + rootPath + ")? (Y/N): ")
                if update == "Y" or update == "y":
                    apiKey = input("Enter your new ComicVine API key: ")
                    if apiKey == "":
                        print("No API Key entered. ComicDownloader will not be able to auto-tag downloaded comics.")
                        input ("Press Enter to continue...")
                    updateRootPathProvider = "UPDATE _config SET comicVineApiKey = '" + apiKey + "'"
                    cur.execute(updateRootPathProvider)
                    conn.commit()
            
            conn.commit()
            conn.close()

            GlobalFunctions.modifySettingsMenu()
        except EnvironmentError:
            GlobalFunctions.modifySettingsMenu()

    def comicSearch():
        try:
            GlobalFunctions.cls()

            sess = requests.session()
            
            retries = Retry(total=5, backoff_factor=1)
            sess.mount('http://', HTTPAdapter(max_retries=retries))
            headers = {
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'sec-fetch-mode': 'navigate',
                'secfetch-user': '?1'
            }
            page = sess.get("https://readcomicsonline.ru/comic-list", headers=headers)


            soup = BeautifulSoup(page.text,"html5lib")

            links = soup.findAll('a')

            findLinks = []

            x = 1

            for link in links:
                if "comic-list?alpha=" in link.get('href'):
                    indexLetter = link.get('href').split('=')[1]
                    findLinks.append([x,indexLetter,link.get('href')])
                    x = x + 1

            # Let's create our table
            searchTable = PrettyTable()
            searchTable.field_names = ["Number", "Section", "Link"]

            searchTable.align["Number"] = "l"
            searchTable.align["Section"] = "l"
            searchTable.align["Link"] = "l"

            for item in findLinks:
                searchTable.add_row([item[0],item[1],item[2]])

            print(searchTable)

            selection = input("Enter number for the section you want to browse: ")

            for row in findLinks:
                if row[0] == int(selection):
                    tagLinks = []
                    for link in links:
                        searchHREF = "https://readcomicsonline.ru/comic-list/tag/" + row[1].lower()
                        if searchHREF in link.get('href'):
                            print(link.text)


        except EnvironmentError as e:
            print(e)

    def pullComic(row,rootPath):
        print("\n" + row[2])
        
        #Create connections to database
        conn = sqlite3.connect("/data/comicDatabase.db")
        cur = conn.cursor()

        sess = requests.session()
        retries = Retry(total=5, backoff_factor=1)
        sess.mount('http://', HTTPAdapter(max_retries=retries))
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'secfetch-user': '?1'
        }
        page = sess.get(row[1], headers=headers)
        title = (row[1].split("/"))
        time.sleep(2)
        title = title[-1]
        title = title.replace("-","")
        print("Checking for new issues of "+title)
        createTable = "CREATE TABLE IF NOT EXISTS " + title + " (name text NOT NULL,link text UNIQUE);"
        try:
            cur.execute(createTable)
        except EnvironmentError as e:
            print(e)
        soup = BeautifulSoup(page.text,"html5lib")
        links = soup.findAll('a')

        findLinks = []

        for link in links:
            try:
                if "/comic/" in link.get('href'):
                    findLinks.append(link)
            except EnvironmentError as e:
                print(e)
        
        for link in findLinks:
            try:
                # Create the URL to the issue from the relative link on the page. the '&readType=1' 
                # option specifies to show the full comic on one page.
                comicLink = (link.get('href')).replace(" ","")

                # Get the list of already downloaded issues from the database.  
                checkExistsQuery = "SELECT * from " + title + " where link is " + "'" + comicLink + "' COLLATE NOCASE"
                cur.execute(checkExistsQuery)
                exists = cur.fetchall()

                # If the link exists, continue to the next issue. If not, download the issue.
                if exists:
                    continue
                else:
                    # Insert the link into database. Note that this will not be committed
                    # until the comic successfully downloads.
                    query = "INSERT into " + title + " (name,link) VALUES (%s,%s)" % ("'"+title+"'","'"+comicLink+"'")
                    cur.execute(query)           

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
                    # cbz_name = comicLink.replace("https://readcomicsonline.ru/comic/","").split("/")
                    # cbz_name = cbz_name[0].replace("-"," ")
                    # cbz_name = cbz_name + " " + file_issue_name
                    cbz_name = (link.string).replace(":","").replace(" / ","").replace("/"," ").replace("-)",")").replace("%","")
                    
                    # Specify the paths. The 'tmpPath' is the issue sub-directory in the comic directory
                    # where the jpegs for the issue will be stored. The 'comicPath' is the top level folder
                    # where the resulting CBZ file will be stored.
                    tmpPath = rootPath + "/" + row[2] + "/" + file_issue_name     
                    comic_path = rootPath + "/" + row[2] + "/"    

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
                        #file_name = imgLink.split("/")
                        #file_name = file_name[-1]
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
                    #GlobalFunctions.generateMetadata(fullComicPath)

                    # Commit the change to the database.
                    conn.commit() 
                        
            except sqlite3.IntegrityError:
                print('ERROR') 

        conn.commit()
        conn.close()

    def generateMetadata(comicFile):
        subprocess.Popen([r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe',
        '-ExecutionPolicy',
        'Unrestricted',
        './comictagger/comictag.ps1 -FileName "',
        comicFile,'"'], cwd=os.getcwd())

    def createNewDatabase():
        conn = None
        try:
            conn = sqlite3.connect('/data/comicDatabase.db')
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                # Create _comicURLs table
                createUrlTable = "CREATE TABLE IF NOT EXISTS _comicURLs (name text NOT NULL, link text UNIQUE, folder TEXT, tracked TEXT)"
                cur = conn.cursor()
                cur.execute(createUrlTable)
                conn.commit()

                # Create _config table
                createConfigTable = "CREATE TABLE IF NOT EXISTS _config (comicFolder TEXT, comicVineAPIKey TEXT)"
                cur.execute(createConfigTable)
                conn.commit()
                
                # Create the default root path config
                comicPath = '/comics'
                cvApiKey = input ("""Enter your ComicVine API key): """)
                if cvApiKey == "":
                    print("No API Key entered. ComicDownloader will not be able to auto-tag downloaded comics.")
                    input ("Press Enter to continue...")
                insertConfigData = "INSERT INTO _config (comicFolder,comicVineAPIKey) VALUES (%s,%s)" % ("'"+comicPath+"'","'"+cvApiKey+"'")
                cur.execute(insertConfigData)
                conn.commit()
                
                #Close database connection
                conn.close()