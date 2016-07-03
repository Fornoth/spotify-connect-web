#!/usr/bin/env python
import os
import argparse
import signal
import sys
import json
import uuid
from connect_ffi import ffi, lib, C
from console_callbacks import audio_arg_parser, mixer, error_callback, connection_callbacks, debug_callbacks, playback_callbacks, playback_setup
from utils import print_zeroconf_vars

class Connect:
    def __init__(self, error_cb = error_callback, web_arg_parser = None):
        arg_parser = argparse.ArgumentParser(description='Web interface for Spotify Connect', parents=[audio_arg_parser])
        arg_parser.add_argument('--debug', '-d', help='enable libspotify_embedded/flask debug output', action="store_true")
        arg_parser.add_argument('--key', '-k', help='path to spotify_appkey.key (can be obtained from https://developer.spotify.com/my-account/keys )', default='spotify_appkey.key')
        arg_parser.add_argument('--username', '-u', help='your spotify username')
        arg_parser.add_argument('--password', '-p', help='your spotify password')
        arg_parser.add_argument('--name', '-n', help='name that shows up in the spotify client', default='TestConnect')
        arg_parser.add_argument('--bitrate', '-b', help='Sets bitrate of audio stream (may not actually work)', choices=[90, 160, 320], type=int, default=160)
        arg_parser.add_argument('--credentials', '-c', help='File to load and save credentials from/to', default='credentials.json')
        self.args = arg_parser.parse_args()

        print "Using libspotify_embedded version: {}".format(ffi.string(lib.SpGetLibraryVersion()))

        try:
            with open(self.args.key) as f:
                app_key = ffi.new('uint8_t *')
                f.readinto(ffi.buffer(app_key))
                app_key_size = len(f.read()) + 1
        except IOError as e:
            print "Error opening app key: {}.".format(e)
            print "If you don't have one, it can be obtained from https://developer.spotify.com/my-account/keys"
            sys.exit(1)


        self.credentials = dict({
            'device-id': str(uuid.uuid4()),
            'username': None,
            'blob': None
        })

        try:
            with open(self.args.credentials) as f:
                self.credentials.update(
                        { k: v.encode('utf-8') if isinstance(v, unicode) else v
                            for (k,v)
                            in json.loads(f.read()).iteritems() })
        except IOError:
            pass

        if self.args.username:
            self.credentials['username'] = self.args.username

        userdata = ffi.new_handle(self)

        if self.args.debug:
            lib.SpRegisterDebugCallbacks(debug_callbacks, userdata)

        self.config = {
             'version': 4,
             'buffer': C.malloc(0x100000),
             'buffer_size': 0x100000,
             'app_key': app_key,
             'app_key_size': app_key_size,
             'deviceId': ffi.new('char[]', self.credentials['device-id']),
             'remoteName': ffi.new('char[]', self.args.name),
             'brandName': ffi.new('char[]', 'DummyBrand'),
             'modelName': ffi.new('char[]', 'DummyModel'),
             'client_id': ffi.new('char[]', '0'),
             'deviceType': lib.kSpDeviceTypeAudioDongle,
             'error_callback': error_cb,
             'userdata': userdata,
        }

        init = ffi.new('SpConfig *' , self.config)
        init_status = lib.SpInit(init)
        print "SpInit: {}".format(init_status)
        if init_status != 0:
            print "SpInit failed, exiting"
            sys.exit(1)

        lib.SpRegisterConnectionCallbacks(connection_callbacks, userdata)
        lib.SpRegisterPlaybackCallbacks(playback_callbacks, userdata)

        mixer_volume = int(mixer.getvolume()[0] * 655.35)
        lib.SpPlaybackUpdateVolume(mixer_volume)

        bitrates = {
            90: lib.kSpBitrate90k,
            160: lib.kSpBitrate160k,
            320: lib.kSpBitrate320k
        }

        lib.SpPlaybackSetBitrate(bitrates[self.args.bitrate])

        playback_setup()

        print_zeroconf_vars()

        if self.credentials['username'] and self.args.password:
            self.login(password=self.args.password)
        elif self.credentials['username'] and self.credentials['blob']:
            self.login(blob=self.credentials['blob'])
        else:
            if __name__ == '__main__':
                raise ValueError("No username given, and none stored")

    def login(self, username=None, password=None, blob=None, zeroconf=None):
        if username is not None:
            self.credentials['username'] = username
        elif self.credentials['username']:
            username = self.credentials['username']
        else:
            raise ValueError("No username given, and none stored")

        if password is not None:
            lib.SpConnectionLoginPassword(username, password)
        elif blob is not None:
            lib.SpConnectionLoginBlob(username, blob)
        elif zeroconf is not None:
            lib.SpConnectionLoginZeroConf(username, *zeroconf)
        else:
            raise ValueError("Must specify a login method (password, blob or zeroconf)")

def signal_handler(signal, frame):
        lib.SpConnectionLogout()
        lib.SpFree()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

#Only run if script is run directly and not by an import
if __name__ == "__main__":
    @ffi.callback('void(SpError err, void *userdata)')
    def console_error_callback(error, userdata):
        if error == lib.kSpErrorLoginBadCredentials:
            print 'Invalid username or password'
            #sys.exit() doesn't work inside of a ffi callback
            C.exit(1)
        else:
            error_callback(msg)
    connect = Connect(console_error_callback)

    while 1:
        lib.SpPumpEvents()
