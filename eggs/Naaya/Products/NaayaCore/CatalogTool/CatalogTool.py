"""
This tool is a wrapper around Products.ZCatalog. On initialization it creates
the required indexes and metadata and offers a few convenience and
maintenance functionalities such as catalog rebuilding and missing objects
reporting.

"""

from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import Catalog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.component import queryAdapter
from OFS.Uninstalled import BrokenClass

from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
try:
    from Products.ZCTextIndex.ZCTextIndex import PLexicon
    from Products.ZCTextIndex.Lexicon import (
        CaseNormalizer, Splitter, StopWordRemover,
    )
    _has_zctextindex = True
except ImportError:
    _has_zctextindex = False

def _ensure_lexicon(catalog):
    """Create a PLexicon in the catalog if not already present."""
    if _has_zctextindex and 'Lexicon' not in catalog.objectIds():
        lexicon = PLexicon('Lexicon', 'Default lexicon',
                           Splitter(), CaseNormalizer(), StopWordRemover())
        catalog._setObject('Lexicon', lexicon)


def _add_zctextindex(catalog, index_name):
    """Add a ZCTextIndex to the catalog."""
    _ensure_lexicon(catalog)
    extra = type('Extra', (), {
        'doc_attr': index_name,
        'index_type': 'Okapi BM25 Rank',
        'lexicon_id': 'Lexicon',
    })()
    catalog.addIndex(index_name, 'ZCTextIndex', extra=extra)


from .interfaces import INyCatalogAware, INyCatalogIndexing
from naaya.core.interfaces import INyObjectContainer
from Products.NaayaBase.interfaces import INyContainer, INyCommentable


# Python 3 BTree compatibility: OOBTree can't mix str/int keys.
# After Py2→Py3 migration, ZODB objects have inconsistent types for
# the same attribute (e.g. validation_status: int 0 vs str '0').
# Patch UnIndex to convert the entry type when a mismatch occurs.
from Products.PluginIndexes.unindex import UnIndex as _UnIndex

_orig_insertForward = _UnIndex.insertForwardIndexEntry
_orig_removeForward = _UnIndex.removeForwardIndexEntry


def _coerce_entry(entry):
    """Try converting str↔int to match the other type."""
    if isinstance(entry, str):
        try:
            return int(entry)
        except (ValueError, TypeError):
            return None
    elif isinstance(entry, (int, bool)):
        return str(entry)
    return None


def _safe_insertForwardIndexEntry(self, entry, documentId):
    try:
        return _orig_insertForward(self, entry, documentId)
    except TypeError:
        alt = _coerce_entry(entry)
        if alt is not None:
            return _orig_insertForward(self, alt, documentId)


def _safe_removeForwardIndexEntry(self, entry, documentId):
    try:
        return _orig_removeForward(self, entry, documentId)
    except TypeError:
        alt = _coerce_entry(entry)
        if alt is not None:
            return _orig_removeForward(self, alt, documentId)


_UnIndex.insertForwardIndexEntry = _safe_insertForwardIndexEntry
_UnIndex.removeForwardIndexEntry = _safe_removeForwardIndexEntry


# Patch for Products.ZCatalog.Catalog, recordify method must
# receive an adapted object in order to properly index properties
def patch_zope_catalog_indexing():
    """ This is applied by zca, through naaya:call in configure.zcml """

    # Patch for meta data
    def patch_object(object):
        adapted_object = queryAdapter(object, INyCatalogIndexing)
        if adapted_object is None:
            # no adapter found
            return object
        else:
            return adapted_object

    if not getattr(Catalog.recordify, 'patched_by_Naaya', False):
        orig_recordify = Catalog.recordify

        def patched_recordify(self, object):
            return orig_recordify(self, patch_object(object))
        setattr(patched_recordify, 'patched_by_Naaya', True)

        Catalog.recordify = patched_recordify

    # Patch for index data
    if not getattr(Catalog.catalogObject, 'patched_by_Naaya', False):
        orig_catalogObject = Catalog.catalogObject

        def patched_catalogObject(self, object, uid, threshold=None, idxs=None,
                                  update_metadata=1):
            return orig_catalogObject(self, patch_object(object), uid,
                                      threshold, idxs, update_metadata)
        setattr(patched_catalogObject, 'patched_by_Naaya', True)

        Catalog.catalogObject = patched_catalogObject


