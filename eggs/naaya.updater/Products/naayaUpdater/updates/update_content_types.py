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
# Alin Voinea, Eau de Web
# David Batranu, Eau de Web

import os
import Globals

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from ZPublisher.HTTPRequest import FileUpload

PATH = Globals.package_home(globals())
PATH = os.path.join(PATH, 'www')

CONTENT_TYPES = [{'id':'text/plain', 'title':'TXT', 'picture':'txt.png'}, 
                 {'id':'text/html', 'title':'HTML', 'picture':'html.png'}, 
                 {'id':'text/xml', 'title':'XML', 'picture':'xml.png'}, 
                 {'id':'image/gif', 'title':'GIF', 'picture':'gif.png'}, 
                 {'id':'image/pjpeg', 'title':'JPEG', 'picture':'jpeg.png'}, 
                 {'id':'image/jpeg', 'title':'JPEG', 'picture':'jpeg.png'}, 
                 {'id':'image/jpg', 'title':'JPG', 'picture':'jpg.png'}, 
                 {'id':'image/bmp', 'title':'BMP', 'picture':'jpg.png'}, 
                 {'id':'image/png', 'title':'PNG', 'picture':'png.png'}, 
                 {'id':'image/x-png', 'title':'PNG', 'picture':'png.png'}, 
                 {'id':'application/octet-stream', 'title':'BINARY', 'picture':'file.png'}, 
                 {'id':'application/msword', 'title':'DOC', 'picture':'doc.png'}, 
                 {'id':'application/msaccess', 'title':'MDB', 'picture':'mdb.png'}, 
                 {'id':'application/pdf', 'title':'PDF', 'picture':'pdf.png'}, 
                 {'id':'application/vnd.ms-powerpoint', 'title':'PPT', 'picture':'ppt.png'}, 
                 {'id':'application/vnd.ms-excel', 'title':'XLS', 'picture':'xls.png'}, 
                 {'id':'application/x-zip-compressed', 'title':'ZIP', 'picture':'zip.png'}, 
                 {'id':'application/postscript', 'title':'PS', 'picture':'ps.png'}, 
                 {'id':'audio/aiff', 'title':'AIFF', 'picture':'aiff.png'}, 
                 {'id':'text/css', 'title':'CSS', 'picture':'css.png'}, 
                 {'id':'application/x-gzip', 'title':'GZ', 'picture':'gz.png'}, 
                 {'id':'application/x-javascript', 'title':'JS', 'picture':'js.png'}, 
                 {'id':'audio/mpeg', 'title':'MP3', 'picture':'mp3.png'}, 
                 {'id':'video/mpeg', 'title':'MPG', 'picture':'mpg.png'}, 
                 {'id':'text/x-ms-odc', 'title':'ODC', 'picture':'odc.png'}, 
                 {'id':'application/vnd.oasis.opendocument.formula', 'title':'ODF', 'picture':'odf.png'}, 
                 {'id':'application/vnd.oasis.opendocument.graphics', 'title':'ODG', 'picture':'odg.png'}, 
                 {'id':'application/vnd.oasis.opendocument.presentation', 'title':'ODP', 'picture':'odp.png'}, 
                 {'id':'application/vnd.oasis.opendocument.spreadsheet', 'title':'ODS', 'picture':'ods.png'}, 
                 {'id':'application/vnd.oasis.opendocument.text', 'title':'ODT', 'picture':'odt.png'}, 
                 {'id':'application/x-shockwave-flash', 'title':'SWF', 'picture':'swf.png'}, 
                 {'id':'application/vnd.sun.xml.calc', 'title':'SXC', 'picture':'sxc.png'}, 
                 {'id':'application/vnd.sun.xml.draw', 'title':'SXD', 'picture':'sxd.png'}, 
                 {'id':'application/vnd.sun.xml.impress', 'title':'SXI', 'picture':'sxi.png'}, 
                 {'id':'application/vnd.sun.xml.writer', 'title':'SXW', 'picture':'sxw.png'}, 
                 {'id':'application/x-tar', 'title':'TAR', 'picture':'tar.png'}, 
                 {'id':'application/x-compressed', 'title':'TGZ', 'picture':'tgz.png'}, 
                 {'id':'text/x-vcard', 'title':'VCF', 'picture':'vcf.png'}, 
                 {'id':'audio/wav', 'title':'WAV', 'picture':'wav.png'}, 
                 {'id':'audio/x-ms-wma', 'title':'WMA', 'picture':'wma.png'}, 
                 {'id':'video/x-ms-wmv', 'title':'WMV', 'picture':'wmv.png'}, 
                 {'id':'application/x-xpinstall', 'title':'XPI', 'picture':'xpi.png'}, 
    ]

class CustomContentUpdater(NaayaContentUpdater):
    """ Add new content types and icons"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya content types'
        self.description = 'Add new content types and icons.'
        self.update_meta_type = ''

    def _verify_doc(self, doc):
        """ """
        return doc

    def _list_updates(self):
        """ Return all portals that need update """
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals(meta_types=['EnviroWindows Site', 'Naaya Site', 'CHM Site'])
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal

    def _update(self):
        """ """
        updates = self._list_updates()
        for site in updates:
            pp = site.portal_properties
            ct_list = pp.getContentTypesList()
            for ct in ct_list:
                pp.manageDeleteContentTypes(ct.id)
            logger.debug('Deleted obsolete content-type from site: %s' % site.id)
            
            for ct in CONTENT_TYPES:
                # Make FileUpload instance from filename
                fp = open(os.path.join(PATH, ct['picture']), 'rb')
                fs = SimpleFieldStorage()
                fs.file = fp
                fs.filename = ct['title']
                file_obj = FileUpload(fs)
                pp.manageAddContentType(id=ct['id'], title=ct['title'], picture=file_obj)
            logger.debug('Added new content-type to site: %s\n' % site.id)


class SimpleFieldStorage:
    """ File Storage used to create FileUpload instance.
    """
    file = None
    filename = ''
    headers = []


def register(uid):
    return CustomContentUpdater(uid)
