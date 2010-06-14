from datetime import datetime
from os import path

def relative_object_path(obj, ancestor):
    """
    Compute the relative path from `ancestor` to `obj` (`obj` must be
    somewhere inside `ancestor`)
    """

    ancestor_path = '/'.join(ancestor.getPhysicalPath())
    obj_path = '/'.join(obj.getPhysicalPath())

    if not obj_path.startswith(ancestor_path):
        raise ValueError('My path is not in the site. Panicking.')
    return obj_path[len(ancestor_path)+1:]

def path_in_site(obj):
    """
    Compute the relative path of `obj` in reference to its
    containing site
    """
    return relative_object_path(obj, obj.getSite())

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

def ofs_path(obj):
    """
    Return a string representation of an object's path, e.g.
    ``/mysite/about/info``
    """
    return '/'.join(obj.getPhysicalPath())

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
    '.js'   : 'application/x-javascript',
    '.rar'  : 'application/x-rar-compressed',
    '.zip'  : 'application/zip',

    '.mp3'  : 'audio/mpeg',

    '.mpeg' : 'video/mpeg',
    '.mpg'  : 'video/mpeg',
}

def mimetype_from_filename(filename, default=None):
    ext = path.splitext(filename)[1]
    return mimetype_map.get(ext, default)
