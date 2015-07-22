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
import string
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports
from Products.Naaya.constants import *
#from Products.NaayaContent import *

class skel_struct:
    def __init__(self):
        self.forms = None
        self.layout = None
        self.syndication = None
        self.pluggablecontenttypes = None
        self.portlets = None
        self.properties = None
        self.emails = None
        self.security = None
        self.notification = None
        self.others = None

class forms_struct:
    def __init__(self):
        self.forms = []

class form_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class layout_struct:
    def __init__(self, default_skin_id, default_scheme_id):
        self.skins = []
        self.default_skin_id = default_skin_id
        self.default_scheme_id = default_scheme_id

class skin_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.templates = []
        self.schemes = []

class template_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class scheme_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.styles = []
        self.images = []

class style_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class image_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class syndication_struct:
    def __init__(self):
        self.namespaces = []
        self.channeltypes = []
        self.scriptchannels = []
        self.localchannels = []
        self.remotechannels = []

class namespace_struct:
    def __init__(self, id, prefix, value):
        self.id = id
        self.prefix = prefix
        self.value = value

class channeltype_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class scriptchannel_struct:
    def __init__(self, id, title, description, language, type, numberofitems, portlet):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.numberofitems = numberofitems
        self.portlet = int(portlet)

class localchannel_struct:
    def __init__(self, id, title, description, language, type, objmetatype, numberofitems):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.type = type
        self.objmetatype = objmetatype
        self.numberofitems = numberofitems

class remotechannel_struct:
    def __init__(self, id, title, url, numbershownitems):
        self.id = id
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems

class pluggablecontenttypes_struct:
    def __init__(self):
        self.pluggablecontenttypes = []

class pluggablecontenttype_struct:
    def __init__(self, meta_type, action):
        self.meta_type = meta_type
        self.action = action

class portlets_struct:
    def __init__(self, left, center):
        self.left = left
        self.center = center
        self.portlets = []
        self.linkslists = []
        self.reflists = []
        self.reftrees = []

class portlet_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class linkslist_struct:
    def __init__(self, id, title, portlet):
        self.id = id
        self.title = title
        self.portlet = portlet
        self.links = []

class link_struct:
    def __init__(self, id, title, description, url, relative, permission, order):
        self.id = id
        self.title = title
        self.description = description
        self.url = url
        self.relative = relative
        self.permission = permission
        self.order = order

class reflist_struct:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.items = []

class item_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class reftree_struct:
    def __init__(self, id):
        self.id = id
        self.properties = {}
        self.nodes = []

class property_struct:
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang

class node_struct:
    def __init__(self, id, parent, pickable):
        self.id = id
        self.parent = parent
        self.pickable = pickable
        self.properties = {}

class properties_struct:
    def __init__(self):
        self.contenttypes = []
        self.languages = []

class language_struct:
    def __init__(self, code):
        self.code = code

class contenttype_struct:
    def __init__(self, id, title, picture):
        self.id = id
        self.title = title
        self.picture = picture

class emails_struct:
    def __init__(self):
        self.emailtemplates = []

class emailtemplate_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class security_struct:
    def __init__(self):
        self.grouppermissions = []
        self.roles = []

class permission_struct:
    """ """
    def __init__(self, name, description, permissions):
        """ """
        self.name = name
        self.description = description
        self.permissions = permissions

class role_struct:
    """ """
    def __init__(self, name, grouppermissions, permissions):
        """ """
        self.name = name
        self.grouppermissions = grouppermissions
        self.permissions = permissions

class notification_struct:
    def __init__(self):
        self.newsmetatypes = []
        self.uploadmetatypes = []
        self.foldermetatypes = []

class newsmetatype_struct:
    def __init__(self, meta_type, action):
        self.meta_type = meta_type
        self.action = action

class uploadmetatype_struct:
    def __init__(self, meta_type, action):
        self.meta_type = meta_type
        self.action = action

class foldermetatype_struct:
    def __init__(self, meta_type, action):
        self.meta_type = meta_type
        self.action = action

class others_struct:
    def __init__(self):
        self.favicon = None
        self.robots = None
        self.sitemap_xml = None
        self.images = None
        self.submit_unapproved = None
        self.nyexp_schema = None

