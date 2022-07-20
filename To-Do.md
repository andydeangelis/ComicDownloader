To-Do

* Add tracker (true/false) to _comicURLs table - Keep all URLs
* Modify batch download to only download if tracked = 'true'
* Modify delete function to change tracked to 'false' upon removal
* Dynamically create ComicInfo.xml file for each cbz file created (use ComicInfo.xsd 2.0 for reference) - Need to determine where to get metadata
Add URLs/entries for existing Libraries not already listed
Reindex/Recreate entire library (to create metadata files)
Add ability to download/search from GetComics.info

Eventually create GUI front end (flask?)
Update requirements

subprocess.call(".\\comictagger\comictagger.exe --cv-api-key 4a6d1824adf3ac9dc351741d7dc3f7c81e99cf58 -f 'c:\qnap\books\comics\spiderman 2099 2015\Spider-Man 2099 (2015-) #1.cbz' -t CR -o -v -s -n")