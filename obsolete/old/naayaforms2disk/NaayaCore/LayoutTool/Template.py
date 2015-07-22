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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join, isfile


#Zope imports
from OFS.History import Historical, html_diff
from OFS.Cache import Cacheable
from OFS.Traversable import Traversable
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.NaayaCore.constants import *


manage_addTemplateForm = PageTemplateFile('zpt/template_add', globals())
def manage_addTemplate(self, id='', title='', file='', REQUEST=None):
    """ """
    content_type = None
    #if file != '':
    #    if file.filename:
    #        headers = getattr(file, 'headers', None)
    #        content_type = headers.get('content_type')
    content = ''
    if isinstance(file,str) and isfile(file):
        content = self.futRead(file, 'r')
        #content = zptCache.get(self.path)
    elif isinstance(file,str) and file == '':
        content = file
    else:
        if hasattr(file, 'filename'):
            headers = getattr(file, 'headers', None)
            content_type = headers.get('content_type')
            content = file

    ob = Template(id, title, content, content_type)
    
    if file != '' and isinstance(file,str):
        ob.path = file
    else:
        ob.path = None
        ob.setCustomized(True)
        
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

from Products.NaayaCore.managers.utils import file_utils

#class TemplateCache:
#"""Implements template caching"""
#    _cache = {}
#    
#    def get(self, path):
#        """
#        Retrieve an element from cache
#        @param id: Path of the element to be retrieved
#        @return Content if found in cache or None
#        """
#        if path in self._cache:
#            print 'Cache hit for %s' % (path)
#            return self._cache[ path ]
#        else:
#            print 'Cache miss for %s' % (path)
#            return self._load_in_cache(path)
#
#    def _load_in_cache(self, path):
#        content = open(path, 'r').read()
#        self._cache[ path ] = content
#        return content
#
#    def invalidate(self, path):
#        self._load_in_cache(path)
#
#zptCache = TemplateCache()

class Template(ZopePageTemplate):
    """
    """
    
    meta_type = METATYPE_TEMPLATE
    icon = 'misc_/NaayaCore/Template.gif'

    manage_options = (
    {'label':'Edit', 'action':'pt_editForm',
     'help': ('PageTemplates', 'PageTemplate_Edit.stx')},
    {'label':'View modifications', 'action':'pt_viewModifications'}
    ) + PropertyManager.manage_options \
    + Historical.manage_options \
    + SimpleItem.manage_options \
    + Cacheable.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, text, content_type):
        """ """
        ZopePageTemplate.__dict__['__init__'](self, id, text, content_type)
        self.title = title
        self.path = None
        self.customized = False

    def __call__(self, context={}, *args):
        """ """
        import time
        start = time.time()
        ret = None
        if not context.has_key('args'):
            context['args'] = args
        if self.customized:
            print "'%s' Form is customized. Serving from ZODB" % (self.id)
            
            ret = self.pt_render(extra_context=context)
        else:
            if self.path:
                #Read file from disk
                print 'Serving form from disk (%s) ' % self.path 
                content = open(self.path, 'r').read()
                #content = zptCache.get(self.path)
                self._text = content
                
                ret = self.pt_render(extra_context=context)
            else:
                
                ret = self.pt_render(extra_context=context)
        stop = time.time()
        print 'took %s seconds' % ((stop*1000)-(start*1000))
        return ret


    def pt_editAction(self, REQUEST, title, text, content_type, expand):
        """Change the title and document."""
        #print 'pd_etitAction'
        self.setCustomized(True)
        return super(Template, self).pt_editAction(REQUEST, title, text, content_type, expand)


    def PUT(self, REQUEST, RESPONSE):
        """We override PUT in order to mark the form as customized when 
        modifying it from FTP or WebDAV"""
        #print 'PUT called'
        self.setCustomized(True)
        return super(Template, self).PUT(REQUEST, RESPONSE)


    def setCustomized(self, customized=True, copyContents=True):
        """
        Set the form to be customized or not. Customized forms are served from
        ZODB while forms not customized are loaded directly from disk
        @param customized  Boolean value setting form customized(True) or not(False). Default True
        @param copyContents If customized is False, if copyContents is True, content is copied into ZODB from disk file, otherwise no. Default True
        @return: Nothing
        """
        self.customized = customized
        if self.customized:
            self.icon = 'misc_/NaayaCore/TemplateCustomized.gif'
        else:
            self.icon = 'misc_/NaayaCore/Template.gif'
            if self.path and self.path != '' and isfile(self.path):
                if copyContents:
                    print 'Restoring content from disk into _text from %s' % (self.path)
                    content = open(self.path, 'r').read()
                    #content = zptCache.get(self.path)
                    self._text = content


    def isCustomized(self):
        return self.customized


    def setPath(self, path):
        self.path = path


    def getPath(self):
        """ """
        return self.path


    def getText(self):
        return self._text


    def getOriginalContent(self):
        if self.path and self.path != '':
            return open(self.path, 'r').read()
        else:
            return 'This form has no disk version'


    security.declarePublic(view, 'pt_unCustomize')
    def pt_unCustomize(self):
        """ Restoring form from disk """
        print "Restoring form from disk"
        self.setCustomized(False)
        return self.pt_editForm()


    security.declarePublic(view, 'pt_startCustomization')
    def pt_startCustomization(self):
        """Starting to customize the form"""
        print "Starting to customize the form"
        self.setCustomized(True)
        return self.pt_editForm()


    def om_icons(self):
        """ """
        icons = ({'path': self.icon, 'alt': self.meta_type, 'title': self.meta_type},)
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif', 'alt': 'Error', 'title': 'This template has an error'},)
        return icons

    security.declareProtected(view, 'pt_editForm')
    pt_editForm = PageTemplateFile('zpt/ptEdit', globals())
    
    security.declareProtected(view, 'pt_viewModifications')
    pt_viewModifications = PageTemplateFile('zpt/ptViewModifications', globals(), __name__='pt_viewModifications')


InitializeClass(Template)
