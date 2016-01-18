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
        var artist = false;
        infowindow = new google.maps.InfoWindow({
		    content: ''
		});
        markerBounds = new google.maps.LatLngBounds();
        sense_id = $(this).find('.sense_id').text();
        artist_slug = $(this).find('.artist-slug').text();
        if (artist_slug) {
            endpoint = '/artist_origins/' + artist_slug + '/';
            artist = true;
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
        if (artist == true) {
            zoomChangeBoundsListener =
                google.maps.event.addListenerOnce(map, 'bounds_changed', function(event) {
                    if (this.getZoom()){
                        this.setZoom(10);
                    }
            });
            setTimeout(function(){google.maps.event.removeListener(zoomChangeBoundsListener)}, 2000);
        }
        var bindInfoWindow = function(marker, map, infowindow, html) {
        google.maps.event.addListener(marker, 'click', function() {
            infowindow.setContent(html);
            infowindow.open(map, marker);
            });
        }
    })
}

function drop() {
    clearMarkers();
    for (var i = 0; i < neighborhoods.length; i++) {
        addMarkerWithTimeout(neighborhoods[i], i * 200);
    }
}

function addMarkerWithTimeout(position, timeout) {
    window.setTimeout(function() {
        markers.push(new google.maps.Marker({
            position: position,
            map: map,
            animation: google.maps.Animation.DROP
        }));
    }, timeout);
}

function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];
}

google.maps.event.addDomListener(window, "load", initialize);