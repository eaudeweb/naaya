// The contents of this file are subject to the Mozilla Public
// License Version 1.1 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of
// the License at http://www.mozilla.org/MPL/

// Software distributed under the License is distributed on an "AS
// IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
// implied. See the License for the specific language governing
// rights and limitations under the License.

// The Initial Owner of the Original Code is European Environment
// Agency (EEA).  Portions created by Eau de Web are
// Copyright (C) European Environment Agency.  All
// Rights Reserved.

// Authors:

// Alex Morega, Eau de Web

(function() {

var comments_visible = true;

function comment_add(comment_link) {
    // if this comment box is already open, don't re-open it
    if($('div.talkback-comment_floating_box', $(comment_link).parent()).length)
        return;

    $('div.talkback-comment_floating_box').remove();

    var top = $(comment_link).attr('offsetTop') - 5;
    var left = $(comment_link).attr('offsetLeft') + 150;

    var comment_box = $('<div class="talkback-comment_floating_box"></div>').css({
        top: String(top) + 'px',
        left: String(left) + 'px'
    });

    function close_comment_box() {
        try { comment_box.remove(); }
        catch(e) {} return false;
    }

    var comment_form_box = $('<div>Loading...</div>');
    var comment_list = $('fieldset', $(comment_link).parent()).clone().css({display: 'block'});

    comment_box.append(
        $('<a href="javascript:;" class="talkback-comment_close_box">[close]</a>').click(close_comment_box),
        $('<div class="talkback-js_comment_window"></div>').append(
            comment_form_box,
            $('<div class="comments_list">').append(
                $('<h2>Previous comments</h2>').css({display: (comment_list.length ? 'block' : 'none')}),
                comment_list
            ).css({display: (comments_visible ? 'none' : 'block')})
        )
    );

    comment_box.insertAfter(comment_link);

    $.get(comment_link.href, function(data){
        comment_form_box.empty().append(
            $('p.talkback-cannot_comment', data),
            $('div.talkback-add_comment_form', data)
        );
        $('form', comment_form_box).append(
            $('<input type="submit" value="Cancel" />').click(close_comment_box)
        ).attr('action', $(comment_link).attr('href') + '/' + $('form', comment_box).attr('action'));
    });
}

function comment_buttons_display(comments_visible) {
    $('a.talkback-show_comments').css({display: (comments_visible ? 'none' : 'block')});
    $('a.talkback-hide_comments').css({display: (comments_visible ? 'block' : 'none')});
}

function show_comments() {
    comment_buttons_display(true);
    $('div.talkback-comments_list > fieldset').show();
    $('div.talkback-js_comment_window > div.comments_list').css({display: 'none'});
    $('a.talkback-add_comment').text('Add comment');
    comments_visible = true;
}

function hide_comments() {
    comment_buttons_display(false);
    $('div.talkback-comments_list > fieldset').hide();
    $('div.talkback-js_comment_window > div.comments_list').css({display: 'block'});
    $('a.talkback-add_comment').text('Comments');
    comments_visible = false;
}

var button_bg = 'none'

$(document).ready(function() {setTimeout(function(){
    // if the comments are already hidden, don't apply any javascript
    if (String(window.location.search).search("comments=off") > 0)
        return;

    hide_comments();

    if(window.location.hash) {
        window.location.hash = window.location.hash;
    }

    $('a.talkback-show_comments').click(function() { try { show_comments(); } catch(e) {}; return false; });
    $('a.talkback-hide_comments').click(function() { try { hide_comments(); } catch(e) {}; return false; });

    $('a.talkback-add_comment').each(function() {
        var n_comments = String($('fieldset', $(this).parent()).length);
        var text = (n_comments == 1 ? 'comment' : 'comments');
        //$(this).text(n_comments + ' ' + text);
    }).click(function() {
        try { comment_add(this); }
        catch(e) {} return false;
    });

    $('a.talkback-add_comment').mouseover(function() {
        var elem_url = this.href.split('/');
        var elem_paragraph = $("#" + elem_url[elem_url.length - 1]);
        // save previous background value
        button_bg = $(this).css("background");
        // highlight background
        elem_paragraph.css({"background": "#eee"});
        $(this).css({"background": "#eee"});
    });

    $('a.talkback-add_comment').mouseout(function() {
        var elem_url = this.href.split('/');
        var elem_paragraph = $("#" + elem_url[elem_url.length - 1]);
        elem_paragraph.css({"background": 'transparent'});
        $(this).css({"background": button_bg});
    });
}, 0); });

})();

