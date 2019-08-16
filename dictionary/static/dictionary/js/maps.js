mapboxgl.accessToken = mapsToken;

function initializeMaps() {
    setTimeout("initializeMapsDelay();", 100);
}

function initializeMapsDelay() {

    $.each($('.map-canvas'), function (i) {
        var index = i + 1;

        var plot = new mapboxgl.Map({
            container: 'map' + index,
            style: 'mapbox://styles/mattkohl/cjzbh31rv0g3c1cpcos3l17xv',
            center: [-98.5795, 39.8283],
            zoom: 2
        });

        var isEntry = true;
        var senseId = $(this).find('.sense_id').text();
        var artistSlug = $(this).find('.artist-slug').text();
        var placeSlug = $(this).find('.place-slug').text();
        if (artistSlug) {
            endpoint = '/data/artists/' + artistSlug + '/geojson';
            isEntry = false;
        } else if (placeSlug) {
            endpoint = '/data/places/' + placeSlug + '/geojson';
            isEntry = false;
        } else {
            endpoint = '/data/senses/' + senseId + '/artists/geojson';
        }

        console.log(endpoint);

        $.getJSON(endpoint, {'csrfmiddlewaretoken': '{{csrf_token}}'}, function (data) {
            plot.on('load', function () {

                plot.addSource('points', {
                    type: 'geojson',
                    data: data
                });

                plot.addLayer({
                    "id": "points-heat",
                    "type": "heatmap",
                    "source": "points",
                    "maxzoom": 9,
                    "paint": {
                        // Increase the heatmap weight based on frequency and property magnitude
                        "heatmap-weight": [
                            "interpolate",
                            ["linear"],
                            ["get", "weight"],
                            0, 0,
                            6, 3
                        ],
                        // Increase the heatmap color weight weight by zoom level
                        // heatmap-intensity is a multiplier on top of heatmap-weight
                        "heatmap-intensity": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            0, 1,
                            9, 3
                        ],
                        // Color ramp for heatmap.  Domain is 0 (low) to 1 (high).
                        // Begin color ramp at 0-stop with a 0-transparancy color
                        // to create a blur-like effect.
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0, "rgba(33,102,172,0)",
                            0.2, "rgb(103,169,207)",
                            0.4, "rgb(209,229,240)",
                            0.6, "rgb(253,219,199)",
                            0.8, "rgb(239,138,98)",
                            1, "rgb(178,24,43)"
                        ],
                        // Adjust the heatmap radius by zoom level
                        "heatmap-radius": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            0, 2,
                            9, 20
                        ],
                        // Transition from heatplot to circle layer by zoom level
                        "heatmap-opacity": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            7, 1,
                            9, 0
                        ],
                    }
                });

                plot.addLayer({
                    "id": "points-circles",
                    "type": "circle",
                    "source": "points",
                    "minzoom": 7,
                    "paint": {
                        // Size circle radius by earthquake magnitude and zoom level
                        "circle-radius": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            7, [
                                "interpolate",
                                ["linear"],
                                ["get", "weight"],
                                1, 1,
                                6, 4
                            ],
                            16, [
                                "interpolate",
                                ["linear"],
                                ["get", "weight"],
                                1, 5,
                                6, 50
                            ]
                        ],
                        // Color circle by earthquake magnitude
                        "circle-color": [
                            "interpolate",
                            ["linear"],
                            ["get", "weight"],
                            1, "rgba(33,102,172,0)",
                            2, "rgb(103,169,207)",
                            3, "rgb(209,229,240)",
                            4, "rgb(253,219,199)",
                            5, "rgb(239,138,98)",
                            6, "rgb(178,24,43)"
                        ],
                        "circle-stroke-color": "white",
                        "circle-stroke-width": 1,
                        // Transition from heatmap to circle layer by zoom level
                        "circle-opacity": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            7, 0,
                            8, 1
                        ]
                    }
                });

            });
            plot.fitBounds;
            plot.scrollZoom.disable();

        });
    });

}

initializeMaps();
