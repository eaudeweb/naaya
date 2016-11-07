
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime

from Products.NaayaCore.interfaces import ILocalChannel
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils, get_nsmap
from Products.NaayaCore.managers.utils import rss_channel_for_channel
from Products.NaayaCore.managers.utils import rss_item_for_channel

from lxml import etree
from lxml.builder import ElementMaker

manage_addLocalChannelForm = PageTemplateFile('zpt/localchannel_manage_add',
                                              globals())


def manage_addLocalChannel(self, id='', title='', description='',
                           language=None, type='', objmetatype=[],
                           numberofitems='', portlet='', REQUEST=None):
    """ """
    id = self.utSlugify(id)
    if language is None:
        language = self.gl_get_selected_language()
    if not id:
        id = PREFIX_SUFIX_LOCALCHANNEL % (self.utGenRandomId(6), language)
    objmetatype = self.utConvertToList(objmetatype)
    try:
        numberofitems = abs(int(numberofitems))
    except:
        numberofitems = 0
    ob = LocalChannel(id, title, description, language, type, objmetatype,
                      numberofitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_localchannel(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class LocalChannel(SimpleItem, utils):
    """ """

    implements(ILocalChannel)

    meta_type = METATYPE_LOCALCHANNEL
    icon = 'misc_/NaayaCore/LocalChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'View', 'action': 'index_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, language, type, objmetatype,
                 numberofitems):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems

    security.declarePrivate('syndicateThis')

    def syndicateThis(self):
        xml = rss_item_for_channel(self)
        return etree.tostring(xml, xml_declaration=False, encoding="utf-8")

    security.declareProtected(view_management_screens, 'manageProperties')

    def manageProperties(self, title='', description='', language=None,
                         type='', objmetatype=[], numberofitems='',
                         REQUEST=None):
        """ """
        if language is None:
            language = self.gl_get_selected_language()
        objmetatype = self.utConvertToList(objmetatype)
        try:
            numberofitems = abs(int(numberofitems))
        except:
            numberofitems = 0
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    def get_objects_for_rdf(self):
        # return the objects to be syndicated
        l_items = []
        if len(self.objmetatype) > 0:
            l_howmany = -1
            if self.numberofitems != 0:
                l_howmany = self.numberofitems
            l_items = self.query_translated_objects(meta_type=self.objmetatype,
                                                    lang=self.language,
                                                    approved=1,
                                                    howmany=l_howmany)
        now = DateTime()
        return [item for item in l_items
                if getSecurityManager().checkPermission(view, item) and
                (getattr(item, 'topitem', None) or
                 getattr(item, 'expirationdate', now) is None or
                 getattr(item, 'expirationdate', now) + 1 > DateTime())
                ]

    security.declareProtected(view, 'index_html')

    def index_html(self, feed='', REQUEST=None, RESPONSE=None):
        """ """
        if feed == 'atom':
            return self.syndicateAtom(self, self.get_objects_for_rdf(),
                                      self.language)

        s = self.getSite()
        lang = self.language
        if lang == 'auto':
            lang = self.gl_get_selected_language()
        l_items = self.get_objects_for_rdf()
        namespaces = self.getNamespaceItemsList()
        nsmap = nsmap = get_nsmap(namespaces)
        header = []
        for n in namespaces:
            header.append(str(n))
        rdf_namespace = nsmap['rdf']
        Rdf = ElementMaker(namespace=rdf_namespace, nsmap=nsmap)
        E = ElementMaker(None, nsmap=nsmap)

        xml = Rdf.RDF(rss_channel_for_channel(self, lang))

        channel = xml[0]
        items = channel[-1]
        seq = etree.SubElement(items, '{%s}Seq' % rdf_namespace)
        for i in l_items:
            x = etree.SubElement(seq, '{%s}li' % rdf_namespace,
                                 resource=i.absolute_url())
        if self.hasImage():
            image = E.image(
                E.title(self.title),
                E.url(self.getImagePath()),
                E.link(s.absolute_url()),
                E.description(self.utToUtf8(self.description))
                )
            xml.append(image)
        received_items = ''.join([i.syndicateThis() for i in l_items])
        received = '<rdf:RDF %s>%s</rdf:RDF>' % (''.join(header),
                                                 received_items)
        xml_received = etree.XML(received, etree.XMLParser(strip_cdata=False))
        xml.extend(xml_received)
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return etree.tostring(xml, xml_declaration=True, encoding="utf-8")

    # zmi pages
    security.declareProtected(view_management_screens,
                              'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/localchannel_properties',
                                              globals())

InitializeClass(LocalChannel)
