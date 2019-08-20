mapboxgl.accessToken = mapsToken;

function initializeMaps() {

    $.each($('.map-canvas'), function (i) {
        var index = i + 1;

        var plot = new mapboxgl.Map({
            container: 'map' + index,
            scrollZoom: false,
            tolerance: 3.5,
            maxzoom: 12,
            buffer: 0,
            style: 'mapbox://styles/mattkohl/cjzbh31rv0g3c1cpcos3l17xv'
        });

        var isEntry = true;
        var senseId = $(this).find('.sense_id').text();
        var artistSlug = $(this).find('.artist-slug').text();
        var placeSlug = $(this).find('.place-slug').text();
        if (artistSlug) {
            endpoint = '/data/artists/' + artistSlug + '/geojson?format=json';
            isEntry = false;
        } else if (placeSlug) {
            endpoint = '/data/places/' + placeSlug + '/geojson?format=json';
            isEntry = false;
        } else {
            endpoint = '/data/senses/' + senseId + '/artists/geojson?format=json';
        }

        plot.on('load', function () {
            $.getJSON(endpoint, {'csrfmiddlewaretoken': '{{csrf_token}}'})
            .done(function (data) {
                plot.addSource('points', {
                    type: 'geojson',
                    data: data
                });
                plot.addLayer({
                    "id": "heatmap-point",
                    "source": "points",
                    "type": "heatmap",
                    "paint": {
                        "heatmap-weight": ["interpolate", ["linear"], ["get", "weight"], 0, 0, 6, 1],
                        'heatmap-color': [
                            'interpolate',
                            ['linear'],
                            ['heatmap-density'],
                            0, "rgba(33,102,172,0)",
                            0.2, "rgb(103,169,207)",
                            0.4, "rgb(209,229,240)",
                            0.6, "rgb(253,219,199)",
                            0.8, "rgb(239,138,98)",
                            1, "rgb(178,24,43)"
                        ],
                        'heatmap-radius': { stops: [ [11, 15], [15, 20] ] },
                        'heatmap-opacity': { default: 1, stops: [ [14, 1], [15, 0] ] }
                    }
                });

                plot.addLayer({
                    id: 'circles-point',
                    type: 'circle',
                    source: 'points',
                    minzoom: 10,
                    paint: {
                    // increase the radius of the circle as the zoom level and dbh value increases
                        'circle-radius': {
                            property: 'weight',
                            type: 'exponential',
                            stops: [
                                [{ zoom: 10, value: 1 }, 5],
                                [{ zoom: 10, value: 62 }, 10],
                                [{ zoom: 17, value: 1 }, 20],
                                [{ zoom: 17, value: 62 }, 50],
                        ] },
                        'circle-color': {
                            property: 'weight',
                            type: 'exponential',
                            stops: [
                                [0, 'rgba(236,222,239,0)'],
                                [10, 'rgb(236,222,239)'],
                                [20, 'rgb(208,209,230)'],
                                [30, 'rgb(166,189,219)'],
                                [40, 'rgb(103,169,207)'],
                                [50, 'rgb(28,144,153)'],
                                [60, 'rgb(1,108,89)']
                            ]
                        },
                        'circle-stroke-color': 'white',
                        'circle-stroke-width': 1,
                        'circle-opacity': { stops: [ [14, 0], [15, 1] ] }
                    }
                });

                plot.addControl(new mapboxgl.NavigationControl());
                var bounds = new mapboxgl.LngLatBounds();
                data.features.forEach(function(feature) {
                    bounds.extend(feature.geometry.coordinates);
                });
                plot.fitBounds(bounds, {padding: 50});
            });

        });
    });

}

initializeMaps();
