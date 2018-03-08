(function(d, s, id) {
var js, fjs = d.getElementsByTagName(s)[0];
if (d.getElementById(id)) return;
js = d.createElement(s);
js.id = id;
js.src = "//connect.facebook.net/en_GB/all.js#xfbml=1";
fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

$(document).ready(function() {
var plus_url = 'misc_/Naaya/plus.gif';
var minus_url = 'misc_/Naaya/minus.gif';
var refreshTimer;
var refreshInterval = 2000;
$('.hidden').hide();
$('.hidden').each(function() {
  if ($(this).attr('id') != 'dialog-delete-confirm') {
    $(this).before('<img class="show_more" src=' + plus_url + ' /> <a class="show_more" href="javascript:void(0)">More<' + '/a>');
  }
});
$('a.show_more').click(function() {
  if ($(this).text() == 'More') {
    $(this).text('Less');
    $(this).prev().attr('src', minus_url);
    $(this).next().slideDown();
  } else {
    $(this).next().slideUp();
    $(this).text('More');
    $(this).prev().attr('src', plus_url);
  }
});
$('img.show_more').click(function() {
  if ($(this).attr('src') == plus_url) {
    $(this).next().text('Less');
    $(this).attr('src', minus_url);
    $(this).next().next().slideDown();
  } else {
    $(this).next().next().slideUp();
    $(this).next().text('More');
    $(this).attr('src', plus_url);
  }
});
if ($('#folderfile_list table tr').length > 0){
  $('#folderfile_list').DataTable({
    'sPaginationType': 'full_numbers',
    "pageLength": 10https://wbox.ro/,
    "lengthMenu": [ [10, 15, 25, 50, 100, -1], [10, 15, 25, 50, 100, "All"] ]
  });
}

$('#compas_topics').click(function(event) {
  event.preventDefault();
});

$('.select2').select2()

//map configuration
$('#geo_query').select2({
  allowClear: true,
  placeholder: 'Enter keyword',
  tags: true,
  createTag: function (params) {
    return {
      id: params.term,
      text: params.term,
      newOption: true
    }
  },
  templateResult: function (data) {
    var $result = $("<span />");

    $result.text(data.text);

    return $result;
  }
});

$('#certificate_services').select2({placeholder: 'All'})
$('#certificate_services').change(function(){
  if ($(this).val() !== null && $(this).val().indexOf("") !== -1){
    $(this).val("").trigger('change');
  }
  refreshMap();
});

$('.map-refresh').change(function(){
  refreshMap();
});

function refreshMap(){
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(startMapRefresh, refreshInterval);
}

function formatState (state) {
  if (!state.id) {
    return state.text;
  }
  var baseUrl = "/user/pages/images/flags";
  var $state = $(
    '<span><img src="' + baseUrl + '/' + state.element.value.toLowerCase() + '.png" class="img-flag" /> ' + state.text + '<' + '/span>'
  );
  return $state;
};

});
