from time import time
import logging
from StringIO import StringIO
from zope.publisher.browser import BrowserPage
from devel import aoa_devel_hook
import shadow

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class SetUpCatalogIndexes(BrowserPage):
    def __call__(self):
        aoa_devel_hook(__name__)
        aoa_devel_hook(shadow.__name__)
        return set_up_catalog_indexes(self.aq_parent, self.request)

def set_up_catalog_indexes(site, request):
    catalog = site.getCatalogTool()

    log_file = StringIO()
    log_handler = logging.StreamHandler(log_file)
    log.addHandler(log_handler)
    try:
        # remove any existing indexes
        for name in ['viewer_title_en', 'viewer_title_ru', 'viewer_theme',
                     'viewer_main_theme', 'viewer_document_type',
                     'viewer_country', 'viewer_region', 'viewer_geolevel',
                     'viewer_author', 'viewer_year']:
            if catalog._catalog.indexes.has_key(name):
                log.info('removing index %r', name)
                catalog.delIndex(name)

        # add our indexes

        def add_fulltext_index(name):
            log.info('adding text index %r', name)
            catalog.manage_addIndex(name, 'TextIndexNG3', extra={
                'default_encoding': 'utf-8',
                'use_converters': 1,
                'splitter_casefolding': True,
            })

        def add_field_index(name):
            log.info('adding field index %r', name)
            catalog.addIndex(name, 'FieldIndex')

        def add_keyword_index(name):
            log.info('adding keyword index %r', name)
            catalog.addIndex(name, 'KeywordIndex')

        add_fulltext_index('viewer_title_en')
        add_fulltext_index('viewer_title_ru')
        add_keyword_index('viewer_main_theme')
        add_keyword_index('viewer_document_type')
        add_keyword_index('viewer_country')
        add_keyword_index('viewer_region')
        add_field_index('viewer_geolevel')
        add_field_index('viewer_author')
        add_field_index('viewer_year')

        # columns for metadata
        for name in ['viewer_country', 'viewer_main_theme']:
            if catalog._catalog.schema.has_key(name):
                log.info('removing metadata column %r', name)
                catalog.delColumn(name)
            log.info('adding metadata column %r', name)
            catalog.addColumn(name)

        log.info('Reindexing VL...')
        t0 = time()
        site['virtual-library-viewer'].manage_recatalog()
        log.info('%.2f seconds', time()-t0)

        log.info('Reindexing CF...')
        t0 = time()
        site['country-fiches-viewer'].manage_recatalog()
        log.info('%.2f seconds', time()-t0)

    finally:
        log.removeHandler(log_handler)

    return log_file.getvalue()
