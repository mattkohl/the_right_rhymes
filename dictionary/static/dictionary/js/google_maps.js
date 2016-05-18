/**
 * Created by MBK on 13/01/16.
 */
$(document).ready(function() {
    $(function () {
        function initialize() {

            var endpoint;
            var latlng = new google.maps.LatLng(40.650002, -73.949997);
            var isDraggable = !('ontouchstart' in document.documentElement);
            var options = {
                zoom: 10,
                center: latlng,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                scrollwheel: false,
                draggable: isDraggable
            };

            $.each($('.map-canvas'), function (i) {
                var index = i + 1;
                var map = new google.maps.Map(document.getElementById('map' + index), options);
                var markers = [];
                var mc = new MarkerClusterer(map);
                var isEntry = true;
                var infoWindow = new google.maps.InfoWindow({content: ''});
                var markerBounds = new google.maps.LatLngBounds();
                var senseId = $(this).find('.sense_id').text();
                var artistSlug = $(this).find('.artist-slug').text();
                var placeSlug = $(this).find('.place-slug').text();
                if (artistSlug) {
                    endpoint = '/data/artists/' + artistSlug + '/';
                    isEntry = false;
                } else if (placeSlug) {
                    endpoint = '/data/places/' + placeSlug + '/';
                    isEntry = false;
                } else {
                    endpoint = '/data/senses/' + senseId + '/artists/';
                }
                $.getJSON(endpoint, {'csrfmiddlewaretoken': '{{csrf_token}}'}, function (data) {
                    if (artistSlug) {
                        processArtists(data.artists);
                    } else if (placeSlug) {
                        processPlaces(data.places);
                    } else {
                        processArtists(data.senses);
                    }
                });
                function processArtists(children) {
                    $.each(children, function (index, p) {
                        if (p != null && p.origin) {
                            tmpLatLng = new google.maps.LatLng(p.origin.latitude, p.origin.longitude);
                            if (p.name) {
                                markerText = "<b>" + p.name + "</b>" + "<br>" + "<a href='/places/" + p.origin.slug + "/'>" + p.origin.name + "</a>";
                            } else {
                                markerText = p.origin.name;
                            }
                            var marker = new google.maps.Marker({
                                map: map,
                                position: tmpLatLng,
                                title: markerText,
                                animation: google.maps.Animation.DROP,
                                url: "/places/" + p.origin.slug + "/"
                            });
                            markerBounds.extend(tmpLatLng);
                            bindInfoWindow(marker, map, infoWindow, markerText);
                            markers.push(marker);
                            mc.addMarker(marker);
                            map.fitBounds(markerBounds);
                        }
                    });
                }
                function processPlaces(children) {
                    $.each(children, function (index, p) {
                        if (p != null && p.latitude) {
                            tmpLatLng = new google.maps.LatLng(p.latitude, p.longitude);
                            if (p.name) {
                                markerText = "<b>" + p.name + "</b>" + "<br>" + "<a href='/places/" + p.slug + "/'>" + p.name + "</a>";
                            } else {
                                markerText = p.name;
                            }
                            var marker = new google.maps.Marker({
                                map: map,
                                position: tmpLatLng,
                                title: markerText,
                                animation: google.maps.Animation.DROP,
                                url: "/places/" + p.slug + "/"
                            });
                            markerBounds.extend(tmpLatLng);
                            bindInfoWindow(marker, map, infoWindow, markerText);
                            markers.push(marker);
                            mc.addMarker(marker);
                            map.fitBounds(markerBounds);
                        }
                    });
                }
                if (!isEntry) {
                    zoomChangeBoundsListener = google.maps.event.addListener(map, 'bounds_changed', function (event) {
                        this.setZoom(10)
                    });
                    //setTimeout(function(){google.maps.event.removeListener(zoomChangeBoundsListener)}, 5000);
                }
                var bindInfoWindow = function (marker, map, infowindow, html) {
                    google.maps.event.addListener(marker, 'click', function () {
                        infowindow.setContent(html);
                        infowindow.open(map, marker);
                    });
                };
            })
        }
        google.maps.event.addDomListener(window, "load", initialize);
    });
});