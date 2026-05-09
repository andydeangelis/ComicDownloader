# ComicDownloader
ComicDownloader is a small utility that will track a comic book collection in a SQL Lite database and download missing/new issues for series. While it is simple to use, there are some limitations to be aware of. Note that this app is designed to run as a docker container.

# Directories
There are two directories in the container that should be mapped to directories on your docker host (otherwise, you'll delete all you're data whenever you destroy and recreate the image). These directories are:

    - /comics - This is where your comic CBZ files will be stored.
    - /data - This is where your database will be stored.

# Create the image
ComicDownloader uses the base Ubuntu docker image from hub,docker.com. While I may switch to alpine in the future for a smaller image size, I had neither the time nor patience to get it working with all the missing dependencies. To create the image, clone this repo (really, all you need is the dockerfile), then run this command from wherever the dockerfile is saved:

    docker build -t ComicDownloader .

# Run the script using a container.
This container is designed to be run once and then destroyed after completion. If you have mapped your volumes correctly, the database and comic files will persist just fine.

    docker run -ti --rm --volume=/path/to/config/data:/data --volume=/path/to/comic/files:/comics --name comicdownloader

The first time the script runs, it will create the base database (if it doesn't already exist). Note that you will be prompted to enter your ComicVine API key. If you don't have an API key, head over to ComicVine.com and sign up for one (they're free). Note that if you do not enter an API key (which is fine), no metadata will be added to the resulting CBZ file.

# More about Metadata
If you've supplied a valid ComicVine API key, ComicDownloader will attempt to match and tag the created file. Most of the time (roughly 95%), this works fine, but there will be some instances where either there are multiple possible matches, or the entry doesn't exist in ComicVine's database. The most times I have seen this happen if you are downloading issues on day of release, and ComicVine hasn't been updated yet with the new issue. I suggest NOT setting to this run on actual comic release day (usually Tuesdays), but rather set the schedule to some time later in the week.

# Comictagger.py
Comictagger.py is installed during the image build so as to be used for generating the metadata. When invoked, it will use the API key set previously to look up the issue, download the metadata and then add the ComicInfo.xml file to the comic CBZ. This allows the Metadata to be carried with the file and be read by various comic software. This particular instance creates ComicInfo.xml files that adhere to the standard used by applications such as Komga.