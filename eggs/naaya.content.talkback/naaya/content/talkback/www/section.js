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

function is_ie9(){
    return (jQuery.browser.msie != undefined  && jQuery.browser.version.slice(0,2) == "9.");
}

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

    var close_button_1 = $('<a href="javascript:;">['+gettext("close")+']</a>');
    var close_button_2 = close_button_1.clone();
    close_button_1.addClass('tb-iframe-close-top').appendTo(comment_box);
    close_button_2.addClass('tb-iframe-close-bottom');
    var close_buttons = $([close_button_1[0], close_button_2[0]]);
    close_buttons.click(function() {
                var tinymce = iframe[0].contentWindow.tinymce;
                if (tinymce === undefined)
                    var mce_text = '';
                else {
                    var mce_text = tinymce.editors[0].getContent();
                    mce_text = mce_text.replace('<p>', '')
                            .replace('</p>', '')
                            .replace(/&nbsp;/g,'');
                }
		if (mce_text.length > 0)
		{
			var r=confirm(gettext('Are you sure you want to close this window without adding your comment?'));
			if (r == true){
				clearInterval(resize_interval);
				comment_box.remove();
				overlay.remove();
			}
		}
		else{
			clearInterval(resize_interval);
			comment_box.remove();
			overlay.remove();
		}
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
            if (is_ie9() && (new_height == height+15)) return;
            iframe.height(new_height + 15);
            height = new_height;
            overlay.height($(document).height());
        }, 500);
    });

    close_button_2.appendTo(comment_box);
}

function get_height(the_window) {
    var the_document = the_window.document;
    if (jQuery.browser.msie != undefined  && !is_ie9()) {
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
            return $(the_document.body).height() + 25;
        } else {
            return scrollHeight + 25;
        }
    } else {
        // handle "good" browsers
        return $('html', the_document).height();
    }
}

});
