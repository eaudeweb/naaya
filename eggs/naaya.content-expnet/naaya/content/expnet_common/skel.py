import logging

log = logging.getLogger('naaya.content.expnet_common')

def setup_expnet_skel(portal):
    #Create catalog index if it doesn't exist
    catalog_tool = portal.getCatalogTool()

    if not 'topics' in catalog_tool.indexes():
        log.info('Creating ExpNet catalog index "topics"')
        try:
            catalog_tool.addIndex('topics', 'KeywordIndex',
                           extra={'indexed_attrs' : 'topics'})
            catalog_tool.manage_reindexIndex(['topics'])
        except:
            print ( 'Failed to create topics index. Naaya Expert content '
                    'type may not work properly' )

    if not 'title_field' in catalog_tool.indexes():
        log.info('Creating ExpNet catalog index "title_field"')
        try:
            catalog_tool.addIndex('title_field', 'FieldIndex',
                           extra={'indexed_attrs' : 'title'})
            catalog_tool.manage_reindexIndex(['title_field'])
        except:
            print ( 'Failed to create title_field index. Naaya Expert '
                    'Network content types may not work properly.' )
