if(M.after_map_load == null) {
M.config['country_code'] = {};
$.each(response['country_name'], function(code, names) {
  var name = names[M.config['language']];
  M.config['country_code'][name] = code;
});

M.config['region_code'] = {};
$.each(response['region_name'], function(code, names) {
  var name = names[M.config['language']];
  M.config['region_code'][name] = code;
});

M.config['country_name_en'] = values_for_language(response['country_name'], 'en');
M.config['region_name_en'] = values_for_language(response['region_name'], 'en');

var slug = function(name) {
  return name.replace(/ /g, "-");
}

M.document_url = function(country_name, theme_name) {
  var code = M.config['country_code'][country_name];
  var country_name_en = M.config['country_name_en'][code];
  return M.config['report_documents_url'] + '/' +
      slug(country_name_en) + '-' + slug(theme_name);

};

M.region_info_url = function(region_name) {
  var code = M.config['region_code'][region_name];
  if(code == 'eea' || code == 'western-balkans') {
    setTimeout(function() {
      $('div#aoa-search-map a.link-region-profile').remove();
    }, 1);
  }
  var region_name_en = M.config['region_name_en'][code];
  return M.config['report_documents_url'] + '/' + slug(region_name_en) + '-info';
};

M.patched = 1;
}
