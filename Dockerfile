FROM armelbuild/debian:jessie
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update

RUN apt-get -y install python-pip python-dev libffi-dev libasound2-dev python-alsaaudio python-gevent libssl-dev
RUN apt-get -y install alsa-utils

RUN wget -q -O /usr/lib/libspotify_embedded_shared.so https://github.com/sashahilton00/spotify-connect-resources/raw/master/Rocki%20Firmware/dlna_upnp/spotify/lib/libspotify_embedded_shared.so

ADD requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN pip install -r requirements.txt

ADD . /usr/src/app

ENTRYPOINT ["python", "main.py"]
EXPOSE 4000
