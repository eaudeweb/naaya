(function() {

    window.NaayaOpenLayers = {

        osm_layer: function() {
            return new OpenLayers.Layer.OSM();
        },

        google_layer: function(layer_info) {
            return new OpenLayers.Layer.Google(
                layer_info['label'],
                {type: layer_info['google_map_type']});
        },

        bing_layer: function(layer_info) {
            return new OpenLayers.Layer.Bing({
                name: layer_info['label'],
                key: ("AlKaIe5F9S8XxrUxhKHFClkoL6hTuPSTF-"+
                      "kcfqg47zP4A7pvna-FhyyzEc8IVkBw"),
                type: layer_info['bing_map_type']
            });
        }

    };


    OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
        mapClicked: function() {},

        initialize: function(mapClicked, options) {
            OpenLayers.Control.prototype.initialize.apply(this, [options]);
            if(mapClicked) this.mapClicked = mapClicked;
            this.handler = new OpenLayers.Handler.Click(
                this, {'click': this.trigger});
        },

        trigger: function(e) {
            this.mapClicked(e.xy);
        }
    });


    var engine = window.naaya_map_engine = {name: 'openlayers'};

    engine.config = naaya_openlayers_map_api_config;

    engine.wgs84 = new OpenLayers.Projection("EPSG:4326");

    engine.geotype_icons = {};
    $.each(engine.config['icons'], function(i, icon_data) {
        engine.geotype_icons['mk_' + icon_data['id']] = {
            url: icon_data['url'],
            width: icon_data['w'],
            height: icon_data['h'],
            offset_x: -icon_data['w'] / 2,
            offset_y: -icon_data['h'],
            color: icon_data['color']
        };
    });

    engine.new_icon = function(path, width, height, offset_x, offset_y) {
        var size = new OpenLayers.Size(width, height);
        var offset = new OpenLayers.Pixel(offset_x, offset_y);
        return new OpenLayers.Icon(path, size, offset);
    };

    engine.geocode_nominatim = function(address, callback) {
        var url = engine.config['server_url'] + '/geocode_nominatim';
        $.getJSON(url, {'address': address}, callback);
    };

    engine.geocode = function(address, callback) {
        var url = engine.config['server_url'] + '/geocode';
        $.getJSON(url, {'address': address}, callback);
    };

    engine.bounds_btlr = function(box) {
        // construct a Bounds object from [bottom, top, left, right] values
        var b = box[0], t = box[1], l = box[2], r = box[3];
        return new OpenLayers.Bounds(l, b, r, t);
    };

    engine.config['initial_bounds'] = engine.bounds_btlr(
        engine.config['initial_bounding_box']);

    engine.create_olmap = function(div_id) {
        $('#' + div_id).addClass('naaya-openlayers');
        var nav_control = new OpenLayers.Control.Navigation();
        nav_control.zoomWheelEnabled = engine.config['mouse_wheel_zoom'];
        var olmap = new OpenLayers.Map({
            'div': div_id,
            controls: [
                nav_control,
                new OpenLayers.Control.ZoomPanel(),
                new OpenLayers.Control.Attribution()
            ]
        });
        var layer_factory = eval(engine.config['base_layer']['factory']);
        var layer = layer_factory(engine.config['base_layer']);
        olmap.addLayer(layer);
        return olmap;
    };

    engine.new_map = function(div_id) {
        var map = {_move_handlers: []};
        map.olmap = engine.create_olmap(div_id);
        map.projection = map.olmap.getProjectionObject();

        map.from_wgs84 = function(point, name) {
            return point.clone().transform(engine.wgs84, map.projection);
        };

        map.to_wgs84 = function(point, name) {
            return point.clone().transform(map.projection, engine.wgs84);
        };

        map.get_center_and_zoom = function() {
            var center = map.olmap.center;
            var lat_lon = map.to_wgs84(new OpenLayers.LonLat(center.lon, center.lat));
            return {lat_center: lat_lon.lat,
                    lon_center: lat_lon.lon,
                    map_zoom: map.olmap.zoom};
        };

        map.set_zoom_and_center = function(position) {
            var lonlat = new OpenLayers.LonLat(position.lon, position.lat);
            var center = map.from_wgs84(lonlat);
            map.olmap.setCenter(center, position.zoom);
        };

        map.add_click_callback = function(callback) {
            var add_point = new OpenLayers.Control.Click(map_clicked);
            map.olmap.addControl(add_point);
            add_point.activate();
            function map_clicked(xy) {
                var map_coord = map.olmap.getLonLatFromViewPortPx(xy);
                callback(map.to_wgs84(map_coord));
            };
        };

        map.get_bounds = function() {
            var extent = map.olmap.getExtent();
            var tl = map.to_wgs84(new OpenLayers.LonLat(
                        extent.left, extent.top));
            var br = map.to_wgs84(new OpenLayers.LonLat(
                        extent.right, extent.bottom));
            return {
                'lat_min': br.lat,
                'lat_max': tl.lat,
                'lon_min': tl.lon,
                'lon_max': br.lon
            };
        };

        map.get_resolution = function() {
            var p_1_0 = new OpenLayers.LonLat(1, 0);
            var one_degree = map.from_wgs84(p_1_0).lon;
            return one_degree / map.olmap.getResolution();
        };

        map.coord_to_page_xy = function(coord) {
            var lonlat = new OpenLayers.LonLat(coord.lon, coord.lat);
            var xy = map.olmap.getViewPortPxFromLonLat(
                map.from_wgs84(lonlat));
            return xy;
        };

        map.zoom_to_extent = function(extent, fill_ratio, max_zoom) {
            // `fill_ratio` means how much of the map viewport we can
            // fill up. Defaults to `1.0`.
            if(fill_ratio == null) fill_ratio = 1.0;
            if(max_zoom == null) max_zoom = 14;

            var map_extent = extent.transform(engine.wgs84, map.projection);
            map_extent = map_extent.scale(1/fill_ratio);
            var zoom = Math.min(map.olmap.getZoomForExtent(map_extent), max_zoom);
            map.olmap.setCenter(map_extent.getCenterLonLat(), zoom);
        };

        map.go_to_address = function(address) {
            engine.geocode(address, function(results) {
                var result = results[0];
                var bb = result['boundingbox'];
                var btlr = [bb['bottom'], bb['top'], bb['left'], bb['right']];
                var bounds = engine.bounds_btlr(btlr);
                map.zoom_to_extent(bounds);
            });
        };

        map.add = function(something) {
            something.map(map);
        };

        map.show_mouse_coordinates = function() {
            var mouse_position = new OpenLayers.Control.MousePosition(
                {displayProjection: engine.wgs84});
            map.olmap.addControl(mouse_position);
            mouse_position.activate();
        };

        map.on_move = function(handler) {
            map._move_handlers.push(handler);
        };

        map.olmap.events.register("moveend", null, function() {
            var zoom = map.olmap.getZoom();
            var center = map.to_wgs84(map.olmap.getCenter());
            $.each(map._move_handlers, function(i, handler) {
                handler(center.lon, center.lat, zoom);
            });
        });

        map.add_scale_line_control = function() {
            var scale_line_control = new OpenLayers.Control.ScaleLine(
                {geodesic: true});
            map.olmap.addControl(scale_line_control);
            scale_line_control.activate();
        };

        map.get_map_layer = function() {
            return map.olmap.baseLayer.type;
        };

        return map;
    };

    engine.new_marker = function(place_info) {
        var marker = {};

        marker.collection = function(collection) {
            /* get or set the current collection for this marker */
            if(arguments.length == 0) {
                return marker._collection;
            }
            marker._collection = collection;
            var map_coord = collection.map().from_wgs84(place_info['lonlat']);
            marker._ol_marker = new OpenLayers.Marker(map_coord,
                                                      place_info['icon']);
            collection._ol_layer.addMarker(marker._ol_marker);
            var img = $('img', marker._ol_marker.icon.imageDiv);
            img.attr('title', place_info['label']);
        };

        return marker;
    };

    engine.new_markers_collection = function(name) {
        var collection = {};
        collection._ol_layer = new OpenLayers.Layer.Markers(name);

        collection.add = function(something) {
            if (typeof something == 'undefined'){
                throw "Undefined collection";
            }
            something.collection(collection);
        };

        collection.empty = function() {
            collection._ol_layer.clearMarkers();
        };

        collection.map = function(map) {
            /* get or set the parent map for this collection */
            if(arguments.length == 0) {
                return collection._map;
            }
            collection._map = map;
            map.olmap.addLayer(collection._ol_layer);
        };

        return collection;
    };

    engine.new_portal_map_marker = function(place, collection) {
        var lonlat = new OpenLayers.LonLat(place.lon, place.lat);
        var i = engine.geotype_icons[place.icon_name];
        if(i['color']) {
            var icon = engine.new_icon(i['url'] + '&size=12', 12, 12, -6, -6);
        }
        else {
            var icon = engine.new_icon(i['url'],
                                       i['width'], i['height'],
                                       i['offset_x'], i['offset_y']);
        }

        var marker = engine.new_marker({
            lonlat: lonlat,
            icon: icon,
            label: place.label
        });

        var _super_collection = marker.collection;
        marker.collection = function (collection) {
            _super_collection(collection);
            if(collection) {
                setup_event_handlers();
            }
        };

        return marker;
        // unused code?

        function setup_event_handlers() {
            marker._ol_marker.events.register("click", null, function() {
                var balloon = map_marker_clicked(place);
                marker._has_balloon = true;
                update_icon();
                balloon.destroy(function() {
                    marker._has_balloon = false;
                    update_icon();
                });
            });

            if(i['color']) {
                marker._ol_marker.events.register("mouseover", null, function() {
                    marker._mouse_over = true;
                    update_icon();
                });

                marker._ol_marker.events.register("mouseout", null, function() {
                    marker._mouse_over = false;
                    update_icon();
                });
            };
        }

        function update_icon() {
            var large = (marker._mouse_over || marker._has_balloon);
            var size = (large ? 16 : 12);
            var url = i['url'] + (large ? '&size=16&halo=on' : '&size=12');
            var offset = new OpenLayers.Pixel(-size/2, -size/2);
            var icon = marker._ol_marker.icon
            icon.offset = offset;
            icon.setSize(new OpenLayers.Size(size, size));
            icon.setUrl(url);
            icon.moveTo(icon.px); // force offset calculation
        }
    };

    engine.portal_map = function(div_id) {
        var map = engine.new_map(div_id);
        map.add_scale_line_control();
        var points = map.points = engine.new_markers_collection('points');
        map.add(points);
        map.zoom_to_extent(engine.config['initial_bounds']);
        if(engine.config['initial_zoom']) {
            map.olmap.zoomTo(engine.config['initial_zoom']);
        }

        map.display_points = function(places) {
            points.empty();
            $.each(places, function(j, place) {
                points.add(engine.new_portal_map_marker(place));
            });
        };

        var current_places = [];
        map.refresh_points = function(event, callback) {
            var bounds = map.get_bounds();
            load_map_points(bounds, function(places) {
                map.display_points(places);
                current_places = places;
                if(typeof callback !== "undefined")
                    callback(places);
            });
        };

        map.refresh_points();
        map.olmap.events.register("moveend", null, map.refresh_points);

        map.get_current_places = function() {
            return current_places;
        };

        map.page_position = function(lat, lon) {
            // TODO deprecate and remove `page_position`
            return map.coord_to_page_xy({'lat': lat, 'lon': lon});
        };

        map.set_center_and_zoom_in = function(lat, lon) {
            var zoom = map.olmap.getZoom();
            map.set_zoom_and_center({'lat': lat, 'lon': lon, 'zoom': zoom+1});
        };

        return map;
    };

    engine.object_index_map = function(div_id, coord) {
        var map = engine.new_map(div_id);
        map.set_zoom_and_center(engine.object_map_position(coord));
        var points = engine.new_markers_collection('points');
        map.add(points);
        var lonlat = new OpenLayers.LonLat(coord.lon, coord.lat);
        points.add(engine.new_marker({lonlat: lonlat, icon: null}));
    };

    engine.object_map_position = function(coord) {
        return {
            lon: coord.lon,
            lat: coord.lat,
            zoom: engine.config['objmap_zoom']
        };
    };

    engine.object_edit_map = function(div_id, coord, callback) {
        var map = engine.new_map(div_id);
        var current_point = engine.new_markers_collection('current_point');
        map.add(current_point);

        if(coord != null) {
            map.set_zoom_and_center(engine.object_map_position(coord));
            show_marker(coord);
        }
        else {
            map.zoom_to_extent(engine.config['initial_bounds']);
        }

        map.add_click_callback(update_location);

        map.marker_at_address = function(address) {
            engine.geocode(address, function(results) {
                var result = results[0];
                var coord = {
                    lat: result['location']['lat'],
                    lon: result['location']['lon']
                };
                map.set_zoom_and_center(engine.object_map_position(coord));
                update_location(coord);
            });
        };

        function show_marker(coord) {
            var lonlat = new OpenLayers.LonLat(coord.lon, coord.lat);
            current_point.empty();
            current_point.add(engine.new_marker({lonlat: lonlat, icon: null}));
        }

        function update_location(coord) {
            show_marker(coord);
            callback(latlon_6digits(coord));
        }

        function decimals_6(n) {
            return Math.round(n*1000000) / 1000000;
        }

        function latlon_6digits(lonlat) {
            return {
                lat: decimals_6(lonlat.lat),
                lon: decimals_6(lonlat.lon)
            };
        }

        return map;
    };

    engine.map_with_points = function(div_id, list_of_places) {
        var map = engine.new_map(div_id);
        var places = engine.new_markers_collection('places');
        map.add(places);

        var bounds = new OpenLayers.Bounds();
        $.each(list_of_places, function(i, place) {
            var lonlat = new OpenLayers.LonLat(place.lon, place.lat);
            places.add(engine.new_marker({lonlat: lonlat, icon: null}));
            bounds.extend(lonlat);
        });

        map.zoom_to_extent(bounds, 0.6);

        return map;
    };

})();
