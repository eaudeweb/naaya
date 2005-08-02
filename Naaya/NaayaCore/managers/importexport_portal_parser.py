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
#
#
#
#$Id: importexport_portal_parser.py 3664 2005-05-19 12:26:08Z chiridra $

#Python imports
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO

#Zope imports

#Product imports
from Products.Naaya.constants import *

class tree_node_struct:
    def __init__(self, id, meta_type, object, parent):
        self.id = id
        self.meta_type = meta_type
        self.object = object
        self.parent= parent
        self.childs = []

class folder_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, publicinterface, maintainer_email):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email

class url_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, locator, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.locator = locator
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by


class file_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, downloadfilename, file, content_type, precondition, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.downloadfilename = downloadfilename
        self.file = file
        self.content_type = content_type
        self.precondition = precondition
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class event_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, location, location_address, location_url, start_date, end_date, host, agenda_url, event_url, details, event_type, contact_person, contact_email, contact_phone, contact_fax, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.location = location
        self.location_address = location_address
        self.location_url = location_url
        self.start_date = start_date
        self.end_date = end_date
        self.host = host
        self.agenda_url = agenda_url
        self.event_url = event_url
        self.details = details
        self.event_type = event_type
        self.contact_person = contact_person
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.contact_fax = contact_fax
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class news_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, details, expirationdate, topitem, resourceurl, source, smallpicture, bigpicture, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.details = details
        self.expirationdate = expirationdate
        self.topitem = topitem
        self.resourceurl = resourceurl
        self.source = source
        self.smallpicture = smallpicture
        self.bigpicture = bigpicture
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class story_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, details, resourceurl, source, storypicture, bigpicture_url, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.details = details
        self.resourceurl = resourceurl
        self.source = source
        self.storypicture = storypicture
        self.bigpicture_url = bigpicture_url
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class document_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, body, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.body = body
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class pointer_struct:
    def __init__(self, id, title, description, language, coverage, keywords, sortorder, approved, releasedate, pointer, validation_status, validation_by, validation_comment, validation_date, contributor, approved_by):
        self.id = id
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.releasedate = releasedate
        self.pointer = pointer
        self.validation_status = validation_status
        self.validation_by = validation_by
        self.validation_comment = validation_comment
        self.validation_date = validation_date
        self.contributor = contributor
        self.approved_by = approved_by

class image_struct:
    def __init__(self, id, title, file, content_type):
        self.id = id
        self.title = title
        self.file = file
        self.content_type = content_type

class normalfolder_struct:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class dtmlmethod_struct:
    def __init__(self, id, title, body):
        self.id = id
        self.title = title
        self.body = body

class dtmldocument_struct:
    def __init__(self, id, title, body):
        self.id = id
        self.title = title
        self.body = body

class importexport_portal_handler(ContentHandler):
    """ """

    def __init__(self):
        """ """
        self.tree_objects = {}
        self.tree_objects[0] = tree_node_struct(0, None, None, None)
        self.__current_node_id = 0
        self.__node_id = 1

    def startElement(self, name, attrs):
        """ """
        l_attrs = {}
        for attr in attrs.keys():
            l_attrs[attr] = attrs[attr].encode('latin-1')
        if name == METATYPE_EWFOLDER:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWFOLDER, folder_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['publicinterface'], l_attrs['maintainer_email']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__current_node_id = self.__node_id
            self.__node_id += 1
        elif name == METATYPE_EWURL:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWURL, url_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['locator'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == METATYPE_EWFILE:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWFILE, file_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['downloadfilename'], l_attrs['file'], l_attrs['content_type'], l_attrs['precondition'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == METATYPE_EWEVENT:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWEVENT, event_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['location'], l_attrs['location_address'], l_attrs['location_url'], l_attrs['start_date'], l_attrs['end_date'], l_attrs['host'], l_attrs['agenda_url'], l_attrs['event_url'], l_attrs['details'], l_attrs['event_type'], l_attrs['contact_person'], l_attrs['contact_email'], l_attrs['contact_phone'], l_attrs['contact_fax'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == METATYPE_EWNEWS:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWNEWS, news_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['details'], l_attrs['expirationdate'], l_attrs['topitem'], l_attrs['resourceurl'], l_attrs['source'], l_attrs['smallpicture'], l_attrs['bigpicture'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == METATYPE_EWSTORY:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWSTORY, story_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['details'], l_attrs['resourceurl'], l_attrs['source'], l_attrs['storypicture'], l_attrs['bigpicture_url'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1    
        elif name == METATYPE_EWDOCUMENT:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWDOCUMENT, document_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['body'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == METATYPE_EWPOINTER:
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, METATYPE_EWPOINTER, pointer_struct(l_attrs['id'], l_attrs['title'], l_attrs['description'], l_attrs['language'], l_attrs['coverage'], l_attrs['keywords'], l_attrs['sortorder'], l_attrs['approved'], l_attrs['releasedate'], l_attrs['pointer'], l_attrs['validation_status'], l_attrs['validation_by'], l_attrs['validation_comment'], l_attrs['validation_date'], l_attrs['contributor'], l_attrs['approved_by']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        #other types of objects
        elif name == 'Folder':
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, 'Folder', normalfolder_struct(l_attrs['id'], l_attrs['title']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__current_node_id = self.__node_id
            self.__node_id += 1
        elif name == 'Image':
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, 'Image', image_struct(l_attrs['id'], l_attrs['title'], l_attrs['file'], l_attrs['content_type']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == 'DTMLDocument':
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, 'DTML Document', dtmldocument_struct(l_attrs['id'], l_attrs['title'], l_attrs['body']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1
        elif name == 'DTMLMethod':
            self.tree_objects[self.__node_id] = tree_node_struct(self.__node_id, 'DTML Method', dtmlmethod_struct(l_attrs['id'], l_attrs['title'], l_attrs['body']), self.__current_node_id)
            self.tree_objects[self.__current_node_id].childs.append(self.__node_id)
            self.__node_id += 1

    def endElement(self, name):
        """ """
        if name in [METATYPE_EWFOLDER, 'Folder']:
            self.__current_node_id = self.tree_objects[self.__current_node_id].parent

    def testImportTree(self, p_node_id=0):
        """ """
        l_node = self.tree_objects[p_node_id]
        if l_node.meta_type in ['EWFolder', 'Folder'] :
            print '[%s][%s][%s][%s][%s]' % (l_node.id, l_node.meta_type, l_node.object.id, l_node.parent, l_node.childs)
        for l_child_node_id in l_node.childs:
            self.testImportTree(l_child_node_id)

class importexport_portal_parser:
    """ """

    def __init__(self):
        """ """
        pass

    def parseContent(self, p_content):
        """ """
        l_handler = importexport_portal_handler()
        l_parser = make_parser()
        l_parser.setContentHandler(l_handler)
        l_inpsrc = InputSource()
        l_inpsrc.setByteStream(StringIO(p_content))
        #try:
        l_parser.parse(l_inpsrc)
        #l_handler.testImportTree()
        return (l_handler, '')
        #except Exception, error:
        #    return (None, error)
