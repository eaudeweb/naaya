from datetime import datetime
from os import path
import re
import htmlentitydefs
import warnings
import tempfile
import urllib

from zope.deprecation import deprecate

mimetype_map = {
    '.css'  : 'text/css',
    '.html' : 'text/html',
    '.htm'  : 'text/html',
    '.txt'  : 'text/plain',
    '.xml'  : 'text/xml',

    '.gif'  : 'image/gif',
    '.jpg'  : 'image/jpeg',
    '.jpeg' : 'image/jpeg',
    '.png'  : 'image/png',

    '.doc'  : 'application/msword',
    '.pdf'  : 'application/pdf',
    '.xls'  : 'application/vnd.ms-excel',
    '.ppt'  : 'application/vnd.ms-powerpoint',
    '.swf'  : 'application/x-shockwave-flash',
    '.js'   : 'application/javascript',
    '.rar'  : 'application/x-rar-compressed',
    '.zip'  : 'application/zip',

    '.mp3'  : 'audio/mpeg',

    '.mpeg' : 'video/mpeg',
    '.mpg'  : 'video/mpeg',
}

@deprecate('mimetype_from_filename is deprecated, use mimetype.guess_type')
def mimetype_from_filename(filename, default=None):
    ext = path.splitext(filename)[1]
    return mimetype_map.get(ext, default)

def get_noaq_attr(obj, attr, default):
    """
    Return the wanted attribute without
    checking the acquisition tree or `default`.
    """
    return getattr(obj.aq_base, attr, default)

def call_method(obj, attr, default):
    """
    Return the result of calling `obj`s `attr`
    or `default` if `obj` doesn't have `attr`.
    """
    if get_noaq_attr(obj, attr, default) != default:
        return obj[attr]()
    else:
        return default

def force_to_unicode(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            return s.decode('latin-1')
    else:
        raise ValueError('expected `str` or `unicode`')

_cooldown_map = {}
def cooldown(name, interval):
    """
    Return ``True`` if called sooner than ``interval`` with the same
    ``name`` argument. Intended usage::

        @component.adapter(INySite, IHeartbeat)
        def hourly_foobar(site, hb):
            if cooldown('foobar %r' % ofs_path(site), timedelta(hours=1)):
                return
            # ... code that will run (almost) every hour

        component.provideHandler(hourly_foobar)
    """
    now = datetime.now()
    if name in _cooldown_map and _cooldown_map[name] + interval > now:
        return True
    else:
        _cooldown_map[name] = now
        return False

def unescape_html_entities(text):
    # from http://effbot.org/zone/re-sub.htm#unescape-html
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def is_ajax(request):
    """Check if an REQUEST object has 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'

    """
    return request.environ.get('HTTP_X_REQUESTED_WITH', '') == \
            'XMLHttpRequest'

def render_macro(context, template_name, macro, **kw):
    """ Render just a part of the macro """
    from Products.PageTemplates.PageTemplate import PageTemplate
    template = PageTemplate()
    template.write("<metal:block\
        use-macro=\"python: here.getFormsTool().getForm('%s').macros['%s']\"\
        />" % (template_name, macro))
    kw.update({'here': context, 'context': context})
    return template.pt_render(extra_context=kw)

def pretty_size(n_bytes):
    if n_bytes < 1024:
        return '%d bytes' % n_bytes
    elif n_bytes < 1024**2:
        return '%d KB' % (n_bytes/1024)
    elif n_bytes < 1024**3:
        return '%d MB' % (n_bytes/1024**2)
    else:
        return '%d GB' % (n_bytes/1024**3)

VALID_EMAIL_PATTERN = re.compile("(?:^|\s)[-a-z0-9_.]+@"
                                 "(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",
                                 re.IGNORECASE)
def is_valid_email(email):
    """
    Validate e-mail address against regular expression
    """
    if VALID_EMAIL_PATTERN.match(str(email)):
        return True
    return False


# these functions were initially defined here, but they are zope2-specific,
# and belong to zope2util, so we moved them over there.

def relative_object_path(obj, ancestor):
    warnings.warn("naaya.core.utils.relative_object_path moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.relative_object_path(obj, ancestor)

def path_in_site(obj):
    warnings.warn("naaya.core.utils.path_in_site moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.path_in_site(obj)

def ofs_path(obj):
    warnings.warn("naaya.core.utils.ofs_path moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.ofs_path(obj)

def download_to_temp_file(url):
    """
    Download contents of URL to a temporary file created with
    `tempfile.TemporaryFile`. Returns an open file containing the response
    body.  When the file is closed it will be automatically removed.
    """
    temp_file = tempfile.TemporaryFile()
    url_file = urllib.urlopen(url)
    try:
        while True:
            buf = url_file.read(2**16)
            if not buf:
                break
            temp_file.write(buf)
    finally:
        url_file.close()
    temp_file.seek(0)
    return temp_file
