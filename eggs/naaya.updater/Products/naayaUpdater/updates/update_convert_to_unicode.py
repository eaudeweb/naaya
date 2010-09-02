from Products.naayaUpdater.updates import UpdateScript

class UpdateConvertToUnicode(UpdateScript):
    """ Update object attributes to unicode"""
    title = 'Update object attributes to unicode'
    creation_date = 'Jan 20, 2010'
    authors = ['David Batranu', 'Alexandru Plugaru']
    description = 'Updates object attributes to unicode if needed. Works with \
 title attribute only.'

    def _update(self, portal):
        self.update_title(portal)
        self.update_portlets(portal)
        return True

    def update_portlets(self, portal):
        ptool = portal.getPortletsTool()
        for portlet in ptool.objectValues():
            if not hasattr(portlet, '_text'):
                continue
            self.convert_attribute(portlet, '_text')

    def update_title(self, portal):
        catalog = portal.getCatalogTool()
        for brain in catalog(title="1") + catalog(title="NOT 1"):
            try:
                obj = brain.getObject()
            except:
                continue
            self.convert_attribute(obj, 'title')

    def convert_attribute(self, obj, attr, enc='utf-8'):
        attribute = getattr(obj, attr)
        if isinstance(attribute, unicode):
            #self.log.debug('Skipping (%s is unicode) %s' % (attr, obj.absolute_url(1)))
            return
        else:
            setattr(obj, attr, unicode(attribute, enc))
            self.log.debug('Updated (%s) %s' % (attr, obj.absolute_url(1)))
            obj._p_changed = 1
