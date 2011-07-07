import lxml.cssselect, lxml.html.soupparser

def css(target, selector):
    return lxml.cssselect.CSSSelector(selector)(target)

def csstext(target, selector):
    return ' '.join(e.text_content() for e in css(target, selector)).strip()

def parse_html(html):
    return lxml.html.soupparser.fromstring(html)
