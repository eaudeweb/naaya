import zope.component
from DateTime import DateTime
import urllib
from interfaces import IBFileContentViewer
from naaya.core.utils import pretty_size, force_to_unicode, icon_for_content_type

def file_has_content(file_ob):
    return (file_ob is not None) and (file_ob.filename != '')

def get_view_adapter(version):
    """Find an file content viewer adapter based on content type"""

    name = version.content_type
    try:
        return zope.component.getAdapter(version, IBFileContentViewer, name)
    except zope.component.interfaces.ComponentLookupError:
        name = name.split('/')[0] + '/*'
        return zope.component.queryAdapter(version, IBFileContentViewer, name)

def tmpl_version(context, version, ver_id):
    """ """
    #Try to get the adapter for this version and set viewable
    viewable = False
    if get_view_adapter(version) is not None:
        viewable = True
    pretty_version_size = None
    url = None
    icon_url = None
    if not version.removed:
        pretty_version_size = pretty_size(version.size)
        url = ('%s/download/%s/%s' %
                            (context.absolute_url(),
                             ver_id,
                             urllib.quote(version.filename, safe='')))
        icon_url = (icon_for_content_type(version.content_type)['url'])

    return {
        'contributor': getattr(version, 'contributor', ''),
        'filename': force_to_unicode(version.filename),
        'content_type': version.content_type,
        'pretty_size': pretty_version_size,
        'removed': version.removed,
        'url': url,
        'icon_url': icon_url,
        'pretty_timestamp': version.timestamp.strftime('%d %b %Y'),
        'timestamp': DateTime(version.timestamp.replace(tzinfo=None)),
        'id': ver_id,
        'is_current': False,
        'viewable': viewable,
        'ob': context,
    }

