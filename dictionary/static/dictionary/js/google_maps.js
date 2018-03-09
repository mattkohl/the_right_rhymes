/**
* Created by MBK on 13/01/16.
*/

function initializeMaps() {

    var endpoint;
    var latlng = new google.maps.LatLng(40.650002, -73.949997);
    var isDraggable = !('ontouchstart' in document.documentElement);
    var style = [
        {
            "featureType": "all",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "saturation": 36
                },
                {
                    "color": "#000000"
                },
                {
                    "lightness": 40
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#000000"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 17
                },
                {
                    "weight": 1.2
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 21
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 17
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 29
                },
                {
                    "weight": 0.2
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 18
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 19
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 17
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "saturation": "-100"
                },
                {
                    "lightness": "-100"
                },
                {
                    "gamma": "0.00"
                }
            ]
        }
    ];
    var options = {
        zoom: 10,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        backgroundColor:"#eeeeee",
        draggable: isDraggable
    };
    var mapType = new google.maps.StyledMapType(style, {name:"Grayscale"});

    $.each($('.map-canvas'), function (i) {
        var index = i + 1;
        var map = new google.maps.Map(document.getElementById('map' + index), options);
            map.mapTypes.set('grey', mapType);
            map.setMapTypeId('grey');
            map.setOptions({zoomControl: false, mapTypeControl: false, streetViewControl: false});
        var pointArray = new google.maps.MVCArray([]);
        var heatmap = new google.maps.visualization.HeatmapLayer({
            data: pointArray,
            map: map
        });
        heatmap.set('radius', 20);
        heatmap.set('opacity', 0.8);
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
                    pointArray.push({location: tmpLatLng, weight: Math.pow(1.6, p.count)});
                    markerBounds.extend(tmpLatLng);
                    map.fitBounds(markerBounds);
                }
            });
        }
        function processPlaces(children) {
            $.each(children, function (index, p) {
                if (p != null && p.latitude) {
                    tmpLatLng = new google.maps.LatLng(p.latitude, p.longitude);
                    pointArray.push(tmpLatLng);
                    markerBounds.extend(tmpLatLng);
                    map.fitBounds(markerBounds);
                }
            });
        }
        if (!isEntry) {
            zoomChangeBoundsListener = google.maps.event.addListener(map, 'bounds_changed', function (event) {
                this.setZoom(10)
            });
        }
        var bindInfoWindow = function (marker, map, infowindow, html) {
            google.maps.event.addListener(marker, 'click', function () {
                infowindow.setContent(html);
                infowindow.open(map, marker);
            });
        };
    })
}
