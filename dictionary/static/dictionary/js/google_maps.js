/**
 * Created by MBK on 13/01/16.
 */

function initialize() {

	var infowindow, markerBounds;
	var latlng = new google.maps.LatLng(40.650002, -73.949997);
	var options = {
        zoom: 10,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };

	$.each($('.map-canvas'), function(i) {
        index = i+1;
        var map = new google.maps.Map(document.getElementById('map' + index), options);
        var markers = [];
        var is_artist = false;
        infowindow = new google.maps.InfoWindow({ content: '' });
        markerBounds = new google.maps.LatLngBounds();
        sense_id = $(this).find('.sense_id').text();
        artist_slug = $(this).find('.artist-slug').text();
        if (artist_slug) {
            endpoint = '/artist_origins/' + artist_slug + '/';
            is_artist = true;
        } else {
            endpoint = '/senses/' + sense_id + '/artist_origins/';
        }
        $.getJSON(endpoint, { 'csrfmiddlewaretoken': '{{csrf_token}}' }, function(data) {
                parsed = $.parseJSON(data);
                $.each(parsed.places, function(index, p) {
                    if (p != null) {
                        tmpLatLng = new google.maps.LatLng(p.latitude, p.longitude);
                        markerText = p.artist + "<br>" + p.place_name;
                        var marker = new google.maps.Marker({
                            map: map,
                            position: tmpLatLng,
                            title: markerText,
                            animation: google.maps.Animation.DROP
                        });
                        markerBounds.extend(tmpLatLng);
                        bindInfoWindow(marker, map, infowindow, markerText);
                        markers.push(marker);
                        map.fitBounds(markerBounds);
                    }
                });
            });
        if (is_artist) {
            zoomChangeBoundsListener = google.maps.event.addListenerOnce(map, 'bounds_changed', function(event) {
                if (this.getZoom()){
                    this.setZoom(10);
                }
            });
            setTimeout(function(){google.maps.event.removeListener(zoomChangeBoundsListener)}, 5000);
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