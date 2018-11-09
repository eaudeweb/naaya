from Products.NaayaCore.SchemaTool.widgets.GeoTypeWidget import GeoTypeWidget
from Products.NaayaCore.managers.utils import slugify
from naaya.core.zope2util import ofs_path
import logging

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
    in who-who, who-who/market-place, or None if not found

    """
    if not geo_type:
        return None
    widget = GeoTypeWidget('').__of__(site)
    title = widget.convert_to_user_string(geo_type).replace('&', 'and')
    slug = slugify(title, removelist=[])
    who_who = site['who-who']
    candidates = map(lambda x: (x, x.objectIds('Naaya Folder')), [
        who_who, who_who['market-place']])
    for (candidate_parent, candidate_ids) in candidates:
        if slug in candidate_ids:
            return candidate_parent[slug]

    return None


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


def alter_contact(obj):
    """ Make various changes to contact objects

    * add the Destinet User keyword
    """
    lang = 'en'
    v = obj.getLocalAttribute("keywords", lang)
    keywords = [x.strip() for x in v.split(',') if x.strip()]

    if "Destinet User" not in keywords:
        keywords.append("Destinet User")

    obj.set_localpropvalue('keywords', lang, ", ".join(set(keywords)))

    obj._p_changed = True


def handle_add_content(event):
    """
    Make sure that the Destinet User keyword is added and perform the action

    """
    obj = event.context
    site = obj.getSite()
    if not getattr(site, 'destinet.publisher', False):
        return None

    # Make sure that the Destinet User keyword is added
    if obj.meta_type == "Naaya Contact":
        obj.geo_type = _get_geo_type(obj)
        if obj.aq_parent.getId() == "destinet-users":
            alter_contact(obj)
        obj.aq_parent.recatalogNyObject(obj)


def handle_edit_content(event):
    """
    Make sure that the Destinet User keyword is added and perform the action

    """
    obj = event.context
    site = obj.getSite()
    if not getattr(site, 'destinet.publisher', False):
        return None

    # Make sure that the Destinet User keyword is added
    if (obj.meta_type == "Naaya Contact"):
        obj.geo_type = _get_geo_type(obj)
        if (obj.aq_parent.getId() == "destinet-users"):
            alter_contact(obj)
        obj.aq_parent.recatalogNyObject(obj)
