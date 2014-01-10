(function() {
    var config = naaya_google_map_api_config;       // a mapping of conf options
    var the_map;                                    // the google.maps.Map instance
    var the_map_div;                                // the map container DOM element
    var the_geocoder = new google.maps.Geocoder();  // the geocoder service
    var icons = {};                                 // icon definitions
    var current_places = [];                        // cache of curent places
    var markers = [];                               // currently placed markers on the map

    $.each(config.icons, function() {
        // define new Icons
        var icon = {};
        icon.url = this.url;
        icon.size = new google.maps.Size(this.w, this.h);   // ex GSize
        icon.anchor = new google.maps.Point(1, 25);
        icons["mk_" + this.id] = icon;
    });

    var base_layer_names = {
        'map':       google.maps.MapTypeId.ROADMAP,
        'hybrid':    google.maps.MapTypeId.HYBRID,
        'physical':  google.maps.MapTypeId.TERRAIN,
        'satellite': google.maps.MapTypeId.SATTELITE
    };

    function get_map_layer() {
        // get the naaya id of current map layer type
        // see base_layer_names for a definition of them
        var current_type = the_map.getMapTypeId();  // ex getCurrentMapType();
        for (var prop in base_layer_names){
            if (current_type == base_layer_names[prop]) {
                return prop;
            }
        }
    }

    function setup_map(map_div_id) {
        // Initialize the Google Map control
        the_map_div = document.getElementById(map_div_id);
        the_map = new google.maps.Map(the_map_div, {  // ex GMap2
            mapTypes: [
                google.maps.MapTypeId.HYBRID,
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.SATTELITE,
                google.maps.MapTypeId.TERRAIN
            ]
        });
        the_map.setMapTypeId(base_layer_names[config.base_layer]);
    }

    function page_position(lat, lon) {
        // coverts geo coordinates to pixel offset on the map div
        var B = the_map.getBounds();
        var P = the_map.getProjection();
        var Z = the_map.getZoom();
        var latLng = new google.maps.LatLng(lat, lon);

        var topRight = P.fromLatLngToPoint(B.getNorthEast());
        var bottomLeft = P.fromLatLngToPoint(B.getSouthWest());
        var scale = Math.pow(2, Z);
        var worldPoint = P.fromLatLngToPoint(latLng);
        var point = new google.maps.Point((worldPoint.x - bottomLeft.x) * scale, 
                                          (worldPoint.y - topRight.y) * scale);
        return point;
    }

    function map_coords(x, y) {
        // translates the given map x/y position to a geographical coordinate
        // TODO: check this

        var point = new google.maps.Point(x, y);
        var projection = the_map.getProjection();
        var latlng = projection.fromPointToLatLng(point);
        return {'lat': latlng.lat(), 'lon': latlng.lng()};
    }

    function clearMarkers(){
        // removes all markers from display
        for (var i=0;i<markers.length;i++){
            markers[i].setMap(null);
        }
    }

    function refresh_points(event, callback) {
        // refreshes the map after the map is changed (bounds changed, zoom, etc)

        var bounds = get_bounds();
        load_map_points(bounds, function(places) {
            clearMarkers();
            $.each(places, function() {
                var place = this;
                var point = new google.maps.LatLng(place.lat, place.lon);
                var icon = icons[place.icon_name];
                var marker = new google.maps.Marker({
                        position:point,
                        title:place.label,
                        icon:icon,
                        map:the_map
                });
                google.maps.event.addListener(marker, "click", function() {
                    onclickpoint(place.lat, place.lon, place.id, place.tooltip);
                });
                google.maps.event.addListener(marker, "mouseover", function() {
                    onmouseoverpoint(place.lat, place.lon, place.id, place.tooltip);
                });
                markers.push(marker);
            });
            current_places = places;
            if (typeof callback !== "undefined")
                callback(places);
        });
    }

    function getBoundsZoomLevel(bounds, mapDim) {
        var WORLD_DIM = { height: 256, width: 256 };
        var ZOOM_MAX = 21;

        function latRad(lat) {
            var sin = Math.sin(lat * Math.PI / 180);
            var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
            return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
        }

        function zoom(mapPx, worldPx, fraction) {
            return Math.floor(Math.log(mapPx / worldPx / fraction) / Math.LN2);
        }

        var ne = bounds.getNorthEast();
        var sw = bounds.getSouthWest();

        var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;

        var lngDiff = ne.lng() - sw.lng();
        var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

        var latZoom = zoom(mapDim.height, WORLD_DIM.height, latFraction);
        var lngZoom = zoom(mapDim.width, WORLD_DIM.width, lngFraction);

        return Math.min(latZoom, lngZoom, ZOOM_MAX);
    }

    function get_bounds() {
        var bounds = the_map.getBounds();
        var sw = bounds.getSouthWest();
        var ne = bounds.getNorthEast();
        var output = {
            'lat_min': sw.lat(),
            'lat_max': ne.lat(),
            'lon_min': sw.lng(),
            'lon_max': ne.lng()
        }

        var center_lat = the_map.getCenter().lat();

        // NOTE: this is used when the map is so zoomed out that 
        // it shows the continents multiple times.
        // This will set the bounds to only the "main" area of the map
        // The problem is that adding a marker with a lat/lng position will 
        // show it multiple times by the map engine

        var horiz_bounds = new google.maps.LatLngBounds(
                new google.maps.LatLng(center_lat, -180),
                new google.maps.LatLng(center_lat, 180));
        var mapDim = {'height':$(the_map_div).height(), 
                      'width':$(the_map_div).width()};
        var zoom_level_for_full_360 = getBoundsZoomLevel(horiz_bounds, mapDim); //the_map.getBoundsZoomLevel(horiz_bounds);

        if(the_map.getZoom() <= zoom_level_for_full_360) {
            // looks like the map fits horizontally in the viewport
            output['lon_min'] = -180;
            output['lon_max'] = 180;
        }

        return output;
    }

    function point_to_coord(point) {
        return {
            lat: point.lat().toFixed(the_map.getZoom()),
            lon: point.lng().toFixed(the_map.getZoom())
        };
    }

    function geocode_address(address, callback) {
        // Converts a query address to coordinates, using google geocoding services
        the_geocoder.geocode({'address':address}, function(result, status) {
            if (status != google.maps.GeocoderStatus.OK) return;

            var place = result[0];
            var point = place.geometry.location;
            var bounds = place.geometry.bounds;
            var zoom_level = [3, 6, 8, 10,12, 14, 16, 17, 18, 19];

            callback(point, bounds, zoom_level[place.address_components.length - 1]);
            //callback(point, bounds);    //zoom_level[place.AddressDetails.Accuracy]);
        });
    }

    function go_to_address_with_zoom(address, zoom) {
        // given a query address, it finds the coordinates and zooms to it
        if(! zoom) {
            return go_to_address(address);
        }
        console.log("Geocoding", address);
        geocode_address(address, function(point, bounds, zoom) {
            if(! point) {
                if(console) { console.log('Could not geocode:', address); }
                return;
            }
            the_map.setCenter(point);
            the_map.setZoom(zoom);
        });
    }

    function go_to_address(address) {
        // given a query address, it finds the coordinates and zooms to it
        console.log("Geocoding", address);
        geocode_address(address, function(point, bounds, zoom) {
            if(! point) {
                if(console) { console.log('Could not geocode:', address); }
                return;
            }
            console.log("Finish geocoding", point, bounds, zoom);
            //the_map.fitBounds(bounds);
            the_map.setCenter(point);
            the_map.setZoom(zoom);
        });
    }

    function set_center_and_zoom_in(lat, lon) {
        var point = new google.maps.LatLng(lat, lon);
        var zoom_level = the_map.getZoom();
        the_map.setCenter(point);
        the_map.setZoom(zoom_level+1);
    }

    function addMarker(point){
        var marker = new google.maps.Marker({
            position:point,
            map:the_map
        });
        markers.push(marker);
    }

    function editor_show_point(point, zoom) {
        clearMarkers();
        addMarker(point);
        the_map.setCenter(point);
        if (zoom !== null) the_map.setZoom(zoom);
    }

    function editor_marker_at_address(address, callback) {
        geocode_address(address, function(point, bounds, zoom) {
            editor_show_point(point, zoom);
            callback(point_to_coord(point));   // changed how this is called
        });
    }

    function setup_editor(coord, click_callback) {
        // set up current value
        if(coord) {
            var point = new google.maps.LatLng(coord.lat, coord.lon);
            editor_show_point(point);
        } else {
            go_to_address(config.initial_address);
        }

        google.maps.event.addListener(the_map, 'click', function(e) {
            clearMarkers();
            var point = e.latLng;
            addMarker(point);
            click_callback(point_to_coord(point));
        });
    }

    function draw_points_on_map(points) {
        $.each(points, function(i, p) {
            var point = new google.maps.LatLng(p.lat, p.lon);
            addMarker(point);
        });
        var first_point = new google.maps.LatLng(points[0].lat, points[0].lon);
        the_map.setCenter(first_point);
        the_map.setZoom(10);
    }

    function get_current_places() {
        return current_places;
    }

    function get_center_and_zoom() {
        var center = the_map.getCenter();
        return {lat_center: center.lat(),
                lon_center: center.lng(),
                map_zoom: the_map.getZoom()};
    }

    window.naaya_map_engine = {
        name: 'google',
        config: config,
        map_with_points: function(map_div_id, points) {
            setup_map(map_div_id);
            draw_points_on_map(points);

            return {
                the_map: the_map
            }
        },
        portal_map: function(map_div_id) {
            setup_map(map_div_id);

            google.maps.event.addListener(the_map, 'bounds_changed', refresh_points);

            if ('map_zoom' in config) {
                map_zoom = parseInt(config.map_zoom);
            } else {
                map_zoom = config.portal_map_zoom;
            }
            if ('lat_center' in config && 'lon_center' in config) {
                var point = new google.maps.LatLng(config.lat_center, config.lon_center);
                the_map.setCenter(point);    //, map_zoom);
                the_map.setZoom(map_zoom);
            } else {
                go_to_address_with_zoom(config.initial_address, map_zoom);
            }

            return {
                go_to_address: go_to_address,
                refresh_points: refresh_points,
                page_position: page_position,
                map_coords: map_coords,
                set_center_and_zoom_in: set_center_and_zoom_in,
                get_current_places: get_current_places,
                get_center_and_zoom: get_center_and_zoom,
                get_map_layer: get_map_layer
            };
        },
        object_index_map: function(map_div_id, coord) {
            setup_map(map_div_id);
            var point = new google.maps.LatLng(coord.lat, coord.lon);
            the_map.setCenter(point);
            the_map.setZoom(config.objmap_zoom);
            addMarker(point);
        },
        object_edit_map: function(map_div_id, coord, click_callback) {
            debugger;
            setup_map(map_div_id);
            setup_editor(coord, click_callback);
            return {
                marker_at_address: editor_marker_at_address
            };
        }
    };
})();
