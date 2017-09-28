import operator
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from DateTime import DateTime
from naaya.core.zope2util import physical_path
from constants import METATYPE_NYFORUMMESSAGE, METATYPE_NYFORUMTOPIC

_tmpl_feed_atom = NaayaPageTemplateFile('zpt/feed_atom', globals(),
                                        'naaya.forum.feed_atom')
_tmpl_feed_rss = NaayaPageTemplateFile('zpt/feed_rss', globals(),
                                       'naaya.forum.feed_rss')

def messages_feed(context, REQUEST=None, format='rss'):
    """ Atom feed with forum messages under this location """

    catalog = context.getSite().getCatalogTool()
    query = {
        'meta_type': [METATYPE_NYFORUMMESSAGE, METATYPE_NYFORUMTOPIC],
        'path': physical_path(context),
    }
    messages_list = [b.getObject() for b in catalog(**query)]
    messages_list.sort(key=operator.attrgetter('postdate'), reverse=True)

    if messages_list:
        feed_updated = messages_list[0].postdate
    else:
        feed_updated = DateTime()

    options = {
        'messages_list': messages_list,
        'feed_updated': feed_updated,
    }
    if format == 'rss':
        tmpl = _tmpl_feed_rss
        content_type = 'application/rss+xml'
    elif format == 'atom':
        tmpl = _tmpl_feed_atom
        content_type = 'application/atom+xml'
    else:
        raise ValueError("Unknown feed format %r" % format)

    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', content_type)
    return tmpl.__of__(context)(**options)
