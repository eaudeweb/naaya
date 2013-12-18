import logging

#from OFS.interfaces import IObjectWillBeAddedEvent

from naaya.core.zope2util import is_descendant_of, path_in_site, ofs_path
from naaya.content.pointer.pointer_item import addNyPointer
from naaya.content.event.event_item import NyEvent
from naaya.content.news.news_item import NyNews
from naaya.content.contact.contact_item import NyContact
from naaya.content.url.url_item import NyURL
from naaya.content.file.file_item import NyFile_extfile
from naaya.content.bfile.bfile_item import NyBFile
from naaya.content.mediafile.mediafile_item import NyMediaFile_extfile
from Products.NaayaContent.NyPublication.NyPublication import NyPublication
from Products.NaayaCore.SchemaTool.widgets.GeoTypeWidget import GeoTypeWidget
from Products.NaayaCore.managers.utils import slugify

logger = logging.getLogger(__name__)

def get_countries(ob):
    """
    Extracts coverage from ob, iterates countries and returns
    nyfolders of them in `countries` location (creates them if missing)

    """
    ret = []
    site = ob.getSite()
    cat = site.getCatalogTool()
    filters = {'title': '', 'path': ofs_path(site.countries),
               'meta_type': 'Naaya Folder'}
    coverage = list(set(getattr(ob, 'coverage', u'').strip(',').split(',')))
    for country_item in coverage:
        country = country_item.strip()
        if country:
            country_folders = []
            filters['title'] = country
            bz = cat.search(filters)
            for brain in bz:
                if brain.title.strip().lower() == country.lower():
                    country_folders.append(brain.getObject())
            ret.extend(country_folders)
            if not country_folders:
                logger.info("Country '%s' not found in destinet countries",
                            country)
    return ret

def get_category_location(site, geo_type):
    """
    Based on geo_type (Category) value, returns the corresponding location
    in who-who, who-who/market-place, who-who/market-solutions
    or None if not found

    """
    if not geo_type:
        return None
    widget = GeoTypeWidget('').__of__(site)
    title = widget.convert_to_user_string(geo_type).replace('&', 'and')
    slug = slugify(title, removelist=[])
    who_who = site['who-who']
    candidates = map(lambda x: (x, x.objectIds('Naaya Folder')),
                [who_who, who_who['market-place'], who_who['market-solutions']])
    for (candidate_parent, candidate_ids) in candidates:
        if slug in candidate_ids:
            return candidate_parent[slug]

    return None

def place_pointers(ob, exclude=[]):
    """ Ads pointers to ob in target_groups, topics and countries """
    props = {
        'title': ob.title,
        'description': getattr(ob, 'description', ''),
        'topics': ob.__dict__.get('topics', []),
        'target-groups': ob.__dict__.get('target-groups', []),
        'geo_location.lat': '',
        'geo_location.lon': '',
        'geo_location.address': '',
        'geo_type': getattr(ob, 'geo_type', ''),
        'coverage': ob.__dict__.get('coverage', ''),
        'keywords': ob.__dict__.get('keywords', ''),
        'sortorder': getattr(ob, 'sortorder', ''),
        'redirect': True,
        'pointer': path_in_site(ob)
    }
    if ob.geo_location:
        if ob.geo_location.lat:
            props['geo_location.lat'] = unicode(ob.geo_location.lat)
        if ob.geo_location.lon:
            props['geo_location.lon'] = unicode(ob.geo_location.lon)
        if ob.geo_location.address:
            props['geo_location.address'] = ob.geo_location.address
    site = ob.getSite()
    target_groups = ob.__dict__.get("target-groups", [])
    topics = ob.__dict__.get("topics", [])
    locations = [] # pointer locations
    if 'target-groups' not in exclude and isinstance(target_groups, list):
        for tgrup in target_groups:
            locations.append(site.unrestrictedTraverse("resources/%s" % str(tgrup)))
    if isinstance(topics, list):
        for topic in topics:
            locations.append(site.unrestrictedTraverse("topics/%s" % str(topic)))
    locations.extend(get_countries(ob))
    for loc in locations:
        if not props['sortorder']:
            props['sortorder'] = '200'
        p_id = addNyPointer(loc, '', contributor=ob.contributor, **props)
        pointer = getattr(loc, p_id)
        if pointer:
            if ob.approved:
                pointer.approveThis(1, ob.contributor)
            else:
                pointer.approveThis(0, None)

def _qualifies_for_both(obj):
    """
    Matches condition for adding pointers for both topics and target_groups

    """
    site = obj.getSite()
    resources = site.resources
    news = site.News
    events = site.events
    who_who = getattr(site, 'who-who')
    return ((isinstance(obj, NyEvent) and is_descendant_of(obj, events)) or
        (isinstance(obj, NyNews) and is_descendant_of(obj, news)) or
        (isinstance(obj, (NyFile_extfile, NyBFile, NyMediaFile_extfile, NyURL, NyPublication))
          and is_descendant_of(obj, resources))
         or
        (isinstance(obj, (NyFile_extfile, NyBFile, NyMediaFile_extfile, NyURL, NyPublication, NyNews, NyEvent))
          and is_descendant_of(obj, who_who))
        )

def _qualifies_for_topics_only(obj):
    """
    Matches condition for adding pointers for topics seulement

    """
    site = obj.getSite()
    market_place = getattr(site, 'market-place')
    who_who = getattr(site, 'who-who')
    return (
          (isinstance(obj, NyContact)
           and (is_descendant_of(obj, market_place) or is_descendant_of(obj, who_who))
           )
        or
          (isinstance(obj, NyPublication) and is_descendant_of(obj, market_place))
        )

