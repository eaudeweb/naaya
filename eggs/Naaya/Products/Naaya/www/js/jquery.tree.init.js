function load_js_tree(options){
    var initial_url = options.TREE_GET_URL;
    if(options.TREE_INITIAL_NODE) {
        var separator = (initial_url.indexOf('?') > -1) ? '&' : '?';
        initial_url += separator + "node=" + options.TREE_INITIAL_NODE;
    }
    $(options.TREE_CONTAINER).tree({
        data:{
            type : "json",
            opts : {
                url : initial_url
            }
        },
        callback : {
            onload: function(TREE_OBJ){
                TREE_OBJ.opened_nodes = []
                $.each(TREE_OBJ.container.children().children(), function(i, node){
                    TREE_OBJ.opened_nodes.push(node);
                    TREE_OBJ.open_branch(node); //Opening first level of the site
                })
            },
            onopen: function(NODE, TREE_OBJ){
                if ($.inArray(NODE, TREE_OBJ.opened_nodes) == -1){//Reload
                    TREE_OBJ.opened_nodes.push(NODE);
                    $.getJSON(options.TREE_GET_URL, {'node': $(NODE).attr('title')}, function(data){
                        $.each($(NODE).children().children('li'), function(i, node){
                            TREE_OBJ.remove(node);
                        })
                        $.each(data, function(i, node_data){
                            TREE_OBJ.create(node_data, $(NODE), 'inside');
                        })
                    })
                }
            },
            onselect: function(NODE, TREE_OBJ){
                // If the tree_container has xxx_tree id the target input should have xxx_tree_target class
                var target = $('.' + TREE_OBJ.container.attr('id') + '_target');
                if (target.length){
                    target.val(options.TREE_URL_PREFIX + $(NODE).attr('title'));
                } else {
                    alert('Error: Please set up the target input class');
                }
            }
        },
        types : {
            "default" : {
                draggable: false
            }
        }
   });
}
