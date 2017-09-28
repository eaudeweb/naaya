"""
Utilities to make Zope2 a friendlier place.

"""

import threading
import logging
import transaction
import datetime
import os
import sys
import sha
import types
import urllib
import simplejson as json
from decimal import Decimal

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permission import Permission
from Acquisition import Implicit, aq_base
from App.config import getConfiguration
from OFS.interfaces import IItem, IObjectManager
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Globals import DTMLFile
from ZPublisher.HTTPRequest import FileUpload
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.configuration.name import resolve
from DateTime import DateTime

from Products.Naaya.interfaces import IObjectView
from naaya.core.utils import force_to_unicode, is_valid_email  # keep!
from naaya.core.utils import unescape_html_entities
from backport import any
from interfaces import IRstkMethod


log = logging.getLogger(__name__)

html_escape_table = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
    ' ': '&nbsp;', '\t': '&#09'}


def getExtConfiguration():
    CONFIG = getConfiguration()
    CONFIG.environment.update(os.environ)
    return CONFIG


def redirect_to(tmpl):
    """
    Generate a simple view that redirects to the specified URL.

    For example, this declaration:
    >>> the_old_page = redirect_to('%(self_url)s/the_new_page')

    is equivalent with:
    >>> def the_new_page(self, REQUEST):
    >>>     ''' perform redirect '''
    >>>     REQUEST.RESPONSE.redirect(self.absolute_url() + '/the_new_page')

    """
    def redirect(self, REQUEST):
        """ automatic redirect """
        url = tmpl % {
            'self_url': self.absolute_url(),
        }
        REQUEST.RESPONSE.redirect(url)
    return redirect


def json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    else:
        raise ValueError('Can not encode value %r' % value)


def json_dumps(obj):
    """
    Convert a Python object to JSON
    """
    return json.dumps(obj, default=json_default)


json_loads = json.loads  # needed for ZCML registration of RSTK method


_button_form = PageTemplateFile('zpt/button_form.zpt', globals())


def button_form(**kwargs):
    """
    A simple one-button form, useful when a button that does POST
    is more appropriate than a link that does GET.

    It takes a few keyword arguments.
    `label`: what text should appear on the button;
    `button_title`: tooltip text for the button;
    `action`: what should the form do (e.g. ``"POST"``);
    `formdata`: dictionary of name/value pairs to be embedded as
    hidden inputs in the form.

    None of the fields are translated by default; it's your
    responsability to do that before calling ``button_form``.
    """
    return _button_form(**kwargs)


def DT_strftime_rfc3339(date):
    """
    Convert a Zope DateTime value to rfc-3339 format, suitable for use
    in an Atom feed.
    """
    d = DT2dt(date).strftime('%Y-%m-%dT%H:%M:%S%z')
    return d[:-2] + ':' + d[-2:]


def dt_strftime(date, format):
    """
    Convert a Zope DateTime value to rfc-3339 format, suitable for use
    in an Atom feed.
    """
    return datetime.datetime.strftime(date, format)


def we_provide(feature):
    """ Check if the instance provides certain features """
    if feature == 'Excel export':
        try:
            from xlwt import Workbook
            return True
        except ImportError:
            pass
    if feature == 'Excel import':
        # For excel import we also need xlwt, to generate the template
        try:
            from xlwt import Workbook
            from xlrd import open_workbook
            return True
        except ImportError:
            pass
    return False


def catch_unauthorized():
    """
    useful in try..except handlers, like `tal:on-error`::

    <p tal:content="here/read_value" on-error="here/rstk/catch_unauthorized"/>

    """
    if sys.exc_info()[0] is Unauthorized:
        return None
    else:
        raise


def url_quote(text):
    """URL encode text"""
    return urllib.quote_plus(text)


def url_unquote(text):
    """URL decode text"""
    return urllib.unquote_plus(text)


def escape_html(text):
    """Produce HTML entities within text"""
    return "".join(html_escape_table.get(c, c) for c in text)


def unescape_html_entities(text):
    """ unescape html entities from the given text """
    return unescape_html_entities(text)


