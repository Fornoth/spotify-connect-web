FROM armelbuild/debian:jessie

RUN apt-get update

RUN apt-get -y install python-pip python-dev libffi-dev libasound2-dev python-alsaaudio python-gevent
RUN apt-get -y install alsa-utils

RUN cd /tmp \
 && wget -q http://update.myrocki.com/dlna_upnp.tar.gz \
 && tar xzf dlna_upnp.tar.gz \
 && mkdir /usr/src/app \
 && cp dlna_upnp/spotify/lib/libspotify_embedded_shared.so /usr/lib/ \
 && rm /tmp/dlna_upnp* -fR

ADD requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN pip install -r requirements.txt

ADD . /usr/src/app

ENTRYPOINT ["python", "main.py"]
EXPOSE 4000
