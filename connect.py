import os
import argparse
import signal
import sys
from connect_ffi import ffi, lib, C
from console_callbacks import audio_arg_parser, mixer, error_callback, connection_callbacks, debug_callbacks, playback_callbacks, playback_setup
from utils import print_zeroconf_vars


class Connect:
    def __init__(self, error_cb = error_callback):
        pass_required = False
        if __name__ == "__main__":
            #Require username and password when used without a web server
            pass_required = True
        arg_parser = argparse.ArgumentParser(description='Web interface for Spotify Connect', parents=[audio_arg_parser])
        arg_parser.add_argument('--debug', '-d', help='enable libspotify_embedded/flask debug output', action="store_true")
        arg_parser.add_argument('--key', '-k', help='path to spotify_appkey.key', default='spotify_appkey.key', type=file)
        arg_parser.add_argument('--username', '-u', help='your spotify username', required=pass_required)
        arg_parser.add_argument('--password', '-p', help='your spotify password', required=pass_required)
        arg_parser.add_argument('--name', '-n', help='name that shows up in the spotify client', default='TestConnect')
        arg_parser.add_argument('--bitrate', '-b', help='Sets bitrate of audio stream (may not actually work)', choices=[90, 160, 320], type=int, default=160)
        self.args = arg_parser.parse_args()

        app_key = ffi.new('uint8_t *')
        self.args.key.readinto(ffi.buffer(app_key))
        app_key_size = len(self.args.key.read()) + 1

        self.init_vars = {
             'version': 4,
             'buffer': C.malloc(0x100000),
             'buffer_size': 0x100000,
             'os_device_id': ffi.new('char[]', 'abcdef-{}'.format(os.getpid())),
             'remoteName': ffi.new('char[]', self.args.name),
             'brandName': ffi.new('char[]', 'DummyBrand'),
             'modelName': ffi.new('char[]', 'DummyModel'),
             'deviceType': lib.kSpDeviceTypeAudioDongle,
             'error_callback': error_cb,
             'zero1': 0,
             'app_key': app_key,
             'app_key_size': app_key_size
        }

        init = ffi.new('struct init_data *' , self.init_vars)

        print "SpInit: {}".format(lib.SpInit(init))

        lib.SpRegisterConnectionCallbacks(connection_callbacks, ffi.NULL)
        if self.args.debug:
            lib.SpRegisterDebugCallbacks(debug_callbacks, ffi.NULL)
        lib.SpRegisterPlaybackCallbacks(playback_callbacks, ffi.NULL)

        mixer_volume = int(mixer.getvolume()[0] * 655.35)
        lib.SpPlaybackUpdateVolume(mixer_volume)

        bitrates = {
            90: lib.kSpBitrate90,
            160: lib.kSpBitrate160,
            320: lib.kSpBitrate320
        }

        lib.SpPlaybackSetBitrate(bitrates[self.args.bitrate])

        playback_setup()

        print_zeroconf_vars()

        if self.args.username and self.args.password:
            lib.SpConnectionLoginPassword(self.args.username, self.args.password)

def signal_handler(signal, frame):
        lib.SpConnectionLogout()
        lib.SpFree()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

#Only run if script is run directly and not by an import
if __name__ == "__main__":
    @ffi.callback('void(sp_err_t err)')
    def console_error_callback(msg):
        if int(msg) == lib.kSpErrorLoginBadCredentials:
            print 'Invalid username or password'
            #sys.exit() doesn't work inside of a ffi callback
            C.exit(1)
        else:
            error_callback(msg)
    connect = Connect(console_error_callback)

    while 1:
        lib.SpPumpEvents()
