#FROM alpine:latest
FROM ubuntu:latest
#RUN apk add --no-cache git gcc
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git
# Install python/pip
ENV PYTHONUNBUFFERED=1
#RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apt-get install -y python3 python3-pip python-is-python3
#RUN python3 -m ensurepip
#RUN pip3 install --no-cache --upgrade pip setuptools
# Clone the repo and install requirements
RUN mkdir /data
RUN cd / && git clone 'https://github.com/andydeangelis/ComicDownloader.git'
# Switching to dev branch here
RUN cd /ComicDownloader && git switch comicdownloader-dev
RUN pip3 install -r /ComicDownloader/requirements.txt
# Create empty directory to mount comic library
RUN mkdir /comics

# Clone and build comictagger
RUN cd / && git clone 'https://github.com/comictagger/comictagger.git'
RUN cd /comictagger && git switch develop
RUN pip3 install -r /comictagger/requirements_dev.txt
RUN cd /comictagger && python setup.py install

# Clean Up
RUN apt-get autoremove -y

ENTRYPOINT ["comictagger", "-h"]