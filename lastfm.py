import argparse
import json
import pylast
import time
from connect_ffi import lib
from utils import get_metadata

lastfm_arg_parser = argparse.ArgumentParser(add_help=False)

lastfm_arg_parser.add_argument('--lastfm_username', help='your Last.fm username', default=None)
lastfm_arg_parser.add_argument('--lastfm_password', help='your Last.fm password', default=None)
lastfm_arg_parser.add_argument('--lastfm_api_key', help='your Last.fm API key', default=None)
lastfm_arg_parser.add_argument('--lastfm_api_secret', help='your Last.fm API secret', default=None)
lastfm_arg_parser.add_argument('--lastfm_credentials', help='file to load Last.fm credentials from', default=None)

args = lastfm_arg_parser.parse_known_args()[0]

class LastFM:
    def __init__(self):
        self.credentials = dict({
            'username': None,
            'password': None,
            'api_key': None,
            'api_secret': None
        })

        if args.lastfm_credentials:
            with open(args.lastfm_credentials) as f:
                self.credentials.update(
                    {k: v.encode('utf-8') if isinstance(v, unicode) else v
                        for (k, v)
                        in json.loads(f.read()).iteritems()})

        if args.lastfm_username:
            self.credentials['username'] = args.lastfm_username
        if args.lastfm_password:
            self.credentials['password'] = args.lastfm_password
        if args.lastfm_api_key:
            self.credentials['api_key'] = args.lastfm_api_key
        if args.lastfm_api_secret:
            self.credentials['api_secret'] = args.lastfm_api_secret

        if not (self.credentials['username'] and
                self.credentials['password'] and
                self.credentials['api_key'] and
                self.credentials['api_secret']):
            self.on = False
            print 'Last.fm: incomplete credentials, not launched'
            return

        self.on = True
        self.lastfm_network = pylast.LastFMNetwork(
            api_key=self.credentials['api_key'],
            api_secret=self.credentials['api_secret'],
            username=self.credentials['username'],
            password_hash=pylast.md5(self.credentials['password'])
        )
        self.metadata = None
        self.timestamp = None
        self.playing = bool(lib.SpPlaybackIsPlaying())
        self.play_cumul = 0
        self.play_beg = time.time()

    # This two functions are used to count the playing time of each song
    def pause(self):
        if not self.on:
            return
        if self.playing:
            print "LastFM: add " + str(time.time() - self.play_beg) + " to total played time"
            self.play_cumul += time.time() - self.play_beg
            print "LastFM: total play time is " + str(self.play_cumul)
        self.playing = False

    def play(self):
        if not self.on:
            return
        if not self.playing:
            self.play_beg = time.time()
        self.playing = True

    def track_changed(self):
        if not self.on:
            return
        if not bool(lib.SpPlaybackIsActiveDevice()):
            return
        self.pause()
        # Scrobble last song only if the song has been played more than half
        # of its duration or during more than 4 minutes
        if self.metadata and self.play_cumul > min(self.metadata["duration"] / 2000, 240):
            self.lastfm_network.scrobble(artist=self.metadata["artist_name"],
                title=self.metadata["track_name"],
                timestamp=int(self.metadata["time_on"]),
                album=self.metadata["album_name"],
                duration=(self.metadata["duration"] / 1000))
            print "LastFM: scrobbled track " + self.metadata["track_name"] + " - " + self.metadata["artist_name"]

        # Update now playing song
        self.play_cumul = 0
        self.play()
        self.metadata = get_metadata()
        self.metadata["time_on"] = time.time()
        self.lastfm_network.update_now_playing(artist=self.metadata["artist_name"],
            title=self.metadata["track_name"], album=self.metadata["album_name"],
            duration=int(self.metadata["duration"] / 1000))

lastfm = LastFM()
