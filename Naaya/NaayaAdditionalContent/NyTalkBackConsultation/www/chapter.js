function comment_add(comment_link) {
    $.get(comment_link.href, function(data){
        $('div.talkback-comment_floating_box').remove();

        var top = $(comment_link).attr('offsetTop') - 50;
        var left = $(comment_link).attr('offsetLeft') + 200;

        var comment_box = $('<div class="talkback-comment_floating_box"></div>').css({
            position: 'absolute',
            top: top,
            left: left,
            'background-color': 'white',
            border: '2px solid green',
            padding: '10px'
        }).append($('div.talkback-add_comment_form', data));
        $('form', comment_box).append(
            $('<input type="submit" value="cancel" />').click(function() {
                try { comment_box.remove(); }
                catch(e) {} return false;
            })
        ).attr('action', $(comment_link).attr('href') + '/' + $('form', comment_box).attr('action'));
        comment_box.insertAfter(comment_link);
    });
}

function comment_buttons_display(comments_visible) {
    $('a.talkback-show_comments').css({display: (comments_visible ? 'none' : 'block')});
    $('a.talkback-hide_comments').css({display: (comments_visible ? 'block' : 'none')});
}

function show_comments() {
    comment_buttons_display(true);
    $('div.talkback-chapter fieldset').css({display: 'block'});
}

function hide_comments() {
    comment_buttons_display(false);
    $('div.talkback-chapter fieldset').css({display: 'none'});
}

$(document).ready(function() {setTimeout(function(){
    hide_comments();
    
    $('a.talkback-show_comments').click(show_comments);
    $('a.talkback-hide_comments').click(hide_comments);
    
    $('div.talkback-show_hide_comments').css({display: 'block'});

    $('a.talkback-add_comment').each(function() {
        var n_comments = String($('fieldset', $(this).parent()).length);
        var text = (n_comments == 1 ? 'comment' : 'comments');
        $(this).text(n_comments + ' ' + text);
    }).click(function() {
        try { comment_add(this); }
        catch(e) {} return false;
    });
}, 0); });

