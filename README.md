# Spotify Connect Web

This is based off of the example code from https://github.com/plietar/spotify-connect

## Quickstart using a pre-built chroot
If you just want to get running, you can use a pre-built chroot with the latest version installed.

    curl -O http://spotify-connect-web.s3-website.eu-central-1.amazonaws.com/spotify-connect-web.sh
    chmod u+x spotify-connect-web.sh
    # Download the current chroot (~ 180 MB)
    ./spotify-connect-web.sh install
    # Copy your `spotify_appkey.key` into the app directory. (See below for information on how to get that file.)
    sudo cp spotify_appkey.key spotify-connect-web-chroot/usr/src/app/
    # Run using normal cmdline options
    ./spotify-connect-web.sh --username 12345678 --password xyz123 --bitrate 320

(Btw, the chroot is built nightly from master using Docker on a C1. See the [Makefile](Makefile.docker) for details.)

## Quickstart with Docker
(You will have to use `sudo` if not logged in as root.)

* Get Docker running on your machine. (See [this preliminary documentation](https://github.com/aetherical/docker/blob/master/docs/sources/installation/raspberrypi.md) for advice.)
* Get your `spotify_appkey.key` and put it into the base directory. (See below for details.)
* Build the container via `docker build -t spotify-connect-web .`
* Run it via `~/run-with-docker`.

## Installation
Run `pip install -r requirements.txt` and also `apt-get install python-gevent` (Can't be installed from pip (on debian based systems) because of a [bug](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=770616)) (Other distributions can just run `pip install gevent`)

### Pyalsaaudio
Can either be installed via `pip` (requires the ALSA headers (`libasound2-dev` package on Debian/Ubuntu)) or the `python-alsaaudio` package on Debian/Ubuntu

## Usage
Tested against the rocki `libspotify_embedded_shared.so`
```
usage: main.py [-h] [--device DEVICE] [--mixer MIXER] [--dbrange RANGE}] [--debug] [--key KEY]
               [--username USERNAME] [--password PASSWORD] [--name NAME]
               [--bitrate {90,160,320}] [--credentials CREDENTIALS]

Web interface for Spotify Connect

optional arguments:
  -h, --help            show this help message and exit
  --device DEVICE, -D DEVICE
                        alsa output device
  --mixer MIXER, -m MIXER
                        alsa mixer name for volume control
  --dbrange RANGE, -r RANGE
  						alsa mixer volume range in Db
  --debug, -d           enable libspotify_embedded/flask debug output
  --key KEY, -k KEY     path to spotify_appkey.key
  --username USERNAME, -u USERNAME
                        your spotify username
  --password PASSWORD, -p PASSWORD
                        your spotify password
  --name NAME, -n NAME  name that shows up in the spotify client
  --bitrate {90,160,320}, -b {90,160,320}
                        Sets bitrate of audio stream (may not actually work)
  --credentials CREDENTIALS, -c CREDENTIALS
                        File to load and save credentials from/to
```

`libspotify_embedded_shared.so` must be in the same directory as the python scripts.  
Also requires a spotify premium account, and the `spotify_appkey.key` (the binary version) file needs to be obtained from https://developer.spotify.com/my-account/keys , and needs to placed in the python scripts directory, or have the path specified with the `-k` parameter

### Launching
- Running without debug output `LD_LIBRARY_PATH=$PWD python main.py`
- Running with debug output `LD_LIBRARY_PATH=$PWD python main.py -d`
- Run with only flask debug output (flask debug output allows you to see the python exceptions that are thrown) `DEBUG=true LD_LIBRARY_PATH=$PWD python main.py`
- Can also be run without the web server (Requires username and password to be passed in as parameters)  `LD_LIBRARY_PATH=$PWD python connect.py -u username -p password`

### Headers
Generated with `cpp spotify.h > spotify.processed.h && sed -i 's/__extension__//g' spotify.processed.h`
`spotify.h` was taken from from https://github.com/plietar/spotify-connect

## Web server
Server runs on port `4000`

### Logging in
There's a login button on the webpage to enter a username and password, or zeroconf (avahi) login can be used after executing the command `avahi-publish-service TestConnect _spotify-connect._tcp 4000 VERSION=1.0 CPath=/login/_zeroconf` (`avahi-publish-service` is in the `avahi-utils` package).

After logging in successfully, a blob is sent by Spotify and saved to disk (to `credentials.json` by default), and is use to login automatically on next startup.
