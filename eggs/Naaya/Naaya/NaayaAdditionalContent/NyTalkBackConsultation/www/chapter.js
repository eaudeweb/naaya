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

function comment_add(comment_link) {
    $.get(comment_link.href, function(data){
        $('div.talkback-comment_floating_box').remove();

        var top = $(comment_link).attr('offsetTop') - 5;
        var left = $(comment_link).attr('offsetLeft') + 150;

        var comment_box = $('<div class="talkback-comment_floating_box"></div>').css({
            position: 'absolute',
            top: String(top) + 'px',
            left: String(left) + 'px',
            width: '600px',
            height: '400px',
            overflow: 'hidden',
            'background-color': 'white',
            border: '2px solid green',
            padding: '10px'
        });

        function close_comment_box() {
            try { comment_box.remove(); }
            catch(e) {} return false;
        }

        comment_box.append(
            $('<a href="javascript:;">[close]</a>').click(close_comment_box).css({
                'position': 'absolute',
                'top': '0',
                'right': '20px',
                'background-color': 'white',
                'padding': '3px'
            }),
            $('<div></div>').append(
                $('div.talkback-comments_list', data),
                $('div.talkback-add_comment_form', data)
            ).css({
                overflow: 'auto',
                width: '600px',
                height: '400px'
            })
        );

        $('form', comment_box).append(
            $('<input type="submit" value="cancel" />').click(close_comment_box)
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
        $(this).text(n_comments + ' ' + text);
    }).click(function() {
        try { comment_add(this); }
        catch(e) {} return false;
    });
}, 0); });

