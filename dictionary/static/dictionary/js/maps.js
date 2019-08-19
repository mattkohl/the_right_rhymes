mapboxgl.accessToken = mapsToken;

function initializeMaps() {
    setTimeout("initializeMapsDelay();", 1000);
}

function initializeMapsDelay() {

    $.each($('.map-canvas'), function (i) {
        var index = i + 1;

        var plot = new mapboxgl.Map({
            container: 'map' + index,
            scrollZoom: false,
            dragPan: false,
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

        $.getJSON(endpoint, {'csrfmiddlewaretoken': '{{csrf_token}}'}, function (data) {
            plot.on('load', function () {

                plot.addSource('points', {
                    type: 'geojson',
                    data: data
                });

                plot.addLayer({
                    "id": "heatmap-12",
                    "source": "points",
                    "type": "heatmap",
                    paint: {
                        'heatmap-radius': 12,
                        "heatmap-weight": {
                            "type": "identity",
                            "property": "weight"
                        }
                    }
                });

            });
            plot.addControl(new mapboxgl.NavigationControl());
            var bounds = new mapboxgl.LngLatBounds();

            data.features.forEach(function(feature) {
                bounds.extend(feature.geometry.coordinates);
            });

            plot.fitBounds(bounds, {padding: 50});
        });
    });

}

initializeMaps();
