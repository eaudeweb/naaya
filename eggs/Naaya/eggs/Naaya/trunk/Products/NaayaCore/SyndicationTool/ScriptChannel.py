
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PythonScripts.PythonScript import PythonScript
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.interfaces import IScriptChannel
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils, get_nsmap, rss_item_for_channel, rss_channel_for_channel

from lxml import etree
from lxml.builder import ElementMaker

manage_addScriptChannelForm = PageTemplateFile('zpt/scriptchannel_manage_add', globals())
def manage_addScriptChannel(self, id='', title='', description='', language=None, type='',
    body='', numberofitems='', portlet='', REQUEST=None):
    """ """
    id = self.utSlugify(id)
    if language is None: language = self.gl_get_selected_language()
    if not id: id = PREFIX_SUFIX_SCRIPTCHANNEL % (self.utGenRandomId(6), language)
    try: numberofitems = abs(int(numberofitems))
    except: numberofitems = 0
    ob = ScriptChannel(id, title, description, language, type, numberofitems)
    self._setObject(id, ob)
    ob = self._getOb(id)
    if not body:
        body = 'return []'
    ob.write(body)
    if portlet:
        self.create_portlet_for_scriptchannel(ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ScriptChannel(PythonScript, utils):
    """ """

    implements(IScriptChannel)

    meta_type = METATYPE_SCRIPTCHANNEL
    icon = 'misc_/NaayaCore/ScriptChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
        )
        +
        (
            PythonScript.manage_options[0],
        )
        +
        PythonScript.manage_options[2:]
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, language, type, numberofitems):
        """ """
        PythonScript.__dict__['__init__'](self, id)
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.numberofitems = numberofitems

    def ZPythonScript_setTitle(self, title):
        if isinstance(title, str):
            title = title.decode('utf-8')
        self.title = title
        self.ZCacheable_invalidate()

    security.declarePrivate('syndicateThis')
    def syndicateThis(self):
        xml = rss_item_for_channel(self)
        return etree.tostring(xml, xml_declaration=False, encoding="utf-8")

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language=None, type='', numberofitems='', REQUEST=None):
        """ """
        if language is None: language = self.gl_get_selected_language()
        try: numberofitems = abs(int(numberofitems))
        except: numberofitems = 0
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.numberofitems = numberofitems
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_properties_html')

    def get_objects_for_rdf(self, attr=None, reversed=False):
        #return the objects to be syndicated
        #sorted by the attribute attr
        objects = self._exec({'context': self, 'container': self}, {}, {})
        if attr is not None:
            return utils.utSortObjsListByAttr(self, objects, attr, reversed)
        return objects

    security.declareProtected(view, 'index_html')
    def index_html(self, feed='', REQUEST=None, RESPONSE=None):
        """ """
        if feed == 'atom':
            return self.syndicateAtom(self, self.get_objects_for_rdf(), self.language)

        s = self.getSite()
        lang = self.language
        if lang == 'auto':
            lang = self.gl_get_selected_language()
        l_items = self.get_objects_for_rdf()
        namespaces = self.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        header = []
        for n in namespaces:
            header.append(str(n))
        rdf_namespace = nsmap['rdf']
        Rdf = ElementMaker(namespace=rdf_namespace, nsmap=nsmap)
        E = ElementMaker(None, nsmap=nsmap)

        xml = Rdf.RDF(rss_channel_for_channel(self, lang))

        channel = xml[0];  items = channel[-1]
        seq = etree.SubElement(items, '{%s}Seq'%rdf_namespace)
        for i in l_items:
            x = etree.SubElement(seq, '{%s}li'%rdf_namespace, resource=i.absolute_url())
        if self.hasImage():
            image = E.image(
                E.title(self.title),
                E.url(self.getImagePath()),
                E.link(s.absolute_url()),
                E.description(self.utToUtf8(self.description))
               )
            xml.append(image)
        received_items = ''.join([i.syndicateThis() for i in l_items])
        received = '<rdf:RDF %s>%s</rdf:RDF>' % (''.join(header), received_items)
        xml_received = etree.XML(received, etree.XMLParser(strip_cdata = False))
        xml.extend(xml_received)
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return etree.tostring(xml, xml_declaration=True, encoding="utf-8")

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/scriptchannel_properties', globals())

InitializeClass(ScriptChannel)
