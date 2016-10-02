#!/usr/bin/env python
#First run the command avahi-publish-service TestConnect _spotify-connect._tcp 4000 VERSION=1.0 CPath=/login/_zeroconf
#TODO: Add error checking
#TODO: Show when request fails on webpage
import os
import sys
import argparse
import re
from flask import Flask, request, abort, jsonify, render_template, redirect, flash, url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from gevent.wsgi import WSGIServer
from gevent import spawn_later, sleep
from connect_ffi import ffi, lib
from connect import Connect
from utils import get_zeroconf_vars, get_metadata, get_image_url

web_arg_parser = argparse.ArgumentParser(add_help=False)

#Not a tuple, evaluates the same as "" + ""
cors_help = (
    "enable CORS support for this host (for the web api). "
    "Must be in the format <protocol>://<hostname>:<port>. "
    "Port can be excluded if its 80 (http) or 443 (https). "
    "Can be specified multiple times"
)


def validate_cors_host(host):
    host_regex = re.compile(r'^(http|https)://[a-zA-Z0-9][a-zA-Z0-9-.]+(:[0-9]{1,5})?$')
    result = re.match(host_regex, host)
    if result is None:
        raise argparse.ArgumentTypeError('%s is not in the format <protocol>://<hostname>:<port>. Protocol must be http or https' % host)
    return host

web_arg_parser.add_argument('--cors', help=cors_help, action='append', type=validate_cors_host)
args = web_arg_parser.parse_known_args()[0]

app = Flask(__name__, root_path=sys.path[0])
Bootstrap(app)
#Add CORS headers to API requests for specified hosts
CORS(app, resources={r"/api/*": {"origins": args.cors}})

#Serve bootstrap files locally instead of from a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.secret_key = os.urandom(24)

#Used by the error callback to determine login status
invalid_login = False

@ffi.callback('void(SpError error, void *userdata)')
def web_error_callback(error, userdata):
    global invalid_login
    if error == lib.kSpErrorLoginBadCredentials:
        invalid_login = True

connect_app = Connect(web_error_callback, web_arg_parser)

if os.environ.get('DEBUG') or connect_app.args.debug:
    app.debug = True

##Routes

#Home page
@app.route('/')
def index():
    return render_template('index.html')

##API routes

#Playback routes
@app.route('/api/playback/play')
def playback_play():
    lib.SpPlaybackPlay()
    return '', 204

@app.route('/api/playback/pause')
def playback_pause():
    lib.SpPlaybackPause()
    return '', 204

@app.route('/api/playback/prev')
def playback_prev():
    lib.SpPlaybackSkipToPrev()
    return '', 204

@app.route('/api/playback/next')
def playback_next():
    lib.SpPlaybackSkipToNext()
    return '', 204


#TODO: Add ability to disable shuffle/repeat
@app.route('/api/playback/shuffle')
def playback_shuffle():
    lib.SpPlaybackEnableShuffle(True)
    return '', 204

@app.route('/api/playback/shuffle/<status>', endpoint='shuffle_toggle')
def playback_shuffle(status):
    if status == 'enable':
        lib.SpPlaybackEnableShuffle(True)
    elif status == 'disable':
        lib.SpPlaybackEnableShuffle(False)
    return '', 204


@app.route('/api/playback/repeat')
def playback_repeat():
    lib.SpPlaybackEnableRepeat(True)
    return '', 204

@app.route('/api/playback/repeat/<status>', endpoint='repeat_toggle')
def playback_repeat(status):
    if status == 'enable':
        lib.SpPlaybackEnableRepeat(True)
    elif status == 'disable':
        lib.SpPlaybackEnableRepeat(False)
    return '', 204


@app.route('/api/playback/volume', methods=['GET'])
def playback_volume():
    return jsonify({
        'volume': lib.SpPlaybackGetVolume()
    })

@app.route('/api/playback/volume', methods=['POST'], endpoint='playback_volume-post')
def playback_volume():
    volume = request.form.get('value')
    if volume is None:
        return jsonify({
            'error': 'value must be set'
        }), 400
    lib.SpPlaybackUpdateVolume(int(volume))
    return '', 204


#Info routes
@app.route('/api/info/metadata')
def info_metadata():
    res = get_metadata()
    res['volume'] = lib.SpPlaybackGetVolume()
    return jsonify(res)

