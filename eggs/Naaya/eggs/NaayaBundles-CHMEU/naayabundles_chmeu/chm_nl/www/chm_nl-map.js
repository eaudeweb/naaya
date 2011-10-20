(function() {

var engine = naaya_map_engine;

$.extend(engine, {
    cloudmade_api_key: "7a04ece959114c64961e522f5ab7ac7c",
    cloudmade_style_name: "CloudMade - Pale Dawn",
    cloudmade_style_id: "1714",
    cloudmade_attribution: (
        "Data &copy; <a href='http://openstreetmap.org/'>OpenStreetMap</a>. " +
        "Rendering &copy; <a href='http://cloudmade.com'>CloudMade</a>.")
});


// center on the Netherlands
engine.config['initial_bounds'] = engine.bounds_btlr([50.7, 53.7, 3, 7.3]);

var default_create_olmap = engine.create_olmap;
engine.create_olmap = function(div_id) {

    var olmap = default_create_olmap(div_id);
    olmap.removeLayer(olmap.baseLayer);

    var name = engine.cloudmade_style_name;
    var url = (
        'http://a.tile.cloudmade.com/' +
        engine.cloudmade_api_key + '/' + engine.cloudmade_style_id +
        '/256/${z}/${x}/${y}.png');

    olmap.addLayer(new OpenLayers.Layer.XYZ(name, url, {
        attribution: engine.cloudmade_attribution,
        sphericalMercator: true,
        wrapDateLine: true
    }));

    return olmap;
};


})();
