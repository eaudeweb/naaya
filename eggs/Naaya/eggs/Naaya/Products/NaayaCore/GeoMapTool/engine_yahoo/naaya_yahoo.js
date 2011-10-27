(function() {
    var config = naaya_yahoo_map_api_config;
    var the_map;
    var icons = {};
    var current_places = [];

    $.each(config.icons, function() {
        var icon = new YImage();
        icon.src = this.url;
        icon.size = new YSize(this.w, this.h);
        icon.offsetSmartWindow = new YCoordPoint(6, 11);
        icons["mk_" + this.id] = icon;
    });

    var base_layer_names = {
        'map': YAHOO_MAP_REG,
        'hybrid': YAHOO_MAP_HYB,
        'satellite': YAHOO_MAP_SAT
    };

    function get_map_layer() {
        var current_type = the_map.getCurrentMapType();
        if (current_type === YAHOO_MAP_REG) {
            return 'map';
        } else if (current_type == YAHOO_MAP_HYB) {
            return 'hybrid';
        } else if (current_type == YAHOO_MAP_SAT) {
            return 'satellite';
        }
    }

    function setup_map(map_div_id) {
        the_map = new YMap(document.getElementById(map_div_id));
        the_map.setMapType(base_layer_names[config.base_layer]);
        the_map.disableKeyControls();
        the_map.addTypeControl();
        the_map.addPanControl();
        the_map.addZoomLong();
    }

    function page_position(lat, lon) {
        var geopoint = new YGeoPoint(lat, lon);
        return the_map.convertLatLonXY(geopoint);
    }

    function map_coords(x, y) {
        var coordpoint = new YCoordPoint(x, y);
        var geopoint = the_map.convertXYLatLon(coordpoint);
        return {'lat': geopoint.Lat, 'lon': geopoint.Lon};
    }

    function refresh_points(event, callback) {
        var bounds = get_bounds();
        load_map_points(bounds, function(places) {
            the_map.removeMarkersAll();
            $.each(places, function() {
                var place = this;
                var point = new YGeoPoint(place.lat, place.lon);
                var marker = new YMarker(point, icons[place.icon_name]);
                YEvent.Capture(marker, 'MouseClick', function() {
                    // onclickpoint function is implemented in geomaptool.js
                    onclickpoint(place.lat, place.lon,
                        place.id, place.tooltip);
                });
                YEvent.Capture(marker, 'MouseOver', function() {
                    // onmouseoverpoint function is implemented in geomaptool.js
                    onmouseoverpoint(place.lat, place.lon,
                        place.id, place.tooltip);
                });
                the_map.addOverlay(marker);
            });
            current_places = places;
            if(typeof callback !== "undefined")
                callback(places);
        });
    }


    function get_bounds() {
        var bounds = the_map.getBoundsLatLon();
        return {
            'lat_min': bounds.LatMin,
            'lat_max': bounds.LatMax,
            'lon_min': bounds.LonMin,
            'lon_max': bounds.LonMax
        };
    }

    function point_to_coord(point) {
        return {lat: point.Lat, lon: point.Lon};
    }

    function set_center_and_zoom_in(lat, lon) {
        var point = new YGeoPoint(lat, lon);
        var zoom_level = the_map.getZoomLevel();
        the_map.drawZoomAndCenter(point, zoom_level-1);
    }

    function editor_show_point(point) {
        the_map.removeMarkersAll();
        the_map.addMarker(point);
        the_map.drawZoomAndCenter(point, config.objmap_zoom);
    }

    function editor_marker_at_address(address, callback) {
        the_map.drawZoomAndCenter(address, 4);
        YEvent.Capture(the_map, 'endMapDraw', map_done);
        function map_done() {
            YEvent.Remove(the_map, 'endMapDraw', map_done);
            var point = the_map.getCenterLatLon();
            the_map.removeMarkersAll();
            the_map.addMarker(point);
            callback(point_to_coord(point));
        }
    }

    function setup_editor(coord, click_callback) {
        // set up current value
        if(coord) {
            editor_show_point(new YGeoPoint(coord.lat, coord.lon));
        }
        else {
            the_map.drawZoomAndCenter(config.initial_address,
                                      config.initial_zoom);
        }

        // watch for clicks and report them
        var point;
        YEvent.Capture(the_map, 'MouseDown', function(evt, new_point) {
            console.log(evt)
            if(new_point.Lat === 0 && new_point.Lon === -180) {
                point = null; // special case - user clicked on button
            }
            else {
                point = new_point;
            }
        });
        YEvent.Capture(the_map, 'mousemove', function(evt) {
            point = null;
        });
        YEvent.Capture(the_map, 'MouseUp', function(evt) {
            if(point !== null) {
                the_map.removeMarkersAll();
                the_map.addMarker(point);
                click_callback(point_to_coord(point));
            }
        });
    }

    function draw_points_on_map(points) {
        $.each(points, function(i, p) {
            the_map.addMarker(new YGeoPoint(p.lat, p.lon));
        });
        var first_point = new YGeoPoint(points[0].lat, points[0].lon);
        the_map.drawZoomAndCenter(first_point, 16);
    }

    function get_current_places() {
        return current_places;
    }

    function get_center_and_zoom() {
        var center = the_map.getCenterLatLon();
        return {lat_center: center.Lat,
                lon_center: center.Lon,
                map_zoom: the_map.getZoomLevel()};
    }

    window.naaya_map_engine = {
        name: 'yahoo',
        config: config,
        map_with_points: function(map_div_id, points) {
            the_map = new YMap(document.getElementById(map_div_id));
            the_map.setMapType(base_layer_names[config.base_layer]);
            the_map.disableKeyControls();
            draw_points_on_map(points);
        },
        portal_map: function(map_div_id) {
            setup_map(map_div_id);

            YEvent.Capture(the_map, 'endMapDraw', refresh_points);
            YEvent.Capture(the_map, 'endPan', refresh_points);

            if ('map_zoom' in config) {
                map_zoom = config.map_zoom;
            } else {
                map_zoom = 14;
            }
            if ('lat_center' in config && 'lon_center' in config) {
                map_location = new YGeoPoint(config.lat_center,
                                             config.lon_center);
            } else {
                map_location = config.initial_address;
            }
            the_map.drawZoomAndCenter(map_location, map_zoom);

            return {
                go_to_address: function(address) {
                    the_map.drawZoomAndCenter(address, 9);
                },
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
            editor_show_point(new YGeoPoint(coord.lat, coord.lon));
        },
        object_edit_map: function(map_div_id, coord, click_callback) {
            setup_map(map_div_id);
            the_map.addZoomLong();
            setup_editor(coord, click_callback);
            return {
                marker_at_address: editor_marker_at_address
            };
        }
    };
})();
