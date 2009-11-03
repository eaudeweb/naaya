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

$(function() {

if($('ul.tb-comments-tree').length > 0)
    var inline_comments = true;
else
    var inline_comments = false;

$('a.talkback-add_comment').each(function() {
    var $paragraph = $(this).prev('div.talkback-paragraph');
    $(this).mouseover(function() {$paragraph.css({background: '#eee'});});
    $(this).mouseout(function() {$paragraph.css({background: ''});});
    $(this).click(comment_add);
});

function comment_add(evt) {
    evt.preventDefault();
    var $link = $(this);

    // if this comment box is already open, don't re-open it
    if($('div.talkback-comment_floating_box', $link.parent()).length)
        return;

    $('div.talkback-comment_floating_box').remove();

    var overlay = $('<div class="tb-modal-overlay" />').appendTo('body');

    var link_position = $link.position();
    var comment_box = $('<div ></div>').insertAfter($link)
        .addClass("talkback-comment_floating_box").css({
            top: (link_position.top + 20) + 'px',
            left: '130px'
        });

    var close_button_1 = $('<a href="javascript:;">[close]</a>');
    var close_button_2 = close_button_1.clone();
    close_button_1.addClass('tb-iframe-close-top').appendTo(comment_box);
    close_button_2.addClass('tb-iframe-close-bottom');
    var close_buttons = $([close_button_1[0], close_button_2[0]]);
    close_buttons.click(function() {
        clearInterval(resize_interval);
        comment_box.remove();
        overlay.remove();
    });

    var resize_interval;
    var iframe = $('<iframe>').appendTo(comment_box);
    iframe.attr('src', $link.attr('href') + "/embedded_html" +
                       (inline_comments ? '?prev_comments=off' : ''));
    iframe.load(function(){
        clearInterval(resize_interval);
        if(! inline_comments) {
            var comment_count_span = $('span.talkback-comment_count',
                                       this.contentDocument);
            if(comment_count_span.length) {
                $link.children('span.talkback-comment_count').html(
                        comment_count_span.html());
            }
        }
        else {
            var infomsg = $('div.message.information',
                            this.contentDocument
                          ).text()
            if(infomsg.search('Comment submitted successfully') > -1) {
                window.location.reload();
                return;
            }
        }

        var height = 0;
        resize_interval = setInterval(function() {
            var new_height = get_height(iframe[0].contentWindow);
            if(new_height == height) return;
            iframe.height(new_height + 15);
            height = new_height;
            overlay.height($(document).height());
        }, 500);
    });

    close_button_2.appendTo(comment_box);
}

function get_height(the_window) {
    var the_document = the_window.document;
    if ($.browser.msie) {
        // IE6 and IE7 are broken. Fix works with IE8 too.
        var scrollHeight = Math.max(
            the_document.documentElement.scrollHeight,
            the_document.body.scrollHeight
        );
        var offsetHeight = Math.max(
            the_document.documentElement.offsetHeight,
            the_document.body.offsetHeight
        );

        if (scrollHeight < offsetHeight) {
            return $(the_document.body).height();
        } else {
            return scrollHeight;
        }
    } else {
        // handle "good" browsers
        return $('html', the_document).height();
    }
}

});
