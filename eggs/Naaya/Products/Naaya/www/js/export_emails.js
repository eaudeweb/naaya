function selectAllCount(name) {
    var selector = $('.datatable td.checkbox input[@name="'+name+'"][type="checkbox"]')
    selector.attr('checked', $('.select-all').attr('checked') || false);
    return selector.length;
}

$(document).ready(function(){
    if ($('#emails-list').length){
        // change checked status of 'select-all' checkboxes to the status of the one we clicked on
        $('input.select-all').click(function(e) {
            $('.select-all[type=checkbox]').attr('checked', e.target.checked)
            var count = selectAllCount("id");
            if (e.target.checked) {
                $('#selection-text').html(function (i) {
                    return "Selected all <"+"strong>displayed<"+"/strong> items. Choose 'All' from the drop down to display and select all." ;
                });
            } else {
                $('#selection-text').text(function (i) { return "" });
            }
        });
        // deselect all select-all checkboxes if any of the regular ones goes unselected
        $('input[name="id"]').click(function(e) {
            if (e.target.checked === false) {
                $('.select-all[type=checkbox]').attr('checked', false)
                $('#selection-text').text(function (i) { return "" });
            }
        });
    }
})

