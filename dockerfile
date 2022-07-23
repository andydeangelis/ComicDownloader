FROM ubuntu:latest
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get -y upgrade \
    # Install python/pip
    && apt-get install -y git python3 python3-pip python-is-python3 \
    # Make directory to be used for database
    && mkdir /data \
    # Clone the repo and install requirements
    && cd / && git clone 'https://github.com/andydeangelis/ComicDownloader.git' \
    # Switching to dev branch here
    && cd /ComicDownloader && git switch comicdownloader-dev \
    && pip3 install -r /ComicDownloader/requirements.txt \
    # Create empty directory to mount comic library
    && mkdir /comics \
    # Clone and build comictagger
    && cd / && git clone 'https://github.com/comictagger/comictagger.git' \
    && cd /comictagger && git switch develop \
    && pip3 install -r /comictagger/requirements_dev.txt \
    && cd /comictagger && python setup.py install \
    && pip3 install flask \
    # Clean Up
    && apt-get autoremove -y

ENTRYPOINT ["python", "/ComicDownloader/____.py"]