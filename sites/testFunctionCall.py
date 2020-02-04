from readcomiconline import ReadComicOnline
from comicextra import ComicExtra
from prettytable import PrettyTable
import re
import cloudscraper
import requests
from bs4 import BeautifulSoup
import os
import shutil
import sys
from tqdm import tqdm
import sqlite3
import time
from zipfile import ZipFile

searchData = input("Enter search criteria: ")

searchResult = ComicExtra.comicSearchCE(searchData)

# Let's create our table
searchTable = PrettyTable()
searchTable.field_names = ["Number", "Title", "Comic URL"]

searchTable.align["Number"] = "l"
searchTable.align["Title"] = "l"
searchTable.align["Comic URL"] = "l"

x = 1
linkList = []

for link in searchResult:
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

print(selectedLink)

input("Comic successfully entered into pull list. Press Enter to return to the main menu.")