def get_object_view_info(ob):
    """
    Get object icon, meta_label, and other information, useful when
    displaying the object in a list (e.g. folder index, search results,
    latest news). Behind the scenes, data comes from adapters to the
    :class:`~Products.Naaya.interfaces.IObjectView` interface.
    Currently returns the following fields:

    `icon`
        the return value from
        :func:`~Products.Naaya.interfaces.IObjectView.get_icon`
    """

    view_adapter = get_site_manager(ob).getAdapter(ob, IObjectView)

    # Ideally we would just return the adapter, but RestrictedPython blocks
    # all access to its methods.
    return {
        'icon': view_adapter.get_icon(),
        # TODO add other fields as needed
    }


def google_analytics(context, ga_id=''):
    """
    Renders Google Analytics form template using the provided
    `ga_id` Analytics Website property ID (UA-number).

    """
    conf = getExtConfiguration()
    environment = getattr(conf, 'environment', {})
    master_ga_id = environment.get('GA_ID', '')
    ga_domain_name = environment.get('GA_DOMAIN_NAME', '')

    if ga_id == '' and master_ga_id == '':
        # No website ID provided; e.g. not configured in portal_statistics
        return ''

    if context.REQUEST.AUTHENTICATED_USER.has_role('Manager'):
        # no google analytics for managers
        return ''

    gaq = {}
    ga_keys = []
    if master_ga_id:
        ga_keys.append(master_ga_id)
    if ga_id:
        ga_keys.append(ga_id)
    gaq['ga_ids'] = ga_keys
    gaq['ga_domain_name'] = ga_domain_name

    site = context.getSite()
    forms_tool = site.getFormsTool()
    ga_form = forms_tool.getForm("site_googleanalytics")
    return ga_form.__of__(site)(gaq=gaq)


def provides(context, ob, interface_name):
    """ proxy for zope interface.providedBy """
    interface = resolve(interface_name)
    return interface.providedBy(ob)


def latest_visible_uploads(context, howmany=-1):
    """
    Rstk caller for latest_viewable_uploads in
    Products.NaayaCore.managers.catalog_tool

    """
    items = []
    gen = context.getSite().latest_visible_uploads(context.get_meta_types())
    for cnt, ob in enumerate(gen):
        if cnt == howmany:
            break
        items.append(ob)
    return items


def users_in_role(context, role_name=''):
    """ """
    auth_tool = context.getSite().getAuthenticationTool()
    users = auth_tool.search_users(query='', skey='name', rkey=0,
                                   all_users=True, role=role_name,
                                   location='_all_')
    return users


class RestrictedToolkit(SimpleItem):
    """
    RestrictedToolkit exposes some useful methods to RestrictedPython
    code (e.g. Scripts in ZODB, PageTemplates). You can get a hold of
    the RestrictedPython instance (it's a singleton) easily:

      >>> rstk = self.rstk

    It's pulled form the NySite object via acquisition.
    """
    security = ClassSecurityInfo()
    # by default, all methods are "public"

    def __getitem__(self, name):
        method = get_site_manager(self).queryUtility(IRstkMethod, name)
        if method is None:
            raise KeyError('RestrictedToolkit: no method registered %r' % name)
        else:
            return types.MethodType(method, self)


InitializeClass(RestrictedToolkit)


class CaptureTraverse(Implicit):
    """
    Capture any request path and invoke a callback.

    CaptureTraverse is useful when we need to capture arbitrary request
    paths. If our object is published at `http://example.com/my/object`,
    and we expect requests at `http://example.com/my/object/magic/a/b/c`,
    then we can use CaptureTraverse like so::

      >>> def handle_magic(context, path, REQUEST):
      ...     return ('the page! path=%r, url=%r' %
                      (path, context.absolute_url()))
      >>> class MyObject(SimpleItem):
      ...     # implementation of MyObject
      ...     # ...
      ...
      ...     magic = CaptureTraverse(handle_magic)

    GET requests for `http://example.com/my/object/magic/a/b/c` will
    receive the following response::

      the page! path=('a', 'b', 'c'), url='http://example.com/my/object'

    """

    security = ClassSecurityInfo()

    def __init__(self, callback, path=tuple(), context=None):
        self.callback = callback
        self.path = path
        self.context = context

    def __bobo_traverse__(self, REQUEST, name):
        new_path = self.path + (name,)
        context = self.context or (self.aq_parent,)
        return CaptureTraverse(self.callback, new_path, context).__of__(self)

    def __call__(self, REQUEST):
        assert self.path[-1] == 'index_html'
        return self.callback(self.context[0], self.path[:-1], REQUEST)


