(function() {
    var config = naaya_bing_map_api_config;
    var the_map;
    var the_points_layer = null;
    var icon_url = {}
    var map_base_layer = VEMapStyle[config.base_layer];
    var current_places = [];

    $.each(config.icons, function() {
        icon_url["mk_" + this.id] = this.url;
    });

    function get_map_layer() {
        var current_style = the_map.GetMapStyle();
        var styles = ['Road', 'Hybrid', 'Aerial'];
        for (var i = 0; i < 3; i++) {
            if (current_style === VEMapStyle[styles[i]]) {
                return styles[i];
            }
        }
    }

    function setup_map(map_div_id) {
        $('div#'+map_div_id).css('position', 'relative');
        the_map = new VEMap(map_div_id);
        the_map.AttachEvent("onclick", function(evt) {
            if (evt.elementID === null) return;

            var shape = the_map.GetShapeByID(evt.elementID);
            map_marker_clicked(shape.naaya_point);
        });
        the_map.AttachEvent("onmouseover", function(evt) {
            if (evt.elementID === null) return;

            var shape = the_map.GetShapeByID(evt.elementID);
            var point = shape.GetIconAnchor();
            // onmouseoverpoint function is implemented in geomaptool.js
            onmouseoverpoint(point.Latitude, point.Longitude,
                shape.naaya_id, shape.naaya_tooltip);
        });
    }

    function page_position(lat, lon) {
        var point = new VELatLong(lat, lon);
        return the_map.LatLongToPixel(point);
    }

    function map_coords(x, y) {
        var pixel = new VEPixel(x, y);
        var point = the_map.PixelToLatLong(pixel);
        return {'lat': point.Latitude, 'lon': point.Longitude};
    }

    function after_load_map() {
        the_map.SetMouseWheelZoomToCenter(false);
        the_map.AddShapeLayer(the_points_layer = new VEShapeLayer());
    }

    function refresh_points(event, callback) {
        var bounds = get_bounds();
        if(bounds === null)
            return;
        load_map_points(bounds, function(places) {
            the_points_layer.DeleteAllShapes();
            $.each(places, function() {
                var place = this;
                var point = new VELatLong(place.lat, place.lon);
                var marker = new VEShape(VEShapeType.Pushpin, point);
                marker.SetCustomIcon(icon_url[place.icon_name]);
                marker.naaya_point = place;
                marker.naaya_id = place.id;
                marker.naaya_tooltip = place.tooltip;
                the_points_layer.AddShape(marker);
            });
            current_places = places;
            if(typeof callback !== "undefined")
                callback(places);
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

    function set_center_and_zoom_in(lat, lon) {
        var point = new VELatLong(lat, lon);
        var zoom_level = the_map.GetZoomLevel();
        the_map.SetCenterAndZoom(point, zoom_level+1);
    }

    function load_map_show_point(point) {
        the_map.LoadMap(point, config.objmap_zoom, map_base_layer);
        after_load_map();
        var marker = new VEShape(VEShapeType.Pushpin, point);
        the_points_layer.AddShape(marker);
    }

    function load_map_find_address(address, zoom) {
        the_map.LoadMap(null, null, map_base_layer);
        after_load_map();
        var fix_zoom = function() {
            if(zoom) {
                the_map.SetZoomLevel(zoom);
            }
        };
        the_map.Find(null, address, null, null, 0, 1,
                     true, false, false, true, fix_zoom);
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

    function get_current_places() {
        return current_places;
    }

    function get_center_and_zoom() {
        var center = the_map.GetCenter();
        return {lat_center: center.Latitude,
                lon_center: center.Longitude,
                map_zoom: the_map.GetZoomLevel()};
    }

    function get_resolution() {
        // calculate current resolution based on map zoom
        var zoom = the_map.GetZoomLevel();
        var resolution_at_zoom_zero = 256 / 360; // 256 pixels for 360 degrees
        return resolution_at_zoom_zero * Math.pow(2, zoom);
    }

    window.naaya_map_engine = {
        name: 'bing',
        config: config,
        map_with_points: function(map_div_id, points) {
            $('div#'+map_div_id).text(
                'map_with_points not implemented for bing maps');
        },
        portal_map: function(map_div_id) {
            setup_map(map_div_id);

            the_map.AttachEvent('onchangeview', refresh_points);

            if ('lat_center' in config && 'lon_center' in config) {
                var point = new VELatLong(config.lat_center, config.lon_center);
                if ('map_zoom' in config) {
                    the_map.LoadMap(point, config.map_zoom, map_base_layer);
                } else {
                    the_map.LoadMap(point, null, map_base_layer);
                }
                after_load_map();
            } else {
                load_map_find_address(config.initial_address,
                                      config.initial_zoom);
            }

            return {
                go_to_address: go_to_address,
                refresh_points: refresh_points,
                page_position: page_position,
                map_coords: map_coords,
                set_center_and_zoom_in: set_center_and_zoom_in,
                get_current_places: get_current_places,
                get_center_and_zoom: get_center_and_zoom,
                get_resolution: get_resolution,
                get_map_layer: get_map_layer
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
