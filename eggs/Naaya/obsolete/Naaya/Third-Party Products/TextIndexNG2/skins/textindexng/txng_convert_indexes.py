
# Replace SearchableText with a TextIndexNG instance

catalog = context.portal_catalog
indexes = catalog.getIndexObjects()

try:
    catalog.manage_delIndex('SearchableText')
except:
    pass

encoding = context.portal_properties.site_properties.default_charset
catalog.manage_addIndex('SearchableText', 'TextIndexNG2', 
                        extra={'default_encoding' : encoding})
catalog.manage_reindexIndex('SearchableText', context.REQUEST)

context.REQUEST.RESPONSE.redirect('txng_maintenance?portal_status_message=SearchableText+converted')    
