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
            $(this).css("background-color","#9b9b9b");
        } else {
            $(this).text('Hide more examples');
            $(this).css("background-color","lightgray");
            var sense_id = $(this).parent().find('.sense_id').text();
            var ul = $(this).parent().next(".examples");
            if (ul.children().length == 0) {
                context.hide();
                breaker.show();
                addRemainingExamples(sense_id, ul, breaker, context);

            }
        }
		return false;
	});
});

function addRemainingExamples(sense_id, ul, breaker, context) {
    var endpoint = '/senses/' + sense_id + '/remaining_examples/';
    $.getJSON(
        endpoint,
        {'csrfmiddlewaretoken': '{{csrf_token}}' },
        function(data) {
            var parsed = $.parseJSON(data);
            var examples = parsed.examples;
            $.each(examples, function(i, example) {
                var ex = $("<li></li>").append(
                    $('<span></span>', {"class": 'date', "text": example.release_date}),
                    $('<span></span>', {"class": 'artist'}).append(
                        $('<a></a>', {"href": '/artists/' + example.artist_slug, "text": example.artist_name})),
                    $('<span></span>', {"class": 'songTitle'}).append(
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
                    )
                ex.appendTo(ul);
            });
            breaker.hide();
            context.show();
        });
}

$(".toggle").click(function(){
    var content = $(this).find(".the-list");
    var copy = content.clone( true );
    var placeholder = $(this).nextAll('.placeholder:first');
    placeholder.html(copy);
    placeholder.find('.the-list').toggle(100);
});
