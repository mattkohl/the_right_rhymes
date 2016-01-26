/**
 * Created by MBK on 14/01/16.
 */
$(document).ready(function(){
	$(".toggle").click(function(){
		$(this).parent().next(".examples").slideToggle("fast");
		if ($(this).text() == 'Toggle fewer examples') {
            $(this).text('Toggle more examples');
            $(this).css("background-color","#9b9b9b");
        } else {
            $(this).text('Toggle fewer examples');
            $(this).css("background-color","lightgray");
            var sense_id = $(this).parent().find('.sense_id').text();
            var ul = $(this).parent().next(".examples");
            if (ul.children().length == 0) {
                addRemainingExamples(sense_id, ul);
            }
        }
		return false;
	});
});

function addRemainingExamples(sense_id, ul) {
    console.log(sense_id);
    var endpoint = '/senses/' + sense_id + '/remaining_examples/';
    $.getJSON(endpoint, { 'csrfmiddlewaretoken': '{{csrf_token}}' }, function(data) {
        var parsed = $.parseJSON(data);
        var examples = parsed.examples;
        $.each(examples, function(i, example) {
            var ex = $("<li></li>").append(
                $('<span></span>', {"class": 'date', "text": example.release_date}),
                $('<span></span>', {"class": 'artist'}).append(
                    $('<a></a>', {"href": '/artists/' + example.artist_slug, "text": example.artist_name})),
                $('<span></span>', {"class": 'songTitle', "text": '"' + example.song_title + '"'}));
                if (example.featured_artists.length > 0) {
                    ex.append('<span> feat. </span>');
                    var featured = [];
                    $.each(example.featured_artists, function(i, feat) {
                        featured.push(
                            $('<span></span>', {"class": 'artist'}).append(
                                $('<a></a>', {"href": '/artists/' + feat.slug, "text": feat.name}))
                        );
                    });
                    ex.append(featured);

                }
                ex.append(
                    $('<span></span>', {"class": 'album', "text": '[' + example.album + ']'}),
                    $('<div class="lyric">' + example.linked_lyric + '</div>')
                )
            ex.appendTo(ul);
        });
    });

}
