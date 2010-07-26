# Python imports
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, CData
from Queue import Queue
import re
import string
from random import choice

# Zope imports
from DateTime import DateTime
from Products.PythonScripts.standard import url_quote

def _get_absolute_url_regex():
    # This regex matches as much as possible the absolute URLs
    # described by RFC 3986 http://www.ietf.org/rfc/rfc3986.txt
    # Known limitations/issues:
    # - IPv6 addresses are not supported
    # - only registered names intended for resolution via the DNS are supported
    # - invalid URLs might be matched

    # ALPHA / DIGIT / "-" / "." / "_" / "~"
    unreserved = r'[\w\-.~]'

    # "%" HEXDIG HEXDIG
    pct_encoded = r'(?:%[\dA-F][\dA-F])'

    #   "!" / "$" / "&" / "'" / "(" / ")"
    # / "*" / "+" / "," / ";" / "="
    sub_delims  = r'''[!$&'()*+,;=]'''

    # unreserved / pct-encoded / sub-delims / ":" / "@"
    pchar = r'(?:%s|%s|%s|@)' % (unreserved, pct_encoded, sub_delims)

    # *( unreserved / pct-encoded / sub-delims )
    # We are using only DNS registered names. We're restring input with
    # the following rule (taken from RFC 3696):
    # The LDH rule, as updated, provides that the labels (words or strings
    # separated by periods) that make up a domain name must consist of only
    # the ASCII [ASCII] alphabetic and numeric characters, plus the hyphen.
    # No other symbols or punctuation characters are permitted, nor is
    # blank space.  If the hyphen is used, it is not permitted to appear at
    # either the beginning or end of a label.
    reg_name = '(?:[a-zA-Z0-9\-.]+)'

    # IPv4 address
    dec_octet = '(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])'
    ipv4_address = '(?:%s)' % '.'.join((dec_octet, dec_octet, dec_octet, dec_octet))


    #
    # SCHEME
    # scheme        = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
    scheme = r'[a-zA-Z][a-zA-Z\d+\-.]*'


    #
    # AUTHORITY
    #

    # userinfo    = *( unreserved / pct-encoded / sub-delims / ":" )
    userinfo = '(?:%s)+' % '|'.join((unreserved, pct_encoded, sub_delims, ":"))
    host = '(?:%s|%s)' % (ipv4_address, reg_name)
    port = r'\d+'
    # authority     = [ userinfo "@" ] host [ ":" port ]
    authority = r"(?:%s@)?%s(?::%s)?" % (userinfo, host, port)


    #
    # PATH ABEMPTY
    # path-abempty  = *( "/" segment )
    # segment       = *pchar
    path_abempty = r'(?:(?:/%s*)*)' % pchar


    #
    # QUERY
    # query         = *( pchar / "/" / "?" )
    query = r'(?:(?:%s|[/?])*)' % pchar


    #
    # FRAGMENT
    # fragment      = *( pchar / "/" / "?" )
    fragment = r'(?:(?:%s|[/?])*)' % pchar


    #
    # URL
    #
    url = r'\b%(scheme)s://%(authority)s%(path_abempty)s(?:\?%(query)s)?(?:#%(fragment)s)?\b' % \
            {'scheme': scheme,
             'authority': authority,
             'path_abempty': path_abempty,
             'query': query,
             'fragment': fragment,}
    return re.compile(url)

_absolute_url_regex = _get_absolute_url_regex()


