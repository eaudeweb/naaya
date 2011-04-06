import os
import sys
import sha
import types

from Products.Naaya.interfaces import INySite
from Products.Naaya import NySite as NySite_module

def convertToList(data):
    """ convert to list """
    res = []
    add_res = res.append
    if type(data) == type([]):
        res.extend(data)
    else:
        [add_res(k.strip()) for k in data.split(',')]
    return res

def minDate(a,b):
    """.compare dates """
    if a < b: return a
    else:     return b

def isUnixLike():
    """ find if the operating system is Unix-like"""
    if sys.platform == 'win32':
        return False
    return True

def convertLinesToList(value):
    """ takes a value from a textarea control and returns a list of values """
    if type(value) == type([]): return value
    elif value == '': return []
    else:
        values = []
        for v in value.split('\n'):
            if v != '': values.append(v.replace('\r', ''))
    return values

def readFile(p_path, p_flag='r'):
    """ """
    return open(p_path, p_flag).read()

def create_signature(s):
    if s is not None:
        m = sha.new(s)
        res = m.hexdigest()
        m = None
        return res
    else:
        return s

def html_decode(s):
    """Decode some special chars"""
    if isinstance(s, unicode): buf = s.encode('utf-8')
    else: buf = str(s)
    buf = buf.replace('&amp;', '&')
    buf = buf.replace('&lt;', '<')
    buf = buf.replace('&quot;', '"')
    buf = buf.replace('&apos;', '\'')
    buf = buf.replace('&gt;', '>')
    return buf

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath()[1:])

def get_template_content(form):
    """ return a template content given the object """
    try:
        return form._text
    except:
        return str(form.data)

def normalize_template(src):
    src = (src.strip().replace('\r', '')+'\n')
    if isinstance(src, unicode):
        src = src.encode('utf-8')
    return src

def html_diff(source, target):
    import difflib
    from cStringIO import StringIO
    lines = lambda s: StringIO(normalize_template(s)).readlines()
    htmlquote = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    output = StringIO()
    output.write('<div style="font-family: monospace;">')
    for line in difflib.unified_diff(lines(source), lines(target)):
        if line.startswith('+'):
            cls = 'line_added'
        elif line.startswith('-'):
            cls = 'line_removed'
        elif line.startswith('@@'):
            cls = 'line_heading'
        else:
            cls = 'line_normal'
        output.write('<div class="%s">%s</div>\n' % (cls, htmlquote(line)))
    output.write('</div>')
    return output.getvalue()

def get_portals(container, context=None, meta_types=None):
    """ Given a `container` or a `context` recusivly search all portals with
    `meta_types`.

    """

    if context is None:
        context = container.getPhysicalRoot()
    res = []
    for ob in context.objectValues():
        if not INySite.providedBy(ob):
            continue
        if meta_types is not None and ob.meta_type not in meta_types:
            continue
        res.append(ob)
        res.extend(get_portals(container, ob, meta_types))
    return res

def get_portal(container, ppath):
    return container.getPhysicalRoot().unrestrictedTraverse(ppath)

def get_portal_path(container, portal_metatype):
    """ return the portal path given the metatype """

    if isinstance(portal, types.ModuleType):
        m = portal
    else:
        if isinstance(portal, NySite_module.NySite):
            portal = portal.__class__
        m = sys.modules[portal.__module__]
    return os.path.dirname(m.__file__)

def get_contenttype_content(container, id, portal):
    """ return the content of the filesystem content-type template """

    portal_path = get_portal_path(container, portal)
    data_path = os.path.join(portal_path, 'skel', 'forms')

    for meta_type in portal.get_pluggable_metatypes():
        pitem = portal.get_pluggable_item(meta_type)
        #load pluggable item's data
        for frm in pitem['forms']:
            if id == frm:
                frm_name = '%s.zpt' % frm
                if os.path.isfile(os.path.join(data_path, frm_name)):
                    #load form from the 'forms' directory because it is
                    #customized
                    return readFile(os.path.join(data_path, frm_name), 'r')
                else:
                    #load form from the pluggable meta type folder
                    return readFile(os.path.join(pitem['package_path'], 'zpt',
                                                 frm_name), 'r')
                break