@app.route('/api/info/status')
def info_status():
    return jsonify({
        'active': bool(lib.SpPlaybackIsActiveDevice()),
        'playing': bool(lib.SpPlaybackIsPlaying()),
        'shuffle': bool(lib.SpPlaybackIsShuffled()),
        'repeat': bool(lib.SpPlaybackIsRepeated()),
        'logged_in': bool(lib.SpConnectionIsLoggedIn())
    })

@app.route('/api/info/image_url/<image_uri>')
def info_image_url(image_uri):
    return redirect(get_image_url(str(image_uri)))

@app.route('/api/info/display_name', methods=['GET'])
def info_display_name():
    return jsonify({
        'remoteName': get_zeroconf_vars()['remoteName']
    })

@app.route('/api/info/display_name', methods=['POST'], endpoint='display_name-post')
def info_display_name():
    display_name = str(request.form.get('displayName'))
    if not display_name:
        return jsonify({
            'error': 'displayName must be set'
        }), 400
    lib.SpSetDisplayName(display_name)
    return '', 204

#Login routes
@app.route('/login/logout')
def login_logout():
    lib.SpConnectionLogout()
    return redirect(url_for('index'))

@app.route('/login/password', methods=['POST'])
def login_password():
    global invalid_login
    invalid_login = False
    username = str(request.form.get('username'))
    password = str(request.form.get('password'))

    if not username or not password:
        flash('Username or password not specified', 'danger')
    else:
        flash('Waiting for spotify', 'info')
        connect_app.login(username, password=password)

    return redirect(url_for('index'))

@app.route('/login/check_login')
def check_login():
    res = {
        'finished': False,
        'success': False
    }

    if invalid_login:
        res['finished'] = True
    elif bool(lib.SpConnectionIsLoggedIn()):
        res['finished'] = True
        res['success'] = True

    return jsonify(res)

@app.route('/login/_zeroconf', methods=['GET', 'POST'])
def login_zeroconf():
    action = request.args.get('action') or request.form.get('action')
    if not action:
        return jsonify({
            'status': 301,
            'spotifyError': 0,
            'statusString': 'ERROR-MISSING-ACTION'})
    if action == 'getInfo' and request.method == 'GET':
        return get_info()
    elif action == 'addUser' and request.method == 'POST':
        return add_user()
    else:
        return jsonify({
            'status': 301,
            'spotifyError': 0,
            'statusString': 'ERROR-INVALID-ACTION'})

def get_info():
    zeroconf_vars = get_zeroconf_vars()

    return jsonify({
        'status': 101,
        'spotifyError': 0,
        'activeUser': zeroconf_vars['activeUser'],
        'brandDisplayName': ffi.string(connect_app.config['brandName']),
        'accountReq': zeroconf_vars['accountReq'],
        #Doesn't have any specific format (I think)
        'deviceID': zeroconf_vars['deviceId'],
        #Generated from SpZeroConfGetVars()
        #Used to encrypt the blob used for login
        'publicKey': zeroconf_vars['publicKey'],
        'version': '2.0.1',
        #Valid types are UNKNOWN, COMPUTER, TABLET, SMARTPHONE, SPEAKER, TV, AVR, STB and AUDIODONGLE
        'deviceType': zeroconf_vars['deviceType'],
        'modelDisplayName': ffi.string(connect_app.config['modelName']),
        #Status codes are ERROR-OK (not actually an error), ERROR-MISSING-ACTION, ERROR-INVALID-ACTION, ERROR-SPOTIFY-ERROR, ERROR-INVALID-ARGUMENTS, ERROR-UNKNOWN, and ERROR_LOG_FILE
        'statusString': 'ERROR-OK',
        #Name that shows up in the Spotify client
        'remoteName': zeroconf_vars['remoteName']
    })

def add_user():
    args = request.form
    #TODO: Add parameter verification
    username = str(args.get('userName'))
    blob = str(args.get('blob'))
    clientKey = str(args.get('clientKey'))

    connect_app.login(username, zeroconf=(blob,clientKey))

    return jsonify({
        'status': 101,
        'spotifyError': 0,
        'statusString': 'ERROR-OK'
        })

#Loop to pump events
def pump_events():
    lib.SpPumpEvents()
    spawn_later(0.1, pump_events)

pump_events()

#Only run if script is run directly and not by an import
if __name__ == "__main__":
#Can be run on any port as long as it matches the one used in avahi-publish-service
    http_server = WSGIServer(('', 4000), app)
    http_server.serve_forever()

#TODO: Add signal catcher
lib.SpFree()
