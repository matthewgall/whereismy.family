<div id="map" style="height: 500px"></div>
<script>
	mapboxgl.accessToken = "{{args.mapbox_token}}";

	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/mapbox/streets-v9',
		center: [{{data['lon']}}, {{data['lat']}}],
		zoom: {{args.map_zoom - 1}},
		interactive: false
	});
	map.on('load', function () {
		map.addSource(
			"location", {
				"type": "geojson",
				"data": "/{{username}}.mapbox"
			}
		);
		map.addLayer({
			"id": "location",
			"type": "circle",
			"source": "location"
		});
	})
</script>