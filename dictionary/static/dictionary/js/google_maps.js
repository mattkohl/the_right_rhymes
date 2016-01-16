/**
 * Created by MBK on 13/01/16.
 */

function initialize() {

	var map;

	var latlng = new google.maps.LatLng(40.650002, -73.949997);
	var options = {
        zoom: 10,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };

	$.each($('.map-canvas'), function() {
        map = new google.maps.Map($(this).find('.map')[0], options);
        var markers = [];
        var infowindow =  new google.maps.InfoWindow({
		    content: ''
		});
        var markerBounds = new google.maps.LatLngBounds();
        sense_id = $(this).find('.sense_id').text();
        endpoint = '/senses/' + sense_id + '/artist_origins/';
        $.getJSON(endpoint, { 'csrfmiddlewaretoken': '{{csrf_token}}' }, function(data) {
                parsed = $.parseJSON(data);
                $.each(parsed.places, function(index, p) {
                    //console.log(p);
                    if (p != null) {
                        tmpLatLng = new google.maps.LatLng(p.latitude, p.longitude);
                        markerText = p.artist + "<br>" + p.place_name;
                        var marker = new google.maps.Marker({
                            map: map,
                            position: tmpLatLng,
                            title: markerText
                        });
                        markerBounds.extend(tmpLatLng);
                        bindInfoWindow(marker, map, infowindow, markerText);
                        markers.push(marker);
                        map.fitBounds(markerBounds);
                    }
                });
            });
        	var bindInfoWindow = function(marker, map, infowindow, html) {
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.setContent(html);
                infowindow.open(map, marker);
	    });
	}
        })
	}

google.maps.event.addDomListener(window, "load", initialize);