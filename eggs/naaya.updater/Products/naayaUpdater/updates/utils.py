def pat(s):
    """ convert from string into a pattern to use with regexps """
    return reduce(lambda s, c: s.replace(c, '\\'+c), '(){}[]+$', s)

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath())

def list_folders_with_custom_index(portal):
    catalog = portal.getCatalogTool()

    for brain in catalog(meta_type='Naaya Folder'):
        folder = brain.getObject()
        if 'index' in folder.objectIds():
            yield folder

def get_standard_template(portal):
    return portal.getLayoutTool().getCurrentSkin().standard_template
