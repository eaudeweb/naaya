/**
 * The mainsections navigation
 * It can be persistent via jquery.cookie.js (possibly localStorage)
 *
*/
var expand_image;
var collapse_image;

$(document).ready(function(){
    expand_image = $('<img>').attr('src', img_expand).addClass('expand-toggle');
    collapse_image = $('<img>').attr('src', img_collapse).addClass('expand-toggle');

    //Loading navigation from cookie
    load_navigation();

    //Open up .active link (.expand all .expandable parents)
    $('.active').parents('.expandable').each(function(){
        $(this).addClass('expanded');
    });
    //Expand .mainsection_title as well
    $('.active').parents('.left_portlet').find('.mainsection_title:has(.expandable)').addClass('expanded')

    //Attaching toggle images to mainsections
    $('.mainsection_title:has(.expandable)').each(function(){
        if (is_expanded($(this))){
            $(this).append(collapse_image.clone().addClass('mainsection-toggle'));
        }else{
            $(this).append(expand_image.clone().addClass('mainsection-toggle'));
            $(this).parent().siblings().hide();
        }
    });

    //Attaching toggles to folders within
    $('.mainsection_item:has(.expandable)').each(function(){
        if($(this).find('.mainsection_content').length){
            if (is_expanded($(this))){
                collapse_image.addClass('folder-toggle').clone().insertAfter($(this).find('a:first'));
            }else{
                expand_image.addClass('folder-toggle').clone().insertAfter($(this).find('a:first'));
                $(this).find('.mainsection_content:first').hide();
            }
        }
    });

    //Attach event to toggle image and show/hide elements in the list
    $('.expand-toggle').live('click', function(){
        if($(this).hasClass('mainsection-toggle')){
            toggle_image($(this), function(obj){
                obj.parent().parent().siblings().hide();
            }, function(obj){
                obj.parent().parent().siblings().show();
            });
        }else if ($(this).hasClass('folder-toggle')){
            toggle_image($(this), function(obj){
                // only hide sublist, all siblings contain `a` and `ul`
                obj.siblings("ul").hide();
            }, function(obj){
                obj.siblings().show();
            });
        }
        //Save current state to cookie if allowed
        save_navigation();
    });
});

/**
 * Checks whenever the section/folder is exapended.
 * Expects and jquery object as argument.
 *
 * returns true/false
*/
function is_expanded(obj){
    return obj.hasClass('expanded');
}

/**
 * Toggle image function, used in both mainsection and folder section
 * Requires the toggle jquery object that executes the event
 * if case callback and else case callback
 *
*/
function toggle_image(obj, if_callback, else_callback){
    if (is_expanded(obj.parent())){
        obj.parent().removeClass('expanded');
        obj.siblings().removeClass('expanded');
        if_callback(obj)
        obj.attr('src', img_expand);
    }else{
        obj.parent().addClass('expanded');
        obj.siblings().addClass('expanded');
        else_callback(obj)
        obj.attr('src', img_collapse);
    }
}

/**
 * Save navigation state.
 * If jquery.cookie is enabled and persistent navigation is allowed.
*/
function save_navigation(){
    if (!maintopics_settings['persistent']) return;
    if ($.cookie){
        data = {}
        $('li.expandable, div.expandable').each(function(){
            if($(this).hasClass('expanded')){
                data[$(this).attr('id')] = 1;
            }else{
                data[$(this).attr('id')] = 0;
            }
        });
        $.cookie('navigation', JSON.stringify(data), { expires: 7, path: '/' });
    }
}

/**
 * Loads the current navigation (adding/removing classes) from a previously
 * save state
*/
function load_navigation(){
    if (!maintopics_settings['persistent']) return;
    if ($.cookie && $.cookie('navigation')){
        data_str = $.cookie('navigation');
        try{
            data = JSON.parse(data_str);
            $.each(data, function(id, expanded){
                var is_expanded = parseInt(expanded);
                if(is_expanded){
                    $('#' + id).addClass('expanded');
                }else{
                    $('#' + id).removeClass('expanded');
                }
            });
        }catch(e){}
    }
}
