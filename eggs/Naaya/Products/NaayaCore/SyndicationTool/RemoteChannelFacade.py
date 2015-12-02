
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.interfaces import IRemoteChannelFacade
from Products.NaayaCore.constants import *
from RemoteChannel import RemoteChannel

manage_addRemoteChannelFacadeForm = PageTemplateFile('zpt/remotechannelfacade_manage_add', globals())
def manage_addRemoteChannelFacade(self, id='', title='', url='', providername='',
    location='', obtype='news', numbershownitems='', portlet='', REQUEST=None):
    """ """
    id = self.utSlugify(id)
    if not id: id = PREFIX_SUFIX_REMOTECHANNELFACADE % self.utGenRandomId(6)
    try: numbershownitems = abs(int(numbershownitems))
    except: numbershownitems = 0
    ob = RemoteChannelFacade(id, title, url, providername, location, obtype, numbershownitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannelfacade(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RemoteChannelFacade(RemoteChannel):
    """ """

    implements(IRemoteChannelFacade)

    meta_type = METATYPE_REMOTECHANNELFACADE
    icon = 'misc_/NaayaCore/RemoteChannelFacade.gif'

    manage_options = (
        RemoteChannel.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, url, providername, location, obtype, numbershownitems):
        """ """
        RemoteChannel.__dict__['__init__'](self, id, title, url, numbershownitems)
        self.providername = providername
        self.location = location
        self.obtype = obtype

    #api
    def updateChannel(self, uid):
        """ """
        if uid==self.get_site_uid():
            self.harvest_feed()
            if self.get_feed_bozo_exception() is not None: error = self.get_feed_bozo_exception()
            else:
                error = ''
                try:
                    self.generateContent()
                except Exception, l_error:
                    error = l_error
            return str(error)

    security.declarePrivate('generateContent')
    def generateContent(self):
        """
        Generates object in channel's defined location. The objects are by default
        unapproved.
        """
        location_ob = self.utGetObject(self.location)
        if location_ob:
            #start create objects from RDF items
            if self.obtype == 'news':
                #create news objects
                for feed_item in self.get_feed_items():
                    id = self.utToUtf8(feed_item.id.split('/')[-1])
                    ob = location_ob._getOb(id, None)
                    if ob is None:
                        tags = [x['term'] for x in feed_item.tags]
                        keywords = [x.strip() for x in feed_item.ut_keywords.split(',')]
                        subject = self.utListDifference(tags, feed_item.ut_keywords)
                        location_ob.addNySemNews(id=id,
                            creator=feed_item.author,
                            creator_email=feed_item.ut_creator_mail,
                            contact_person=feed_item.ut_contact_name,
                            contact_email=feed_item.ut_contact_mail,
                            contact_phone=feed_item.ut_contact_phone,
                            rights=feed_item.rights,
                            title=feed_item.title_detail['value'],
                            news_type=feed_item.ut_news_type,
                            file_link=feed_item.ut_file_link,
                            file_link_local=feed_item.ut_file_link_local,
                            source=self.providername,
                            source_link=feed_item.ut_source_link,
                            keywords=feed_item.ut_keywords,
                            description=feed_item.dc_description,
                            subject=subject,
                            relation=feed_item.dc_relation,
                            coverage=feed_item.dc_coverage,
                            news_date=self.utConvertDateTimeHTMLToString(feed_item.ut_start_date),
                            lang=feed_item.language)
                        ob = location_ob._getOb(id)
                        ob.approveThis(0, None)
                        self.recatalogNyObject(ob)
            elif self.obtype == 'events':
                #create event objects
                for feed_item in self.get_feed_items():
                    id = self.utToUtf8(feed_item.id.split('/')[-1])
                    ob = location_ob._getOb(id, None)
                    if ob is None:
                        tags = [x['term'] for x in feed_item.tags]
                        keywords = [x.strip() for x in feed_item.ut_keywords.split(',')]
                        subject = self.utListDifference(tags, feed_item.ut_keywords)
                        location_ob.addNySemEvent(id=id,
                            title=feed_item.title_detail['value'],
                            description=feed_item.dc_description,
                            coverage=feed_item.dc_coverage,
                            keywords=feed_item.ut_keywords,
                            creator=feed_item.author,
                            creator_email=feed_item.ut_creator_mail,
                            rights=feed_item.rights,
                            event_type=feed_item.ut_event_type,
                            source=self.providername,
                            source_link=feed_item.ut_source_link,
                            file_link=feed_item.ut_file_link,
                            file_link_copy=feed_item.ut_file_link_copy,
                            subject=subject,
                            relation=feed_item.dc_relation,
                            organizer=feed_item.ut_organizer,
                            duration=feed_item.ut_duration,
                            geozone=feed_item.ut_geozone,
                            address=feed_item.ut_address,
                            start_date=self.utConvertDateTimeHTMLToString(feed_item.ut_start_date),
                            end_date=self.utConvertDateTimeHTMLToString(feed_item.ut_end_date),
                            event_status=feed_item.ut_event_status,
                            contact_person=feed_item.ut_contact_name,
                            contact_email=feed_item.ut_contact_mail,
                            contact_phone=feed_item.ut_contact_phone,
                            lang=feed_item.language)
                        ob = location_ob._getOb(id)
                        ob.approveThis(0, None)
                        self.recatalogNyObject(ob)
        else:
            pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', url='', providername='', location='',
        obtype='news', numbershownitems='', REQUEST=None):
        """ """
        try: numbershownitems = abs(int(numbershownitems))
        except: numbershownitems = self.numbershownitems
        self.title = title
        self.url = url
        self.providername = providername
        self.location = location
        self.obtype = obtype
        self.numbershownitems = numbershownitems
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/remotechannelfacade_properties', globals())

InitializeClass(RemoteChannelFacade)