##################################################################
# `UnnamedTimeZone`, `dt2DT` and `DT2dt` come from Plone's
# Products.ATContentTypes.utils

class UnnamedTimeZone(datetime.tzinfo):
    """Unnamed timezone info"""

    def __init__(self, minutes):
        self.minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minutes)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        aheadUTC = self.minutes > 0
        if aheadUTC:
            sign = '+'
            mins = self.minutes * -1
        else:
            sign = '-'
            mins = self.minutes
        wholehours = int(self.minutes / 60.)
        minutesleft = self.minutes % 60
        return """%s%0.2d%0.2d""" % (sign, wholehours, minutesleft)


def dt2DT(date):
    """ Convert Python's datetime to Zope's DateTime """
    args = (date.year, date.month, date.day, date.hour, date.minute,
            date.second, date.microsecond, date.tzinfo)
    timezone = args[7].utcoffset(date)
    secs = timezone.seconds
    days = timezone.days
    hours = secs/3600 + days*24
    mod = "+"
    if hours < 0:
        mod = ""
    timezone = "GMT%s%d" % (mod, hours)
    args = list(args[:6])
    args.append(timezone)
    return DateTime(*args)


def DT2dt(date):
    """ Convert Zope's DateTime to Pythons's datetime """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    args.append(0)
    args.append(UnnamedTimeZone(int(date.tzoffset()/60)))
    return datetime.datetime(*args)


def ensure_tzinfo(dt, default_tz=UnnamedTimeZone(0)):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=default_tz)
    else:
        return dt

folder_manage_main_plus = DTMLFile('zpt/folder_main_plus', globals())
"""
The OFS.ObjectManager `manage_main` template, modified to render two
extra pieces of content: ``ny_before_listing`` and ``ny_after_listing``.
"""


def exorcize_local_properties(obj):
    """
    remove any data set by LocalPropertyManager, recover plain
    (non-localized) string values, and set them as simple properties.

    Returns `None` if nothing was touched, or a list of extracted
    property names (which may be empty if we only removed empty
    LocalPropertyManager data structures).
    """

    obj.getId()  # make sure it's loaded from zodb
    changed = False

    names = []
    default_lang = obj.__dict__.get('_default_lang', 'en')
    if '_local_properties' in obj.__dict__:
        for name, localdata in obj.__dict__['_local_properties'].items():
            if default_lang in localdata:
                value = localdata[default_lang][0]
            else:
                value = localdata.values()[0][0]
            obj.__dict__[name] = force_to_unicode(value)
            changed = True
            names.append(name)

    for attrname in ['_default_language', '_languages', '_local_properties',
                     '_local_properties_metadata']:
        if attrname in obj.__dict__:
            del obj.__dict__[attrname]
            changed = True

    if changed:
        obj._p_changed = True
        return names
    else:
        return None


def abort_transaction_keep_session(request):
    """
    We need to abort the transaction (e.g. an object was created but the
    add form generated errors). We preserve whatever data has been set on
    the session.
    """
    session = dict(request.SESSION)
    transaction.abort()
    request.SESSION.update(session)


def permission_add_role(context, permission, role):
    """ Adds a role to a permission"""
    p = Permission(permission, (), context)
    crt_roles = p.getRoles()
    ty = type(crt_roles)
    p.setRoles(ty(set(crt_roles) | set([role])))


def permission_del_role(context, permission, role):
    """ Removes permission from role """
    p = Permission(permission, (), context)
    crt_roles = p.getRoles()
    ty = type(crt_roles)
    p.setRoles(ty(set(crt_roles) - set([role])))


