(function() {
    var config = naaya_bing_map_api_config;
    var the_map;
    var the_points_layer = null;
    var icon_url = {}
    var map_base_layer = VEMapStyle[config.base_layer];

    $.each(config.icons, function() {
        icon_url["mk_" + this.id] = this.url;
    });

    function setup_map(map_div_id) {
        $('div#'+map_div_id).css('position', 'relative');
        the_map = new VEMap(map_div_id);
    }

    function after_load_map() {
        the_map.SetMouseWheelZoomToCenter(false);
        the_map.AddShapeLayer(the_points_layer = new VEShapeLayer());
    }

    function refresh_points() {
        var bounds = get_bounds();
        if(bounds === null)
            return;
        load_map_points(bounds, function(places) {
            the_points_layer.DeleteAllShapes();
            $.each(places, function() {
                var place = this;
                var point = new VELatLong(place.lat, place.lon);
                var marker = new VEShape(VEShapeType.Pushpin, point);
                if (place.label != 'cluster') {
                    marker.SetTitle(place.label);
                    marker.SetDescription(place.tooltip);
                }
                marker.SetCustomIcon(icon_url[place.icon_name]);
                the_points_layer.AddShape(marker);
            });
        });
    }

    function get_bounds() {
        var bing_bounds = the_map.GetMapView();
        if(bing_bounds.BottomRightLatLong.Latitude === null) {
            // we're probably in bird's eye view
            return null;
        }
        return {
            'lat_min': bing_bounds.BottomRightLatLong.Latitude,
            'lat_max': bing_bounds.TopLeftLatLong.Latitude,
            'lon_min': bing_bounds.TopLeftLatLong.Longitude,
            'lon_max': bing_bounds.BottomRightLatLong.Longitude
        };
    }

    function point_to_coord(point) {
        return {
            lat: decimals_6(point.Latitude),
            lon: decimals_6(point.Longitude)
        };

        function decimals_6(n) {
            return Math.round(n*1000000) / 1000000;
        }
    }

    function geocode_address(address, callback) {
        // nice api, microsoft!
        the_map.Find(null, address, null, null, null, null,
                     null, null, null, null, results);

        function results(a, b, places) {
            callback(places[0].LatLong);
        }
    }

    function go_to_address(address) {
        the_map.Find(null, address);
    }

    function load_map_show_point(point) {
        if (config.obj_zoom) {
            zoom_level = config.obj_zoom;
        } else {
            zoom_level = 14;
        }
        the_map.LoadMap(point, zoom_level, map_base_layer);
        after_load_map();
        var marker = new VEShape(VEShapeType.Pushpin, point);
        the_points_layer.AddShape(marker);
    }

    function load_map_find_address(address) {
        the_map.LoadMap(null, null, map_base_layer);
        after_load_map();
        the_map.Find(null, address);
    }

    function setup_editor(coord, click_callback) {
        // set up current value
        if(coord) {
            load_map_show_point(new VELatLong(coord.lat, coord.lon));
        }
        else {
            load_map_find_address(config.initial_address);
        }

        // watch for clicks and report them
        var point = null;
        the_map.AttachEvent("onmousedown", function(evt) {
            point = the_map.PixelToLatLong(new VEPixel(evt.mapX, evt.mapY));
        });
        the_map.AttachEvent("onmousemove", function(evt) {
            point = null;
        });
        the_map.AttachEvent("onmouseup", function(evt) {
            if(point) {
                the_points_layer.DeleteAllShapes();
                var marker = new VEShape(VEShapeType.Pushpin, point);
                the_points_layer.AddShape(marker);
                click_callback(point_to_coord(point));
            }
        });
    }

    window.naaya_map_engine = {
        map_with_points: function(map_div_id, points) {
            $('div#'+map_div_id).text(
                'map_with_points not implemented for bing maps');
        },
        portal_map: function(map_div_id) {
            setup_map(map_div_id);
            load_map_find_address(config.initial_address);
            the_map.AttachEvent('onchangeview', refresh_points);
            return {
                go_to_address: go_to_address,
                refresh_points: refresh_points
            };
        },
        object_index_map: function(map_div_id, coord) {
            setup_map(map_div_id);
            load_map_show_point(new VELatLong(coord.lat, coord.lon));
        },
        object_edit_map: function(map_div_id, coord, click_callback) {
            setup_map(map_div_id);
            setup_editor(coord, click_callback);
            return {
                marker_at_address: function(address, callback) {
                    geocode_address(address, function(point) {
                        the_points_layer.DeleteAllShapes();
                        var marker = new VEShape(VEShapeType.Pushpin, point);
                        the_points_layer.AddShape(marker);
                        callback(point_to_coord(point));
                    });
                }
            };
        }
    };
})();
