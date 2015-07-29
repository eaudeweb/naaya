//This is a global object of the tree. It is set durring the tree init.
var tree_obj;
var location_changed = false;

$(document).ready(function(){

function add_link(self){
    var link = $(self.find('a')[0]);
    var pathname = window.location.pathname.substring(1)//remove first slash
    if (pathname.substring(pathname.length-1) != "/")
        pathname += '/';
    var uri = "/" + pathname.replace('index_html', '') + '?insert='  + self.attr('id') + '#glossary_add_div';
    link.after($('<a>')
        .attr('href', uri)
        .html('add')
        .addClass("button add-link")
    );
}

function edit_link(self){
    var link = $(self.find('a')[0]);
    var pathname = window.location.pathname.substring(1)//remove first slash
    var uri = '/' + pathname + '?item=' + self.attr("data-path") + '#glossary_management_div';
    link.after($('<a>')
        .attr('href', uri)
        .html('edit')
        .addClass("button edit-link")
    );
}

function delete_link(self){
    var link = $(self.find('a')[0]);
    var pathname = window.location.pathname.substring(1)//remove first slash
    var uri = '/' + pathname + '/del_element?item=' + self.attr("data-path");
    link.after($('<a>')
        .attr('href', uri)
        .html('delete')
        .addClass("button edit-link")
    );
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
$('.edit-link, .add-link').live('click', function(){
    window.location = $(this).attr('href');
    location_changed = true;
});

$('#jstree_container').tree({
    data:{
        type : "json",
        opts : {
            url : TREE_GET_URL
        }
    },
    callback : {
        onload : function(TREE_OBJ){
            //Set the tree reference
            tree_obj = TREE_OBJ;
            TREE_OBJ.open_all();
            if (CAN_EDIT) {
                //TREE_OBJ.children('li').each(function(){//Folders
                $('#jstree_container').children('ul').children('li').children('ul').children('li').each(function(){//Folders
                    var self = $(this);
                    edit_link(self);
                    add_link(self);
                    self.find('li').each(function(){//Elements
                        delete_link($(this));
                        edit_link($(this));
                    });
                });
            }
        },
        onselect : function(NODE, TREE_OBJ){
            if (!location_changed)
                window.location = $(NODE).find('a').attr('href');
        },
        beforemove : function(NODE, REF_NODE, TYPE, TREE_OBJ){
            //Before moving check if it's the same parent
            var node_id = TREE_OBJ.get_node(NODE).attr('id');
            var parent_id = TREE_OBJ.parent(NODE).attr('id');
            var parent_el = TREE_OBJ.parent(REF_NODE);
            if (parent_el === -1) { //This happens for the root
                return false;
            }

            var new_parent_id = parent_el.attr('id');
            if (new_parent_id !== parent_id){
                return false;
            }
            return true;
        }
    },
    ui : {
        theme_name : "classic"
    },
    types : {
        "default" : {
            max_depth : 2
        },
        "root" : {
            valid_children : ["tree"],
            renameable : false,
            deletable: false,
            draggable: false,
            icon : {
                image: "misc_/NaayaGlossary/glossary.gif"
            }
        },
        "tree" : {
            valid_children : ["node"],
            renameable: false,
            draggable: CAN_EDIT,
            deleteable: CAN_EDIT,
            icon : {
                image: "misc_/NaayaGlossary/folder.gif"
            }
        },
        "node" : {
            renameable : false,
            draggable: CAN_EDIT,
            deleteable: CAN_EDIT,
            icon : {
                image: "misc_/NaayaGlossary/element.gif"
            }
        }
    }
});

//Save the order of elements/folders in the glossary
$('#save_order').click(function(e){
    e.preventDefault();
    $.post($(this).attr('href'), {'data': JSON.stringify(tree_obj.get())},
    function(response){
        if (response.search('ERROR') !== -1){
            alert(response);
        } else {
            //Do somthing to confirm that the save of the order was sucessful.
            //currently refresh the page
            window.location = window.location;
        }
    });
});
//Event handlers for buttons
$('.expand-tree').click(function(e){
    e.preventDefault();
    tree_obj.open_all();
});

$('.collapse-tree').click(function(e){
    e.preventDefault();
    tree_obj.close_all();
});
});
