
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import urllib2

from Products.NaayaCore.interfaces import IRemoteChannel
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.NyFeed import NyFeed
from Products.NaayaBase.countries import language_from_country_code

manage_addRemoteChannelForm = PageTemplateFile('zpt/remotechannel_manage_add', globals())
def manage_addRemoteChannel(self, id='', title='', url='', numbershownitems='', portlet='', filter_by_language='',
        automatic_translation_portlet='', REQUEST=None):
    """ """
    id = self.utSlugify(id)
    if not id: id = PREFIX_SUFIX_REMOTECHANNEL % self.utGenRandomId(6)
    try: numbershownitems = abs(int(numbershownitems))
    except: numbershownitems = 0
    ob = RemoteChannel(id, title, url, numbershownitems, filter_by_language)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannel(self._getOb(id))
    if automatic_translation_portlet:
        self.create_automatic_translation_portlet_for_remotechannel(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RemoteChannel(SimpleItem, NyFeed, utils):
    """ """

    implements(IRemoteChannel)

    meta_type = METATYPE_REMOTECHANNEL
    icon = 'misc_/NaayaCore/RemoteChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'Update information', 'action': 'manage_update_html'},
            {'label': 'Channel data', 'action': 'index_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    filter_by_language = ''
    harvester_name = None

    def __init__(self, id, title, url, numbershownitems, filter_by_language):
        """ """
        self.id = id
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems
        self.filter_by_language = filter_by_language
        NyFeed.__dict__['__init__'](self)

    #api
    def get_feed_url(self):
        #method from NyFeed
        return self.url

    def set_new_feed_url(self, new_url):
        #method from NyFeed
        self.url = new_url
        self._p_changed = 1


    def getFilteredChannelItems(self):
        #returns a list of dictionaries containing channel item information
        #if the item corresponds to the current selected site language
        lang = self.gl_get_selected_language().lower()
        L = self._getAllChannelItems({'summary_detail': 'summary_detail',
                                      'summary': 'summary',
                                      'date': 'modified'})
        f_lang = self.get_feed_lang()
        ret = []
        for item in L:
            try:
                s_lang = item['summary_detail']
            except KeyError:
                s_lang = None
            if (s_lang != None and s_lang == lang) or f_lang == lang:
                ret.append(item)
        if self.numbershownitems > 0: return ret[:self.numbershownitems]
        else: return ret

    def getChannelItems(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        if self.filter_by_language:
            L = self.getFilteredChannelItems()
        else:
            L = self.getAllChannelItems()
        if self.numbershownitems > 0: return L[:self.numbershownitems]
        else: return L

    def getChannelItems_complete(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        if self.filter_by_language:
            L = self.getFilteredChannelItems()
        else:
            L = self._getAllChannelItems({'summary': 'summary', 'date': 'modified'})
        if self.numbershownitems > 0: return L[:self.numbershownitems]
        else: return L

    def getAllChannelItems(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        return self._getAllChannelItems({'summary': 'summary', 'date': 'modified'})

    def _getAllChannelItems(self, extra_tags={}):
        """Returns a list of dictionaries for each channel item with a link and a title.

            Only the link and title values are stored in the dictionary.
            To get the information from other tags, use the extra_tags parameter.

            @param extra_tags: mapping between the dictionary key and the
                               feed tag, e.g. {'date': 'modified'}
        """
        mandatory_tags = ['link', 'title'] # Naaya needs these tags
        L = []
        for feed_item in self.get_feed_items():
            x = {}
            incomplete_feed = False
            for tag in mandatory_tags:
                v = feed_item.get(tag, None)
                if v is None:
                    incomplete_feed = True
                    break
                x[tag] = v
            if incomplete_feed:
                continue
            for key, tag in extra_tags.items():
                v = feed_item.get(tag, None)
                if v is not None:
                    x[key] = v
            L.append(x)
        return L

    def updateChannel(self, uid):
        """ """
        if uid==self.get_site_uid():
            self.harvest_feed(self.get_http_proxy(), self.harvester_name)
            if self.get_feed_bozo_exception() is not None: error = self.get_feed_bozo_exception()
            else: error = ''
            return str(error)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', url='', numbershownitems='', filter_by_language='', harvester_name='', REQUEST=None):
        """ """
        try: numbershownitems = abs(int(numbershownitems))
        except: numbershownitems = self.numbershownitems
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems
        self.filter_by_language = filter_by_language
        if harvester_name == '':
            self.harvester_name = None
        else:
            self.harvester_name = harvester_name
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    def get_language_from_domain(self):
        """ """
        # get main domain name
        rq = urllib2.Request(self.url)
        host = rq.get_host()
        idx = host.rfind('.')
        main_domain = host[idx+1:]

        try:
            language = language_from_country_code(main_domain)
            return language
        except KeyError:
            return None


    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/remotechannel_properties', globals())

    security.declareProtected(view_management_screens, 'manage_update_html')
    manage_update_html = PageTemplateFile('zpt/remotechannel_update', globals())

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/remotechannel_index', globals())

InitializeClass(RemoteChannel)
