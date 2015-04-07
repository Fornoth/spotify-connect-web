from connect_ffi import ffi, lib
import alsaaudio as alsa

mixer_name = alsa.mixers()[0]
mixer = alsa.Mixer(mixer_name)

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

#Implemented in C
# @ffi.callback('void(const void *frames, uint32_t num_frames,\
        # sp_audioformat *format, void *userdata)')
# def playback_data(frames, num_frames, format, userdata):
    # #audio_frame(frames, num_frames, format)
    # pass

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

# playback_callbacks = ffi.new('struct playback_callbacks *', [
    # playback_notify,
    # ffi.NULL,
    # playback_seek,
    # playback_volume
# ])
lib.playback_notify = playback_notify
lib.playback_seek = playback_seek
lib.playback_volume = playback_volume
