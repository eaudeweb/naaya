(function(){
   function init_userinfo(){
       jQuery(".userinfo_item h3").click(
           function(){
               var h3 = jQuery(this);
               jQuery(".items", this.parentNode).toggle('blind',
                   function(){
                       if(jQuery(this).is(":visible")){
                           h3.removeClass("close").addClass("open");
                       } else h3.removeClass("open").addClass("close");
                   }
                   , 800);
           });
        jQuery(".more_link").click(function(){
           var jthis = jQuery(this);
           jQuery(".more_list_item", this.parentNode).show('blind', {}, 800);
           jthis.hide();
        });
    }
    jQuery(document).ready(function(){
        init_userinfo();
    });
})();
$(document).ready(function(){
  $('.userinfo_item .items').show();
  var ob_types = ['news', 'events', 'resources', 'bestpractice', 'contacts'];
  var no_objects = gettext('No items posted so far');
  var i = 0;
  for (i=0;i<ob_types.length;i++){
    var ob_type = ob_types[i];
    var get_url = "destinet.publisher/get_userinfo?ob=" + ob_type;
    $.ajax({
      url: get_url,
      dataType: 'json',
      async: false,
      success: function(data){
        $('#'+ob_type+'_objects').find('div.items').empty();
        if (data.length > 0){
          $('#'+ob_type+'_objects').find('h3').removeClass('open').addClass('close');
          var counter_message = gettext('most recent items - click to open');
          if (data.length == 1){
            counter_message = gettext('item - click to open')
          }
          $('#'+ob_type+'_objects').find('span.ob_counter').text('('+data.length+' '+counter_message+')');
          var j = 0;
          for (j=0;j<data.length;j++){
            var ob = data[j];
            var item_details = $('<div>').append($('<div>')
              .addClass('date_label').text(ob[2]));
            $(item_details).find('div.date_label')
              .after($('<a>').attr('href', ob[1]).text(ob[0]));
            $('#'+ob_type+'_objects').find('div.items').hide();
            $('#'+ob_type+'_objects').find('div.items').append(item_details);
          }
        }
        else{
          $('#'+ob_type+'_objects > div.items').append($('<p>').text(no_objects));
        }
      }
    });
  }
})
