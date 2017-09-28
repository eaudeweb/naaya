(function (){
    jQuery(document).ready(function(){
        jQuery("select#ig_selection").change(function(){
            var jselect = jQuery(this);
            if(jselect.val() != '-'){
                jQuery.post('/zexpcopy_tree_ajax',
                            {
                                'ig': jselect.val()
                            },
                            function(returned){
                                jQuery("#treehere").html(returned);
                                load_js_tree();
                            });
            }
        });
    });
})();