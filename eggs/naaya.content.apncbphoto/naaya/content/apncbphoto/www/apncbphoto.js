$(document).ready(function(){
  $('.datatable').dataTable({
      'oLanguage':{
        'sSearch': 'Filter results '
      },
      'aaSorting': [[0, "desc"]],
      'sPaginationType': 'full_numbers',
      "aLengthMenu": [[10, 25, 50, -1],
                      [10, 25, 50, "All"]]
  });
   $(".fancybox").fancybox({
      type: 'image',
      arrows: false,
  });
});

function delete_document(delete_link){
  $("#dialog-delete-confirm" ).dialog({
    open: function() {
      $(this).siblings(".ui-dialog-buttonpane").find("button:eq(1)").focus();
    },
    resizable: false,
    height: 200,
    width: 500,
    modal: true,
    draggable: false,
    buttons: {
      "Delete items": function() {
        window.location = delete_link;
      },
      "Cancel": function() {
        $( this ).dialog( "close" );
      }
    }
  });
};

