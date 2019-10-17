(function (){
    jQuery(document).ready(function(){
        function update_tree(){
            var jselect = $('select#ig_selection');
            if(jselect.val() != '-'){
                jQuery.post('/zexpcopy_tree_ajax',
                            {
                                'ig': jselect.val()
                            },
                            function(returned){
                                $('#treehere').show();
                                jQuery("#treehere").html(returned);
                                load_js_tree({
                                    TREE_URL_PREFIX:'',
                                    TREE_GET_URL:'${tree_get_url}',
                                    TREE_INITIAL_NODE:'',
                                    TREE_CONTAINER:''
                                });
                            });
            }
        }
        jQuery("select#ig_selection").change(function(){
            update_tree();
        });
        $('#export_complete_ig').click(function(){
            if($('#export_complete_ig:checked').length == 1){
                $('#location').val('');
                $('#treehere').hide();
            } else {
                update_tree();
            };
        });
        $('#import_complete_ig').click(function(){
            if($('#import_complete_ig:checked').length == 1){
                $('#location').val('');
                $('#ig_selection').val('-').attr('disabled', 'disabled').hide();
                $('#treehere').hide();
            } else {
                $('#ig_selection').removeAttr('disabled').show();
                update_tree();
            };
        });
    });
})();
