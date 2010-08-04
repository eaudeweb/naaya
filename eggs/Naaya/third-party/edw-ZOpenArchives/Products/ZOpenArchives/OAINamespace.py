__doc__ = """ Zope OAI Namespace """

from urllib import quote, unquote

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from App.Management import Navigation
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

from utils import processId

oai_dc_defaults = {
    'ns_schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
    'ns_prefix': 'oai_dc',
    'ns_description':
        'Open Archives Initiative metadata format based on Dublin Core',
    'ns_namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'ns_shortname': 'OAI Dublin Core'
}

def manage_addOAINamespace(self, REQUEST=None, **kwargs):
    """ method for adding a new OAI namespace """

    id = processId(kwargs.get('ns_prefix', oai_dc_defaults['ns_prefix']))
    ob = OAINamespace(id, **kwargs)
    self._setObject(id, ob)

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()
                + '/manage_main?update_menu=1')


class OAINamespace(Navigation, SimpleItem, Implicit):
    """ """
    meta_type = 'Open Archive Namespace'

    def __init__(self, id, **kwargs):
        """ """
        self.id = id
        for key, val in oai_dc_defaults.items(): #Set default values
            setattr(self, key, kwargs.get('key', val))

    def title(self):
        """ """
        return self.ns_shortname

    def manage_OAINamespaceUpdate(self, REQUEST=None, **kwargs):
        """ """
        for key, val in oai_dc_defaults.items(): #Set default values
            setattr(self, key, kwargs.get('key', val))

    def get_dict(self):
        dict = {}
        dict['description'] = self.ns_description
        dict['shortname'] = self.ns_shortname
        dict['namespace'] = self.ns_namespace
        dict['prefix'] = self.ns_prefix
        dict['schema'] = self.ns_schema
        return dict
