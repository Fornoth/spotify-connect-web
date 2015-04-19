import argparse
import alsaaudio as alsa
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

#Error callbacks
@ffi.callback('void(sp_err_t err)')
def error_callback(err):
    print "error_callback: {}".format(err)

#Connection callbacks
@ffi.callback('void(sp_connection_notify_t type, void *userdata)')
def connection_notify(type, userdata):
    if type == lib.kSpConnectionNotifyLoggedIn:
        print "kSpConnectionNotifyLoggedIn"
    elif type == lib.kSpConnectionNotifyLoggedOut:
        print "kSpConnectionNotifyLoggedOut"
    else:
        print "UNKNOWN ConnectionNotify {}".format(type)

@ffi.callback('void(const char *msg, void *userdata)')
def connection_message(msg, userdata):
    print ffi.string(msg)

#Debug callbacks
@ffi.callback('void(const char *msg, void *userdata)')
def debug_message(msg, userdata):
    print ffi.string(msg)

#Playback callbacks
@ffi.callback('void(sp_playback_notify_t type, void *userdata)')
def playback_notify(type, userdata):
    if type == lib.kSpPlaybackNotifyPlay:
        print "kSpPlaybackNotifyPlay"
    elif type == lib.kSpPlaybackNotifyPause:
        print "kSpPlaybackNotifyPause"
    elif type == lib.kSpPlaybackNotifyTrackChanged:
        print "kSpPlaybackNotifyTrackChanged"
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

@ffi.callback('int(const void *data, uint32_t num_frames, sp_audioformat *format, uint32_t *pending, void *userdata)')
def playback_data(data, num_frames, format, pending, userdata):
    global pending_data

    # Make sure we don't pass incomplete frames to alsa
    num_frames -= num_frames % CHANNELS

    buf = pending_data + ffi.buffer(data, num_frames * SAMPLESIZE)[:]

    try:
        total = 0
        while len(buf) >= PERIODSIZE * CHANNELS * SAMPLESIZE:
            audio_queue.put(buf[:PERIODSIZE * CHANNELS * SAMPLESIZE], block=False)
            buf = buf[PERIODSIZE * CHANNELS * SAMPLESIZE:]
            total += PERIODSIZE * CHANNELS

        pending_data = buf
        return num_frames
    except Queue.Full:
        return total
    finally:
        pending[0] = audio_queue.qsize() * PERIODSIZE * CHANNELS

@ffi.callback('void(uint32_t millis, void *userdata)')
def playback_seek(millis, userdata):
    print "playback_seek: {}".format(millis)

@ffi.callback('void(uint16_t volume, void *userdata)')
def playback_volume(volume, userdata):
    print "playback_volume: {}".format(volume)
    mixer.setvolume(int(volume / 655.35))


connection_callbacks = ffi.new('struct connection_callbacks *', [
    connection_notify,
    connection_message
])

debug_callbacks = ffi.new('struct debug_callbacks *', [
    debug_message
])

playback_callbacks = ffi.new('struct playback_callbacks *', [
    playback_notify,
    playback_data,
    playback_seek,
    playback_volume
])