def get_linked_pointer_brains(obj):
    """
    Tests if object had met condition to be synced with pointers
    and returns brains to existing ones. Used by handlers to keep them in sync.

    """
    site = obj.getSite()
    q_both = _qualifies_for_both(obj)
    q_topics = _qualifies_for_topics_only(obj)
    pointers = []
    if q_topics or q_both:
        cat = site.getCatalogTool()
        pointers = cat.search({'meta_type': 'Naaya Pointer',
                               'path': [ofs_path(site.countries),
                                        ofs_path(site.topics),
                                        ofs_path(getattr(site, 'resources')),
                                        # kept for pointers prior to v 1.1
                                        ofs_path(getattr(site, 'who-who'))],
                               'pointer': path_in_site(obj)})

    return pointers


def _get_geo_type(obj):
    """ Returns the computed value for geo_type based on the new
    category fields
    """
    # See #17642 for details on this
    if getattr(obj, 'category-supporting-solutions'):
        return getattr(obj, 'category-supporting-solutions')
    elif getattr(obj, 'category-marketplace'):
        return getattr(obj, 'category-marketplace')
    else:
        return getattr(obj, 'category-organization')


def handle_add_content(event):
    """
    Tests whether this requires adding pointers and perform the action

    """
    obj = event.context
    site = obj.getSite()
    if not getattr(site, 'destinet.publisher', False):
        return None

    if _qualifies_for_both(obj):
        place_pointers(obj)
    elif _qualifies_for_topics_only(obj):
        place_pointers(obj, exclude=['target-groups'])

    # Make sure that the Destinet User keyword is added
    if obj.meta_type == "Naaya Contact" and \
        obj.aq_parent.getId() == "destinet-users":
        langs = obj.aq_parent.gl_get_languages()

        for lang in langs:
            v = obj.getLocalAttribute("keywords", lang)
            if not "Destinet User" in v:
                if v.strip():
                    v += ", Destinet User"
                else:
                    v = "Destinet User"
            obj.set_localpropvalue('keywords', lang, 'Destinet user')

        obj.geo_type = _get_geo_type(obj)
        obj._p_changed = True
        obj.aq_parent.recatalogNyObject(obj)


def handle_edit_content(event):
    """
    Test whether this requires adding pointers and perform the action

    """
    obj = event.context
    site = obj.getSite()
    if not getattr(site, 'destinet.publisher', False):
        return None

    q_both = _qualifies_for_both(obj)
    q_topics = _qualifies_for_topics_only(obj)
    if q_topics or q_both:
        # clean-up all existing pointers, then re-add them
        cat = site.getCatalogTool()
        pointers = cat.search({'meta_type': 'Naaya Pointer',
                               'path': [ofs_path(site.countries),
                                        ofs_path(site.topics),
                                        ofs_path(getattr(site, 'resources')),
                                        # kept for pointers prior to v 1.1
                                        ofs_path(getattr(site, 'who-who'))],
                               'pointer': path_in_site(obj)})
        for brain in pointers:
            pointer = brain.getObject()
            pointer.aq_parent._delObject(pointer.id)
        if q_both:
            place_pointers(obj)
        else:
            place_pointers(obj, exclude=['target-groups'])

    # Make sure that the Destinet User keyword is added
    langs = obj.aq_parent.gl_get_languages()
    if obj.meta_type == "Naaya Contact" and \
        obj.aq_parent.getId() == "destinet-users":

        for lang in langs:
            v = obj.getLocalAttribute("keywords", lang)
            if not "Destinet User" in v:
                if v.strip():
                    v += ", Destinet User"
                else:
                    v = "Destinet User"
            obj.set_localpropvalue('keywords', lang, 'Destinet user')

        obj.geo_type = _get_geo_type(obj)

        obj._p_changed = True
        obj.aq_parent.recatalogNyObject(obj)


def handle_del_content(obj, event):
    """
    Test whether this required adding pointers and perform the cleanup of
    pointers.

    """
    site = obj.getSite()
    if not getattr(site, 'destinet.publisher', False):
        return None
    q_both = _qualifies_for_both(obj)
    q_topics = _qualifies_for_topics_only(obj)
    if q_topics or q_both:
        # clean-up all existing pointers
        cat = site.getCatalogTool()
        pointers = cat.search({'meta_type': 'Naaya Pointer',
                               'path': [ofs_path(site.countries),
                                        ofs_path(site.topics),
                                        ofs_path(getattr(site, 'resources')),
                                        # kept for pointers prior to v 1.1
                                        ofs_path(getattr(site, 'who-who'))],
                               'pointer': path_in_site(obj)})
        for brain in pointers:
            pointer = brain.getObject()
            pointer.aq_parent._delObject(pointer.id)

def handle_approval_unapproval(obj, approved, approved_by):
    """
    Approve/Unapprove pointers. Used by the two event handlers for approval

    """
    pointer_brains = get_linked_pointer_brains(obj)
    for brain in pointer_brains:
        pointer = brain.getObject()
        try:
            pointer.approveThis(1, approved_by)
        except Exception:
            logger.exception("Can set approve=%s by %s for pointer %s",
                             approved, approved_by, ofs_path(pointer))

def handle_approve_content(event):
    """ Also approve pointers if this object is synced with pointers. """
    if not getattr(event.context.getSite(), 'destinet.publisher', False):
        return
    handle_approval_unapproval(event.context, 1, event.contributor)

def handle_unapprove_content(event):
    """ Also unapprove pointers if this object is synced with pointers. """
    if not getattr(event.context.getSite(), 'destinet.publisher', False):
        return
    handle_approval_unapproval(event.context, 0, event.contributor)
