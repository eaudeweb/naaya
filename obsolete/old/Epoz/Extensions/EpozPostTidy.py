###
# EpozPostTidy.py
#
# This is just an example for transforming
# absolute urls to relative urls with Epoz.
#
# Use it at your own risk or improve it!
###

from HTMLParser import HTMLParser
import re

# These tags will get a newline after the closing tag
blocktags = ['p', 'pre', 'div',
             'table', 'tr', 'th', 'td', 'thead', 'tbody', 'tfoot',
             'ul','ol','li',
             'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# Just a simple htmlparser
class aHTMLParser(HTMLParser):
    res = ""

    def handle_starttag(self, tag, attrs):
        attributes=""
        for (key,value) in attrs:
            # Internal Link?
            if (tag=="a" and key=="href") or (tag=="img" and key=="src"):
                value = self.getRelativeUrl(self.pageurl, value)
            attributes += ' %s="%s"' % (key,value)
        self.res += "<%s%s>" % (tag, attributes)

    def handle_endtag(self, tag):
        self.res += "</%s>" % (tag,)
        # Some pretty-nice-printing for block-elements
        if tag in blocktags:
            self.res += "\n"

    def handle_startendtag(self, tag, attrs):
        attributes=""
        for (key,value) in attrs:
            # Image?
            if tag=="img" and key=="src":
                value = self.getRelativeUrl(self.pageurl, value)
            attributes += ' %s="%s"' % (key,value)
        self.res += "<%s%s />" % (tag, attributes)

    def handle_data(self, data):
        self.res += data

    def handle_charref(self, data):
        self.res += "&%s;" % data

    def handle_entityref(self, data):
        self.res += "&%s;" % data

    def handle_comment(self, data):
        self.res += "<!-- %s -->" % data


def EpozPostTidy(self, html, pageurl):

    # Create a parser
    parser = aHTMLParser()

    # Give the parser the global method for relative urls
    parser.getRelativeUrl = self.EpozGetRelativeUrl

    # Submit the pageurl as base-url for calculating urls
    parser.pageurl = pageurl

    # And now lets turn the wheels
    parser.feed(html)
    parser.close()

    # Get & return postprocessed html from parser
    html = parser.res

    # Just some cleanups to remove useless whitespace
    html = re.sub("[ ]+"," ",html)
    html = re.sub("[\n]+","\n", html)

    return html
