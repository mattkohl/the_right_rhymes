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

            console.log(sense_id);
            var endpoint = '/senses/' + sense_id + '/remaining_examples/';
            $.getJSON(endpoint, { 'csrfmiddlewaretoken': '{{csrf_token}}' }, function(data) {
                    parsed = $.parseJSON(data);
                    $.each(parsed.remaining_examples, function(index, example) {
                        if (example != null) {
                            console.log(example);
                        }
                    });
                });
        }
		return false;
	});
});
