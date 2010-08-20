function setup_map_events() {
    the_map.AttachEvent("onclick", function(evt) {
        if (evt.elementID) {
            var shape = the_map.GetShapeByID(evt.elementID);
            var point = shape.GetIconAnchor();
            var pixel = the_map.LatLongToPixel(point);
            onclick_onpoint(point.Latitude, point.Longitude, shape.__id__);
        } else if (evt.ctrlKey) {
            var pixel = new VEPixel(evt.mapX, evt.mapY);
            var point = the_map.PixelToLatLong(pixel);
            onctrlclick_onempty(point.Latitude, point.Longitude);
        }
    });
    the_map.AttachEvent("onmouseover", function(evt) {
        if (evt.elementID) {
            var shape = the_map.GetShapeByID(evt.elementID);
            var point = shape.GetIconAnchor();
            var pixel = the_map.LatLongToPixel(point);
            onmouseoverpoint(point.Latitude, point.Longitude, shape.__id__);
        }
    });
    the_map.AttachEvent("onmouseout", function(evt) {
        if (evt.elementID) {
            var shape = the_map.GetShapeByID(evt.elementID);
            var point = shape.GetIconAnchor();
            var pixel = the_map.LatLongToPixel(point);
            onmouseoutpoint(point.Latitude, point.Longitude, shape.__id__);
        }
    });
}

function page_coords(lat, lon) {
    var point = new VELatLong(lat, lon);
    return the_map.LatLongToPixel(point);
}

