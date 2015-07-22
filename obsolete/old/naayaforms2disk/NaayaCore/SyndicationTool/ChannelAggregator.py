#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *


manage_addChannelAggregatorForm = PageTemplateFile('zpt/aggregator_manage_add', globals())
def manage_addChannelAggregator(self, id='', title='', channels=[], portlet='', description='', REQUEST=None):
    """ """
    
    channels = [ch for ch in channels if self.getSyndicationTool()._getOb(ch, None)]
    
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_CHANNELAGGREGATOR % self.utGenRandomId(6)
    ob = ChannelAggregator(id, title, channels, description)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannels_aggregator(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ChannelAggregator(SimpleItem):
    """ """

    meta_type = METATYPE_CHANNEL_AGGREGATOR
    icon = 'misc_/NaayaCore/ChannelAggregator.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'Aggregator data', 'action': 'index_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, channels, description):
        """ """
        self.id = id
        self.title = title
        self.channels = channels
        self.description = description

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.delete_portlet_for_object(item)

    #api
    def getRemoteChannelsItems(self):
        #returns a list with all the item data from each remote channel
        return [self.getSyndicationTool()._getOb(rc).getChannelItems_complete() for rc in self.channels]

    def get_channels(self):
        #returns the remote channel objects for each remote channel id stored
        return map(self.getSyndicationTool()._getOb, self.channels)

   #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', channels=[], description='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.channels = [ch for ch in channels if self.getSyndicationTool()._getOb(ch, None)]
        
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/aggregator_properties', globals())

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/aggregator_index', globals())

InitializeClass(ChannelAggregator)