def manage_addCatalogTool(self, languages=None, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    if languages is None:
        try:
            languages = self.getSite().get_available_languages()
        except:
            languages = []
    ob = CatalogTool(ID_CATALOGTOOL, TITLE_CATALOGTOOL)
    self._setObject(ID_CATALOGTOOL, ob)
    self._getOb(ID_CATALOGTOOL).loadDefaultData(languages)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class CatalogTool(ZCatalog, utils):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_CATALOGTOOL
    icon = 'misc_/NaayaCore/CatalogTool.gif'

    manage_options = (
        ZCatalog.manage_options[:1] +
        ({'label': "Maintenance", 'action': 'manage_maintenance'},) +
        ZCatalog.manage_options[1:]
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        ZCatalog.__dict__['__init__'](self, id, title, None, None)
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')

    def loadDefaultData(self, languages):
        """
        Creates default indexes and metadata.
        """
        languages = self.utConvertToList(languages)
        # TODO for Zope 2.10: remove try: ... except: pass
        try:
            self.addIndex('modification_time', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('id', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('meta_type', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('path', 'PathIndex')
        except:
            pass
        try:
            _add_zctextindex(self, 'PrincipiaSearchSource')
        except:
            pass
        try:
            _add_zctextindex(self, 'title')
        except:
            pass
        try:
            self.addIndex('submitted', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('approved', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('topitem', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('checkout', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('validation_status', 'FieldIndex')
        except:
            pass
        for lang in languages:
            self.add_indexes_for_lang(lang)
        try:
            self.addIndex('releasedate', 'DateIndex')
        except:
            pass
        try:
            self.addIndex('geo_latitude', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('geo_longitude', 'FieldIndex')
        except:
            pass
        try:
            self.addIndex('geo_type', 'FieldIndex')
        except:
            pass
        try:
            _add_zctextindex(self, 'geo_address')
        except:
            pass
        # create columns
        try:
            self.addColumn('id')
        except:
            pass
        try:
            self.addColumn('title')
        except:
            pass
        try:
            self.addColumn('meta_type')
        except:
            pass
        try:
            self.addColumn('modification_time')
        except:
            pass
        try:
            self.addColumn('releasedate')
        except:
            pass
        try:
            self.addColumn('summary')
        except:
            pass

    security.declarePrivate('add_index_for_lang')

    def add_index_for_lang(self, name, lang):
        """
        Create a ZCTextIndex index for given language:
        - B{I{name}_I{lang}}
        @param name: index name
        @type name: string
        @param lang: language code
        @type lang: string
        """
        index_name = '%s_%s' % (name, lang)
        try:
            _add_zctextindex(self, index_name)
            self.reindexIndex(index_name, self.REQUEST)
        except:
            pass

    security.declarePrivate('add_indexes_for_lang')

    def add_indexes_for_lang(self, lang):
        """
        For each portal language related indexes are created:
        - B{objectkeywords_I{lang}}
        - B{istranslated_I{lang}}
        @param lang: language code
        @type lang: string
        """
        self.add_index_for_lang('objectkeywords', lang)
        try:
            self.addIndex('istranslated_%s' % lang, 'FieldIndex')
            self.reindexIndex('istranslated_%s' % lang, self.REQUEST)
        except:
            pass
        try:
            self.addIndex('%s_%s' % ('tags', lang), 'KeywordIndex')
            self.reindexIndex('%s_%s' % ('tags', lang), self.REQUEST)
        except:
            pass

    security.declarePrivate('del_index_for_lang')

    def del_index_for_lang(self, name, lang):
        """
        Delete an index when a language is removed from the portal.
        - B{I{name}_I{lang}}
        @param name: index name
        @type name: string
        @param lang: language code
        @type lang: string
        """
        try:
            self.delIndex('%s_%s' % (name, lang))
        except:
            pass

    security.declarePrivate('del_indexes_for_lang')

    def del_indexes_for_lang(self, lang):
        """
        Delete indexes when a language is removed from the portal.
        @param lang: language code
        @type lang: string
        """
        self.del_index_for_lang('objectkeywords', lang)
        self.del_index_for_lang('istranslated', lang)
        try:
            self.delIndex('%s_%s' % ('tags', lang))
        except:
            pass

    security.declareProtected(view_management_screens, 'manage_maintenance')
    _manage_maintenance = PageTemplateFile('zpt/manage_maintenance', globals())

    def manage_maintenance(self, REQUEST):
        """ maintenance tab """

        ob_path = lambda ob: '/'.join(ob.getPhysicalPath())
        path_ob = lambda p: self.unrestrictedTraverse(p)

        def generate_report():
            found_paths = set(ob_path(ob) for ob in walk_folder(
                self.getSite()))

            cataloged_paths = set()
            broken_paths = set()
            for brain in self():
                broken = False
                try:
                    ob = brain.getObject()
                except:
                    broken = True

                if ob is None or isinstance(ob, BrokenClass):
                    broken = True

                if broken:
                    broken_paths.add(brain.getPath())
                    continue

                cataloged_paths.add(ob_path(ob))

            missing_paths = found_paths - cataloged_paths
            extra_paths = cataloged_paths - found_paths
            ok_paths = found_paths.intersection(cataloged_paths)
            return {
                'missing': set(path_ob(ob) for ob in missing_paths),
                'extra': set(path_ob(ob) for ob in extra_paths),
                'broken': broken_paths,
                'ok': set(path_ob(ob) for ob in ok_paths),
            }

        options = {}
        if REQUEST.get('report', '') == 'on':
            options['report'] = generate_report()

        return self._manage_maintenance(REQUEST, **options)

    security.declareProtected(view_management_screens, 'manage_do_rebuild')

    def manage_do_rebuild(self, REQUEST=None):
        """ maintenance operations for the catalog """

        import logging
        logger = logging.getLogger('CatalogTool')
        errors = []

        def add_to_catalog(ob):
            try:
                self.catalog_object(ob, '/'.join(ob.getPhysicalPath()))
            except Exception as e:
                path = '/'.join(ob.getPhysicalPath())
                logger.error("Error indexing %s: %s", path, e)
                errors.append(path)

        self.manage_catalogClear()
        self._fix_catalog()
        for ob in walk_folder(self.getSite()):
            add_to_catalog(ob)

        if errors:
            logger.warning("Catalog rebuild: %d objects failed to index: %s",
                           len(errors), ', '.join(errors))

        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() +
                                      '/manage_maintenance')

    def _fix_catalog(self):
        _catalog = self._catalog
        if hasattr(_catalog, '_length') and '__len__' in _catalog.__dict__:
            # Old catalogs had a magic __len__ property to get their size; this
            # has been removed in favor of the _length property. There's a
            # migration function (Products.ZCatalog.Catalog.migrate__len__)
            # that removes __len__ and adds _length, but for some reason, some
            # migrated Naaya sites have both properties. In that case we
            # remove __len__.
            del _catalog.__dict__['__len__']
            self._p_changed = True


InitializeClass(CatalogTool)


import logging
_walk_logger = logging.getLogger('CatalogTool.walk')


def _check_broken_children(ob):
    """Log broken sub-objects inside containers (e.g. ExtFile inside NyMediaFile)."""
    try:
        children = ob.objectValues()
    except Exception:
        return
    for child in children:
        if isinstance(child, BrokenClass):
            try:
                path = '/'.join(child.getPhysicalPath())
            except Exception:
                path = '/'.join(ob.getPhysicalPath()) + '/' + getattr(child, 'id', '???')
            _walk_logger.warning(
                'Broken child object: %s  class=%s.%s',
                path, child.__class__.__module__, child.__class__.__name__)


def walk_folder(folder):
    for ob in folder.objectValues():
        if isinstance(ob, BrokenClass):
            try:
                path = '/'.join(ob.getPhysicalPath())
            except Exception:
                path = getattr(ob, 'id', '???')
            _walk_logger.warning(
                'Broken object: %s  class=%s.%s',
                path, ob.__class__.__module__, ob.__class__.__name__)
            continue

        if INyCatalogAware.providedBy(ob):
            _check_broken_children(ob)
            yield ob

        if INyObjectContainer.providedBy(ob) or INyContainer.providedBy(ob):
            for sub_ob in walk_folder(ob):
                yield sub_ob

        if INyCommentable.providedBy(ob):
            for comment_ob in ob.get_comments_list():
                yield comment_ob
