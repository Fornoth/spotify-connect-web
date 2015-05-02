import argparse
import alsaaudio as alsa
import json
import Queue
from threading import Thread
from connect_ffi import ffi, lib

RATE = 44100
CHANNELS = 2
PERIODSIZE = 64
SAMPLESIZE = 2 # 16 bit integer
MAXPERIODS = int(0.5 * RATE / PERIODSIZE) # 0.5s Buffer

audio_arg_parser = argparse.ArgumentParser(add_help=False)
audio_arg_parser.add_argument('--device', '-D', help='alsa output device', default='default')
audio_arg_parser.add_argument('--mixer', '-m', help='alsa mixer name for volume control', default=alsa.mixers()[0])
args = audio_arg_parser.parse_known_args()[0]

device = alsa.PCM(
        alsa.PCM_PLAYBACK,
        card = args.device)

device.setchannels(CHANNELS)
device.setrate(RATE)
device.setperiodsize(PERIODSIZE)
device.setformat(alsa.PCM_FORMAT_S16_LE)

mixer = alsa.Mixer(args.mixer)

def userdata_wrapper(f):
    def inner(*args):
        assert len(args) > 0
        self = ffi.from_handle(args[-1])
        return f(self, *args[:-1])
    return inner

#Error callbacks
@ffi.callback('void(SpError error, void *userdata)')
def error_callback(error, userdata):
    print "error_callback: {}".format(error)

#Connection callbacks
@ffi.callback('void(SpConnectionNotify type, void *userdata)')
@userdata_wrapper
def connection_notify(self, type):
    if type == lib.kSpConnectionNotifyLoggedIn:
        print "kSpConnectionNotifyLoggedIn"
    elif type == lib.kSpConnectionNotifyLoggedOut:
        print "kSpConnectionNotifyLoggedOut"
    elif type == lib.kSpConnectionNotifyTemporaryError:
        print "kSpConnectionNotifyTemporaryError"
    else:
        print "UNKNOWN ConnectionNotify {}".format(type)

@ffi.callback('void(const char *blob, void *userdata)')
@userdata_wrapper
def connection_new_credentials(self, blob):
    print ffi.string(blob)
    self.credentials['blob'] = ffi.string(blob)

    with open(self.args.credentials, 'w') as f:
        f.write(json.dumps(self.credentials))

#Debug callbacks
@ffi.callback('void(const char *msg, void *userdata)')
@userdata_wrapper
def debug_message(self, msg):
    print ffi.string(msg)

#Playback callbacks
@ffi.callback('void(SpPlaybackNotify type, void *userdata)')
@userdata_wrapper
def playback_notify(self, type):
    if type == lib.kSpPlaybackNotifyPlay:
        print "kSpPlaybackNotifyPlay"
    elif type == lib.kSpPlaybackNotifyPause:
        print "kSpPlaybackNotifyPause"
    elif type == lib.kSpPlaybackNotifyTrackChanged:
        print "kSpPlaybackNotifyTrackChanged"
    elif type == lib.kSpPlaybackNotifyNext:
        print "kSpPlaybackNotifyNext"
    elif type == lib.kSpPlaybackNotifyPrev:
        print "kSpPlaybackNotifyPrev"
    elif type == lib.kSpPlaybackNotifyShuffleEnabled:
        print "kSpPlaybackNotifyShuffleEnabled"
    elif type == lib.kSpPlaybackNotifyShuffleDisabled:
        print "kSpPlaybackNotifyShuffleDisabled"
    elif type == lib.kSpPlaybackNotifyRepeatEnabled:
        print "kSpPlaybackNotifyRepeatEnabled"
    elif type == lib.kSpPlaybackNotifyRepeatDisabled:
        print "kSpPlaybackNotifyRepeatDisabled"
    elif type == lib.kSpPlaybackNotifyBecameActive:
        print "kSpPlaybackNotifyBecameActive"
    elif type == lib.kSpPlaybackNotifyBecameInactive:
        print "kSpPlaybackNotifyBecameInactive"
    elif type == lib.kSpPlaybackNotifyPlayTokenLost:
        print "kSpPlaybackNotifyPlayTokenLost"
    elif type == lib.kSpPlaybackEventAudioFlush:
        print "kSpPlaybackEventAudioFlush"
        #audio_flush();
    else:
        print "UNKNOWN PlaybackNotify {}".format(type)

def playback_thread(q):
    while True:
        data = q.get()
        device.write(data)
        q.task_done()

audio_queue = Queue.Queue(maxsize=MAXPERIODS)
pending_data = str()

def playback_setup():
    t = Thread(args=(audio_queue,), target=playback_thread)
    t.daemon = True
    t.start()

@ffi.callback('uint32_t(const void *data, uint32_t num_samples, SpSampleFormat *format, uint32_t *pending, void *userdata)')
@userdata_wrapper
def playback_data(self, data, num_samples, format, pending):
    global pending_data

    # Make sure we don't pass incomplete frames to alsa
    num_samples -= num_samples % CHANNELS

    buf = pending_data + ffi.buffer(data, num_samples * SAMPLESIZE)[:]

    try:
        total = 0
        while len(buf) >= PERIODSIZE * CHANNELS * SAMPLESIZE:
            audio_queue.put(buf[:PERIODSIZE * CHANNELS * SAMPLESIZE], block=False)
            buf = buf[PERIODSIZE * CHANNELS * SAMPLESIZE:]
            total += PERIODSIZE * CHANNELS

        pending_data = buf
        return num_samples
    except Queue.Full:
        return total
    finally:
        pending[0] = audio_queue.qsize() * PERIODSIZE * CHANNELS

@ffi.callback('void(uint32_t millis, void *userdata)')
@userdata_wrapper
def playback_seek(self, millis):
    print "playback_seek: {}".format(millis)

@ffi.callback('void(uint16_t volume, void *userdata)')
@userdata_wrapper
def playback_volume(self, volume):
    print "playback_volume: {}".format(volume)
    mixer.setvolume(int(volume / 655.35))

connection_callbacks = ffi.new('SpConnectionCallbacks *', [
    connection_notify,
    connection_new_credentials
])

debug_callbacks = ffi.new('SpDebugCallbacks *', [
    debug_message
])

playback_callbacks = ffi.new('SpPlaybackCallbacks *', [
    playback_notify,
    playback_data,
    playback_seek,
    playback_volume
])
