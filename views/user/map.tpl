<div id="map" style="height: 600px"></div>
<script>
	L.mapbox.accessToken = "{{mapbox}}";

	var map = L.mapbox.map('map').setView([{{data['lat']}}, {{data['lon']}}], 14);		
	
	L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);		
	var featureLayer = L.mapbox.featureLayer()
		.loadURL('/{{username}}.mapbox')
		.addTo(map);

	window.setInterval(function() {
		featureLayer.loadURL('/{{username}}.mapbox')
	}, 60000);
</script>