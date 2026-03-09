L_NO_TOUCH = false;
                L_DISABLE_3D = false;
function applyFilters() {
    var zip = document.getElementById('zipfilter').value.toLowerCase();
    var city = document.getElementById('cityfilter').value.toLowerCase();
    cluster.eachLayer(function(marker){
        var props = marker.options.popup ? marker.options.popup._content : '';
        var show = true;
        if (zip && props.toLowerCase().indexOf(zip) === -1) show = false;
        if (city && props.toLowerCase().indexOf(city) === -1) show = false;
        if (show) marker.addTo(cluster);
        else cluster.removeLayer(marker);
    });
}

function exportVisible() {
    var rows = [];
    cluster.eachLayer(function(marker){
        if (marker._map) { // visible
            var c = marker.getLatLng();
            rows.push([c.lat, c.lng, marker.options.popup._content]);
        }
    });
    var csv = 'lat,lon,popup\n' + rows.map(r=>r.join(',')).join('\n');
    var blob = new Blob([csv], {type:'text/csv'});
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'visible.csv';
    link.click();
}
    
            var map_cf915bf6beaf8ce7c48ce681407fe2b8 = L.map(
                "map_cf915bf6beaf8ce7c48ce681407fe2b8",
                {
                    center: [47.1625, 19.5033],
                    crs: L.CRS.EPSG3857,
                    ...{
  "zoom": 7,
  "zoomControl": true,
  "preferCanvas": false,
}

                }
            );
            L.control.scale().addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);

            

        
    
            var tile_layer_70f0760a3032eeb46f3d4215229c994d = L.tileLayer(
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                {
  "minZoom": 0,
  "maxZoom": 19,
  "maxNativeZoom": 19,
  "noWrap": false,
  "attribution": "\u0026copy; OpenStreetMap contributors",
  "subdomains": "abc",
  "detectRetina": false,
  "tms": false,
  "opacity": 1,
}

            );
        
    
            tile_layer_70f0760a3032eeb46f3d4215229c994d.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var tile_layer_039ba7eea5f21040686c68a67c026766 = L.tileLayer(
                "Stamen Terrain",
                {
  "minZoom": 0,
  "maxZoom": 18,
  "maxNativeZoom": 18,
  "noWrap": false,
  "attribution": "Map tiles by Stamen Design",
  "subdomains": "abc",
  "detectRetina": false,
  "tms": false,
  "opacity": 1,
}

            );
        
    
            tile_layer_039ba7eea5f21040686c68a67c026766.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var tile_layer_7284850f8adcb539716796ae665f6ecd = L.tileLayer(
                "Stamen Toner",
                {
  "minZoom": 0,
  "maxZoom": 18,
  "maxNativeZoom": 18,
  "noWrap": false,
  "attribution": "Map tiles by Stamen Design",
  "subdomains": "abc",
  "detectRetina": false,
  "tms": false,
  "opacity": 1,
}

            );
        
    
            tile_layer_7284850f8adcb539716796ae665f6ecd.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var tile_layer_f151ecba0a57a6ad8219ba0c2db64715 = L.tileLayer(
                "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                {
  "minZoom": 0,
  "maxZoom": 20,
  "maxNativeZoom": 20,
  "noWrap": false,
  "attribution": "\u0026copy; CartoDB",
  "subdomains": "abcd",
  "detectRetina": false,
  "tms": false,
  "opacity": 1,
}

            );
        
    
            tile_layer_f151ecba0a57a6ad8219ba0c2db64715.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var tile_layer_ba17fbbd76c89292f034dfd03d911a0d = L.tileLayer(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                {
  "minZoom": 0,
  "maxZoom": 18,
  "maxNativeZoom": 18,
  "noWrap": false,
  "attribution": "Esri",
  "subdomains": "abc",
  "detectRetina": false,
  "tms": false,
  "opacity": 1,
}

            );
        
    
            tile_layer_ba17fbbd76c89292f034dfd03d911a0d.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            L.control.fullscreen(
                {
  "position": "topleft",
  "title": "Full Screen",
  "titleCancel": "Exit Full Screen",
  "forceSeparateButton": false,
}
            ).addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var tile_layer_adbdd03c8f87a52dca0c9576ae0a6986 = L.tileLayer(
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                {"attribution": "\u0026copy; \u003ca href=\"https://www.openstreetmap.org/copyright\"\u003eOpenStreetMap\u003c/a\u003e contributors", "detect_retina": false, "max_native_zoom": 19, "max_zoom": 19, "min_zoom": 0, "no_wrap": false, "opacity": 1, "subdomains": "abc", "tms": false}
            );
            var mini_map_06338682ac97a62228404736bea57ea9 = new L.Control.MiniMap(
                tile_layer_adbdd03c8f87a52dca0c9576ae0a6986,
                {
  "position": "bottomright",
  "width": 150,
  "height": 150,
  "collapsedWidth": 25,
  "collapsedHeight": 25,
  "zoomLevelOffset": -5,
  "centerFixed": false,
  "zoomAnimation": false,
  "toggleDisplay": true,
  "autoToggleDisplay": false,
  "minimized": false,
}
            );
            map_cf915bf6beaf8ce7c48ce681407fe2b8.addControl(mini_map_06338682ac97a62228404736bea57ea9);
        
    
            var mouse_position_b6cfafa7ac4be06f5f181fbd713cf511 = new L.Control.MousePosition(
                {
  "position": "topright",
  "separator": " | ",
  "emptyString": "Unavailable",
  "lngFirst": false,
  "numDigits": 5,
  "prefix": "LatLng: ",
}
            );
            mouse_position_b6cfafa7ac4be06f5f181fbd713cf511.options["latFormatter"] =
                undefined;
            mouse_position_b6cfafa7ac4be06f5f181fbd713cf511.options["lngFormatter"] =
                undefined;
            map_cf915bf6beaf8ce7c48ce681407fe2b8.addControl(mouse_position_b6cfafa7ac4be06f5f181fbd713cf511);
        
    
            var options = {
              position: "topleft",
              draw: {},
              edit: {},
            }
                // FeatureGroup is to store editable layers.
                var drawnItems_draw_control_868b856f41813093dcf2e5046829f326 =
                    new L.featureGroup().addTo(
                        map_cf915bf6beaf8ce7c48ce681407fe2b8
                    );

            options.edit.featureGroup = drawnItems_draw_control_868b856f41813093dcf2e5046829f326;
            var draw_control_868b856f41813093dcf2e5046829f326 = new L.Control.Draw(
                options
            ).addTo( map_cf915bf6beaf8ce7c48ce681407fe2b8 );
            map_cf915bf6beaf8ce7c48ce681407fe2b8.on(L.Draw.Event.CREATED, function(e) {
                var layer = e.layer,
                    type = e.layerType;
                var coords = JSON.stringify(layer.toGeoJSON());
                layer.on('click', function() {
                    alert(coords);
                });
                drawnItems_draw_control_868b856f41813093dcf2e5046829f326.addLayer(layer);
            });
            map_cf915bf6beaf8ce7c48ce681407fe2b8.on('draw:created', function(e) {
                drawnItems_draw_control_868b856f41813093dcf2e5046829f326.addLayer(e.layer);
            });

            
            document.getElementById('export').onclick = function(e) {
                var data = drawnItems_draw_control_868b856f41813093dcf2e5046829f326.toGeoJSON();
                var convertedData = 'text/json;charset=utf-8,'
                    + encodeURIComponent(JSON.stringify(data));
                document.getElementById('export').setAttribute(
                    'href', 'data:' + convertedData
                );
                document.getElementById('export').setAttribute(
                    'download', "data.geojson"
                );
            }
            
        
    
            var measure_control_10941313848f43f5d84f80e52a9a14bd = new L.Control.Measure(
                {
  "position": "topright",
  "primaryLengthUnit": "meters",
  "secondaryLengthUnit": "miles",
  "primaryAreaUnit": "sqmeters",
  "secondaryAreaUnit": "acres",
});
            map_cf915bf6beaf8ce7c48ce681407fe2b8.addControl(measure_control_10941313848f43f5d84f80e52a9a14bd);

            // Workaround for using this plugin with Leaflet>=1.8.0
            // https://github.com/ljagis/leaflet-measure/issues/171
            L.Control.Measure.include({
                _setCaptureMarkerIcon: function () {
                    // disable autopan
                    this._captureMarker.options.autoPanOnFocus = false;
                    // default function
                    this._captureMarker.setIcon(
                        L.divIcon({
                            iconSize: this._map.getSize().multiplyBy(2)
                        })
                    );
                },
            });

        
    
            var feature_group_287c48e91d46842cff17e722bc2f59f2 = L.featureGroup(
                {
}
            );
        
    
            var heat_map_ef1a44cc2007d59bd4522d64d2d3af47 = L.heatLayer(
                [[47.531399, 21.6259782], [47.4978789, 19.0402383], [47.1910169, 18.410811], [46.9358768, 19.4825067], [47.0264714, 19.5582644], [47.5222089, 19.5508325], [47.4739442, 18.8232855], [47.5899177, 17.6889689], [46.9438023, 17.0790205], [47.1753833, 20.1946279], [46.2546312, 20.1486016], [48.3960978, 21.6561497], [46.3484884, 18.701663], [48.1207157, 20.9129384], [47.8731793, 17.2722342], [47.531399, 21.6259782], [47.3299049, 18.7687291], [47.3772495, 18.9213833], [46.0765092, 18.2280317], [48.2257593, 22.0784247], [47.8452241, 21.4279002], [47.7799838, 19.9291176], [46.2972264, 19.3235909], [47.2613795, 17.8718188], [47.1910169, 18.410811], [48.1207157, 20.9129384], [47.6532732, 19.4747432], [47.4978789, 19.0402383], [46.6524049, 20.2566408], [47.6116279, 21.3437378], [48.0960676, 19.8005642], [47.6683971, 19.6743874], [47.956619, 21.3680532], [47.3772495, 18.9213833], [46.9649048, 18.9405047]],
                {
  "minOpacity": 0.5,
  "maxZoom": 12,
  "radius": 10,
  "blur": 15,
  "gradient": {
  0.4: "blue",
  0.65: "lime",
  1: "red",
},
}
            );
        
    
            heat_map_ef1a44cc2007d59bd4522d64d2d3af47.addTo(feature_group_287c48e91d46842cff17e722bc2f59f2);
        
    
            feature_group_287c48e91d46842cff17e722bc2f59f2.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var feature_group_f9fc493a28ac5b92bb84e09a1a7068e2 = L.featureGroup(
                {
}
            );
        
    
            var heat_map_fcc87dec5affa24e62e88dee0c3f89bf = L.heatLayer(
                [],
                {
  "minOpacity": 0.5,
  "maxZoom": 12,
  "radius": 10,
  "blur": 15,
  "gradient": {
  0.4: "purple",
  0.65: "orange",
  1: "red",
},
}
            );
        
    
            heat_map_fcc87dec5affa24e62e88dee0c3f89bf.addTo(feature_group_f9fc493a28ac5b92bb84e09a1a7068e2);
        
    
            feature_group_f9fc493a28ac5b92bb84e09a1a7068e2.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1searchControl = new L.Control.Search({
                layer: marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1,
                
                propertyName: 'City',
                
                collapsed: false,
                textPlaceholder: 'Search city...',
                position:'topleft',
            
                initial: false,
                
                hideMarkerOnCollapse: true
            
                });
                marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1searchControl.on('search:locationfound', function(e) {
                    marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1.setStyle(function(feature){
                        return feature.properties.style
                    })
                    
                    if(e.layer._popup)
                        e.layer.openPopup();
                })
                marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1searchControl.on('search:collapsed', function(e) {
                        marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1.setStyle(function(feature){
                            return feature.properties.style
                    });
                });
            map_cf915bf6beaf8ce7c48ce681407fe2b8.addControl( marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1searchControl );

        
    
            L.Control.TimeDimensionCustom = L.Control.TimeDimension.extend({
                _getDisplayDateFormat: function(date){
                    var newdate = new moment(date);
                    return newdate.format("YYYY/MM/DD");
                }
            });
            map_cf915bf6beaf8ce7c48ce681407fe2b8.timeDimension = L.timeDimension(
                {
                    period: "P1D",
                }
            );
            var timeDimensionControl = new L.Control.TimeDimensionCustom(
                {
  "position": "bottomleft",
  "minSpeed": 0.1,
  "maxSpeed": 1,
  "autoPlay": false,
  "loopButton": true,
  "timeSliderDragUpdate": true,
  "speedSlider": true,
  "playerOptions": {
  "transitionTime": 200,
  "loop": false,
  "startOver": true,
},
}
            );
            map_cf915bf6beaf8ce7c48ce681407fe2b8.addControl(this.timeDimensionControl);

            var geoJsonLayer = L.geoJson({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"City": "Debrecen, K\u00e1roli G\u00e1sp\u00e1r utca 414, 4032, Hajd\u00fa-Bihar v\u00e1rmegye, Magyarorsz\u00e1g", "search_type": "city", "Zip": 8956, "RecdAt": "2026.02.17. 17:00"}, "geometry": {"type": "Point", "coordinates": [21.6259782, 47.531399]}, "timestamp": "2026.02.17. 17:00"}, {"type": "Feature", "properties": {"City": "Budapest, Szepess\u00e9g utca 8, 1201, Magyarorsz\u00e1g", "search_type": "city", "Zip": 8956, "RecdAt": "2026.02.17. 16:30"}, "geometry": {"type": "Point", "coordinates": [19.0402383, 47.4978789]}, "timestamp": "2026.02.17. 16:30"}, {"type": "Feature", "properties": {"City": "Sz\u00e9kesfeh\u00e9rv\u00e1r, Keszegfalvi K\u00f6z 3, 8000, Fej\u00e9r, Hungary", "search_type": "city", "Zip": 8956, "RecdAt": "2026.02.17. 16:00"}, "geometry": {"type": "Point", "coordinates": [18.410811, 47.1910169]}, "timestamp": "2026.02.17. 16:00"}, {"type": "Feature", "properties": {"City": "Kerekegyh\u00e1za", "search_type": "city", "Zip": 6041, "RecdAt": "2026.02.17. 15:42"}, "geometry": {"type": "Point", "coordinates": [19.4825067, 46.9358768]}, "timestamp": "2026.02.17. 15:42"}, {"type": "Feature", "properties": {"City": "Lajosmizse", "search_type": "city", "Zip": 6050, "RecdAt": "2026.02.17. 15:42"}, "geometry": {"type": "Point", "coordinates": [19.5582644, 47.0264714]}, "timestamp": "2026.02.17. 15:42"}, {"type": "Feature", "properties": {"City": "D\u00e1ny, Szent Istv\u00e1n utca 48, 2118, Pest v\u00e1rmegye, Magyarorsz\u00e1g", "search_type": "city", "Zip": 8956, "RecdAt": "2026.02.17. 14:00"}, "geometry": {"type": "Point", "coordinates": [19.5508325, 47.5222089]}, "timestamp": "2026.02.17. 14:00"}, {"type": "Feature", "properties": {"City": "Biatorb\u00e1gy, Forr\u00e1s Utca 20, 2051, Pest, Hungary", "search_type": "city", "Zip": 8956, "RecdAt": "2026.02.17. 12:00"}, "geometry": {"type": "Point", "coordinates": [18.8232855, 47.4739442]}, "timestamp": "2026.02.17. 12:00"}, {"type": "Feature", "properties": {"City": "Ny\u00fal", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.17. 03:21"}, "geometry": {"type": "Point", "coordinates": [17.6889689, 47.5899177]}, "timestamp": "2026.02.17. 03:21"}, {"type": "Feature", "properties": {"City": "Zalaszentgrot", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.17. 03:21"}, "geometry": {"type": "Point", "coordinates": [17.0790205, 46.9438023]}, "timestamp": "2026.02.17. 03:21"}, {"type": "Feature", "properties": {"City": "Szolnok", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.17. 03:21"}, "geometry": {"type": "Point", "coordinates": [20.1946279, 47.1753833]}, "timestamp": "2026.02.17. 03:21"}, {"type": "Feature", "properties": {"City": "Szeged", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.17. 03:21"}, "geometry": {"type": "Point", "coordinates": [20.1486016, 46.2546312]}, "timestamp": "2026.02.17. 03:21"}, {"type": "Feature", "properties": {"City": "Satoraljaujhely", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [21.6561497, 48.3960978]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Szekszard", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [18.701663, 46.3484884]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Onga", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [20.9129384, 48.1207157]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Mosonmagyarovar", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [17.2722342, 47.8731793]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Debrecen", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [21.6259782, 47.531399]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Martonvasar", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 16:48"}, "geometry": {"type": "Point", "coordinates": [18.7687291, 47.3299049]}, "timestamp": "2026.02.16. 16:48"}, {"type": "Feature", "properties": {"City": "Erd", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [18.9213833, 47.3772495]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Pecs", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [18.2280317, 46.0765092]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Kisvarda", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [22.0784247, 48.2257593]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Hajdunanas", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [21.4279002, 47.8452241]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Gyongyos", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.9291176, 47.7799838]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Janoshalma", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.3235909, 46.2972264]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Zirc", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [17.8718188, 47.2613795]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Szekesfehervar", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [18.410811, 47.1910169]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Onga", "search_type": "city", "Zip": 3562, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [20.9129384, 48.1207157]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Aszod", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.4747432, 47.6532732]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Budapest", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.0402383, 47.4978789]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Szentes", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [20.2566408, 46.6524049]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Balmazujvaros", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [21.3437378, 47.6116279]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Salgotarjan", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.8005642, 48.0960676]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Hatvan", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [19.6743874, 47.6683971]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Tiszavasv\u00e1ri", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [21.3680532, 47.956619]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Erd", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [18.9213833, 47.3772495]}, "timestamp": "2026.02.16. 14:35"}, {"type": "Feature", "properties": {"City": "Dunaujvaros", "search_type": "city", "Zip": 0, "RecdAt": "2026.02.16. 14:35"}, "geometry": {"type": "Point", "coordinates": [18.9405047, 46.9649048]}, "timestamp": "2026.02.16. 14:35"}]}, {
                    pointToLayer: function (feature, latLng) {
                        if (feature.properties.icon == 'marker') {
                            if(feature.properties.iconstyle){
                                return new L.Marker(latLng, {
                                    icon: L.icon(feature.properties.iconstyle)});
                            }
                            //else
                            return new L.Marker(latLng);
                        }
                        if (feature.properties.icon == 'circle') {
                            if (feature.properties.iconstyle) {
                                return new L.circleMarker(latLng, feature.properties.iconstyle)
                                };
                            //else
                            return new L.circleMarker(latLng);
                        }
                        //else

                        return new L.Marker(latLng);
                    },
                    style: function (feature) {
                        return feature.properties.style;
                    },
                    onEachFeature: function(feature, layer) {
                        if (feature.properties.popup) {
                        layer.bindPopup(feature.properties.popup);
                        }
                        if (feature.properties.tooltip) {
                        layer.bindTooltip(feature.properties.tooltip);
                        }
                    }
                })

            var timestamped_geo_json_4441ff5efdc9ac9b034a876eee51c68d = L.timeDimension.layer.geoJson(
                geoJsonLayer,
                {
                    updateTimeDimension: true,
                    addlastPoint: true,
                    duration: undefined,
                }
            ).addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var feature_group_28164d2982ea1c59b8c56b5fc23bdd27 = L.featureGroup(
                {
}
            );
        
    
            var marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1 = L.markerClusterGroup(
                {
}
            );
        
    
            var circle_marker_aa537cf17226cc244a524b02036131da = L.circleMarker(
                [47.531399, 21.6259782],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_e463250eabdc62c25e12116d7b239c66 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_32102db2da7d3e92383a65961ce01ca7 = $(`<div id="html_32102db2da7d3e92383a65961ce01ca7" style="width: 100.0%; height: 100.0%;"><b>City:</b> Debrecen, Károli Gáspár utca 414, 4032, Hajdú-Bihar vármegye, Magyarország<br><b>Type:</b> city</div>`)[0];
                popup_e463250eabdc62c25e12116d7b239c66.setContent(html_32102db2da7d3e92383a65961ce01ca7);
            
        

        circle_marker_aa537cf17226cc244a524b02036131da.bindPopup(popup_e463250eabdc62c25e12116d7b239c66)
        ;

        
    
    
            var circle_marker_bd96351c3bd2c900187f1af218faced9 = L.circleMarker(
                [47.4978789, 19.0402383],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_353c27b5c1e4637f18b11999a74381e5 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_7ec0df8f5f6fd93dbfa12b3c0bd68358 = $(`<div id="html_7ec0df8f5f6fd93dbfa12b3c0bd68358" style="width: 100.0%; height: 100.0%;"><b>City:</b> Budapest, Szepesség utca 8, 1201, Magyarország<br><b>Type:</b> city</div>`)[0];
                popup_353c27b5c1e4637f18b11999a74381e5.setContent(html_7ec0df8f5f6fd93dbfa12b3c0bd68358);
            
        

        circle_marker_bd96351c3bd2c900187f1af218faced9.bindPopup(popup_353c27b5c1e4637f18b11999a74381e5)
        ;

        
    
    
            var circle_marker_dde8cf11f37d60432136ad6f9763845e = L.circleMarker(
                [47.1910169, 18.410811],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_bf06897604e1c82b82e971b891504b19 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_c69e5b6d6faa7c12d4e582ae2761c191 = $(`<div id="html_c69e5b6d6faa7c12d4e582ae2761c191" style="width: 100.0%; height: 100.0%;"><b>City:</b> Székesfehérvár, Keszegfalvi Köz 3, 8000, Fejér, Hungary<br><b>Type:</b> city</div>`)[0];
                popup_bf06897604e1c82b82e971b891504b19.setContent(html_c69e5b6d6faa7c12d4e582ae2761c191);
            
        

        circle_marker_dde8cf11f37d60432136ad6f9763845e.bindPopup(popup_bf06897604e1c82b82e971b891504b19)
        ;

        
    
    
            var circle_marker_b445a2595c28558ed9a3ff90ef60dff5 = L.circleMarker(
                [46.9358768, 19.4825067],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_549783818897a79d4265fa3f232fe2d8 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_817df08ff498c67f58297fdf9311bd75 = $(`<div id="html_817df08ff498c67f58297fdf9311bd75" style="width: 100.0%; height: 100.0%;"><b>City:</b> Kerekegyháza<br><b>Type:</b> city</div>`)[0];
                popup_549783818897a79d4265fa3f232fe2d8.setContent(html_817df08ff498c67f58297fdf9311bd75);
            
        

        circle_marker_b445a2595c28558ed9a3ff90ef60dff5.bindPopup(popup_549783818897a79d4265fa3f232fe2d8)
        ;

        
    
    
            var circle_marker_90fea4a2fd1d87f3e405bb8c579174b0 = L.circleMarker(
                [47.0264714, 19.5582644],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_b55682567b4da1642810e65604135b47 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_b0089b2c66248610081605392220cf07 = $(`<div id="html_b0089b2c66248610081605392220cf07" style="width: 100.0%; height: 100.0%;"><b>City:</b> Lajosmizse<br><b>Type:</b> city</div>`)[0];
                popup_b55682567b4da1642810e65604135b47.setContent(html_b0089b2c66248610081605392220cf07);
            
        

        circle_marker_90fea4a2fd1d87f3e405bb8c579174b0.bindPopup(popup_b55682567b4da1642810e65604135b47)
        ;

        
    
    
            var circle_marker_d090f2558f1dc461f12bb3237ebc908a = L.circleMarker(
                [47.5222089, 19.5508325],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_36ee1b607975f991c0ae488f513f8a93 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_6b786bf467a2ad547cdd4526072770e0 = $(`<div id="html_6b786bf467a2ad547cdd4526072770e0" style="width: 100.0%; height: 100.0%;"><b>City:</b> Dány, Szent István utca 48, 2118, Pest vármegye, Magyarország<br><b>Type:</b> city</div>`)[0];
                popup_36ee1b607975f991c0ae488f513f8a93.setContent(html_6b786bf467a2ad547cdd4526072770e0);
            
        

        circle_marker_d090f2558f1dc461f12bb3237ebc908a.bindPopup(popup_36ee1b607975f991c0ae488f513f8a93)
        ;

        
    
    
            var circle_marker_7738d2d15b7b9f9798dd935bbabea7c2 = L.circleMarker(
                [47.4739442, 18.8232855],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_64399b6acaca17a7c9ffdae4da87c7f4 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_8a9f574ea05f57c9e1beefd818339909 = $(`<div id="html_8a9f574ea05f57c9e1beefd818339909" style="width: 100.0%; height: 100.0%;"><b>City:</b> Biatorbágy, Forrás Utca 20, 2051, Pest, Hungary<br><b>Type:</b> city</div>`)[0];
                popup_64399b6acaca17a7c9ffdae4da87c7f4.setContent(html_8a9f574ea05f57c9e1beefd818339909);
            
        

        circle_marker_7738d2d15b7b9f9798dd935bbabea7c2.bindPopup(popup_64399b6acaca17a7c9ffdae4da87c7f4)
        ;

        
    
    
            var circle_marker_996614c76df2a23f16ae383dcc1c0d81 = L.circleMarker(
                [47.5899177, 17.6889689],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_27930c87065b53be7ed1880079f1e6ff = L.popup({
  "maxWidth": 250,
});

        
            
                var html_43842ea268711db709b3ff1045dd0c9c = $(`<div id="html_43842ea268711db709b3ff1045dd0c9c" style="width: 100.0%; height: 100.0%;"><b>City:</b> Nyúl<br><b>Type:</b> city</div>`)[0];
                popup_27930c87065b53be7ed1880079f1e6ff.setContent(html_43842ea268711db709b3ff1045dd0c9c);
            
        

        circle_marker_996614c76df2a23f16ae383dcc1c0d81.bindPopup(popup_27930c87065b53be7ed1880079f1e6ff)
        ;

        
    
    
            var circle_marker_e2fa46fd7fa4b948fb2a2e77f674e962 = L.circleMarker(
                [46.9438023, 17.0790205],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_f87a5e377cfae059ca62aab5da8917b6 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_d1df771b1fe8b707344b8f8645ae1c14 = $(`<div id="html_d1df771b1fe8b707344b8f8645ae1c14" style="width: 100.0%; height: 100.0%;"><b>City:</b> Zalaszentgrot<br><b>Type:</b> city</div>`)[0];
                popup_f87a5e377cfae059ca62aab5da8917b6.setContent(html_d1df771b1fe8b707344b8f8645ae1c14);
            
        

        circle_marker_e2fa46fd7fa4b948fb2a2e77f674e962.bindPopup(popup_f87a5e377cfae059ca62aab5da8917b6)
        ;

        
    
    
            var circle_marker_8e5f12af7856c3848a5a269b2465fa8b = L.circleMarker(
                [47.1753833, 20.1946279],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_17ff824de5312bf3564a307a8db7c39e = L.popup({
  "maxWidth": 250,
});

        
            
                var html_6ec61b80b31b41f00c4ebb7827f801c6 = $(`<div id="html_6ec61b80b31b41f00c4ebb7827f801c6" style="width: 100.0%; height: 100.0%;"><b>City:</b> Szolnok<br><b>Type:</b> city</div>`)[0];
                popup_17ff824de5312bf3564a307a8db7c39e.setContent(html_6ec61b80b31b41f00c4ebb7827f801c6);
            
        

        circle_marker_8e5f12af7856c3848a5a269b2465fa8b.bindPopup(popup_17ff824de5312bf3564a307a8db7c39e)
        ;

        
    
    
            var circle_marker_e1e823f36bc960caf118d5f1580caf50 = L.circleMarker(
                [46.2546312, 20.1486016],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_a676633c6ec1521afae2c65449abbf43 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_25ef150c563ea3ab314cae598289d7b6 = $(`<div id="html_25ef150c563ea3ab314cae598289d7b6" style="width: 100.0%; height: 100.0%;"><b>City:</b> Szeged<br><b>Type:</b> city</div>`)[0];
                popup_a676633c6ec1521afae2c65449abbf43.setContent(html_25ef150c563ea3ab314cae598289d7b6);
            
        

        circle_marker_e1e823f36bc960caf118d5f1580caf50.bindPopup(popup_a676633c6ec1521afae2c65449abbf43)
        ;

        
    
    
            var circle_marker_daf9175b712d6370ffe7d660c9015635 = L.circleMarker(
                [48.3960978, 21.6561497],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_d9805bdc1bc31c5cc3114bf92d027705 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_004bbb096d32d26d793863c192c1fdba = $(`<div id="html_004bbb096d32d26d793863c192c1fdba" style="width: 100.0%; height: 100.0%;"><b>City:</b> Satoraljaujhely<br><b>Type:</b> city</div>`)[0];
                popup_d9805bdc1bc31c5cc3114bf92d027705.setContent(html_004bbb096d32d26d793863c192c1fdba);
            
        

        circle_marker_daf9175b712d6370ffe7d660c9015635.bindPopup(popup_d9805bdc1bc31c5cc3114bf92d027705)
        ;

        
    
    
            var circle_marker_2b462b033655ca2496fffe4bd6403205 = L.circleMarker(
                [46.3484884, 18.701663],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_c002c3999226fe2ba25885c98b874c56 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_a9eaf5a48db41145df2f7ea16b5518bf = $(`<div id="html_a9eaf5a48db41145df2f7ea16b5518bf" style="width: 100.0%; height: 100.0%;"><b>City:</b> Szekszard<br><b>Type:</b> city</div>`)[0];
                popup_c002c3999226fe2ba25885c98b874c56.setContent(html_a9eaf5a48db41145df2f7ea16b5518bf);
            
        

        circle_marker_2b462b033655ca2496fffe4bd6403205.bindPopup(popup_c002c3999226fe2ba25885c98b874c56)
        ;

        
    
    
            var circle_marker_0d9c2c114224076b502d7d45ab6e5987 = L.circleMarker(
                [48.1207157, 20.9129384],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_e3d80eeb0f9bf7404e5269692b1798b6 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_d7ef7d8314b8183126924428d6c963f3 = $(`<div id="html_d7ef7d8314b8183126924428d6c963f3" style="width: 100.0%; height: 100.0%;"><b>City:</b> Onga<br><b>Type:</b> city</div>`)[0];
                popup_e3d80eeb0f9bf7404e5269692b1798b6.setContent(html_d7ef7d8314b8183126924428d6c963f3);
            
        

        circle_marker_0d9c2c114224076b502d7d45ab6e5987.bindPopup(popup_e3d80eeb0f9bf7404e5269692b1798b6)
        ;

        
    
    
            var circle_marker_981530c58c2325b5861fce08ec6ee021 = L.circleMarker(
                [47.8731793, 17.2722342],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_246064963cdc2701992ccb2f9f289212 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_94f27ed230c312a3f9046e99ba9feb59 = $(`<div id="html_94f27ed230c312a3f9046e99ba9feb59" style="width: 100.0%; height: 100.0%;"><b>City:</b> Mosonmagyarovar<br><b>Type:</b> city</div>`)[0];
                popup_246064963cdc2701992ccb2f9f289212.setContent(html_94f27ed230c312a3f9046e99ba9feb59);
            
        

        circle_marker_981530c58c2325b5861fce08ec6ee021.bindPopup(popup_246064963cdc2701992ccb2f9f289212)
        ;

        
    
    
            var circle_marker_5a99a537ef51a295c0dd541adb3f968d = L.circleMarker(
                [47.531399, 21.6259782],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_f5c5c569dab211e3ce3fd7c27862bfe8 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_2cccd4b0f0eeeac97766b6e11ad0aacc = $(`<div id="html_2cccd4b0f0eeeac97766b6e11ad0aacc" style="width: 100.0%; height: 100.0%;"><b>City:</b> Debrecen<br><b>Type:</b> city</div>`)[0];
                popup_f5c5c569dab211e3ce3fd7c27862bfe8.setContent(html_2cccd4b0f0eeeac97766b6e11ad0aacc);
            
        

        circle_marker_5a99a537ef51a295c0dd541adb3f968d.bindPopup(popup_f5c5c569dab211e3ce3fd7c27862bfe8)
        ;

        
    
    
            var circle_marker_3e063bef2a6d8d406c4613cbcb040fb0 = L.circleMarker(
                [47.3299049, 18.7687291],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_0ce7523821d1ca67a91e00f5ae44d29c = L.popup({
  "maxWidth": 250,
});

        
            
                var html_0ae954c6002d717d49b4a0af55bb36fe = $(`<div id="html_0ae954c6002d717d49b4a0af55bb36fe" style="width: 100.0%; height: 100.0%;"><b>City:</b> Martonvasar<br><b>Type:</b> city</div>`)[0];
                popup_0ce7523821d1ca67a91e00f5ae44d29c.setContent(html_0ae954c6002d717d49b4a0af55bb36fe);
            
        

        circle_marker_3e063bef2a6d8d406c4613cbcb040fb0.bindPopup(popup_0ce7523821d1ca67a91e00f5ae44d29c)
        ;

        
    
    
            var circle_marker_bc4db43f521c607c27f1195ea3a97c6c = L.circleMarker(
                [47.3772495, 18.9213833],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_515ad6f309a60e9b683b9036e0a54157 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_77d04bc12fea46be833cd01b7f45e8a2 = $(`<div id="html_77d04bc12fea46be833cd01b7f45e8a2" style="width: 100.0%; height: 100.0%;"><b>City:</b> Erd<br><b>Type:</b> city</div>`)[0];
                popup_515ad6f309a60e9b683b9036e0a54157.setContent(html_77d04bc12fea46be833cd01b7f45e8a2);
            
        

        circle_marker_bc4db43f521c607c27f1195ea3a97c6c.bindPopup(popup_515ad6f309a60e9b683b9036e0a54157)
        ;

        
    
    
            var circle_marker_4b4166f53aab133be4fd69630bc3f36b = L.circleMarker(
                [46.0765092, 18.2280317],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_c3dbed1ca83ed986cf37ace672997d5b = L.popup({
  "maxWidth": 250,
});

        
            
                var html_bd2687659e203a85935a71b2dbcf754c = $(`<div id="html_bd2687659e203a85935a71b2dbcf754c" style="width: 100.0%; height: 100.0%;"><b>City:</b> Pecs<br><b>Type:</b> city</div>`)[0];
                popup_c3dbed1ca83ed986cf37ace672997d5b.setContent(html_bd2687659e203a85935a71b2dbcf754c);
            
        

        circle_marker_4b4166f53aab133be4fd69630bc3f36b.bindPopup(popup_c3dbed1ca83ed986cf37ace672997d5b)
        ;

        
    
    
            var circle_marker_265b49fc95b72865991d98f71d42d58c = L.circleMarker(
                [48.2257593, 22.0784247],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_a198dd3f64fe528db86dff25fef7f4c6 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_de96b815a589b93b78b56540302c757f = $(`<div id="html_de96b815a589b93b78b56540302c757f" style="width: 100.0%; height: 100.0%;"><b>City:</b> Kisvarda<br><b>Type:</b> city</div>`)[0];
                popup_a198dd3f64fe528db86dff25fef7f4c6.setContent(html_de96b815a589b93b78b56540302c757f);
            
        

        circle_marker_265b49fc95b72865991d98f71d42d58c.bindPopup(popup_a198dd3f64fe528db86dff25fef7f4c6)
        ;

        
    
    
            var circle_marker_6a07d4f5edb4f892cb0b6308b1bd0f57 = L.circleMarker(
                [47.8452241, 21.4279002],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_ac56c86c432bb1a8d771f1212b499083 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_8e06f6b29e86810415dda8bb8339edd9 = $(`<div id="html_8e06f6b29e86810415dda8bb8339edd9" style="width: 100.0%; height: 100.0%;"><b>City:</b> Hajdunanas<br><b>Type:</b> city</div>`)[0];
                popup_ac56c86c432bb1a8d771f1212b499083.setContent(html_8e06f6b29e86810415dda8bb8339edd9);
            
        

        circle_marker_6a07d4f5edb4f892cb0b6308b1bd0f57.bindPopup(popup_ac56c86c432bb1a8d771f1212b499083)
        ;

        
    
    
            var circle_marker_b4b179263932b3854514a55d75dbdd65 = L.circleMarker(
                [47.7799838, 19.9291176],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_9a7f591e35876132b94ccb6d6c1a0d15 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_b94ab65a6840c3faab7a6061a520a153 = $(`<div id="html_b94ab65a6840c3faab7a6061a520a153" style="width: 100.0%; height: 100.0%;"><b>City:</b> Gyongyos<br><b>Type:</b> city</div>`)[0];
                popup_9a7f591e35876132b94ccb6d6c1a0d15.setContent(html_b94ab65a6840c3faab7a6061a520a153);
            
        

        circle_marker_b4b179263932b3854514a55d75dbdd65.bindPopup(popup_9a7f591e35876132b94ccb6d6c1a0d15)
        ;

        
    
    
            var circle_marker_fe40915859ef99b68a00e25a5b7d9409 = L.circleMarker(
                [46.2972264, 19.3235909],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_54bbfac8e57dd0a7fa9771d8cf692243 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_a820c9d8aac2a0b6872df686552a2394 = $(`<div id="html_a820c9d8aac2a0b6872df686552a2394" style="width: 100.0%; height: 100.0%;"><b>City:</b> Janoshalma<br><b>Type:</b> city</div>`)[0];
                popup_54bbfac8e57dd0a7fa9771d8cf692243.setContent(html_a820c9d8aac2a0b6872df686552a2394);
            
        

        circle_marker_fe40915859ef99b68a00e25a5b7d9409.bindPopup(popup_54bbfac8e57dd0a7fa9771d8cf692243)
        ;

        
    
    
            var circle_marker_1dd76264968851ccab9f787bbda9f9d1 = L.circleMarker(
                [47.2613795, 17.8718188],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_c5e3c962c9adb796f800d504e557b92e = L.popup({
  "maxWidth": 250,
});

        
            
                var html_2c418740306365c5c07669a51b45d5cd = $(`<div id="html_2c418740306365c5c07669a51b45d5cd" style="width: 100.0%; height: 100.0%;"><b>City:</b> Zirc<br><b>Type:</b> city</div>`)[0];
                popup_c5e3c962c9adb796f800d504e557b92e.setContent(html_2c418740306365c5c07669a51b45d5cd);
            
        

        circle_marker_1dd76264968851ccab9f787bbda9f9d1.bindPopup(popup_c5e3c962c9adb796f800d504e557b92e)
        ;

        
    
    
            var circle_marker_89df5b8ce4f713c92aba0bf48f17a26f = L.circleMarker(
                [47.1910169, 18.410811],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_fcf1d04efc1cf1d7c487d764bc1faa24 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_1890422b8bc10d849529add198c8336e = $(`<div id="html_1890422b8bc10d849529add198c8336e" style="width: 100.0%; height: 100.0%;"><b>City:</b> Szekesfehervar<br><b>Type:</b> city</div>`)[0];
                popup_fcf1d04efc1cf1d7c487d764bc1faa24.setContent(html_1890422b8bc10d849529add198c8336e);
            
        

        circle_marker_89df5b8ce4f713c92aba0bf48f17a26f.bindPopup(popup_fcf1d04efc1cf1d7c487d764bc1faa24)
        ;

        
    
    
            var circle_marker_9a0b98e9ffbbd8496b4fe453564032f6 = L.circleMarker(
                [48.1207157, 20.9129384],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_9f4cd2696be4b2f8de3a15e35009c13c = L.popup({
  "maxWidth": 250,
});

        
            
                var html_c527a2dfa7b93075e8756a66684186c0 = $(`<div id="html_c527a2dfa7b93075e8756a66684186c0" style="width: 100.0%; height: 100.0%;"><b>City:</b> Onga<br><b>Type:</b> city</div>`)[0];
                popup_9f4cd2696be4b2f8de3a15e35009c13c.setContent(html_c527a2dfa7b93075e8756a66684186c0);
            
        

        circle_marker_9a0b98e9ffbbd8496b4fe453564032f6.bindPopup(popup_9f4cd2696be4b2f8de3a15e35009c13c)
        ;

        
    
    
            var circle_marker_ca57b8c05886fe46c996b434ce314b2f = L.circleMarker(
                [47.6532732, 19.4747432],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_7ca482cd3ec0ea9eee5811a7144ae089 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_91e762c125725ed57bf38cb943d31378 = $(`<div id="html_91e762c125725ed57bf38cb943d31378" style="width: 100.0%; height: 100.0%;"><b>City:</b> Aszod<br><b>Type:</b> city</div>`)[0];
                popup_7ca482cd3ec0ea9eee5811a7144ae089.setContent(html_91e762c125725ed57bf38cb943d31378);
            
        

        circle_marker_ca57b8c05886fe46c996b434ce314b2f.bindPopup(popup_7ca482cd3ec0ea9eee5811a7144ae089)
        ;

        
    
    
            var circle_marker_66365843af6b676db4fdb3376f37614b = L.circleMarker(
                [47.4978789, 19.0402383],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_6b21df1293144a32511dd27180116696 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_f05eb9310bf640f86fdf4d79bacf3e4e = $(`<div id="html_f05eb9310bf640f86fdf4d79bacf3e4e" style="width: 100.0%; height: 100.0%;"><b>City:</b> Budapest<br><b>Type:</b> city</div>`)[0];
                popup_6b21df1293144a32511dd27180116696.setContent(html_f05eb9310bf640f86fdf4d79bacf3e4e);
            
        

        circle_marker_66365843af6b676db4fdb3376f37614b.bindPopup(popup_6b21df1293144a32511dd27180116696)
        ;

        
    
    
            var circle_marker_6e1e4a937b61d4cac03454e03dea3fb4 = L.circleMarker(
                [46.6524049, 20.2566408],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_360f2256c0afd21d63cd2d142b0d0e07 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_21ab9c352fbf14b0f01e63aeadb07b3a = $(`<div id="html_21ab9c352fbf14b0f01e63aeadb07b3a" style="width: 100.0%; height: 100.0%;"><b>City:</b> Szentes<br><b>Type:</b> city</div>`)[0];
                popup_360f2256c0afd21d63cd2d142b0d0e07.setContent(html_21ab9c352fbf14b0f01e63aeadb07b3a);
            
        

        circle_marker_6e1e4a937b61d4cac03454e03dea3fb4.bindPopup(popup_360f2256c0afd21d63cd2d142b0d0e07)
        ;

        
    
    
            var circle_marker_a457f3bc37d4a5f6998d3e73667e61fb = L.circleMarker(
                [47.6116279, 21.3437378],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_941f0fbbcfaff3f6d2fc8a6d36564bef = L.popup({
  "maxWidth": 250,
});

        
            
                var html_8735ccb71d0fe66debf1b3b40ff5927d = $(`<div id="html_8735ccb71d0fe66debf1b3b40ff5927d" style="width: 100.0%; height: 100.0%;"><b>City:</b> Balmazujvaros<br><b>Type:</b> city</div>`)[0];
                popup_941f0fbbcfaff3f6d2fc8a6d36564bef.setContent(html_8735ccb71d0fe66debf1b3b40ff5927d);
            
        

        circle_marker_a457f3bc37d4a5f6998d3e73667e61fb.bindPopup(popup_941f0fbbcfaff3f6d2fc8a6d36564bef)
        ;

        
    
    
            var circle_marker_93475125b40b69bc898daf3f8f65bea8 = L.circleMarker(
                [48.0960676, 19.8005642],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_6f6241a579bcd9c8b36ce58bbfadfbdd = L.popup({
  "maxWidth": 250,
});

        
            
                var html_ddd620a10b20aec00f9bc58963e2f8f1 = $(`<div id="html_ddd620a10b20aec00f9bc58963e2f8f1" style="width: 100.0%; height: 100.0%;"><b>City:</b> Salgotarjan<br><b>Type:</b> city</div>`)[0];
                popup_6f6241a579bcd9c8b36ce58bbfadfbdd.setContent(html_ddd620a10b20aec00f9bc58963e2f8f1);
            
        

        circle_marker_93475125b40b69bc898daf3f8f65bea8.bindPopup(popup_6f6241a579bcd9c8b36ce58bbfadfbdd)
        ;

        
    
    
            var circle_marker_901701b70744be995342f515b51e0ef0 = L.circleMarker(
                [47.6683971, 19.6743874],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_b3ec1e11e6dd35c111f9763e20d6656a = L.popup({
  "maxWidth": 250,
});

        
            
                var html_0b0792fb7601d7a460b803fc9edbaa09 = $(`<div id="html_0b0792fb7601d7a460b803fc9edbaa09" style="width: 100.0%; height: 100.0%;"><b>City:</b> Hatvan<br><b>Type:</b> city</div>`)[0];
                popup_b3ec1e11e6dd35c111f9763e20d6656a.setContent(html_0b0792fb7601d7a460b803fc9edbaa09);
            
        

        circle_marker_901701b70744be995342f515b51e0ef0.bindPopup(popup_b3ec1e11e6dd35c111f9763e20d6656a)
        ;

        
    
    
            var circle_marker_d518058376913e727738be1dc351091e = L.circleMarker(
                [47.956619, 21.3680532],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_0a72dc3e7e70fd5cb31fa17432e81c39 = L.popup({
  "maxWidth": 250,
});

        
            
                var html_901f748e95ef6c4ac0ab42c4f261ef76 = $(`<div id="html_901f748e95ef6c4ac0ab42c4f261ef76" style="width: 100.0%; height: 100.0%;"><b>City:</b> Tiszavasvári<br><b>Type:</b> city</div>`)[0];
                popup_0a72dc3e7e70fd5cb31fa17432e81c39.setContent(html_901f748e95ef6c4ac0ab42c4f261ef76);
            
        

        circle_marker_d518058376913e727738be1dc351091e.bindPopup(popup_0a72dc3e7e70fd5cb31fa17432e81c39)
        ;

        
    
    
            var circle_marker_b08b3b006876cef0379f88a916898f79 = L.circleMarker(
                [47.3772495, 18.9213833],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_ca083d3f2ee7f85b3c0778db5afe965f = L.popup({
  "maxWidth": 250,
});

        
            
                var html_46c75e2d8be7f243258d9ac21243c04f = $(`<div id="html_46c75e2d8be7f243258d9ac21243c04f" style="width: 100.0%; height: 100.0%;"><b>City:</b> Erd<br><b>Type:</b> city</div>`)[0];
                popup_ca083d3f2ee7f85b3c0778db5afe965f.setContent(html_46c75e2d8be7f243258d9ac21243c04f);
            
        

        circle_marker_b08b3b006876cef0379f88a916898f79.bindPopup(popup_ca083d3f2ee7f85b3c0778db5afe965f)
        ;

        
    
    
            var circle_marker_d0fc0ea7c771e682d28a83fb58a8d13c = L.circleMarker(
                [46.9649048, 18.9405047],
                {"bubblingMouseEvents": true, "color": "green", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "green", "fillOpacity": 0.7, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}
            ).addTo(marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1);
        
    
        var popup_cae814cd6d4eb5c7c12cbad7b0b9adcb = L.popup({
  "maxWidth": 250,
});

        
            
                var html_2e67b65b205e71f6e2dc687d277ef5ab = $(`<div id="html_2e67b65b205e71f6e2dc687d277ef5ab" style="width: 100.0%; height: 100.0%;"><b>City:</b> Dunaujvaros<br><b>Type:</b> city</div>`)[0];
                popup_cae814cd6d4eb5c7c12cbad7b0b9adcb.setContent(html_2e67b65b205e71f6e2dc687d277ef5ab);
            
        

        circle_marker_d0fc0ea7c771e682d28a83fb58a8d13c.bindPopup(popup_cae814cd6d4eb5c7c12cbad7b0b9adcb)
        ;

        
    
    
            marker_cluster_8f77a0be7e3dd2f4fa7eb8ea1a6381b1.addTo(feature_group_28164d2982ea1c59b8c56b5fc23bdd27);
        
    
            feature_group_28164d2982ea1c59b8c56b5fc23bdd27.addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
        
    
            var layer_control_a27c3321bf87b23e75f095b663c06b25_layers = {
                base_layers : {
                    "OSM" : tile_layer_70f0760a3032eeb46f3d4215229c994d,
                    "Terrain" : tile_layer_039ba7eea5f21040686c68a67c026766,
                    "Toner" : tile_layer_7284850f8adcb539716796ae665f6ecd,
                    "Dark" : tile_layer_f151ecba0a57a6ad8219ba0c2db64715,
                    "Satellite" : tile_layer_ba17fbbd76c89292f034dfd03d911a0d,
                },
                overlays :  {
                    "Heatmap - City" : feature_group_287c48e91d46842cff17e722bc2f59f2,
                    "Heatmap - Address" : feature_group_f9fc493a28ac5b92bb84e09a1a7068e2,
                    "Markers" : feature_group_28164d2982ea1c59b8c56b5fc23bdd27,
                },
            };
            let layer_control_a27c3321bf87b23e75f095b663c06b25 = L.control.layers(
                layer_control_a27c3321bf87b23e75f095b663c06b25_layers.base_layers,
                layer_control_a27c3321bf87b23e75f095b663c06b25_layers.overlays,
                {
  "position": "topright",
  "collapsed": true,
  "autoZIndex": true,
}
            ).addTo(map_cf915bf6beaf8ce7c48ce681407fe2b8);
