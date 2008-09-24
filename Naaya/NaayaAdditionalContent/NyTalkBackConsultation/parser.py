import re
from BeautifulSoup import BeautifulSoup, Tag

# FIXME: if tags in the source code are uppercase, the parser will not
# recognise them.

big_tags = ['img', 'object', 'embed']
heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
block_level_tags = big_tags + heading_tags + \
                 ['p', 'div', 'ol', 'ul', 'dl', 'table', 'blockquote', 'pre']

class Section(object):
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
    current_section = ''

    def add_section(content):
        output.append(
            Section(unicode(content),
                    check_blank(content),
                    check_heading(content)))

    # iterate over all top-level elements in document
    for current_element in soup:
        # if the element is a block-level tag, it (usually) gets its own section
        if isinstance(current_element, Tag) and \
           current_element.name in block_level_tags:

            # but first, make a section from any plain text above here
            if current_section:
                add_section(current_section)
                current_section = ''

            add_section(current_element)

        else:
            # this is not a tag, so it must be plain text; store it.
            current_section += unicode(current_element)

    # make sure we don't miss text at the end of the document
    if current_section:
        add_section(current_section)

    # merge down all whitespace sections
    i = 0
    while i+1 < len(output):
        if output[i].is_blank:
            output[i+1].content = output[i].content + output[i+1].content
            del output[i]
        else:
            i += 1

    # merge down all heading sections
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

    return [section.content for section in output]

