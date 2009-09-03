# Python imports
import os
from copy import copy

# Zope imports
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Application import Application
from OFS.misc_ import Misc_
import zLOG
from zope.interface import Interface
from zope.interface import implements
from zope.configuration.fields import GlobalObject
from zope.app.i18n import ZopeMessageFactory as _

# Products imports
from constants import *
from Products.NaayaBase.NyValidation import NyValidation
from Products.Naaya import NyFolder


class INaayaContent(Interface):
    """ Basic Naaya Content """

class INaayaContentDirective(Interface):
    """
    Register a content
    """
    klass = GlobalObject(
        title=_("Klass"),
        description=_("Python name of a klass which can create the"
                      " implementation object.  This must identify an"
                      " object in a module using the full dotted name."),
        required=True,
    )

class NaayaContent(object):
    """ NaayaContent abstract type """
    implements(INaayaContent)
    _contents = {}
    _misc = {}
    _constants = {}

    @property
    def contents(self):
        return self._contents

    @property
    def misc(self):
        return self._misc

    @property
    def constants(self):
        return self._constants

    def __call__(self, key):
        return self._contents.get(key)

def register_naaya_content(_context, klass, **kwargs):
    """ """
    _contents = NaayaContent._contents
    _misc = NaayaContent._misc
    _constants = NaayaContent._constants

    if not klass:
        raise TypeError("No klass provided")

    name = getattr(klass, 'METATYPE_OBJECT', None)
    if not name:
        raise TypeError("Invalid klass: meta_type property is empty or not defined")

    module = klass
    module_string = module.__name__.split('.')[-1]
    import_string = module_string.lower()[2:] #NyFile -> file
    content_class = module.__dict__[module_string]
    module_path = os.path.dirname(module.__file__)
    meta_type = module.METATYPE_OBJECT
    this_content = {}
    this_content['product'] = NAAYACONTENT_PRODUCT_NAME
    this_content['module'] = module_string
    this_content['package_path'] = module_path
    this_content['meta_type'] = meta_type
    this_content['label'] = module.LABEL_OBJECT
    this_content['permission'] = module.PERMISSION_ADD_OBJECT
    this_content['forms'] = copy(module.OBJECT_FORMS)
    this_content['constructors'] = copy(module.OBJECT_CONSTRUCTORS)
    this_content['addform'] = module.OBJECT_ADD_FORM
    this_content['validation'] = issubclass(content_class, NyValidation)
    this_content['description'] = module.DESCRIPTION_OBJECT
    this_content['properties'] = module.PROPERTIES_OBJECT
    this_content['default_schema'] = getattr(module, 'DEFAULT_SCHEMA', None) # TODO: 'DEFAULT_SCHEMA' should be mandatory
    this_content['_module'] = module
    this_content['_class'] = content_class
    style = getattr(module, 'ADDITIONAL_STYLE', None)
    if style:
        this_content['additional_style'] = style
    _contents[meta_type] = this_content

    # meta types in the constants dict
    _constants['METATYPE_%s' % module_string.upper()] = meta_type
    _constants['PERMISSION_ADD_%s' % module_string.upper()] = this_content['permission']

    # images
    _misc['%s.gif' % module_string] = ImageFile('%s/www/%s.gif' % (module_path, module_string), globals())
    _misc['%s_marked.gif' % module_string] = ImageFile('%s/www/%s_marked.gif' % (module_path, module_string), globals())
    ct_misc = {}
    try:
        exec("from naaya.content.%s import misc_ as ct_misc" % import_string)
    except ImportError:
        pass
    else:
        _misc.update(ct_misc)

    # register _misc into Zope
    if not Application.misc_.__dict__.has_key('NaayaContent'):
        Application.misc_.__dict__['NaayaContent'] = Misc_('NaayaContent', _misc)
    else:
        Application.misc_.__dict__['NaayaContent'].__dict__['_d'].update(_misc)

    # used by site_header
    _constants['METATYPE_FOLDER'] = 'Naaya Folder'

    security = ClassSecurityInfo()
    NyFolder.NyFolder.security = security

    if meta_type != 'Naaya Folder':
        for cns in _contents[meta_type]['constructors']:
            c = 'from naaya.content.%s import %s' % (import_string, module_string)
            exec(c)
            c = 'NyFolder.NyFolder.%s = %s.%s' % (cns, module_string, cns)
            exec(c)
            NyFolder.NyFolder.security.declareProtected(_contents[meta_type]['permission'], cns)

    InitializeClass(NyFolder.NyFolder)
    # log success
    zLOG.LOG(NAAYACONTENT_PRODUCT_NAME, zLOG.INFO, 'Pluggable module "%s" registered' % module_string)

