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

