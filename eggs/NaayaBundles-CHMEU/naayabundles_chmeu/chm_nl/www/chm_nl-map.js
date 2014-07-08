(function() {
    var engine = naaya_map_engine;
    // center on the Netherlands
    if (engine.name === 'openlayers') {
        engine.config['initial_bounds'] = engine.bounds_btlr([50.7, 53.7, 3, 7.3]);
    }
})();
