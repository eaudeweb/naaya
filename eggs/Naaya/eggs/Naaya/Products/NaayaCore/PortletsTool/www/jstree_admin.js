var rename_action = {"action" : "rename"};
var move_action = {"action" : "move"};
var creating_object = false;

function get_node_parent_id(TREE_OBJ, NODE) {
    return {
        "type" : TREE_OBJ.get_type(TREE_OBJ.parent(NODE)),
        "id": TREE_OBJ.parent(NODE).attr('id')
    }
}

function get_node_parent_tree_id(TREE_OBJ, NODE) {
    parent_type = TREE_OBJ.get_type(TREE_OBJ.parent(NODE));
    if (parent_type == 'node') {
        return get_node_parent_id(TREE_OBJ, TREE_OBJ.parent(NODE));
    }
    return {
        "type" : parent_type,
        "id": TREE_OBJ.parent(NODE).attr('id')
    }
}

function get_children(TREE_OBJ, NODE) {
    var all_children = [];
    var node_children = TREE_OBJ.children(NODE);
    node_children.each(function(){
        all_children[all_children.length] = this;
        $(get_children(TREE_OBJ, this)).each(function(){
            all_children[all_children.length] = this;
        });
    });
    return all_children;
}

$(function () {
    $("#jstree_container").tree({
        callback : {
            onload : function(TREE_OBJ){
                TREE_OBJ.open_all();
            },
            oncreate : function(NODE, REF_NODE, TYPE, TREE_OBJ){
                var action = {
                    "action" : "add",
                    "type" : TREE_OBJ.get_type(NODE),
                    "name" : TREE_OBJ.get_text(NODE),
                    "parent" : get_node_parent_id(TREE_OBJ, NODE),
                    "parent_tree" : get_node_parent_tree_id(TREE_OBJ, NODE),
                }
                var created_response = jQuery.ajax({
                    'async' : false,
                    'url' : 'portal_portlets/handle_jstree_actions',
                    'data' : {'data' : JSON.stringify(action)},
                    'success' : function(data){return data},
                    });
                var created_id = created_response.responseText;
                creating_object = true;
                TREE_OBJ.get_node(NODE).attr('id', created_id);
            },
            beforerename : function(NODE, LANG, TREE_OBJ){
                rename_action["type"] = TREE_OBJ.get_type(NODE);
                rename_action["id"] = TREE_OBJ.get_node(NODE).attr('id');
                rename_action["old_name"] = TREE_OBJ.get_text(NODE);
                return true;
            },
            onrename : function(NODE, TREE_OBJ){
                rename_action["new_name"] = TREE_OBJ.get_text(NODE);
                rename_action["parent_tree"] = get_node_parent_tree_id(TREE_OBJ, NODE);
                rename_action['object_creation'] = false;
                var action = rename_action;
                if (creating_object == true) {
                    action['object_creation'] = true;
                    var renamed_response = jQuery.ajax({
                        'async' : false,
                        'url' : 'portal_portlets/handle_jstree_actions',
                        'data' : {'data' : JSON.stringify(action)},
                        'success' : function(data){return data},
                        });
                    var renamed_id = renamed_response.responseText;
                    TREE_OBJ.get_node(NODE).attr('id', renamed_id);
                    TREE_OBJ.refresh();
                }
                else {
                    jQuery.post('portal_portlets/handle_jstree_actions', {"data": JSON.stringify(action)});
                    TREE_OBJ.refresh();
                }
                rename_action = {"action": "rename"};
                creating_object = false;
            },
            beforedelete : function(NODE, TREE_OBJ){
                var node_id = TREE_OBJ.get_node(NODE).attr('id');
                var children = [];
                $(get_children(TREE_OBJ, NODE)).each(function(){
                    children[children.length] = $(this).attr('id');
                    });
                var action = {
                    "action" : "delete",
                    "type" : TREE_OBJ.get_type(NODE),
                    "id" : node_id,
                    "parent" : get_node_parent_id(TREE_OBJ, NODE),
                    "parent_tree" : get_node_parent_tree_id(TREE_OBJ, NODE),
                    "children" : children
                }
                if (confirm('Are you sure you want to delete this node?')){
                    jQuery.post('portal_portlets/handle_jstree_actions', {"data": JSON.stringify(action)});
                    return true;
                }
                else return false;
            },
            beforemove : function(NODE, REF_NODE, TYPE, TREE_OBJ){
                var node_id = TREE_OBJ.get_node(NODE).attr('id');
                var children = [];
                $(get_children(TREE_OBJ, NODE)).each(function(){
                    children[children.length] = $(this).attr('id');
                    });
                move_action["type"] = TREE_OBJ.get_type(NODE);
                move_action["id"] = TREE_OBJ.get_node(NODE).attr('id');
                move_action["old_parent"] = get_node_parent_id(TREE_OBJ, NODE);
                move_action["old_parent_tree"] = get_node_parent_tree_id(TREE_OBJ, NODE);
                move_action["children"] = children;
                return true;
                },
            onmove : function(NODE, REF_NODE, TYPE, TREE_OBJ, RB){
                move_action["new_parent"] = get_node_parent_id(TREE_OBJ, NODE);
                move_action["new_parent_tree"] = get_node_parent_tree_id(TREE_OBJ, NODE);
                move_action["new_prev"] = TREE_OBJ.prev(NODE).attr('id');
                move_action["new_next"] = TREE_OBJ.next(NODE).attr('id');                
                var action = move_action;
                var created_response = jQuery.ajax({
                    'async' : false,
                    'url' : 'portal_portlets/handle_jstree_actions',
                    'data' : {'data' : JSON.stringify(action)},
                    'success' : function(data){return data},
                    });
                var created_id = created_response.responseText
                TREE_OBJ.get_node(NODE).attr('id', created_id)
                move_action = {"action" : "move"};
                TREE_OBJ.refresh();
            }
        },
        rules : {
            valid_children : ["root"],
        },
        types : {
            "default" : {
                max_depth : 3
            },
            "root" : {
                valid_children : ["tree"],
                renameable : false,
                deletable: false,
                draggable: false,
                icon : {
                    image : "/misc_/Naaya/Site.gif"
                }
            },
            "tree" : {
                valid_children : ["node"],
                renameable: "true",
                icon : {
                    image : "/misc_/NaayaCore/RefTree.gif"
                    },
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
        data : { 
            type : "json",
            opts : {
                url : "portal_portlets/get_reftrees_as_json_data"
            }
        },
        ui : {
            theme_name : "classic"
        },
        plugins : { 
            contextmenu : {
                items : {
                    create_tree : {
                        label : "Add List",
                        icon : "create",
                        action : function(NODE, TREE_OBJ){
                            var new_list = TREE_OBJ.create({
                                "data": "New List",
                                "attributes" : {"rel" : "tree"}
                                }, TREE_OBJ.get_node(NODE[0]));
                            TREE_OBJ.rename(new_list);
                        },
                        visible : function (NODE, TREE_OBJ) {
                            if (NODE.attr('rel') != 'root') return -1;
                            if (NODE.length != 1) return 0;
                            return TREE_OBJ.check("creatable", NODE);
                        },
                    },
                    create_node : {
                        label : "Add Item",
                        icon : "create",
                        action : function(NODE, TREE_OBJ){
                            var new_item = TREE_OBJ.create({
                                "data": "New Item",
                                "attributes" : {"rel" : "node"}
                                }, TREE_OBJ.get_node(NODE[0]));
                            TREE_OBJ.rename(new_item);
                        },
                        visible : function(NODE, TREE_OBJ) {
                            if (NODE.attr('rel') == 'root') return -1;
                            var node_parent = TREE_OBJ.parent(NODE);
                            if (TREE_OBJ.get_type(node_parent) == 'node') {
                                return -1;
                            }
                            if (NODE.length != 1) return 0;
                            return TREE_OBJ.check("creatable", NODE);
                        },
                        separator_after : true,
                    },
                    remove_ : {
                        label   : "Delete",
                        icon    : "remove",
                        visible : function (NODE, TREE_OBJ) { 
                            var ok = true; 
                            $.each(NODE, function () { 
                                if(TREE_OBJ.check("deletable", this) == false) {
                                    ok = false; 
                                    return false; 
                                }
                            }); 
                            return ok; 
                        }, 
                        action  : function (NODE, TREE_OBJ) { 
                            $.each(NODE, function () { 
                                TREE_OBJ.remove(this); 
                            }); 
                        } 
                    },
                    rename_ : {
                        label   : "Rename", 
                        icon    : "rename",
                        visible : function (NODE, TREE_OBJ) { 
                            if(NODE.length != 1) return false; 
                            return TREE_OBJ.check("renameable", NODE); 
                        }, 
                        action  : function (NODE, TREE_OBJ) { 
                            TREE_OBJ.rename(NODE); 
                        } 
                    },
                    create : {visible : function(NODE, TREE_OBJ){return -1;}},
                    rename : {visible : function(NODE, TREE_OBJ){return -1;}},
                    remove : {visible : function(NODE, TREE_OBJ){return -1;}},
                }
            }
        }
    });
});
