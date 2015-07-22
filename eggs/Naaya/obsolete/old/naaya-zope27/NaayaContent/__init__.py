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
# Cornel Nitu, Eau de Web
# Dragos Chirila

#Python imports
import os
from os import listdir
from os.path import join, isdir
from copy import copy

#Zope imports
from ImageFile import ImageFile
import zLOG

#Product imports
from constants import *
from Products.NaayaBase.NyValidation import NyValidation

misc_ = {
}

#read list of directories
dirs = []
for x in listdir(NAAYACONTENT_PRODUCT_PATH):
    if isdir(join(NAAYACONTENT_PRODUCT_PATH, x)) and x.startswith('Ny'):
        dirs.append(x)

#run imports
content = {}
err_list = []
for x in dirs:
    try:
        module = __import__('%s.%s' % (x, x), globals(), locals())
        module = getattr(module, x) # the top-level package (the name up till the first dot) was returned
        module_path = os.path.dirname(module.__file__)
        content_class = getattr(module, x)
        m = module.METATYPE_OBJECT
        content[m] = {}
        content[m]['product'] = NAAYACONTENT_PRODUCT_NAME
        content[m]['module'] = x
        content[m]['package_path'] = module_path
        content[m]['meta_type'] = m
        content[m]['label'] = module.LABEL_OBJECT
        content[m]['permission'] = module.PERMISSION_ADD_OBJECT
        content[m]['forms'] = copy(module.OBJECT_FORMS)
        content[m]['constructors'] = copy(module.OBJECT_CONSTRUCTORS)
        content[m]['addform'] = module.OBJECT_ADD_FORM
        content[m]['validation'] = issubclass(content_class, NyValidation)
        content[m]['description'] = module.DESCRIPTION_OBJECT
        content[m]['properties'] = module.PROPERTIES_OBJECT
        content[m]['_module'] = module
        content[m]['_class'] = content_class
        style = getattr(module, 'ADDITIONAL_STYLE', None)
        if style:
            content[m]['additional_style'] = style
        zLOG.LOG(NAAYACONTENT_PRODUCT_NAME, zLOG.INFO,
            'Pluggable module "%s" registered' % x)
    except Exception, error:
        err_list.append(x)
        zLOG.LOG(NAAYACONTENT_PRODUCT_NAME, zLOG.WARNING,
            'Pluggable module "%s" NOT registered because %s' % (x, error))

#clean up
for x in err_list:
    dirs.remove(x)

def get_pluggable_content():
    return content

def initialize(context):
    """ """

    #register classes
    for x in content.values():
        context.registerClass(
                x['_class'],
                permission=x['permission'],
                constructors=(getattr(x['_module'], 'manage_add%s_html' % (x['module'],)),
                              getattr(x['_module'], 'add%s' % (x['module'],))),
                icon='%s/www/%s.gif' % (x['module'], x['module']),
                visibility=None)

#meta types as global variables
for x in content.values():
    c = 'METATYPE_%s = %s' % (x['module'].upper(), repr(x['meta_type']))
    exec(c)
    c = 'PERMISSION_ADD_%s = %s' % (x['module'].upper(), repr(x['permission']))
    exec(c)

#images
for x in dirs:
    misc_['%s.gif' % x] = ImageFile('%s/www/%s.gif' % (x, x), globals())
    misc_['%s_marked.gif' % x] = ImageFile('%s/www/%s_marked.gif' % (x, x), globals())
    
    ct_misc = {}
    try:
        exec("from %s import misc_ as ct_misc" % x)
    except ImportError:
        continue
    
    misc_.update(ct_misc)
