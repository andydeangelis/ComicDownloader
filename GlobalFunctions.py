#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

class GlobalFunctions:
    def cls():
        os.system('cls' if os.name=='nt' else 'clear')
    
    def mainMenu():
        try:
            GlobalFunctions.cls()
            choice = input("""
            ***PLEASE MAKE YOUR SELECTION***

            1: Run batch downloader
            2: Add/Remove Comics
            
            0: Quit

            S: Modify System Settings

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

    def add_new_comic():
        try:
            GlobalFunctions.cls()
            #Create connections to database
            conn = sqlite3.connect("./config/comicDatabase.db")
            cur = conn.cursor()

            #Get the current list of comics

            selectAllComicsQuery = "SELECT * FROM _comicURLs"
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
                checkExistsQuery = "SELECT * from _comicURLs where link is " + "'" + newComic + "'"
                cur.execute(checkExistsQuery)
                exists = cur.fetchall()
                if exists:
                    print("Comic already exists in pull list!")
                    GlobalFunctions.add_new_comic()
            else:
                GlobalFunctions.addRemoveComicMenu()
            
            title = (newComic.split("/"))
            title = title[-1]
            comicFolder = title.replace("-"," ")
            title = title.replace("-","")
            insertComic = "INSERT INTO _comicURLs (name, link, folder) VALUES (%s,%s,%s)" % ("'"+title+"'","'"+newComic+"'","'"+comicFolder+"'")
            
            cur.execute(insertComic)
            conn.commit()
            conn.close()

            GlobalFunctions.addRemoveComicMenu()
        except EnvironmentError:
            print(EnvironmentError)

    def remove_comic():
        GlobalFunctions.cls()

        #Create connections to database
        conn = sqlite3.connect("./config/comicDatabase.db")
        cur = conn.cursor()

        #Get the current list of comics
        comicListQuery = "SELECT * from _comicURLs"
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
            dropComicSql = "DELETE FROM _comicURLs WHERE link is " + "'" + removeComic + "'"
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
            GlobalFunctions.add_new_comic()
        elif choice == "2":
            GlobalFunctions.remove_comic()
        elif choice == "3":
            GlobalFunctions.single_comic_download()
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
        conn = sqlite3.connect("./config/comicDatabase.db")
        cur = conn.cursor()

        #Get the current list of comics

        selectAllComicsQuery = "SELECT * FROM _comicURLs"
        cur.execute(selectAllComicsQuery)
        allComics = cur.fetchall()

        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        for rootRow in root_path:
            rootPath = rootRow[0]

        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'secfetch-user': '?1'
        }

        sess = requests.session()
        sess = cloudscraper.create_scraper(sess, delay=10)

        for row in tqdm(allComics):
            print("\n" + row[2])
            page = sess.get(row[1], headers=headers)
            title = (row[1].split("/"))
            time.sleep(5)
            title = title[-1]
            title = title.replace("-","")
            print("Creating/updating database table for series "+title)
            createTable = "CREATE TABLE IF NOT EXISTS " + title + " (name text NOT NULL,link text UNIQUE);"
            try:
                cur.execute(createTable)
            except EnvironmentError as e:
                print(e)
            soup = BeautifulSoup(page.text,"html5lib")
            table = soup.find("table")

            for i in range (1,3):
                try:
                    findLinks = table.find_all('a') 
                except EnvironmentError as e:
                    print(e)
            for link in findLinks:
                try:
                    # Create the URL to the issue from the relative link on the page. the '&readType=1' 
                    # option specifies to show the full comic on one page.
                    comicLink = "https://readcomiconline.to" + link.get('href') + "&readType=1"

                    # Get the list of already downloaded issues from the database.  
                    checkExistsQuery = "SELECT * from " + title + " where link is " + "'" + comicLink + "'"
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
                        img_list = re.findall(r"lstImages.push\(\"(.*?)\"\);", str(page_source))

                        # Generate the issue name.
                        file_issue_name = comicLink.split("/")
                        file_issue_name = file_issue_name[-1]
                        file_issue_name = file_issue_name.split("?")
                        file_issue_name = file_issue_name[0]
                        file_issue_name = file_issue_name.replace("-"," ")

                        # Set the name for the CBZ file.
                        cbz_name = comicLink.replace("https://readcomiconline.to/Comic/","").split("/")
                        cbz_name = cbz_name[0].replace("-"," ")
                        cbz_name = cbz_name + " - Ch " + file_issue_name
                        
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
                        links = []

                        for img in img_list:
                            hdImgLink = img.replace("=s1600", "=s0").replace("/s1600", "/s0")
                            links.append(hdImgLink)
                        
                        total_images = len(links)
                        
                        print("Downloading images for "+cbz_name)
                        #This downloads all the images for the comic as jpgs in a folder named for the issue.
                        for link in tqdm(links):
                            # Ensures that a zero is prepended to ensure proper page order.
                            max_digits = int(math.log10(int(total_images))) + 1
                            current_chapter_value = links.index(link)
                            file_name = str(current_chapter_value).zfill(max_digits) + ".jpg"
                            r = requests.get(link)
                            with open(tmpPath + "/" + file_name, 'wb') as f:
                                f.write(r.content)
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
                        # Commit the change to the database.
                        conn.commit() 

                    #Create connections to database
                    conn = sqlite3.connect("./config/comicDatabase.db")
                    cur = conn.cursor()

                    completed = "<span class=\"info\">Status:</span>&nbsp;Completed"
                    ongoing = "<span class=\"info\">Status:</span>&nbsp;Ongoing"

                    if completed in page.text:
                        dropComicSql = "DELETE FROM _comicURLs WHERE name is '" + title + "'"
                        cur.execute(dropComicSql)
                    elif ongoing in page.text:
                        continue

                    # Commit the change to the database.
                    conn.commit()
                            
                except sqlite3.IntegrityError:
                    print('ERROR') 

            conn.commit()

        conn.close()
    def single_comic_download():
        conn = sqlite3.connect("./config/comicDatabase.db")
        cur = conn.cursor()
        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        conn.close()

        for rootRow in root_path:
            rootPath = rootRow[0]

        try:
            newComic = input ("""Enter URL for new comic (Leave blank and press Enter to return to menu): """)
            if not newComic:
                GlobalFunctions.addRemoveComicMenu()                
        except:
            GlobalFunctions.addRemoveComicMenu()
        
        sess = requests.session()
        sess = cloudscraper.create_scraper(sess, delay=10)
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'secfetch-user': '?1'
        }
        title = (newComic.split("/"))
        if title[4] == title[-1]:
            newComic = "https://readcomiconline.to/Comic/" + title[4]
            print(newComic)
        else:
            newComic = "https://readcomiconline.to/Comic/" + title[4]
            print(newComic)
        
        page = sess.get(newComic, headers=headers)
        time.sleep(5)

        soup = BeautifulSoup(page.text,"html5lib")
        table = soup.find("table")
        
        comicFolder = title[4].replace("-"," ")
        
        for i in range (1,3):
            try:
                findLinks = table.find_all('a') 
            except EnvironmentError as e:
                print(e)
        
        for link in findLinks:
            try:
                # Create the URL to the issue from the relative link on the page. the '&readType=1' 
                # option specifies to show the full comic on one page.  
                comicLink = "https://readcomiconline.to" + link.get('href') + "&readType=1"
                
                # Create our sesion to the issue and get the encoded html. 
                comicChapterPage = sess.get(comicLink, headers=headers)
                page_source = BeautifulSoup(comicChapterPage.text.encode("utf-8"), "html.parser")

                # Find each image link from the encoded html.
                img_list = re.findall(r"lstImages.push\(\"(.*?)\"\);", str(page_source))
                
                # Generate the issue name.
                file_issue_name = comicLink.split("/")
                file_issue_name = file_issue_name[-1]
                file_issue_name = file_issue_name.split("?")
                file_issue_name = file_issue_name[0]
                file_issue_name = file_issue_name.replace("-"," ")     

                # Set the name for the CBZ file.
                cbz_name = comicLink.replace("https://readcomiconline.to/Comic/","").split("/")
                cbz_name = cbz_name[0].replace("-"," ")
                cbz_name = cbz_name + " - Ch " + file_issue_name            
                
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
                links = []

                for img in img_list:
                    hdImgLink = img.replace("=s1600", "=s0").replace("/s1600", "/s0")
                    links.append(hdImgLink)

                total_images = len(links)
                
                print("Downloading images for "+cbz_name)
                #This downloads all the images for the comic as jpgs in a folder named for the issue.
                for link in tqdm(links):
                    # Ensures that a zero is prepended to ensure proper page order.
                    max_digits = int(math.log10(int(total_images))) + 1
                    current_chapter_value = links.index(link)
                    file_name = str(current_chapter_value).zfill(max_digits) + ".jpg"
                    r = requests.get(link)
                    with open(tmpPath + "/" + file_name, 'wb') as f:
                        f.write(r.content)
                        f.close()  

                print("Creating comic file "+cbz_name+".cbz...")
                # Create the CBZ file from the downloaded images, then delete the image files.
                zipObj = ZipFile(comic_path + cbz_name + ".cbz", 'w')
                for issuePage in tqdm(os.listdir(tmpPath)):
                    zipObj.write(tmpPath + "/" + issuePage)
                    os.remove(tmpPath + "/" + issuePage)
                zipObj.close()    
                os.rmdir(tmpPath)
            except EnvironmentError as e:
                print(e)
            
        GlobalFunctions.addRemoveComicMenu()

    def modifySettingsMenu():
        GlobalFunctions.cls()

        conn = sqlite3.connect("./config/comicDatabase.db")
        cur = conn.cursor()
        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        conn.close()
        
        for rootRow in root_path:
            rootPath = rootRow[0]

        choice = input("""
        ***PLEASE MAKE YOUR SELECTION***

        1: Set comic root path (Current path: """ + rootPath + """)

        0: Quit

        M: Main Menu

        Please enter your choice: """)

        if choice == "1":
            GlobalFunctions.set_comic_root_path()
        elif choice=="0":
            sys.exit
        elif choice == "M" or choice == "m":
            GlobalFunctions.mainMenu()
        else:
            print("You must only select a valid entry.")
            print("Please try again")
            GlobalFunctions.modifySettingsMenu()

    def set_comic_root_path():
        GlobalFunctions.cls()

        conn = sqlite3.connect("./config/comicDatabase.db")
        cur = conn.cursor()
        root_path_query = "SELECT * FROM _config"
        cur.execute(root_path_query)
        root_path = cur.fetchall()
        
        for rootRow in root_path:
            rootPath = rootRow[0]

        try:
            comicPath = input("Enter the path to your comic directory (Current is: " + rootPath + "): ")
            
            while not comicPath:
                print("No path selected.")
                comicPath = input("Enter the path to your comic directory (Current is: " + rootPath + "): ")
            
            comicPath = comicPath.replace("\\","/")
            updateRootPathSql = "UPDATE _config SET comicFolder = '" + comicPath + "'"
            cur.execute(updateRootPathSql)
            conn.commit()
        except EnvironmentError:
            GlobalFunctions.modifySettingsMenu()
        
        conn.close()
        GlobalFunctions.modifySettingsMenu()

    def comicSearch():
        try:
            GlobalFunctions.cls()

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

            searchData = input("What comic would you like to search for (Ctrl+C to exit)? ")
            
            while not searchData:
                GlobalFunctions.cls()
                print("No valid criteria entered.")
                searchData = input("What comic would you like to search for (Ctrl+C to exit)? ")

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

            # Let's create our table
            searchTable = PrettyTable()
            searchTable.field_names = ["Number", "Title", "Comic URL"]

            searchTable.align["Number"] = "l"
            searchTable.align["Title"] = "l"
            searchTable.align["Comic URL"] = "l"

            x = 1
            linkList = []

            for link in findLinks:
                newLink = link.get('href')
                title = newLink.split("/")
                if len(title) == 3:
                    title = title[2].replace("-"," ")
                    searchTable.add_row([str(x),title,newLink])
                    linkList.append(newLink)
                    x = x+1                    

            print(searchTable.get_string(fields=["Number","Title"]))
            selection = int(input("Enter the number for the comic you want to enter: "))
            print(linkList[selection-1])
            
            if selection is None:
                input("No comic selected. Press Enter to return to the main menu.")
                GlobalFunctions.mainMenu()

            selectedLink = linkList[selection-1]
            selectedtitle = selectedLink.split("/")
            filteredtitle = selectedtitle[2].replace("-"," ")
            print(filteredtitle)

            selectedLink = "https://readcomiconline.to" + selectedLink
            print(selectedLink)

            #Create connections to database
            conn = sqlite3.connect("./config/comicDatabase.db")
            cur = conn.cursor()

            #Get the current list of comics

            selectAllComicsQuery = "SELECT * FROM _comicURLs"
            cur.execute(selectAllComicsQuery)
            allComics = cur.fetchall()

            if selectedLink:
                checkExistsQuery = "SELECT * from _comicURLs where link is " + "'" + selectedLink + "'"
                cur.execute(checkExistsQuery)
                exists = cur.fetchall()
                if exists:
                    input("Comic already exists in pull list! Press Enter to return to the main menu.")
                    GlobalFunctions.add_new_comic()
            else:
                GlobalFunctions.addRemoveComicMenu()
            
            comicFolder = filteredtitle
            title = selectedtitle[2].replace("-","")
            insertComic = "INSERT INTO _comicURLs (name, link, folder) VALUES (%s,%s,%s)" % ("'"+title+"'","'"+selectedLink+"'","'"+comicFolder+"'")
            
            cur.execute(insertComic)
            conn.commit()
            conn.close()

            input("Comic successfully entered into pull list. Press Enter to return to the main menu.")
            GlobalFunctions.mainMenu()
        except EnvironmentError as e:
            print(e)