def get_links_from_text(text):
    """ Extract all absolute URLs from text.

    This functions tries as much as possible to be compliant with RFC 3986 (Uniform Resource Identifier (URI): Generic Syntax).

        >>> from Products.NaayaLinkChecker.Utils import get_links_from_text
        >>> get_links_from_text(' http://www.eaudeweb.ro ') == ['http://www.eaudeweb.ro']
        True
        >>> get_links_from_text(' http://dorel@www.eaudeweb.ro ') == ['http://dorel@www.eaudeweb.ro']
        True
        >>> get_links_from_text(' http://vasile:secret@www.eaudeweb.ro ') == ['http://vasile:secret@www.eaudeweb.ro']
        True
        >>> get_links_from_text(' http://vasile:secret@www.eaudeweb.ro?search=xyz ') == ['http://vasile:secret@www.eaudeweb.ro?search=xyz']
        True
        >>> get_links_from_text(' http://vasile:secret@www.eaudeweb.ro?search=xyz#section2 ') == ['http://vasile:secret@www.eaudeweb.ro?search=xyz#section2']
        True
        >>> get_links_from_text(' www.example.org ') == []
        True
        >>> get_links_from_text(' www.example.org/search?num=20 ') == []
        True
        >>> get_links_from_text(' www.example.org/search?num=20#last ') == []
        True
        >>> get_links_from_text(' http://www.emag.ro/hdd/seagate/filter/buffer-(mb)-v153,32-i2102/interfata-v149,s-ata-i3814/last/f3f1mn ') == ['http://www.emag.ro/hdd/seagate/filter/buffer-(mb)-v153,32-i2102/interfata-v149,s-ata-i3814/last/f3f1mn']
        True

    """

    return _absolute_url_regex.findall(text)


_is_absolute_url_regex = re.compile(r'^[a-zA-Z][a-zA-Z\d+\-.]*:')
def is_absolute_url(url):
    """Quick & dirty way to see if an URL is absolute"""
    return bool(_is_absolute_url_regex.match(url))

def get_links_from_html(html):
    """Return the list of links from HTML attributes and text.

        The following attributes are checked:
         - a.href
         - script.src
         - img.src

        @param html: html source code
        @type html: string
        @rtype: iterator
        @return: the list of URLs from html after filtering them
    """
    soup = BeautifulSoup(html, convertEntities=BeautifulStoneSoup.XHTML_ENTITIES)
    for tag, attr in (('a', 'href'), ('script', 'src'), ('img', 'src')):
        for t in soup.findAll(tag, {attr: True}):
            yield t.get(attr)
    for text in soup.findAll(text=lambda x: x is not None and not x.startswith('<!--')):
        for x in get_links_from_text(text):
            yield x


class UtilsManager:
    """UtilsManager class"""

    def __init__(self):
        """Constructor"""
        pass

    def umGetROOT(self):
        """ get the ROOT object"""
        return self.unrestrictedTraverse(('',))

    def umGenRandomKey(self, length=10, chars=string.digits):
        """Generate a random numeric key."""
        return ''.join([choice(chars) for i in range(length)])

    def umConvertToList(self, something):
        """Convert to list"""
        ret = something
        if type(something) is type(''):
            ret = [something]
        return ret

    def umFormatDateTimeToString(self, date):
        """Gets a date (tuple - (yyyy, mm, dd, hh, mm, ss, 3, 311, 0)) and returns a string like dd/mm/yyyy hh:mm:ss"""
        year = str(date[0])
        month = str(date[1])
        if len(month)==1:
            month = '0' + month
        day = str(date[2])
        if len(day)==1:
            day = '0' + day
        hours = str(date[3])
        if len(hours)==1:
            hours = '0' + hours
        minutes = str(date[4])
        if len(minutes)==1:
            minutes = '0' + minutes
        return day + '/' + month + '/' + year + ' ' + hours + ':' + minutes

    def umGetTodayDate(self):
        """Returns today date in a DateTime object"""
        return DateTime()

    #############
    # ENCODING  #
    #############

    def umURLEncode(self, str):
        """Encode a string using url_encode"""
        return url_quote(str)

    #################
    # PARSING STUFF #
    #################

    def getItemTitle(self, url, size=20):
        """ return the object by url """
        try:
            obj_title = self.unrestrictedTraverse(url).title_or_id()
            if size == 0:
                return obj_title
            if len(obj_title) > size:
                return '%s...' % obj_title[:size]
        except KeyError:
            return None


def iter2Queue(iterable):
    """Returns a Queue from iterable"""
    q = Queue()
    for x in iterable:
        q.put_nowait(x)
    return q


def _test():
    import doctest, Utils
    return doctest.testmod(Utils)

if __name__ == '__main__':
    _test()