def physical_path(ob):
    # TODO deprecate and replace with ofs_path
    return '/'.join(ob.getPhysicalPath())


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


def ofs_path(obj):
    """
    Return a string representation of an object's path, e.g.
    ``/mysite/about/info``
    """
    return '/'.join(obj.getPhysicalPath())


def is_descendant_of(obj, ancestor):
    """
    Return if the `obj` is somewhere inside `ancestor`
    """
    # add '/' to make sure last ids are compared correctly
    ancestor_path = ofs_path(ancestor) + '/'
    obj_path = ofs_path(obj) + '/'
    return obj_path.startswith(ancestor_path)


def path_in_site(obj):
    """
    Compute the relative path of `obj` in reference to its
    containing site
    """
    return relative_object_path(obj, obj.getSite())


def parents_in_site_path(obj):
    """
    Returns the objects traversed from containing site to object, both included

    """
    site = obj.getSite()
    parents = []
    while obj != site:
        parents.append(obj)
        obj = obj.aq_parent
    parents.append(site)
    parents.reverse()
    parents = map(lambda o: o.title_or_id(), parents)
    return parents


def ofs_walk(top, filter=[IItem], containers=[IObjectManager]):
    """
    Walk the Zope object graph and yield the objects it finds.

    :param top: Object where the walk starts. Regardless of `filter` and
        `containers`, `top` is never yielded, but always walked.
    :param filter: Filter yielded objects. An object will be yielded only if
        it provides one of the specified interfaces.
    :param containers: Choose which container objects are walked.
        :func:`ofs_walk` will call itself recursively if an object implements
        one of the specified interfaces.
    """

    if not hasattr(aq_base(top), 'objectValues'):
        raise ValueError("Object %r does not have sub-objects" % top)

    for ob in top.objectValues():
        if any(i.providedBy(ob) for i in filter):
            yield ob

        if any(i.providedBy(ob) for i in containers):
            for item in ofs_walk(ob, filter, containers):
                yield item


def simple_paginate(items, per_page=4):
    output = []
    for offset in xrange(0, len(items), per_page):
        output.append(items[offset:offset+per_page])
    return output


def get_site_manager(context):
    """
    Return the site manager for a given object. It will typically return the
    local site manager of the object's site.
    """
    return context.getSite().getSiteManager()


def iter_file_data(f):
    """
    Iterate through contents of given file. Can auto-detect if the file
    is a Zope FileUpload or an OFS File/ImageFile.
    """
    # TODO add support for any file-like objects, with unit tests
    if isinstance(f, FileUpload):
        while True:
            buf = f.read(2**16)
            if not buf:
                break
            yield buf
        f.seek(0)

    elif hasattr(f, 'data'):
        if isinstance(f.data, str):
            yield f.data

        else:
            data = f.data
            while data is not None:
                yield data.data
                data = data.next


def sha_hexdigest(f):
    sha_hash = sha.new()
    for buf in iter_file_data(f):
        sha_hash.update(buf)
    return sha_hash.hexdigest()


def get_template_source(template):
    """ Returns the source text of a template """

    template._cook_check()
    return template._text


def launch_job(callback, context, obj_path):
    """ Launch a job in a separate thread"""

    db = context._p_jar.db()
    trans = transaction.get()
    trans.addAfterCommitHook(
        _start_thread,
        kws={'db': db, 'context_path': obj_path, 'callback': callback})


def _start_thread(status, db, context_path, callback):
    t = threading.Thread(target=_run_job, args=(db, context_path, callback))
    t.start()


def _run_job(db, context_path, callback):
    c = db.open()
    app = c.root()['Application']
    context = app.unrestrictedTraverse(context_path)
    try:
        callback(context)
        transaction.commit()
    except:
        log.exception('Error in worker thread')
        transaction.abort()


def json_response(data, response):
    response.setHeader('Content-Type', 'application/json')
    return json.dumps(data)


def get_zope_env(var, default=''):
    """
    Returns the value from buildout of specified variable if exists,
    otherwise returns a default value

    """
    configuration = getExtConfiguration()
    return getattr(configuration, 'environment', {}).get(var, default)
