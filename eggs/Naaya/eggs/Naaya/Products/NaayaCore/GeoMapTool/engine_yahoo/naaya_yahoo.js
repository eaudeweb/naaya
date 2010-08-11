(function() {
    var config = naaya_yahoo_map_api_config;
    var the_map;
    var icons = {};

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

    function setup_map(map_div_id) {
        the_map = new YMap(document.getElementById(map_div_id));
        the_map.setMapType(base_layer_names[config.base_layer]);
        the_map.disableKeyControls();
        the_map.addTypeControl();
        the_map.addPanControl();
        the_map.addZoomLong();
    }

    function refresh_points() {
        var bounds = get_bounds();
        load_map_points(bounds, function(places) {
            the_map.removeMarkersAll();
            $.each(places, function() {
                var place = this;
                var point = new YGeoPoint(place.lat, place.lon);
                var marker = new YMarker(point, icons[place.icon_name]);
                if (place.label === 'cluster') {
                    YEvent.Capture(marker, 'MouseClick', function() {
                        the_map.drawZoomAndCenter(point,
                                the_map.getZoomLevel() - 1);
                    });
                } else {
                    YEvent.Capture(marker, 'MouseClick', function() {
                        load_marker_balloon(place.lat, place.lon,
                            function(html) {
                                marker.openSmartWindow(html);
                            });
                    });
                }
                the_map.addOverlay(marker);
            });
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

    window.naaya_map_engine = {
        map_with_points: function(map_div_id, points) {
            the_map = new YMap(document.getElementById(map_div_id));
            the_map.setMapType(base_layer_names[config.base_layer]);
            the_map.disableKeyControls();
            draw_points_on_map(points);
        },
        portal_map: function(map_div_id) {
            setup_map(map_div_id);
            the_map.drawZoomAndCenter(config.initial_address, 14);
            YEvent.Capture(the_map, 'endMapDraw', refresh_points);
            YEvent.Capture(the_map, 'endPan', refresh_points);
            return {
                go_to_address: function(address) {
                    the_map.drawZoomAndCenter(address, 9);
                },
                refresh_points: refresh_points
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
