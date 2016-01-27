/**
 * Created by MBK on 13/01/16.
 */

function initialize() {

	var markerBounds, endpoint;
	var latlng = new google.maps.LatLng(40.650002, -73.949997);
	var options = {
        zoom: 10,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scrollwheel: false
      };

	$.each($('.map-canvas'), function(i) {
        index = i+1;
        var map = new google.maps.Map(document.getElementById('map' + index), options);
        var infowindow;
        var markers = [];
        var is_entry = true;
        infowindow = new google.maps.InfoWindow({ content: '' });
        markerBounds = new google.maps.LatLngBounds();
        var sense_id = $(this).find('.sense_id').text();
        var artist_slug = $(this).find('.artist-slug').text();
        var place_slug = $(this).find('.place-slug').text();
        if (artist_slug) {
            endpoint = '/artist_origins/' + artist_slug + '/';
            is_entry = false;
        } else if (place_slug) {
            endpoint = '/places/' + place_slug + '/latlng/';
            is_entry = false;
        } else {
            endpoint = '/senses/' + sense_id + '/artist_origins/';
        }
        $.getJSON(endpoint, { 'csrfmiddlewaretoken': '{{csrf_token}}' }, function(data) {
                parsed = $.parseJSON(data);
                $.each(parsed.places, function(index, p) {
                    if (p != null) {
                        tmpLatLng = new google.maps.LatLng(p.latitude, p.longitude);

                        if (p.artist) {
                            markerText = "<b>" + p.artist + "</b>" + "<br>" + "<a href='/places/" + p.place_slug + "/'>" + p.place_name + "</a>";
                        } else {
                            markerText = p.place_name;
                        }
                        var marker = new google.maps.Marker({
                            map: map,
                            position: tmpLatLng,
                            title: markerText,
                            animation: google.maps.Animation.DROP,
                            url: "/places/" + p.place_slug + "/"
                        });
                        markerBounds.extend(tmpLatLng);
                        bindInfoWindow(marker, map, infowindow, markerText);
                        markers.push(marker);
                        map.fitBounds(markerBounds);
                    }
                });
            });
        if (!is_entry) {
            zoomChangeBoundsListener = google.maps.event.addListenerOnce(map, 'bounds_changed', function(event) { this.setZoom(10) });
            //setTimeout(function(){google.maps.event.removeListener(zoomChangeBoundsListener)}, 5000);
        }
        var bindInfoWindow = function(marker, map, infowindow, html) {
        google.maps.event.addListener(marker, 'click', function() {
            infowindow.setContent(html);
            infowindow.open(map, marker);
            });
        }
    })
}

google.maps.event.addDomListener(window, "load", initialize);