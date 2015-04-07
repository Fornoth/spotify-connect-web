var loggedIn = false;
var metadataSetup = false;
var checkLoginInterval;
var metadataInterval;
var slider;

//Show a message on the page
//type is either success, info, warning, or danger
function flash(message, type) {
    var messageBlock = $('<div class="alert" role="alert"></div>');
    messageBlock.addClass('alert-' + type);
    messageBlock.text(message);
    $('#messageDiv').append(messageBlock);
    messageBlock.fadeOut(5000, function() {
        $(this).remove();
    });
}

function playbackControl(e) {
    var type = e.currentTarget.getAttribute('data-type');
    var action = e.currentTarget.getAttribute('data-action');
    console.log(e);
    var value;
    var ajaxSettings = {
        url: '/api/' + type + '/' + action,
        method: 'GET'
    }
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
    } else if (action === 'volume') {
        ajaxSettings.method = 'POST';
        ajaxSettings.data = {value: Math.round(e.currentTarget.value * 655.35)}
    }
    $.ajax(ajaxSettings).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
}

//Call api when a playback control button is clicked
$('#controls button').click(playbackControl);

$('#displayNameForm').submit(function() {
    $('#displayNameModal').modal('hide');
    event.preventDefault();

    $.post(event.target.action, $(event.target).serialize()).done(function(data) {
        flash('Sucessfully updated display name', 'info');
     }).fail(function(jqXHR, textStatus, error) {
        flash('Updating display name failed', 'danger');
        console.log("Request failed: " + error);
     });
});

function updateMetadata() {
    $.ajax('/api/info/metadata').done(function(metadata) {
        var track = $('#trackInfo');
        var artist = $('#artistInfo');
        var album = $('#albumInfo');
        var albumCover = $('#albumCover');
        var musicInfo = $('[data-music-info]');
        var albumCoverPlaceholder = $('#albumCoverPlaceholder');

        //Temporary fix until better error checking is added server side
        if (metadata.track_uri === '') {
            musicInfo.text('No music playing');
            albumCover.hide();
            albumCoverPlaceholder.show();
            return;
        }

        albumCover.show();
        albumCoverPlaceholder.hide();

        track.attr('data-id', metadata.track_uri);
        track.text(metadata.track_name);

        artist.attr('data-id', metadata.artist_uri);
        artist.text(metadata.artist_name);

        album.attr('data-id', metadata.album_uri);
        album.text(metadata.album_name);

        albumCover.attr('src', '/api/info/image_url/' + metadata.cover_uri)

        volumeSlider.slider('setValue', metadata.volume / 655.35);
    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
}

function getStatus() {
    $.ajax('/api/info/status').done(function(data) {
        var musicInfo = $('[data-music-info]');
        var albumCover = $('#albumCover');
        var albumCoverPlaceholder = $('#albumCoverPlaceholder');

        //Display buttons depending on play state
        $('[data-action=play]').toggle(!data.playing);
        $('[data-action=pause]').toggle(data.playing);

        $('[data-action=shuffle]').toggleClass('active', data.shuffle);
        $('[data-action=repeat]').toggleClass('active', data.repeat);

        //$('#player').toggle(data.logged_in);

        $('#activeDevice').text(data.active);
        $('#controls button').toggleClass('disabled', !data.active);

        $('#loginLink').toggle(!data.logged_in);
        $('#logoutLink').toggle(data.logged_in);

        if (data.active) {
            volumeSlider.slider('enable');
        } else {
            volumeSlider.slider('disable');
        }


        if (!loggedIn && data.logged_in && !metadataSetup) {
            $('[data-login-required]').show();
            albumCover.show();
            albumCoverPlaceholder.hide();
            loggedIn = true;
            metadataSetup = true;
            updateMetadata();
            metadataInterval = setInterval(updateMetadata, 5000);
        } else if (!data.logged_in) {
            $('[data-login-required]').hide();
            musicInfo.text('Not logged in');
            albumCover.hide();
            albumCoverPlaceholder.show();
            loggedIn = false;
            metadataSetup = false;
            clearInterval(metadataInterval);
            volumeSlider.slider('disable');
        }

    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    });
}

function checkLogin() {
    $.ajax('/login/check_login').done(function(data) {
        if (data.finished) {
            var message = $('.container .row .col-md-12 .alert-info:contains("Waiting for spotify")')
            message.removeClass('alert-info');
            if (data.success) {
                message.text('Login Successful');
                message.addClass('alert-success');
                getStatus();
            } else {
                message.text('Invalid username or password');
                message.addClass('alert-danger');
            }
            message.fadeOut(5000, function() {
                message.remove();
            });
            clearInterval(checkLoginInterval);
        }
    }).fail(function(jqXHR, textStatus, error) {
        console.log("Request failed: " + error);
    })
}

volumeSlider = $('#volumeSlider').slider({
	formatter: function(value) {
		return value;
	}
}).on('slideStop', playbackControl);

getStatus();

//Check for login status (and check if selector is empty)
if ($('.container .row .col-md-12 .alert-info:contains("Waiting for spotify")').length) {
    checkLoginInterval = setInterval(checkLogin, 1000);
}

//Update every 5 seconds
setInterval(getStatus, 5000);
