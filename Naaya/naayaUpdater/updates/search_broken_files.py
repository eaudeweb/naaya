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
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ """
    _properties = NaayaContentUpdater._properties + (
      {'id': 'update_meta_type', 'label': 'Search meta types', 
       'type': 'lines', 'mode': 'w'},
    )
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Search broken ExtFiles'
        self.description = "Search file objects that are broken"

    def _verify_doc(self, doc):
        doc_broken = False
        if getattr(doc, 'getFileItems', None):
            for lang, item in doc.getFileItems():
                filename = item._get_data_name()
                if not filename:
                    continue
                data = item.get_data(as_string=False)
                if data.is_broken():
                    logger.debug('Broken %s: %s, lang: %s, filename: %s', doc.meta_type, doc.absolute_url(1), lang, filename)
                    doc_broken = True
                if not getattr(item, 'getVersions', None):
                    continue
                for version in item.getVersions():
                    data = version
                    key = data.getId()
                    if not getattr(data, 'filename', []):
                        continue
                    if data.is_broken():
                        logger.debug('Broken version %s: %s, lang: %s, version id: %s, version filename: %s',
                        doc.meta_type, doc.absolute_url(1), lang, key, getattr(data, 'filename', []))
                        doc_broken = True
            if getattr(doc, 'hasVersion', None) and doc.hasVersion() and doc.version != doc:
                if self._verify_doc(doc.version):
                    doc_broken = True
	
        elif getattr(doc, 'get_data', None):
            filename = doc._get_data_name()
            if filename:
                data = doc.get_data(as_string=False)
                if data.is_broken():
                    logger.debug('Broken %s: %s, filename: %s', doc.meta_type, doc.absolute_url(1), filename)
        	    doc_broken = True
            if getattr(doc, 'hasVersion', None) and doc.hasVersion() and doc.version != doc:
                if self._verify_doc(doc.version):
                    doc_broken = True
            
    	    if getattr(doc, 'getVersions', None):
    	        for version in doc.getVersions():
                    data = version
    	            key = data.getId()
    	            if not getattr(data, 'filename', []):
    	                continue
    	            if data.is_broken():
    	                logger.debug('Broken version %s: %s, version id: %s, version filename: %s',
    	                doc.meta_type, doc.absolute_url(1), key, getattr(data, 'filename', []))
    	                doc_broken = True
        if doc_broken:
            return doc
        return None

    def _update(self):
        pass

def register(uid):
    return CustomContentUpdater(uid)
