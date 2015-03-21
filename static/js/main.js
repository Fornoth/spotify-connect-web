var loggedIn = false;
var metadataSetup = false;
var checkLoginInterval;

//Call api when a playback control button is clicked
$('#controls button').click(function(e) {
    var type = e.currentTarget.getAttribute('data-type');
    var action = e.currentTarget.getAttribute('data-action');
    if (action === 'play') {
        $('[data-action=play]').hide();
        $('[data-action=pause]').show();
    } else if (action === 'pause') {
        $('[data-action=pause]').hide();
        $('[data-action=play]').show();
    } else if (action === 'shuffle') {
        $('[data-action=shuffle]').toggleClass('active');
    } else if (action === 'repeat') {
        $('[data-action=repeat]').toggleClass('active');
    }
    $.ajax('/api/' + type + '/' + action).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
});

function updateMetadata() {
    $.ajax('/api/info/metadata').done(function(metadata) {
        var track = $('#trackInfo');
        var artist = $('#artistInfo');
        var album = $('#albumInfo');
        var albumCover = $('#albumCover');

        track.attr('data-id', metadata.track_uri);
        track.text(metadata.track_name);

        artist.attr('data-id', metadata.artist_uri);
        artist.text(metadata.artist_name);

        album.attr('data-id', metadata.album_uri);
        album.text(metadata.album_name);

        albumCover.attr('src', '/api/info/image_url/' + metadata.cover_uri)
    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
}

function getStatus() {
    $.ajax('/api/info/status').done(function(data) {
        //Display buttons depending on play state
        $('[data-action=play]').toggle(!data.playing);
        $('[data-action=pause]').toggle(data.playing);

        $('[data-action=shuffle]').toggleClass('active', data.shuffle);
        $('[data-action=repeat]').toggleClass('active', data.repeat);

        $('#player').toggle(data.logged_in);

        $('#activeDevice').text(data.active);
        $('#controls button').toggleClass('disabled', !data.active);

        $('#loginLink').toggle(!data.logged_in);
        $('#logoutLink').toggle(data.logged_in);

        if (!loggedIn && data.logged_in && !metadataSetup) {
            loggedIn = true;
            metadataSetup = true;
            updateMetadata();
            setInterval(updateMetadata, 5000);
        }

    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
}

function checkLogin() {
    $.ajax('/login/check_login').done(function(data) {
        if (data.finished) {
            var message = $('.container .row .col-md-12 .alert-info')
            message.removeClass('alert-info');
            if (data.success) {
                message.text('Login Successful');
                message.addClass('alert-success');
                getStatus();
            } else {
                message.text('Invalid username or password');
                message.addClass('alert-danger');
            }
            clearInterval(checkLoginInterval);
        }
    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    })
}

getStatus();

//Check for login status
if ($('.container .row .col-md-12 .alert-info').text() === 'Waiting for spotify') {
    checkLoginInterval = setInterval(checkLogin, 1000);
}

//Update every 5 seconds
setInterval(getStatus, 5000);