# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

class UpdateConvertToUnicode(UpdateScript):
    """ Update object attributes to unicode"""
    id = 'update_convert_to_unicode'
    title = 'Update object attributes to unicode'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Jan 20, 2010')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = 'Updates object attributes to unicode if needed. Currently only works for Naaya Local Channel `title` and Naaya Portlet `_text`'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        self.update_local_channels(portal)
        self.update_portlets(portal)
        return True

    def update_portlets(self, portal):
        ptool = portal.getPortletsTool()
        for portlet in ptool.objectValues():
            if not hasattr(portlet, '_text'):
                continue
            self.convert_attribute(portlet, '_text')

    def update_local_channels(self, portal):
        syndication = portal.getSyndicationTool()
        lchannels = syndication.objectValues(['Naaya Local Channel'])
        for channel in lchannels:
            self.convert_attribute(channel, 'title')

    def convert_attribute(self, obj, attr, enc='utf-8'):
        attribute = getattr(obj, attr)
        if isinstance(attribute, unicode):
            self.log.debug('Skipping (%s is unicode) %s' % (attr, obj.absolute_url(1)))
            return
        else:
            setattr(obj, attr, unicode(attribute, enc))
            self.log.debug('Updated (%s) %s' % (attr, obj.absolute_url(1)))
            obj._p_changed = 1
