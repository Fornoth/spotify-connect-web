# Spotify Connect Web

This is based off of the example code from https://github.com/plietar/spotify-connect

## Quickstart using a packaged release
This is a version of spotify-connect-web with all dependencies bundled (about 7MB compressed, 13MB extracted)  
For armv7+ (Rpi 2, Rpi 3, etc, but not Rpi 1/Rpi Zero) devices only for now

Grab the latest release from [Releases](https://github.com/Fornoth/spotify-connect-web/releases)
### Installation instructions (example):
```
wget https://github.com/Fornoth/spotify-connect-web/releases/download/0.0.4-alpha/spotify-connect-web_0.0.4-alpha.tar.gz
tar zxvf spotify-connect-web_0.0.4-alpha.tar.gz
```
A `spotify-connect-web` directory will be created, and you'll need to put your `spotify_appkey.key` in that directory

### Running:
Just run `./spotify-connect-web`  in the extracted directory  
Supports the same options as the regular version


## Quickstart using a pre-built chroot
Grab the latest release from [Releases](https://github.com/Fornoth/spotify-connect-web/releases)

If you just want to get running, you can use a pre-built chroot with the latest version installed.
### Installation instructions (example):

    curl -O curl -OL https://github.com/Fornoth/spotify-connect-web/releases/download/0.0.4-alpha/spotify-connect-web.sh
    chmod u+x spotify-connect-web.sh
    # Download the current chroot (~ 180 MB)
    ./spotify-connect-web.sh install
    # Copy your `spotify_appkey.key` into the app directory. (See below for information on how to get that file.)
    sudo cp spotify_appkey.key spotify-connect-web-chroot/usr/src/app/
    # Run using normal cmdline options
    ./spotify-connect-web.sh --username 12345678 --password xyz123 --bitrate 320

(~~Btw, the chroot is built nightly from master using Docker on a C1.~~ Manually built for now. See the [Makefile](Makefile.docker) for details.)

## Quickstart with Docker
(You will have to use `sudo` if not logged in as root.)

* Get Docker running on your machine. (See [this preliminary documentation](https://github.com/aetherical/docker/blob/master/docs/sources/installation/raspberrypi.md) for advice.)
* Get your `spotify_appkey.key` and put it into the base directory. (See below for details.)
* Build the container via `docker build -t spotify-connect-web .`
* Run it via `~/run-with-docker`.

## Installation from source
Requires development packages for `Python`, `FFI`, and `Alsa`  
 - For Debian/Ubuntu: `apt-get install python-dev libffi-dev libasound2-dev`  

To install the other requirements: `pip install -r requirements.txt`

## Usage
```
usage: main.py [-h] [--device DEVICE | --playback_device PLAYBACK_DEVICE]
               [--mixer_device_index MIXER_DEVICE_INDEX] [--mixer MIXER]
               [--dbrange DBRANGE] [--cors CORS] [--debug] [--key KEY]
               [--username USERNAME] [--password PASSWORD] [--name NAME]
               [--bitrate {90,160,320}] [--credentials CREDENTIALS]

Web interface for Spotify Connect

optional arguments:
  -h, --help            show this help message and exit
  --device DEVICE, -D DEVICE
                        alsa output device (deprecated, use --playback_device)
  --playback_device PLAYBACK_DEVICE, -o PLAYBACK_DEVICE
                        alsa output device (get name from aplay -L)
  --mixer_device_index MIXER_DEVICE_INDEX
                        alsa card index of the mixer device
  --mixer MIXER, -m MIXER
                        alsa mixer name for volume control
  --dbrange DBRANGE, -r DBRANGE
                        alsa mixer volume range in Db
  --lastfm_username LASTFM_USERNAME
                        your Last.fm username
  --lastfm_password LASTFM_PASSWORD
                        your Last.fm password
  --lastfm_api_key LASTFM_API_KEY
                        your Last.fm API key
  --lastfm_api_secret LASTFM_API_SECRET
                        your Last.fm API secret
  --lastfm_credentials LASTFM_CREDENTIALS
                        file to load Last.fm credentials from
  --cors CORS           enable CORS support for this host (for the web api).
                        Must be in the format <protocol>://<hostname>:<port>.
                        Port can be excluded if its 80 (http) or 443 (https).
                        Can be specified multiple times
  --debug, -d           enable libspotify_embedded/flask debug output
  --key KEY, -k KEY     path to spotify_appkey.key (can be obtained from
                        https://developer.spotify.com/my-account/keys )
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
Also requires a spotify premium account, and the `spotify_appkey.key` (the binary version) file can be be obtained from https://developer.spotify.com/technologies/libspotify/application-keys/. Fill the 'App-key Request Form' in, send it and wait until you get the key sent via email (it can take a few weeks...).

After receiving it, you need to place it in the python scripts directory, or have the path specified with the `-k` parameter

### Launching from source
- Running without debug output `LD_LIBRARY_PATH=$PWD python main.py`
- Running with debug output `LD_LIBRARY_PATH=$PWD python main.py -d`
- Run with only flask debug output (flask debug output allows you to see the python exceptions that are thrown) `DEBUG=true LD_LIBRARY_PATH=$PWD python main.py`
- Can also be run without the web server (Requires username and password to be passed in as parameters)  `LD_LIBRARY_PATH=$PWD python connect.py -u username -p password`

### Headers
Generated with `cpp spotify.h > spotify.processed.h && sed -i 's/__extension__//g' spotify.processed.h`
`spotify.h` was taken from from https://github.com/plietar/spotify-connect

## Web server
Server runs on port `4000`

## Logging in
After logging in successfully, a blob is sent by Spotify and saved to disk (to `credentials.json` by default), and is use to login automatically on next startup.

### Username/Password
There's a login button on the webpage to enter a username and password, or you can pass the `--username` and `--password` arguments

### Last.fm
If you want to enable Last.fm scrobbling, you should first obtain API key at http://www.last.fm/api/account/create. You can pass your `--lastfm_username`, `--lastfm_password`, `--lastfm_api_key` and `--lastfm_api_secret` on the command line. You can also use `lastfm_credentials.json` and pass `--lastfm_credentials lastfm_credentials.json` to the command line. You can find an example of the file format in `lastfm_credentials.json.dist`. You need to explicitly pass the credentials file, otherwise the Last.fm module will not launch.

### Passwordless/Multiuser (Zeroconf/Avahi)
Zeroconf (Avahi) login can be used after executing the command `avahi-publish-service TestConnect _spotify-connect._tcp 4000 VERSION=1.0 CPath=/login/_zeroconf` (`avahi-publish-service` is in the `avahi-utils` package).

## Support
You can [file an issue](https://github.com/Fornoth/spotify-connect-web/issues/new) or come to the [Gitter chat](https://gitter.im/sashahilton00/spotify-connect-resources)
