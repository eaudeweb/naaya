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
}, 0); });

