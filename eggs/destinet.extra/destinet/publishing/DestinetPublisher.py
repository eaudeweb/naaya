try:
    import simplejson as json
except ImportError:
    import json
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo, getSecurityManager
try: # Zope >= 2.12
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass
import operator

from destinet.registration.core import handle_groups
from Products.NaayaBase.NyContentType import SchemaFormHelper
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
from naaya.core import submitter
from naaya.core.zope2util import ofs_path
from naaya.content.event.event_item import event_add_html, NyEvent
from naaya.content.event.event_item import addNyEvent as original_addNyEvent
from naaya.content.news.news_item import news_add_html, NyNews
from naaya.content.news.news_item import addNyNews as original_addNyNews
from naaya.content.contact.contact_item import NyContact
from naaya.content.contact import contact_item
from naaya.content.url.url_item import NyURL, url_add_html
from naaya.content.url.url_item import addNyURL as original_addNyURL
from naaya.content.file.file_item import NyFile_extfile, file_add_html
from naaya.content.file.file_item import addNyFile as original_addNyFile
from naaya.content.mediafile.mediafile_item import NyMediaFile_extfile, mediafile_add_html
from naaya.content.mediafile.mediafile_item import addNyMediaFile as original_addNyMediaFile
from Products.NaayaContent.NyPublication.NyPublication import (NyPublication,
                                  addNyPublication as original_addNyPublication)
from constants import (ID_PUBLISHER, METATYPE_PUBLISHER, TITLE_PUBLISHER,
                       PERMISSION_DESTINET_PUBLISH)

NaayaPageTemplateFile('zpt/destinet_disseminate', globals(),
                      'destinet_disseminate')
NaayaPageTemplateFile('zpt/destinet_add_to_market', globals(),
                      'destinet_add_to_market')
NaayaPageTemplateFile('zpt/destinet_userinfo', globals(), 'destinet_userinfo')

def manage_addDestinetPublisher(self, REQUEST=None, RESPONSE=None):
    """
    Add a new DestinetPublisher instance (destinet_publisher)

    """
    self._setObject(ID_PUBLISHER,
                    DestinetPublisher(ID_PUBLISHER, TITLE_PUBLISHER))
    if REQUEST is not None:
        RESPONSE.redirect('manage_main')

