# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
# Alex Morega, Eau de Web

import re
from BeautifulSoup import BeautifulSoup, Tag

# FIXME: if tags in the source code are uppercase, the parser will not
# recognise them.

big_tags = ['img', 'object', 'embed']
heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
block_level_tags = big_tags + heading_tags + \
                 ['p', 'div', 'ol', 'ul', 'dl', 'table', 'blockquote', 'pre']

class Paragraph(object):
    def __init__(self, content, is_blank, is_heading=False):
        self.content = content
        self.is_blank = is_blank
        self.is_heading = is_heading

def check_blank(content):
    """
    Checks if a node of content contains only whitespace
    """
    if not re.sub(r'&nbsp;|<\s*br\s*/\s*>|\s', '', unicode(content)):
        return True

    if isinstance(content, Tag) and content.name not in big_tags:
        for child in content:
            if not check_blank(child):
                return False
        return True

    return False

def check_heading(content):
    if isinstance(content, Tag):
        if content.name in heading_tags:
            return True
    return False

def parse(content):
    output = []

    soup = BeautifulSoup(content)
    current_paragraph = ''

    def add_paragraph(content):
        output.append(
            Paragraph(unicode(content),
                    check_blank(content),
                    check_heading(content)))

    # iterate over all top-level elements in document
    for current_element in soup:
        # if the element is a block-level tag, it (usually) gets its own paragraph
        if isinstance(current_element, Tag) and \
           current_element.name in block_level_tags:

            # but first, make a paragraph from any plain text above here
            if current_paragraph:
                add_paragraph(current_paragraph)
                current_paragraph = ''

            add_paragraph(current_element)

        else:
            # this is not a tag, so it must be plain text; store it.
            current_paragraph += unicode(current_element)

    # make sure we don't miss text at the end of the document
    if current_paragraph:
        add_paragraph(current_paragraph)

    # merge down all whitespace paragraphs
    i = 0
    while i+1 < len(output):
        if output[i].is_blank:
            output[i+1].content = output[i].content + output[i+1].content
            del output[i]
        else:
            i += 1

    # merge down all heading paragraphs
    i = 0
    while i+1 < len(output):
        if output[i].is_heading:
            output[i+1].content = output[i].content + output[i+1].content
            del output[i]
        else:
            i += 1

    # gather all whitespace from the end of the document; merge it upwards
    while len(output) > 1 and output[-1].is_blank:
        output[-2].content += output[-1].content
        del(output[-1])

    return [paragraph.content for paragraph in output]

