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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Batranu David, Eau de Web
# Cornel Nitu, Eau de Web
# Dragos Chirila


content_list = [
    'NyConsultation',
    'NyContact',
    'NyDocument',
    'NyEvent',
    'NyExFile',
    'NyFile',
    'NyGeoPoint',
    'NyMediaFile',
    'NyNews',
    'NyPointer',
    'NyPublication',
    'NySimpleConsultation',
    'NyTalkBackConsultation',
    'NySMAPExpert',
    'NySMAPProject',
    'NyStory',
    "NyURL",
]
content_list = None

#Python imports
import os
from copy import copy

#Zope imports
from App.ImageFile import ImageFile
import zLOG

#Product imports
from constants import *
from Products.NaayaBase.NyValidation import NyValidation

def _list_dirs():
    """ read list of directories for Ny*** content types """
    if content_list:
        return content_list
    else:
        content_path = Globals.package_home(globals())
        dirs = []
        for x in os.listdir(content_path):
            if os.path.isdir(os.path.join(content_path, x)) and x.startswith('Ny'):
                dirs.append(x)
        return dirs

def _discover_content_types():
    """ Walks through the NaayaContent package, finding all Ny*** packages """

    misc_ = {}
    constants = {}

    dirs = _list_dirs()

    #run imports
    content = {}
    err_list = []

    for x in dirs:
        try:
            module = __import__('%s.%s' % (x, x), globals(), locals()) # __init__.py
            module = getattr(module, x) # the top-level package (the name up till the first dot) was returned (x.py)
            module_path = os.path.dirname(module.__file__)
            content_class = getattr(module, x)
            m = module.METATYPE_OBJECT
            this_content = {}
            this_content['product'] = NAAYACONTENT_PRODUCT_NAME
            this_content['module'] = x
            this_content['package_path'] = module_path
            this_content['meta_type'] = m
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
            content[m] = this_content
            zLOG.LOG(NAAYACONTENT_PRODUCT_NAME, zLOG.INFO,
                'Pluggable module "%s" registered' % x)
        except Exception, error:
            zLOG.LOG(NAAYACONTENT_PRODUCT_NAME, zLOG.WARNING,
                'Pluggable module "%s" NOT registered because %s' % (x, error))

    # meta types in the constants dict
    for x in content.values():
        constants['METATYPE_%s' % x['module'].upper()] = x['meta_type']
        constants['PERMISSION_ADD_%s' % x['module'].upper()] = x['permission']

    # images
    for x in content.keys():
        x, x_path = content[x]['module'], content[x]['package_path']
        misc_['%s.gif' % x] = ImageFile('%s/www/%s.gif' % (x_path, x), globals())
        misc_['%s_marked.gif' % x] = ImageFile('%s/www/%s_marked.gif' % (x_path, x), globals())

        ct_misc = {}
        try:
            exec("from Products.NaayaContent.%s import misc_ as ct_misc" % x)
        except ImportError:
            continue

        misc_.update(ct_misc)

    # TODO: does anybody use these 2 values? if not, remove them.
    constants['METATYPE_FOLDER'] = 'Naaya Folder'
    constants['PERMISSION_ADD_FOLDER'] = 'Naaya - Add Naaya Folder objects'

    return {'content': content, 'constants': constants, 'misc_': misc_}

_discovered_content = None
def _get_content_types():
    """ make sure _discover_content_types has been run, and return its output """
    global _discovered_content
    if not _discovered_content:
        _discovered_content = _discover_content_types()
    return _discovered_content

def get_constant(name):
    """ returns a constant of the form METATYPE_*** or PERMISSION_ADD_*** """
    return _get_content_types()['constants'][name]

def get_pluggable_content():
    return _get_content_types()['content']

def initialize(context):
    """ """

    #register classes
    for x in _get_content_types()['content'].values():
        context.registerClass(
                x['_class'],
                permission=x['permission'],
                constructors=(getattr(x['_module'], 'manage_add%s_html' % (x['module'],)),
                              getattr(x['_module'], 'add%s' % (x['module'],))),
                icon='%s/www/%s.gif' % (x['package_path'], x['module']),
                visibility=None)

misc_ = _get_content_types()['misc_']

# TODO: we still have global constants for the content types, for backwards compatibility
for cname, cvalue in _get_content_types()['constants'].iteritems():
    exec('%s = "%s"' % (cname, cvalue))


