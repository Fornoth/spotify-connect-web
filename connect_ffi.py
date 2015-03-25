from cffi import FFI
ffi = FFI()

#Header generated with cpp spotify.h > spotify.processed.h && sed -i 's/__extension__//g' spotify.processed.h
with open("spotify.processed.h") as file:
    header = file.read()

ffi.cdef(header)
ffi.cdef("""
void *malloc(size_t size);
void exit(int status);
sp_err_t setup_audio_callbacks();
void (*playback_seek)(uint32_t millis, void *userdata);
void (*playback_volume)(uint16_t volume, void *userdata);
void (*playback_notify)(sp_playback_notify_t type, void *userdata);
""")

C = ffi.dlopen(None)
lib = ffi.verify("""
    #include "spotify.h"

    //Audio code from https://github.com/plietar/spotify-connect/blob/master/example/audio.c
    static int audio_fd = -1;
    static int audio_pid = -1;

    int audio_init(void) {
        int fds[2];
        pipe(fds);
        audio_pid = fork();
        if (audio_pid == 0) {
            dup2(fds[0], 0);
            close (fds[0]);
            close (fds[1]);
            execlp("aplay", "aplay",
                    "-t", "raw",
                    "-r", "44100",
                    "-f", "S16_LE",
                    "-c", "2",
                    "-", NULL);
            perror("exec");
            exit(1);
        } else {
            close (fds[0]);
            audio_fd = fds[1];
        }

        return 0;
    }

    void audio_frame(const void *frames, uint32_t num_frames, sp_audioformat *format, void *userdata) {
        if (format->sample_type != SP_SAMPLETYPE_INT16_NATIVE_ENDIAN
                || format->sample_rate != 44100
                || format->channels != 2) {
            printf("Wrong audio format: %d %d %d\\n", format->sample_type,
                format->sample_rate, format->channels);
        } else {
            write(audio_fd, frames, num_frames * 2);
        }
    }

    //Implemented in python
    void (*playback_seek)(uint32_t millis, void *userdata);
    void (*playback_volume)(uint16_t volume, void *userdata);
    void (*playback_notify)(sp_playback_notify_t type, void *userdata);

    sp_err_t setup_audio_callbacks() {
        struct playback_callbacks playback_callbacks = {
            playback_notify,
            audio_frame,
            playback_seek,
            playback_volume,
        };
        audio_init();
        return SpRegisterPlaybackCallbacks(&playback_callbacks, NULL);
    }
""", include_dirs=['./'],
    library_dirs=['./'],
    libraries=[str('spotify_embedded_shared')])