class DestinetPublisher(SimpleItem):
    """
    DestinetPublisher is the OFS object that holds Destinet publishing views
    (left side menu actions).

    You need the `Destinet Publish Content` permission to use this publishing
    tool. Usually, this permission must be assigned to Authenticated user role.
    Everything published using these forms gets a pointer (back-link) in
    selected target groups and topics. The respective pointers have the same
    contributor and approval state.

    """
    meta_type = METATYPE_PUBLISHER
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security.declarePublic("checkPermission")
    def checkPermission(self):
        return getSecurityManager().checkPermission(PERMISSION_DESTINET_PUBLISH,
                                                    self)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "promote_event")
    def promote_event(self, REQUEST=None, RESPONSE=None):
        """ promote (add) event form """
        return event_add_html(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyEvent")
    def addNyEvent(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create an Event type of object in 'events' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyEvent('', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/promote_event' % self.absolute_url())
            return

        response = original_addNyEvent(self.restrictedTraverse('events'),
                                       '', REQUEST)
        if isinstance(response, NyEvent):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/promote_event' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "promote_news")
    def promote_news(self, REQUEST=None, RESPONSE=None):
        """ promote (add) news form """
        return news_add_html(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyNews")
    def addNyNews(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a News type of object in 'news' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyNews('', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/promote_news' % self.absolute_url())
            return

        response = original_addNyNews(self.restrictedTraverse('News'),
                                      '', REQUEST)
        if isinstance(response, NyNews):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/promote_news' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "disseminate")
    def disseminate(self):
        """ Returns the intermediate page for disseminate your sust. tourism """
        return self.getSite().getFormsTool().getContent({'here': self},
                                                        'destinet_disseminate')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "disseminate_url")
    def disseminate_url(self, REQUEST=None, RESPONSE=None):
        """ Disseminate your sustainable tourism publications or tools (URL) """
        return url_add_html(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyURL")
    def addNyURL(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create an URL type of object in 'resources' folder adding
        * extra validation for topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyURL('', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/disseminate_url' % self.absolute_url())
            return

        response = original_addNyURL(self.restrictedTraverse('resources'),
                                     '', REQUEST)
        if isinstance(response, NyURL):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/disseminate_url' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "disseminate_file")
    def disseminate_file(self, REQUEST=None, RESPONSE=None):
        """ Disseminate your sust. tourism publications or tools (File) """
        return file_add_html(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyFile")
    def addNyFile(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a File type of object in 'resources' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyFile_extfile('', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/disseminate_file' % self.absolute_url())
            return

        response = original_addNyFile(self.restrictedTraverse('resources'),
                                           '', REQUEST)
        if isinstance(response, NyFile_extfile):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/disseminate_file' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "disseminate_mediafile")
    def disseminate_mediafile(self, REQUEST=None, RESPONSE=None):
        """ Disseminate your sust. tourism publications or tools (MediaFile) """
        return mediafile_add_html(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyMediaFile")
    def addNyMediaFile(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a MediaFile type of object in 'resources' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyMediaFile_extfile('', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/disseminate_mediafile' % self.absolute_url())
            return

        response = original_addNyMediaFile(self.restrictedTraverse('resources'),
                                           '', REQUEST)
        if isinstance(response, NyMediaFile_extfile):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/disseminate_mediafile' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "place_on_market")
    def place_on_market(self):
        """ Returns the intermediate page for `Place on global Market..` """
        return self.getSite().getFormsTool().getContent({'here': self},
                                                       'destinet_add_to_market')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "show_on_atlas")
    def show_on_atlas(self, REQUEST=None, RESPONSE=None):
        """ Show your organisation on the global DestiNet Atlas """
        meta_type = 'Naaya Contact'
        form_helper = get_schema_helper_for_metatype(self, meta_type)

        schema_tool = self.getSite().getSchemaTool()
        register_extra_schema = schema_tool['registration']
        register_helper = SchemaFormHelper(register_extra_schema, self)
        groups_widget = register_helper._get_renderer(
            'groups', register_extra_schema['groups-property'], False)

        return self.getFormsTool().getContent({
            'here': self,
            'kind': meta_type,
            'action': 'addNyContact_who_who',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(self, REQUEST),
            'groups_widget':groups_widget,
        }, 'contact_add')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "market_place_contact")
    def market_place_contact(self, REQUEST=None, RESPONSE=None):
        """ Place your product/service on the global sust tour. Market Place """
        meta_type = 'Naaya Contact'
        form_helper = get_schema_helper_for_metatype(self, meta_type)
        return self.getFormsTool().getContent({
            'here': self,
            'kind': meta_type,
            'action': 'addNyContact_market',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(self, REQUEST),
        }, 'contact_add')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "market_place_publication")
    def market_place_publication(self, REQUEST=None, RESPONSE=None):
        """ Place your product/service on the global sust tour. Market Place """
        meta_type = 'Naaya Publication'
        form_helper = get_schema_helper_for_metatype(self, meta_type)
        return self.getFormsTool().getContent({
            'here': self,
            'kind': meta_type,
            'action': 'addNyPublication_market',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(self, REQUEST),
        }, 'publication_add')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "disseminate_publication")
    def disseminate_publication(self, REQUEST=None, RESPONSE=None):
        """ Disseminate your sust. tour publications or tools (NyPublication) """
        meta_type = 'Naaya Publication'
        form_helper = get_schema_helper_for_metatype(self, meta_type)
        return self.getFormsTool().getContent({
            'here': self,
            'kind': meta_type,
            'action': 'addNyPublication_disseminate',
            'form_helper': form_helper,
            'submitter_info_html': submitter.info_html(self, REQUEST),
        }, 'publication_add')

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyContact_who_who")
    def addNyContact_who_who(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a Contact type of object in 'who-who' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        topics = schema_raw_data.get("topics", [])
        if not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyContact('', '').__of__(self)
            form_errors = {'topics': ['Please select at least one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/show_on_atlas' % self.absolute_url())
            return

        response = contact_item.addNyContact(self.restrictedTraverse('who-who'),
                                         '', REQUEST)
        form = REQUEST.form.copy()
        form['username'] = response.contributor
        handle_groups(response, form)
        if isinstance(response, NyContact):
            REQUEST.RESPONSE.redirect(response.absolute_url())
            pass # Contacts are now redirected from post-add event
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/show_on_atlas' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyContact_market")
    def addNyContact_market(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a Contact type of object in 'market-place' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        topics = schema_raw_data.get("topics", [])
        if not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyContact('', '').__of__(self)
            form_errors = {'topics': ['Please select at least one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/market_place_contact' % self.absolute_url())
            return

        response = contact_item.addNyContact(self.restrictedTraverse('market-place'),
                                         '', REQUEST)
        if isinstance(response, NyContact):
            REQUEST.RESPONSE.redirect(response.absolute_url())
            pass # Contacts are now redirected from post-add event
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/market_place_contact' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyPublication_disseminate")
    def addNyPublication_disseminate(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a NyPublication type of object in 'resources' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        target_groups = schema_raw_data.get("target-groups", [])
        topics = schema_raw_data.get("topics", [])
        if not target_groups and not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyPublication('', '', '', '').__of__(self)
            form_errors = {'target-groups':
                       ['Please select at least one Target Group or one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/disseminate_publication' % self.absolute_url())
            return

        response = original_addNyPublication(self.restrictedTraverse('resources'),
                                             '', REQUEST)
        if isinstance(response, NyPublication):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/disseminate_publication' % self.absolute_url())

    security.declareProtected(PERMISSION_DESTINET_PUBLISH, "addNyPublication_market")
    def addNyPublication_market(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        Create a NyPublication type of object in 'market-place' folder adding
        * extra validation for topics and target-groups
        * pointers in the selected topics and target-groups

        """
        schema_raw_data = dict(REQUEST.form)
        topics = schema_raw_data.get("topics", [])
        if not topics:
            # unfortunately we both need _prepare_error_response
            # (on NyContentData) and methods for session (by acquisition)
            ob = NyPublication('', '', '', '').__of__(self)
            form_errors = {'topics': ['Please select at least one Topic']}
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/market_place_publication' % self.absolute_url())
            return

        response = original_addNyPublication(self.restrictedTraverse('market-place'),
                                             '', REQUEST)
        if isinstance(response, NyPublication):
            REQUEST.RESPONSE.redirect(response.absolute_url())
        else: # we have errors
            REQUEST.RESPONSE.redirect('%s/market_place_publication' % self.absolute_url())

#********** Viewing Information ***************#

    security.declarePublic('get_userinfo')
    def get_userinfo(self, ob):
        """ returns a list of objects based on the ob type"""

        site = self.getSite()
        cat = site.getCatalogTool()
        user = self.REQUEST.AUTHENTICATED_USER.getId()
        filters = {'contributor': user}
        if ob == 'events':
            filters['meta_type'] = 'Naaya Event'
            ob_list = cat.search(filters)
        elif ob == 'news':
            filters['meta_type'] = 'Naaya News'
            ob_list = cat.search(filters)
        elif ob == 'topics':
            ob_list = cat.search({'path': ofs_path(site.topics),
                                  'contributor': user})
        elif ob == 'resources':
            ob_list = cat.search({'path': ofs_path(site.resources),
                                  'contributor': user})
        elif ob == 'forums':
            forum_meta_types = ['Naaya Forum Topic', 'Naaya Forum Message']
            ob_list = cat.search({'meta_type': forum_meta_types,
                                    'contributor': user})
        elif ob == 'contacts':
            ob_list = cat.search({'meta_type': 'Naaya Contact',
                                    'contributor': user})
        sorted_list  = site.utSortObjsListByAttr(ob_list, 'releasedate')

        userinfo = [[item.title, item.absolute_url,
                        item.releasedate.strftime('%d %b \'%y')]
                        for item in sorted_list[:50]]
        return json.dumps(userinfo)

    security.declarePublic("userinfo")
    def userinfo(self):
        """ Renders a view with everything the member posted """

        site = self.getSite()
        auth_tool = site.getAuthenticationTool()
        user = self.REQUEST.AUTHENTICATED_USER.getId()
        cat = site.getCatalogTool()

        user_obj = auth_tool.getUser(user)
        contact_obj = None
        if user_obj:
            user_info = {'first_name': user_obj.firstname,
                         'last_name': user_obj.lastname,
                         'email': user_obj.email}
            # --- since destinet.registration: --- #
            container = site['who-who']['destinet-users']
            candidate_brains = cat.search({'path': ofs_path(container),
                                           'contributor': user})
            for candidate_br in candidate_brains:
                try:
                    candidate = candidate_br.getObject()
                except Exception, e:
                    continue
                else:
                    owner_tuple = candidate.getOwnerTuple()
                    if owner_tuple and owner_tuple[1] == user:
                        contact_obj = candidate
                        break
            # --- end --- #
        else:
            user_info = None

        return site.getFormsTool().getContent({'here': self,
                                               'user_info': user_info,
                                               'contact_obj': contact_obj},
                                              'destinet_userinfo')

InitializeClass(DestinetPublisher)
