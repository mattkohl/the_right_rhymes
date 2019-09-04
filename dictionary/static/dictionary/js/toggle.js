/**
 * Created by MBK on 14/01/16.
 */
$(document).ready(function(){
	$(".toggle_more_exx").click(function(){
		$(this).parent().next(".examples").slideToggle("fast");
		var breaker = $(this).parent().find('.loading');
        var context = $(this);
        if ($(this).text() == 'Hide more examples') {
            $(this).text('Show more examples');
            $(this).css("background-color","#838383");
        } else {
            $(this).text('Hide more examples');
            $(this).css("background-color","lightgray");
            var sense_id = $(this).parent().find('.sense_id').text();
            var artist_slug = $(this).parent().find('.artist_slug').text();
            var place_slug = $(this).parent().find('.place_slug').text();
            var place_example_slug = $(this).parent().find('.place_example_slug').text();
            var feat = $(this).parent().find('.feat').text();
            var ul = $(this).parent().next(".examples");
            if (ul.children().length == 0) {
                context.hide();
                breaker.show();
                if (artist_slug != '') {
                    var endpoint = '/data/artists/' + artist_slug + '/sense_examples';
                    if (feat == 'True') {
                        endpoint = endpoint + '?feat=True'
                    }
                    addRemainingArtistSenseExamples(ul, breaker, context, endpoint);
                } else if (place_slug != '') {
                    var endpoint = '/data/places/' + place_slug + '/artists/';
                    addRemainingArtists(ul, breaker, context, endpoint);
                } else if (place_example_slug != '') {
                    var endpoint = '/data/places/' + place_example_slug + '/remaining_examples/';
                    addRemainingExamples(ul, breaker, context, endpoint);
                } else {
                    var endpoint = '/data/senses/' + sense_id + '/remaining_examples/';
                    addRemainingExamples(ul, breaker, context, endpoint);
                }
            }
        }
		return false;
	});
});

function addRemainingArtists(ul, breaker, context, endpoint) {
    $.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token'},
        function(data) {
            var artists = data.artists_with_image;
            $.each(artists, function(i, artist) {
                var ar = $("<li></li>").append(
                    $("<a></a>", {"href": '/artists/' + artist.slug}).append(
                    $("<figure></figure>", {"class": "single-thumb"}).append(
                        $("<img></img>", {"src": artist.image, "height": 200, "width": 200}),
                        $("<figcaption></figcaption>", {"text": artist.name})
                    )));
                ar.appendTo(ul);
            });
            breaker.hide();
            context.show();
        }
    )
}

function addRemainingArtistSenseExamples(ul, breaker, context, endpoint) {
    $.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}' },
        function(data) {
            var senses = data.senses;
            var artist_slug = $('#artist_slug').text();
            $.each(senses, function(i, sense) {
                var ex = $("<li></li>", {"class": 'trr-list-group-item'}).append(
                    $('<div></div>').append(
                        $('<strong></strong>').append(
                            $('<a></a>', {"href": '/' + sense.slug + '#' + sense.xml_id, "text": sense.headword})
                        )
                    ));
                $.each(sense.examples, function(i, example) {
                    ex.append('<div></div>').append(
                        $('<span></span>', {"class": 'date', "text": example.release_date_string}),
                        $('<span></span>', {"class": 'artist'}).append(
                            $('<a></a>', {"href": '/artists/' + example.artist_slug, "text": example.artist_name})),
                        $('<span></span>', {"class": 'song-title'}).append(
                            $('<a></a>', {
                                "href": '/songs/' + example.song_slug,
                                "text": '"' + example.song_title + '"'
                            }))
                    );
                    if (example.featured_artists.length > 0) {
                        ex.append('<span class="comma"> feat. </span>');
                        var featured = [];
                        var last = example.featured_artists.pop();
                        $.each(example.featured_artists, function (i, feat) {
                            featured.push(
                                $('<span></span>', {"class": 'artist'}).append(
                                    $('<a></a>', {"href": '/artists/' + feat.slug, "text": feat.name}),
                                    $('<span></span>', {"class": 'comma', "text": ","}))
                            );
                        });
                        featured.push(
                            $('<span></span>', {"class": 'artist'}).append(
                                $('<a></a>', {"href": '/artists/' + last.slug, "text": last.name})
                            ));
                        ex.append(featured);
                    }
                    ex.append(
                        $('<span></span>', {"class": 'album', "text": '[' + example.album + ']'}),
                        $('<div class="lyric">' + example.linked_lyric + '</div>')
                    );
                });
                ex.appendTo(ul);
            });
            breaker.hide();
            context.show();
            add_tweet();
        });
}

function addRemainingExamples(ul, breaker, context, endpoint) {
    $.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}' },
        function(data) {
            var examples = data.examples;
            var entry_slug = $('#entry_slug').text();
            $.each(examples, function(i, example) {
                var ex = $("<li></li>").append(
                    $('<span></span>', {"class": 'date', "text": example.release_date_string}),
                    $('<span></span>', {"class": 'artist'}).append(
                        $('<a></a>', {"href": '/artists/' + example.artist_slug, "text": example.artist_name})),
                    $('<span></span>', {"class": 'song-title'}).append(
                        $('<a></a>', {"href": '/songs/' + example.song_slug, "text": '"' + example.song_title + '"'}))
                );
                if (example.featured_artists.length > 0) {
                    ex.append('<span class="comma"> feat. </span>');
                    var featured = [];
                    var last = example.featured_artists.pop();
                    $.each(example.featured_artists, function(i, feat) {
                        featured.push(
                            $('<span></span>', {"class": 'artist'}).append(
                                $('<a></a>', {"href": '/artists/' + feat.slug, "text": feat.name}),
                                $('<span></span>', {"class": 'comma', "text": ","}))
                        );
                    });
                    featured.push(
                        $('<span></span>', {"class": 'artist'}).append(
                                $('<a></a>', {"href": '/artists/' + last.slug, "text": last.name})
                        ));
                    ex.append(featured);
                }
                ex.append(
                    $('<span></span>', {"class": 'album', "text": '[' + example.album + ']'}),
                    $('<div class="lyric">' + example.linked_lyric + '</div>')
                );
                ex.appendTo(ul);
            });
            breaker.hide();
            context.show();
            add_tweet();
        });
}

function add_tweet() {
    $('a.tweet').click(function(e){
        e.preventDefault();
        var loc = $(this).attr('href');
        var title  = encodeURIComponent($(this).attr('title'));
        window.open('https://twitter.com/share?url=' + loc + '&text=' + title + '&via=theRightRhymes' + '&', 'twitterwindow', 'height=450, width=550, top='+($(window).height()/2 - 225) +', left='+$(window).width()/2 +', toolbar=0, location=0, menubar=0, directories=0, scrollbars=0');
    });
}

$(".toggle").click(function(){
    var content = $(this).find(".the-list");
    var copy = content.clone( true );
    var placeholder = $(this).nextAll('.placeholder:first');
    placeholder.addClass('placeholder-background');
    placeholder.html(copy);
    placeholder.find('.the-list').toggle(100);

});