class nyexp_schema_struct:
    def __init__(self, url):
        self.url = url

class saxstack_struct:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

class skel_handler(ContentHandler):
    """ """

    def __init__(self):
        self.root = None
        self.stack = []

    def startElement(self, name, attrs):
        """ """
        if name == 'skel':
            obj = skel_struct()
            stackObj = saxstack_struct('skel', obj)
            self.stack.append(stackObj)
        elif name == 'forms':
            obj = forms_struct()
            stackObj = saxstack_struct('forms', obj)
            self.stack.append(stackObj)
        elif name == 'form':
            obj = form_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('form', obj)
            self.stack.append(stackObj)
        elif name == 'layout':
            obj = layout_struct(attrs['default_skin_id'].encode('utf-8'), attrs['default_scheme_id'].encode('utf-8'))
            stackObj = saxstack_struct('layout', obj)
            self.stack.append(stackObj)
        elif name == 'skin':
            obj = skin_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('skin', obj)
            self.stack.append(stackObj)
        elif name == 'template':
            obj = template_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('template', obj)
            self.stack.append(stackObj)
        elif name == 'scheme':
            obj = scheme_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('scheme', obj)
            self.stack.append(stackObj)
        elif name == 'style':
            obj = style_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('style', obj)
            self.stack.append(stackObj)
        elif name == 'image':
            obj = image_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('image', obj)
            self.stack.append(stackObj)
        elif name == 'syndication':
            obj = syndication_struct()
            stackObj = saxstack_struct('syndication', obj)
            self.stack.append(stackObj)
        elif name == 'namespace':
            obj = namespace_struct(attrs['id'].encode('utf-8'), attrs['prefix'].encode('utf-8'), attrs['value'].encode('utf-8'))
            stackObj = saxstack_struct('namespace', obj)
            self.stack.append(stackObj)
        elif name == 'channeltype':
            obj = channeltype_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('namespace', obj)
            self.stack.append(stackObj)
        elif name == 'scriptchannel':
            obj = scriptchannel_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['language'].encode('utf-8'), attrs['type'].encode('utf-8'), attrs['numberofitems'].encode('utf-8'), attrs['portlet'].encode('utf-8'))
            stackObj = saxstack_struct('scriptchannel', obj)
            self.stack.append(stackObj)
        elif name == 'localchannel':
            obj = localchannel_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['language'].encode('utf-8'), attrs['type'].encode('utf-8'), attrs['objmetatype'].encode('utf-8'), attrs['numberofitems'].encode('utf-8'))
            stackObj = saxstack_struct('localchannel', obj)
            self.stack.append(stackObj)
        elif name == 'remotechannel':
            obj = remotechannel_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['url'].encode('utf-8'), attrs['numbershownitems'].encode('utf-8'))
            stackObj = saxstack_struct('remotechannel', obj)
            self.stack.append(stackObj)
        elif name == 'linkslist':
            obj = linkslist_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['portlet'].encode('utf-8'))
            stackObj = saxstack_struct('linkslist', obj)
            self.stack.append(stackObj)
        elif name == 'link':
            if len(self.stack) >=2:
                obj = link_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['url'].encode('utf-8'), attrs['relative'].encode('utf-8'), attrs['permission'].encode('utf-8'), attrs['order'].encode('utf-8'))
                stackObj = saxstack_struct('link', obj)
                self.stack.append(stackObj)
        elif name == 'reflist':
            obj = reflist_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['description'].encode('utf-8'))
            stackObj = saxstack_struct('reflist', obj)
            self.stack.append(stackObj)
        elif name == 'item':
            if len(self.stack) >=2:
                obj = item_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
                stackObj = saxstack_struct('item', obj)
                self.stack.append(stackObj)
        elif name == 'reftree':
            obj = reftree_struct(attrs['id'].encode('utf-8'))
            stackObj = saxstack_struct('reftree', obj)
            self.stack.append(stackObj)
        elif name == 'node':
            if len(self.stack) >=2:
                obj = node_struct(attrs['id'].encode('utf-8'), attrs['parent'].encode('utf-8'), attrs['pickable'].encode('utf-8'))
                stackObj = saxstack_struct('node', obj)
                self.stack.append(stackObj)
        elif name == 'pluggablecontenttypes':
            obj = pluggablecontenttypes_struct()
            stackObj = saxstack_struct('pluggablecontenttypes', obj)
            self.stack.append(stackObj)
        elif name == 'pluggablecontenttype':
            obj = pluggablecontenttype_struct(attrs['meta_type'].encode('utf-8'), attrs['action'].encode('utf-8'))
            stackObj = saxstack_struct('pluggablecontenttype', obj)
            self.stack.append(stackObj)
        elif name == 'portlets':
            obj = portlets_struct(attrs['left'].encode('utf-8'), attrs['center'].encode('utf-8'))
            stackObj = saxstack_struct('portlets', obj)
            self.stack.append(stackObj)
        elif name == 'portlet':
            obj = portlet_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('portlet', obj)
            self.stack.append(stackObj)
        elif name == 'properties':
            obj = properties_struct()
            stackObj = saxstack_struct('properties', obj)
            self.stack.append(stackObj)
        elif name == 'language':
            obj = language_struct(attrs['code'].encode('utf-8'))
            stackObj = saxstack_struct('language', obj)
            self.stack.append(stackObj)
        elif name == 'contenttype':
            obj = contenttype_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'), attrs['picture'].encode('utf-8'))
            stackObj = saxstack_struct('contenttype', obj)
            self.stack.append(stackObj)
        elif name == 'emails':
            obj = emails_struct()
            stackObj = saxstack_struct('emails', obj)
            self.stack.append(stackObj)
        elif name == 'emailtemplate':
            obj = emailtemplate_struct(attrs['id'].encode('utf-8'), attrs['title'].encode('utf-8'))
            stackObj = saxstack_struct('emailtemplate', obj)
            self.stack.append(stackObj)
        elif name == 'security':
            obj = security_struct()
            stackObj = saxstack_struct('security', obj)
            self.stack.append(stackObj)
        elif name == 'grouppermissions':
            obj = permission_struct(attrs['name'].encode('utf-8'), attrs['description'].encode('utf-8'), attrs['permissions'].encode('utf-8').split(','))
            stackObj = saxstack_struct('grouppermissions', obj)
            self.stack.append(stackObj)
        elif name == 'role':
            obj = role_struct(attrs['name'].encode('utf-8'), attrs['grouppermissions'].encode('utf-8').split(','), attrs['permissions'].encode('utf-8').split(','))
            stackObj = saxstack_struct('role', obj)
            self.stack.append(stackObj)
        elif name == 'notification':
            obj = notification_struct()
            stackObj = saxstack_struct('notification', obj)
            self.stack.append(stackObj)
        elif name == 'newsmetatype':
            obj = newsmetatype_struct(attrs['meta_type'].encode('utf-8'), attrs['action'].encode('utf-8'))
            stackObj = saxstack_struct('newsmetatype', obj)
            self.stack.append(stackObj)
        elif name == 'uploadmetatype':
            obj = uploadmetatype_struct(attrs['meta_type'].encode('utf-8'), attrs['action'].encode('utf-8'))
            stackObj = saxstack_struct('uploadmetatype', obj)
            self.stack.append(stackObj)
        elif name == 'foldermetatype':
            obj = foldermetatype_struct(attrs['meta_type'].encode('utf-8'), attrs['action'].encode('utf-8'))
            stackObj = saxstack_struct('foldermetatype', obj)
            self.stack.append(stackObj)
        elif name == 'others':
            obj = others_struct()
            stackObj = saxstack_struct('others', obj)
            self.stack.append(stackObj)
        elif name == 'favicon':
            pass
        elif name == 'robots':
            pass
        elif name == 'images':
            pass
        elif name == 'sitemap_xml':
            pass
        elif name == 'submit_unapproved':
            pass
        elif name == 'nyexp_schema':
            obj = nyexp_schema_struct(attrs['url'].encode('utf-8'))
            stackObj = saxstack_struct('nyexp_schema', obj)
            self.stack.append(stackObj)
        elif attrs.has_key('lang'):
            #multilingual property
            name = name.encode('utf-8')
            obj = property_struct(name, attrs['lang'].encode('utf-8'))
            stackObj = saxstack_struct('name', obj)
            self.stack.append(stackObj)

    def endElement(self, name):
        """ """
        if name == 'skel':
            self.root = self.stack[-1].obj
            self.stack.pop()
        elif name == 'forms':
            self.stack[-2].obj.forms = self.stack[-1].obj
            self.stack.pop()
        elif name == 'form':
            self.stack[-2].obj.forms.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'layout':
            self.stack[-2].obj.layout = self.stack[-1].obj
            self.stack.pop()
        elif name == 'skin':
            self.stack[-2].obj.skins.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'template':
            self.stack[-2].obj.templates.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'scheme':
            self.stack[-2].obj.schemes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'style':
            self.stack[-2].obj.styles.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'image':
            self.stack[-2].obj.images.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'syndication':
            self.stack[-2].obj.syndication = self.stack[-1].obj
            self.stack.pop()
        elif name == 'namespace':
            self.stack[-2].obj.namespaces.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'channeltype':
            self.stack[-2].obj.channeltypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'scriptchannel':
            self.stack[-2].obj.scriptchannels.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'localchannel':
            self.stack[-2].obj.localchannels.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'remotechannel':
            self.stack[-2].obj.remotechannels.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'pluggablecontenttypes':
            self.stack[-2].obj.pluggablecontenttypes = self.stack[-1].obj
            self.stack.pop()
        elif name == 'pluggablecontenttype':
            self.stack[-2].obj.pluggablecontenttypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'portlets':
            self.stack[-2].obj.portlets = self.stack[-1].obj
            self.stack.pop()
        elif name == 'portlet':
            self.stack[-2].obj.portlets.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'linkslist':
            self.stack[-2].obj.linkslists.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'link':
            self.stack[-2].obj.links.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'reflist':
            self.stack[-2].obj.reflists.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'item':
            self.stack[-2].obj.items.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'reftree':
            self.stack[-2].obj.reftrees.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'node':
            self.stack[-2].obj.nodes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'properties':
            self.stack[-2].obj.properties = self.stack[-1].obj
            self.stack.pop()
        elif name == 'language':
            self.stack[-2].obj.languages.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'contenttype':
            self.stack[-2].obj.contenttypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'emails':
            self.stack[-2].obj.emails = self.stack[-1].obj
            self.stack.pop()
        elif name == 'emailtemplate':
            self.stack[-2].obj.emailtemplates.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'security':
            self.stack[-2].obj.security = self.stack[-1].obj
            self.stack.pop()
        elif name == 'grouppermissions':
            self.stack[-2].obj.grouppermissions.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'role':
            self.stack[-2].obj.roles.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'notification':
            self.stack[-2].obj.notification = self.stack[-1].obj
            self.stack.pop()
        elif name == 'newsmetatype':
            self.stack[-2].obj.newsmetatypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'uploadmetatype':
            self.stack[-2].obj.uploadmetatypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'foldermetatype':
            self.stack[-2].obj.foldermetatypes.append(self.stack[-1].obj)
            self.stack.pop()
        elif name == 'others':
            self.stack[-2].obj.others = self.stack[-1].obj
            self.stack.pop()
        elif name == 'favicon':
            self.stack[-1].obj.favicon = 1
        elif name == 'robots':
            self.stack[-1].obj.robots = 1
        elif name == 'images':
            self.stack[-1].obj.images = 1
        elif name == 'sitemap_xml':
            self.stack[-1].obj.sitemap_xml = 1
        elif name == 'submit_unapproved':
            self.stack[-1].obj.submit_unapproved = 1
        elif name == 'nyexp_schema':
            self.stack[-2].obj.nyexp_schema = self.stack[-1].obj
            self.stack.pop()
        elif isinstance(self.stack[-1].obj, property_struct):
            #multilingual property
            name, lang = self.stack[-1].obj.name, self.stack[-1].obj.lang
            content = self.stack[-1].content
            self.stack.pop()
            ob = self.stack[-1].obj
            if not ob.properties.has_key(name):
                ob.properties[name] = {}
            ob.properties[name][lang] = content

    def characters(self, content):
        if len(self.stack) > 0:
            self.stack[-1].content += content.strip(' \t')

class skel_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parse(self, p_content):
        """ """
        l_handler = skel_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        try:
            l_parser.parse(l_inpsrc)
            return (l_handler, '')
        except Exception, error:
            return (None, error)
