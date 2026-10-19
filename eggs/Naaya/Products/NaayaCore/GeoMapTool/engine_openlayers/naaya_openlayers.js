(function() {

    var engine = window.naaya_map_engine = {name: 'openlayers'};

    engine.config = naaya_openlayers_map_api_config;

    engine.base_layers = {
        osm_layer: function(layer_info) {
            return new ol.layer.Tile({source: new ol.source.OSM()});
        },

        esri_imagery_layer: function(layer_info) {
            return new ol.layer.Tile({source: new ol.source.XYZ({
                url: 'https://server.arcgisonline.com/ArcGIS/rest/services/' +
                     'World_Imagery/MapServer/tile/{z}/{y}/{x}',
                maxZoom: 19,
                attributions: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, ' +
                              'Earthstar Geographics, and the GIS User Community'
            })});
        },

        google_layer: function(layer_info) {
            var options = {key: engine.config['google_key'],
                           mapType: layer_info['google_map_type'],
                           scale: 'scaleFactor2x', highDpi: true};
            if(layer_info['google_layer_types']) {
                options.layerTypes = layer_info['google_layer_types'];
            }
            return new ol.layer.Tile({source: new ol.source.Google(options)});
        }
    };

    // Google Map Tiles terms require the Google logo on the map
    function google_logo_control() {
        var element = document.createElement('img');
        element.className = 'naaya-openlayers-google-logo';
        element.src = ('https://developers.google.com/static/maps/' +
                       'documentation/images/google_on_white.png');
        element.alt = 'Google';
        return new ol.control.Control({element: element});
    }

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
        return {url: path, width: width, height: height,
                offset_x: offset_x, offset_y: offset_y};
    };

    engine.default_icon = engine.new_icon(
        engine.config['server_url'] + '/marker_png', 21, 25, -10.5, -25);

    var style_cache = {};
    engine.icon_style = function(icon, z_index) {
        var key = [icon.url, icon.width, icon.height, z_index || 0].join('|');
        if(!style_cache[key]) {
            style_cache[key] = new ol.style.Style({
                zIndex: z_index || 0,
                image: new ol.style.Icon({
                    src: icon.url,
                    width: icon.width,
                    height: icon.height,
                    anchor: [-icon.offset_x / icon.width,
                             -icon.offset_y / icon.height]
                })
            });
        }
        return style_cache[key];
    };

    engine.geocode_nominatim = function(address, callback) {
        var url = engine.config['server_url'] + '/geocode_nominatim';
        $.getJSON(url, {'address': address}, callback);
    };

    engine.geocode = function(address, callback) {
        // Nominatim results converted to the format of GeoMapTool.geocode
        engine.geocode_nominatim(address, function(data) {
            var results = $.map(data, function(r) {
                var bb = $.map(r['boundingbox'], parseFloat);
                return {
                    boundingbox: {bottom: bb[0], top: bb[1],
                                  left: bb[2], right: bb[3]},
                    location: {lat: parseFloat(r['lat']),
                               lon: parseFloat(r['lon'])}
                };
            });
            if(results.length) callback(results);
        });
    };

    engine.address_override = function() {
        // initial_address differs from the one the saved bounding box is for
        function norm(a) { return $.trim(a || '').toLowerCase(); }
        var address = norm(engine.config['initial_address']);
        return address && address != norm(engine.config['saved_address']);
    };

    engine.bounds_btlr = function(box) {
        // WGS84 extent [left, bottom, right, top] from [bottom, top, left, right]
        var b = box[0], t = box[1], l = box[2], r = box[3];
        return [l, b, r, t];
    };

    engine.config['initial_bounds'] = engine.bounds_btlr(
        engine.config['initial_bounding_box']);

    // Zoom only on ctrl/cmd + wheel; plain wheel scrolls the page and shows a hint.
    function setup_ctrl_wheel_zoom(olmap, div_id) {
        var div = $('#' + div_id);
        var is_mac = /Mac/.test(navigator.platform);
        var hint = $('<div class="naaya-openlayers-wheel-hint">')
            .text(is_mac ? 'Use ⌘ + scroll to zoom the map'
                         : 'Use ctrl + scroll to zoom the map')
            .hide().appendTo(div);
        var hint_timer;

        div[0].addEventListener('wheel', function(e) {
            if(e.ctrlKey || e.metaKey) return;
            hint.stop(true, true).fadeIn(150);
            clearTimeout(hint_timer);
            hint_timer = setTimeout(function() { hint.fadeOut(300); }, 1500);
        });

        olmap.addInteraction(new ol.interaction.MouseWheelZoom({
            condition: function(e) {
                return e.originalEvent.ctrlKey || e.originalEvent.metaKey;
            }
        }));
    }

    engine.create_olmap = function(div_id) {
        $('#' + div_id).addClass('naaya-openlayers');
        var layer_info = engine.config['base_layer'];
        var layer_factory = engine.base_layers[layer_info['factory']] ||
                            engine.base_layers.osm_layer;
        var olmap = new ol.Map({
            target: div_id,
            layers: [layer_factory(layer_info)],
            controls: [
                new ol.control.Zoom(),
                new ol.control.Attribution({collapsible: false})
            ],
            interactions: ol.interaction.defaults.defaults({
                mouseWheelZoom: false,
                altShiftDragRotate: false,
                pinchRotate: false
            }),
            view: new ol.View({
                center: [0, 0],
                zoom: 2,
                maxZoom: 19,
                constrainResolution: true,
                enableRotation: false
            })
        });
        if(engine.config['mouse_wheel_zoom']) {
            setup_ctrl_wheel_zoom(olmap, div_id);
        }
        if(layer_info['factory'] == 'google_layer') {
            olmap.addControl(google_logo_control());
        }
        return olmap;
    };

    engine.new_map = function(div_id) {
        var map = {_move_handlers: [], _div_id: div_id};
        map.olmap = engine.create_olmap(div_id);
        map.view = map.olmap.getView();

        map.from_wgs84 = function(point) {
            return ol.proj.fromLonLat([parseFloat(point.lon),
                                       parseFloat(point.lat)]);
        };

        map.to_wgs84 = function(coordinate) {
            var lonlat = ol.proj.toLonLat(coordinate);
            return {lon: lonlat[0], lat: lonlat[1]};
        };

        map.get_size = function() {
            // the size is unknown until the map div has been laid out
            var size = map.olmap.getSize();
            if(size && size[0] && size[1]) return size;
            var div = $('#' + div_id);
            return [div.width() || 256, div.height() || 256];
        };

        map.get_center_and_zoom = function() {
            var lat_lon = map.to_wgs84(map.view.getCenter());
            return {lat_center: lat_lon.lat,
                    lon_center: lat_lon.lon,
                    map_zoom: map.view.getZoom()};
        };

        map.set_zoom_and_center = function(position) {
            if(position.lat == null || position.lon == null) return;
            map.view.setCenter(map.from_wgs84(position));
            if(position.zoom != null && position.zoom !== '') {
                map.view.setZoom(parseInt(position.zoom, 10));
            }
        };

        map.add_click_callback = function(callback) {
            map.olmap.on('singleclick', function(e) {
                callback(map.to_wgs84(e.coordinate));
            });
        };

        map.get_bounds = function() {
            var extent = ol.proj.transformExtent(
                map.view.calculateExtent(map.get_size()),
                'EPSG:3857', 'EPSG:4326');
            var bounds = {
                'lat_min': Math.max(extent[1], -90),
                'lat_max': Math.min(extent[3], 90),
                'lon_min': extent[0],
                'lon_max': extent[2]
            };
            if(extent[2] - extent[0] >= 360) {
                // the whole world is visible
                bounds['lon_min'] = -180;
                bounds['lon_max'] = 180;
            }
            return bounds;
        };

        map.get_resolution = function() {
            // pixels per degree of longitude
            var one_degree = ol.proj.fromLonLat([1, 0])[0];
            return one_degree / map.view.getResolution();
        };

        map.coord_to_page_xy = function(coord) {
            // pixel offset in the map div; picks the world copy nearest the center
            var c = map.from_wgs84(coord);
            var center = map.view.getCenter();
            var res = map.view.getResolution();
            var size = map.get_size();
            var world = ol.proj.get('EPSG:3857').getExtent();
            var world_width = world[2] - world[0];
            var dx = c[0] - center[0];
            dx -= Math.round(dx / world_width) * world_width;
            return {x: dx / res + size[0] / 2,
                    y: (center[1] - c[1]) / res + size[1] / 2};
        };

        map.map_coords = function(x, y) {
            return map.to_wgs84(map.olmap.getCoordinateFromPixel([x, y]));
        };

        map.zoom_to_extent = function(extent, fill_ratio, max_zoom) {
            // `extent` is a WGS84 [left, bottom, right, top] array;
            // `fill_ratio` is how much of the viewport it may fill (default 1).
            if(fill_ratio == null) fill_ratio = 1.0;
            if(max_zoom == null) max_zoom = 14;

            var map_extent = ol.proj.transformExtent(
                extent, 'EPSG:4326', 'EPSG:3857');
            ol.extent.scaleFromCenter(map_extent, 1 / fill_ratio);
            map.view.fit(map_extent, {size: map.get_size(),
                                      maxZoom: max_zoom});
        };

        map.go_to_address = function(address) {
            engine.geocode(address, function(results) {
                var bb = results[0]['boundingbox'];
                map.zoom_to_extent(engine.bounds_btlr(
                    [bb['bottom'], bb['top'], bb['left'], bb['right']]));
            });
        };

        map.add = function(something) {
            something.map(map);
        };

        map.show_mouse_coordinates = function() {
            map.olmap.addControl(new ol.control.MousePosition({
                projection: 'EPSG:4326',
                coordinateFormat: ol.coordinate.createStringXY(5)
            }));
        };

        map.on_move = function(handler) {
            map._move_handlers.push(handler);
        };

        map.olmap.on('moveend', function() {
            var zoom = map.view.getZoom();
            var center = map.to_wgs84(map.view.getCenter());
            $.each(map._move_handlers, function(i, handler) {
                handler(center.lon, center.lat, zoom);
            });
        });

        map.add_scale_line_control = function() {
            map.olmap.addControl(new ol.control.ScaleLine());
        };

        map.get_map_layer = function() {
            return engine.config['base_layer']['id'];
        };

        setup_marker_events(map);

        return map;
    };

    function setup_marker_events(map) {
        // click, hover and tooltip handling for markers that define handlers
        var viewport = map.olmap.getViewport();
        var hovered = null;

        function marker_at(pixel) {
            var found = null;
            map.olmap.forEachFeatureAtPixel(pixel, function(feature) {
                if(feature.get('naaya_marker')) {
                    found = feature.get('naaya_marker');
                    return true;
                }
            }, {hitTolerance: 2});
            return found;
        }

        map.olmap.on('click', function(e) {
            var marker = marker_at(e.pixel);
            if(marker && marker.on_click) marker.on_click();
        });

        map.olmap.on('pointermove', function(e) {
            if(e.dragging) return;
            var marker = marker_at(e.pixel);
            if(marker === hovered) return;
            if(hovered && hovered.on_mouseout) hovered.on_mouseout();
            hovered = marker;
            if(marker && marker.on_mouseover) marker.on_mouseover();
            viewport.title = (marker && marker.label) || '';
            viewport.style.cursor = (marker && marker.on_click) ? 'pointer' : '';
        });

        $(viewport).on('mouseleave', function() {
            if(hovered && hovered.on_mouseout) hovered.on_mouseout();
            hovered = null;
            viewport.title = '';
            viewport.style.cursor = '';
        });
    }

    engine.new_marker = function(place_info) {
        // place_info: {lonlat: {lon, lat}, icon: engine.new_icon(...), label}
        var marker = {label: place_info['label']};
        marker.icon = place_info['icon'] || engine.default_icon;

        marker.set_icon = function(icon, z_index) {
            marker.icon = icon;
            if(marker._feature) {
                marker._feature.setStyle(engine.icon_style(icon, z_index));
            }
        };

        marker.collection = function(collection) {
            /* get or set the current collection for this marker */
            if(arguments.length == 0) {
                return marker._collection;
            }
            marker._collection = collection;
            var map_coord = collection.map().from_wgs84(place_info['lonlat']);
            marker._feature = new ol.Feature({
                geometry: new ol.geom.Point(map_coord),
                naaya_marker: marker
            });
            marker._feature.setStyle(engine.icon_style(marker.icon));
            collection._source.addFeature(marker._feature);
        };

        return marker;
    };

    engine.new_markers_collection = function(name) {
        var collection = {name: name};
        collection._source = new ol.source.Vector();
        collection._ol_layer = new ol.layer.Vector({source: collection._source});

        collection.add = function(something) {
            if (typeof something == 'undefined'){
                throw "Undefined collection";
            }
            something.collection(collection);
        };

        collection.empty = function() {
            collection._source.clear();
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

    engine.new_portal_map_marker = function(place) {
        var i = engine.geotype_icons[place.icon_name];
        var icon;
        if(i['color']) {
            icon = engine.new_icon(i['url'] + '&size=12', 12, 12, -6, -6);
        }
        else {
            icon = engine.new_icon(i['url'], i['width'], i['height'],
                                   i['offset_x'], i['offset_y']);
        }

        var marker = engine.new_marker({
            lonlat: {lon: place.lon, lat: place.lat},
            icon: icon,
            label: place.label
        });

        marker.on_click = function() {
            if(typeof map_marker_clicked !== 'function') return;
            var balloon = map_marker_clicked(place);
            if(!balloon) return;  // cluster click zoomed in instead
            marker._has_balloon = true;
            update_icon();
            balloon.destroy(function() {
                marker._has_balloon = false;
                update_icon();
            });
        };

        if(i['color']) {
            marker.on_mouseover = function() {
                marker._mouse_over = true;
                update_icon();
            };
            marker.on_mouseout = function() {
                marker._mouse_over = false;
                update_icon();
            };
        }

        function update_icon() {
            if(!i['color']) return;
            var large = (marker._mouse_over || marker._has_balloon);
            var size = (large ? 16 : 12);
            var url = i['url'] + (large ? '&size=16&halo=on' : '&size=12');
            marker.set_icon(engine.new_icon(url, size, size, -size/2, -size/2),
                            large ? 1 : 0);
        }

        return marker;
    };

    engine.portal_map = function(div_id) {
        var map = engine.new_map(div_id);
        map.add_scale_line_control();
        var points = map.points = engine.new_markers_collection('points');
        map.add(points);

        var config = engine.config;
        if(config['lat_center'] && config['lon_center']) {
            // position passed in the URL, e.g. by the "embed map" link
            map.set_zoom_and_center({
                lat: config['lat_center'],
                lon: config['lon_center'],
                zoom: config['map_zoom'] || config['initial_zoom']
            });
        }
        else {
            map.zoom_to_extent(config['initial_bounds']);
            var zoom = config['map_zoom'] || config['initial_zoom'];
            if(zoom) {
                map.view.setZoom(parseInt(zoom, 10));
            }
            if(engine.address_override()) {
                // ?address= in the URL, e.g. in embedded maps
                engine.geocode(config['initial_address'], function(results) {
                    var bb = results[0]['boundingbox'];
                    map.zoom_to_extent(engine.bounds_btlr(
                        [bb['bottom'], bb['top'], bb['left'], bb['right']]));
                    if(config['map_zoom']) {
                        map.view.setZoom(parseInt(config['map_zoom'], 10));
                    }
                });
            }
        }

        map.display_points = function(places) {
            points.empty();
            $.each(places, function(j, place) {
                // skip points whose geo type has no symbol
                if(!engine.geotype_icons[place.icon_name]) return;
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
        map.olmap.on('moveend', function() { map.refresh_points(); });

        map.get_current_places = function() {
            return current_places;
        };

        map.page_position = function(lat, lon) {
            // TODO deprecate and remove `page_position`
            return map.coord_to_page_xy({'lat': lat, 'lon': lon});
        };

        map.set_center_and_zoom_in = function(lat, lon) {
            var zoom = map.view.getZoom();
            map.set_zoom_and_center({'lat': lat, 'lon': lon, 'zoom': zoom+1});
        };

        map.zoom_to_cluster = function(cluster) {
            // Fit the cluster's points, at least one level in; false at max zoom
            var zoom = map.view.getZoom();
            var max_zoom = map.view.getMaxZoom();
            if(zoom >= max_zoom) return false;
            var b = cluster.bounds;
            if(!b) {
                map.set_center_and_zoom_in(cluster.lat, cluster.lon);
                return true;
            }
            var extent = ol.proj.transformExtent(
                [b[2], b[0], b[3], b[1]], 'EPSG:4326', 'EPSG:3857');
            var resolution = map.view.getResolutionForExtent(
                ol.extent.buffer(extent, 1), map.get_size());
            var fit_zoom = Math.floor(map.view.getZoomForResolution(resolution / 0.8));
            map.view.animate({
                center: ol.extent.getCenter(extent),
                zoom: Math.min(Math.max(fit_zoom, zoom + 1), max_zoom),
                duration: 300
            });
            return true;
        };

        return map;
    };

    engine.object_index_map = function(div_id, coord) {
        var map = engine.new_map(div_id);
        map.set_zoom_and_center(engine.object_map_position(coord));
        var points = engine.new_markers_collection('points');
        map.add(points);
        points.add(engine.new_marker({lonlat: coord, icon: null}));
        return map;
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
            current_point.empty();
            current_point.add(engine.new_marker({lonlat: coord, icon: null}));
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

        var bounds = ol.extent.createEmpty();
        $.each(list_of_places, function(i, place) {
            var lonlat = {lon: parseFloat(place.lon), lat: parseFloat(place.lat)};
            places.add(engine.new_marker({lonlat: lonlat, icon: null}));
            ol.extent.extendCoordinate(bounds, [lonlat.lon, lonlat.lat]);
        });

        if(ol.extent.isEmpty(bounds)) {
            map.zoom_to_extent(engine.config['initial_bounds']);
        }
        else {
            map.zoom_to_extent(bounds, 0.6);
        }

        return map;
    };

})();
