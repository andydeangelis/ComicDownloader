FROM alpine:latest
RUN apk add --no-cache git
# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
# Clone the repo and install requirements
RUN mkdir /data
RUN cd / && git clone 'https://github.com/andydeangelis/ComicDownloader.git'
RUN cd /ComicDownloader && git switch comicdownloader-dev
RUN pip3 install -r /ComicDownloader/requirements.txt
ENTRYPOINT ["python3", "/ComicDownloader/__main__.py"]