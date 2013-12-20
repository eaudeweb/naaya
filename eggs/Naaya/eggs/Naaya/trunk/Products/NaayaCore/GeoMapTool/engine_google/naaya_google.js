(function() {
    var config = naaya_google_map_api_config;
    var the_map;
    var the_geocoder = new GClientGeocoder();
    var icons = {};
    var current_places = [];

    $.each(config.icons, function() {
        var icon = new GIcon(G_DEFAULT_ICON);
        icon.image = this.url;
        icon.iconSize = new GSize(this.w, this.h);
        icon.iconAnchor = new GPoint(1, 25);
        icon.shadow = "misc_/NaayaCore/shadow.png";
        icon.shadowSize = new GSize(26, 17);
        icon.infoWindowAnchor = new GPoint(5, 1);
        icons["mk_" + this.id] = icon;
    });

    var base_layer_names = {
        'map': G_NORMAL_MAP,
        'hybrid': G_HYBRID_MAP,
        'physical': G_PHYSICAL_MAP,
        'satellite': G_SATELLITE_MAP
    };

    function get_map_layer() {
        var current_type = the_map.getCurrentMapType();
        if (current_type === G_NORMAL_MAP) {
            return 'map';
        } else if (current_type == G_HYBRID_MAP) {
            return 'hybrid';
        } else if (current_type == G_SATELLITE_MAP) {
            return 'satellite';
        } else if (current_type == G_PHYSICAL_MAP) {
            return 'physical';
        }
    }

    function setup_map(map_div_id) {
        the_map = new GMap2(document.getElementById(map_div_id), {
            mapTypes: [G_HYBRID_MAP, G_NORMAL_MAP, G_SATELLITE_MAP, G_PHYSICAL_MAP]
        });
        the_map.setMapType(base_layer_names[config.base_layer]);
        the_map.enableScrollWheelZoom();
        the_map.addControl(new GMenuMapTypeControl());
        the_map.addControl(new GSmallMapControl());
        if(! config.allow_mouse_scroll) {
            the_map.disableScrollWheelZoom();
        }
    }

    function page_position(lat, lon) {
        var latlng = new GLatLng(lat, lon);
        return the_map.fromLatLngToContainerPixel(latlng);
    }

    function map_coords(x, y) {
        var point = new GPoint(x, y);
        var latlng = the_map.fromContainerPixelToLatLng(point);
        return {'lat': latlng.lat(), 'lon': latlng.lng()};
    }

    function refresh_points(event, callback) {
        var bounds = get_bounds();
        load_map_points(bounds, function(places) {
            the_map.clearOverlays();
            $.each(places, function() {
                var place = this;
                var point = new GLatLng(place.lat, place.lon);
                var marker = new GMarker(point, {title:place.label,
                                             icon:icons[place.icon_name]});
                GEvent.addListener(marker, "click", function() {
                    // onclickpoint function is implemented in geomaptool.js
                    onclickpoint(place.lat, place.lon,
                        place.id, place.tooltip);
                });
                GEvent.addListener(marker, "mouseover", function() {
                    // onmouseoverpoint function is implemented in geomaptool.js
                    onmouseoverpoint(place.lat, place.lon,
                        place.id, place.tooltip);
                });
                the_map.addOverlay(marker);
            });
            current_places = places;
            if (typeof callback !== "undefined")
                callback(places);
        });
    }

    function get_bounds() {
        var bounds = the_map.getBounds();
        var sw = bounds.getSouthWest();
        var ne = bounds.getNorthEast();
        output = {
            'lat_min': sw.lat(),
            'lat_max': ne.lat(),
            'lon_min': sw.lng(),
            'lon_max': ne.lng()
        }

        var center_lat = the_map.getCenter().lat();
        var horiz_bounds = new GLatLngBounds(new GLatLng(center_lat, -180),
                                             new GLatLng(center_lat, 180));
        var zoom_level_for_full_360 = the_map.getBoundsZoomLevel(horiz_bounds);
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
        the_geocoder.getLocations(address, function(response) {
            if(response.Status.code != 200) return;
            var place = response.Placemark[0];
            var point = new GLatLng(place.Point.coordinates[1],
                                    place.Point.coordinates[0]);
            var zoom_level = [3, 6, 8, 10, 12, 14, 16, 17, 18, 19];
            callback(point, zoom_level[place.AddressDetails.Accuracy]);
        });
    }

    function go_to_address_with_zoom(address, zoom) {
        if(! zoom) {
            return go_to_address(address);
        }
        geocode_address(address, function(point) {
            if(! point) {
                if(console) { console.log('Could not geocode:', address); }
                return;
            }
            the_map.setCenter(point, zoom);
        });
    }

    function go_to_address(address) {
        geocode_address(address, function(point, zoom) {
            if(! point) {
                if(console) { console.log('Could not geocode:', address); }
                return;
            }
            the_map.setCenter(point, zoom);
        });
    }

    function set_center_and_zoom_in(lat, lon) {
        var point = new GLatLng(lat, lon);
        var zoom_level = the_map.getZoom();
        the_map.setCenter(point, zoom_level+1);
    }

    function editor_show_point(point) {
        the_map.clearOverlays();
        var marker = new GMarker(point);
        the_map.addOverlay(marker);
        the_map.setCenter(point, 14);
    }

    function editor_marker_at_address(address, callback) {
        geocode_address(address, function(point, zoom) {
            editor_show_point(point);
            callback(point_to_coord(point));
        });
    }

    function setup_editor(coord, click_callback) {
        // set up current value
        if(coord) {
            editor_show_point(new GLatLng(coord.lat, coord.lon));
        }
        else {
            go_to_address(config.initial_address);
        }

        // watch for clicks and report them
        var point;
        GEvent.addListener(the_map, 'mousemove', function(p) {
            point = p;
        });
        GEvent.addListener(the_map, 'click', function() {
            the_map.clearOverlays();
            the_map.addOverlay(new GMarker(point));
            click_callback(point_to_coord(point));
        });
    }

    function draw_points_on_map(points) {
        $.each(points, function(i, p) {
            the_map.addOverlay(new GMarker(new GLatLng(p.lat, p.lon)));
        });
        var first_point = new GLatLng(points[0].lat, points[0].lon);
        the_map.setCenter(first_point, 10);
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

            GEvent.addListener(the_map, 'moveend', refresh_points);

            if ('map_zoom' in config) {
                map_zoom = parseInt(config.map_zoom);
            } else {
                map_zoom = config.portal_map_zoom;
            }
            if ('lat_center' in config && 'lon_center' in config) {
                var point = new GLatLng(config.lat_center, config.lon_center);
                the_map.setCenter(point, map_zoom);
            } else {
                go_to_address_with_zoom(config.initial_address,
                                        map_zoom);
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
            var point = new GLatLng(coord.lat, coord.lon);
            the_map.setCenter(point, config.objmap_zoom);
            var marker = new GMarker(point);
            the_map.addOverlay(marker);
        },
        object_edit_map: function(map_div_id, coord, click_callback) {
            setup_map(map_div_id);
            setup_editor(coord, click_callback);
            return {
                marker_at_address: editor_marker_at_address
            };
        }
    };
})();
