# 1 "spotify.h"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "spotify.h"



# 1 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stddef.h" 1 3 4
# 147 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stddef.h" 3 4
typedef int ptrdiff_t;
# 212 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stddef.h" 3 4
typedef unsigned int size_t;
# 324 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stddef.h" 3 4
typedef unsigned int wchar_t;
# 5 "spotify.h" 2
# 1 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stdint.h" 1 3 4
# 9 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stdint.h" 3 4
# 1 "/usr/include/stdint.h" 1 3 4
# 25 "/usr/include/stdint.h" 3 4
# 1 "/usr/include/features.h" 1 3 4
# 374 "/usr/include/features.h" 3 4
# 1 "/usr/include/arm-linux-gnueabi/sys/cdefs.h" 1 3 4
# 385 "/usr/include/arm-linux-gnueabi/sys/cdefs.h" 3 4
# 1 "/usr/include/arm-linux-gnueabi/bits/wordsize.h" 1 3 4
# 386 "/usr/include/arm-linux-gnueabi/sys/cdefs.h" 2 3 4
# 375 "/usr/include/features.h" 2 3 4
# 398 "/usr/include/features.h" 3 4
# 1 "/usr/include/arm-linux-gnueabi/gnu/stubs.h" 1 3 4






# 1 "/usr/include/arm-linux-gnueabi/gnu/stubs-soft.h" 1 3 4
# 8 "/usr/include/arm-linux-gnueabi/gnu/stubs.h" 2 3 4
# 399 "/usr/include/features.h" 2 3 4
# 26 "/usr/include/stdint.h" 2 3 4
# 1 "/usr/include/arm-linux-gnueabi/bits/wchar.h" 1 3 4
# 27 "/usr/include/stdint.h" 2 3 4
# 1 "/usr/include/arm-linux-gnueabi/bits/wordsize.h" 1 3 4
# 28 "/usr/include/stdint.h" 2 3 4
# 36 "/usr/include/stdint.h" 3 4
typedef signed char int8_t;
typedef short int int16_t;
typedef int int32_t;




typedef long long int int64_t;




typedef unsigned char uint8_t;
typedef unsigned short int uint16_t;

typedef unsigned int uint32_t;






typedef unsigned long long int uint64_t;






typedef signed char int_least8_t;
typedef short int int_least16_t;
typedef int int_least32_t;




typedef long long int int_least64_t;



typedef unsigned char uint_least8_t;
typedef unsigned short int uint_least16_t;
typedef unsigned int uint_least32_t;




typedef unsigned long long int uint_least64_t;






typedef signed char int_fast8_t;





typedef int int_fast16_t;
typedef int int_fast32_t;

typedef long long int int_fast64_t;



typedef unsigned char uint_fast8_t;





typedef unsigned int uint_fast16_t;
typedef unsigned int uint_fast32_t;

typedef unsigned long long int uint_fast64_t;
# 125 "/usr/include/stdint.h" 3 4
typedef int intptr_t;


typedef unsigned int uintptr_t;
# 137 "/usr/include/stdint.h" 3 4

typedef long long int intmax_t;

typedef unsigned long long int uintmax_t;
# 10 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stdint.h" 2 3 4
# 6 "spotify.h" 2
# 1 "/usr/lib/gcc/arm-linux-gnueabi/4.9/include/stdbool.h" 1 3 4
# 7 "spotify.h" 2

typedef enum {
    kSpErrorOk = 0,
    kSpErrorFailed = 1,
    kSpErrorInitFailed = 2,
    kSpErrorWrongAPIVersion = 3,
    kSpErrorNullArgument = 4,
    kSpErrorInvalidArgument = 5,
    kSpErrorUninitialized = 6,
    kSpErrorAlreadyInitialized = 7,
    kSpErrorLoginBadCredentials = 8,
    kSpErrorNeedsPremium = 9,
    kSpErrorTravelRestriction = 10,
    kSpErrorApplicationBanned = 11,
    kSpErrorGeneralLoginError = 12,
    kSpErrorUnsupported = 13,
    kSpErrorNotActiveDevice = 14,
    kSpErrorPlaybackErrorStart = 1000,
    kSpErrorGeneralPlaybackError = 1001,
    kSpErrorPlaybackRateLimited = 1002,
    kSpErrorUnknown = 1003,
} SpError;

typedef enum {
    kSpConnectionNotifyLoggedIn = 0,
    kSpConnectionNotifyLoggedOut = 1,
    kSpConnectionNotifyTemporaryError = 2,
} SpConnectionNotify;

typedef enum {
    kSpPlaybackNotifyPlay = 0,
    kSpPlaybackNotifyPause = 1,
    kSpPlaybackNotifyTrackChanged = 2,
    kSpPlaybackNotifyNext = 3,
    kSpPlaybackNotifyPrev = 4,
    kSpPlaybackNotifyShuffleEnabled = 5,
    kSpPlaybackNotifyShuffleDisabled = 6,
    kSpPlaybackNotifyRepeatEnabled = 7,
    kSpPlaybackNotifyRepeatDisabled = 8,
    kSpPlaybackNotifyBecameActive = 9,
    kSpPlaybackNotifyBecameInactive = 10,
    kSpPlaybackNotifyPlayTokenLost = 11,
    kSpPlaybackEventAudioFlush = 12,
} SpPlaybackNotify;

