$(function () {
    $("#" + tree_target).after('<input type="hidden" name="'+prop_name+'" id="'+prop_id+'" value="'+prop_current_value+'"');
    $("input#" + prop_id).after('<div class="cleaner"/>');
    var tree_data_json = undefined;
    $.ajax({
       type: "GET",
       async: false,
       url: data_url,
       dataType: "json",
       success : function(data) {
        tree_data_json = data;
        },
     });

    var selected_nodes = [];
    $(tree_data_json).each(function(){
        if (this['attributes']['id'] == $('#' + value_target).attr('value')) {
            selected_nodes[selected_nodes.length] = this['attributes']['id'];
        }
        $(this['children']).each(function(){
                if (this['attributes'] != null && this['attributes']['id'] == $('#' + value_target).attr('value')) {
                    selected_nodes[selected_nodes.length] = this['attributes']['id'];
                }
            })
        })

    $("#" + tree_target).tree({
        selected : selected_nodes,
        data : {
            type : "json",
            opts : {
                static : tree_data_json,
            },
        },
        types : {
            "default" :{
                clickable : true,
                renameable : false,
                deletable : false,
                creatable : false,
                draggable : false,
            },
            "node" : {
                valid_children : ["node"],
                renameable : "true",
                max_depth : 2,
                icon : {
                    image : "/misc_/NaayaCore/RefTreeNode.gif"
                }
            }
        },
        callback : {
            onload : function(TREE_OBJ){
                TREE_OBJ.open_all();
            },
            onselect : function(NODE, TREE_OBJ){
                var node_id = TREE_OBJ.get_node(NODE).attr('id');
                $('#' + value_target).attr('value', node_id);
            },
            ondblclk : function(NODE, TREE_OBJ){
                TREE_OBJ.deselect_branch(NODE);
                $('#' + value_target).attr('value', '');
            }
        },
    })
})