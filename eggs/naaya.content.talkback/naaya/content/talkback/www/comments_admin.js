$(document).ready(function(){
    if ($('#actions-on-content-list').length){
        $('#actions-on-content-list').dataTable({
            'aaSorting': [[0, "desc"]],
            'sPaginationType': 'full_numbers',
            "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
        });
    }

    $('#plain-text-switch').click(function(){
        var button = $(this);
        $('#log-table-holder').fadeOut('fast', function(){
            $('#log-plain-text-holder').fadeIn('fast');
            button.fadeOut('fast', function(){
                $('#table-switch').fadeIn('fast');
            });
        });
    });

    $('#table-switch').click(function(){
        var button = $(this);
        $('#log-plain-text-holder').fadeOut('fast', function(){
            $('#log-table-holder').fadeIn('fast');
            button.fadeOut('fast', function(){
                $('#plain-text-switch').fadeIn('fast');
            });
        });
    });
});
