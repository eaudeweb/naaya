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
# David Batranu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Change dynamic properties values for existing content """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Change dynamic properties values'
        self.description = 'Intended for use on DESTINET'
        self.update_meta_type = 'Naaya Content'

    def _verify_doc(self, doc):
        return doc

    def _list_updates(self):
        """ Return all objects that need update """
        pass

    def _update(self, path, lt, al):
        """ """
        path = self.restrictedTraverse(path, None)
        portal = path.getSite()
        
        properties = {'landscape_type' : {'landscape_type' : lt}, 
                      'administrative_level' : {'administrative_level' : al}}
        objects = path.getCatalogedObjects()
        
        for ob in objects:
            for k, v in properties.items():
                if hasattr(ob, k):
                    for lang in portal.gl_get_languages():
                        ob.updateDynamicProperties(v, lang)
                    logger.debug('%-15s %s', 'Updated ', ob.absolute_url())

    def index_html(self, path=None, lt='', al=''):
        """ """
        if not path:
            path = 'stakeholders/knowledge_net/social_partners/national-and-subnational-social-partner-and-ngos'
            lt = 'None'
            al = 'National'

        self._update(path, lt, al)
        return 'Done'


def register(uid):
    return CustomContentUpdater(uid)