typedef enum {
    kSpDeviceTypeUnknown = 0,
    kSpDeviceTypeComputer = 1,
    kSpDeviceTypeTablet = 2,
    kSpDeviceTypeSmartphone = 3,
    kSpDeviceTypeSpeaker = 4,
    kSpDeviceTypeTV = 5,
    kSpDeviceTypeAVR = 6,
    kSpDeviceTypeSTB = 7,
    kSpDeviceTypeAudioDongle = 8,
} SpDeviceType;

typedef enum {
    kSpSampleTypeS16NativeEndian,
} SpSampleType;

typedef enum {
    kSpBitrate90k = 0,
    kSpBitrate160k = 1,
    kSpBitrate320k = 2,
} SpBitrate;

typedef enum {
    kSpImageSizeSmall = 0,
    kSpImageSizeNormal = 1,
    kSpImageSizeLarge = 2,
} SpImageSize;

typedef struct {
    uint16_t channels;
    uint16_t sample_type;
    uint32_t sample_rate;
} SpSampleFormat;

typedef struct {
    uint32_t version;
    uint8_t *buffer;
    uint32_t buffer_size;
    uint8_t *app_key;
    uint32_t app_key_size;
    const char *deviceId;
    const char *remoteName;
    const char *brandName;
    const char *modelName;
    char *client_id;
    char *client_secret;
    uint32_t deviceType;
    void (*error_callback)(SpError error, void *userdata);
    void *userdata;
} SpConfig;

typedef struct {
    char publicKey[0x96];
    char deviceId[0x41];
    char activeUser[0x41];
    char remoteName[0x41];
    char accountReq[0x10];
    char deviceType[0x10];
    char libraryVersion[0x1f];
} SpZeroConfVars;

typedef struct {
    char data0[0x100];
    char context_uri[0x80];
    char track_name[0x100];
    char track_uri[0x80];
    char artist_name[0x100];
    char artist_uri[0x80];
    char album_name[0x100];
    char album_uri[0x80];
    char cover_uri[0x80];
    uint32_t duration;
} SpMetadata;

typedef struct {
    uint8_t data[0x84];
} SpPreset;

typedef struct {
    void (*notify)(SpConnectionNotify notification, void *userdata);
    void (*new_credentials)(const char *blob, void *userdata);
} SpConnectionCallbacks;

typedef struct {
    void (*notify)(SpPlaybackNotify notification, void *userdata);
    uint32_t (*audio_data)(const void *samples, uint32_t num_samples,
            SpSampleFormat *format, uint32_t *pending,
            void *userdata);
    void (*seek)(uint32_t millis, void *userdata);
    void (*apply_volume)(uint16_t volume, void *userdata);
} SpPlaybackCallbacks;

typedef struct {
    void (*message)(const char *msg, void *userdata);
} SpDebugCallbacks;


SpError SpInit(const SpConfig *config);
void SpFree(void);

SpError SpPumpEvents(void);

SpError SpGetMetadataValidRange(int *start, int *end);
SpError SpGetMetadata(SpMetadata *, int offset);
SpError SpGetMetadataImageURL(const char *uri, SpImageSize imageSize,
        char *url, size_t size);

SpError SpGetPreset(SpPreset *preset, size_t *size);
SpError SpPlayPreset(const SpPreset *preset, size_t size);

SpError SpSetDisplayName(const char *name);
const char *SpGetLibraryVersion(void);

SpError SpZeroConfGetVars(SpZeroConfVars *vars);

SpError SpPlaybackPlay(void);
SpError SpPlaybackPause(void);
SpError SpPlaybackSkipToNext(void);
SpError SpPlaybackSkipToPrev(void);
SpError SpPlaybackSeek(uint32_t millis);
SpError SpPlaybackUpdateVolume(uint16_t volume);
SpError SpPlaybackEnableShuffle(_Bool enable);
SpError SpPlaybackEnableRepeat(_Bool enable);
SpError SpPlaybackSetBitrate(SpBitrate bitrate);

uint16_t SpPlaybackGetVolume(void);
_Bool SpPlaybackIsPlaying(void);
_Bool SpPlaybackIsShuffled(void);
_Bool SpPlaybackIsRepeated(void);
_Bool SpPlaybackIsActiveDevice(void);

SpError SpConnectionLoginBlob(const char *username, const char *blob);
SpError SpConnectionLoginPassword(const char *login, const char *password);
SpError SpConnectionLoginZeroConf(const char *username, const char *blob,
        const char *clientKey);
SpError SpConnectionLoginOauthToken(const char *token);

_Bool SpConnectionIsLoggedIn(void);
SpError SpConnectionLogout(void);

SpError SpRegisterConnectionCallbacks(
        const SpConnectionCallbacks *callbacks, void *userdata);
SpError SpRegisterPlaybackCallbacks(
        const SpPlaybackCallbacks *callbacks, void *userdata);
SpError SpRegisterDebugCallbacks(
        const SpDebugCallbacks *callbacks, void *userdata);
