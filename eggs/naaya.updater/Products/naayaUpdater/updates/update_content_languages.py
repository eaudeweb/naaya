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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web
# Andrei Laza, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.utils import get_portals

class UpdateContentLanguages(UpdateScript):
    """ Update content languages script  """
    title = 'Content languages'
    creation_date = 'Jul 1, 2009'
    authors = ['Alex Morega']
    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, '_content_languages_html')
    _content_languages_html = PageTemplateFile('zpt/content_languages', globals())

    security.declareProtected(view_management_screens, 'index_html')
    def index_html(self, action=None, portals=None, REQUEST=None, **kwargs):
        """ """
        if REQUEST is not None:
            kwargs.update(REQUEST.form)
        if portals:
            portal_ids = filter(None, map(str.strip, portals.split('\n')))
        else:
            portal_ids = None

        def list_portal_objects(portal):
            from Products.naayaUpdater.updates import nyUpdateLogger as logger
            overview = {}
            query = {}
            brains = portal.getCatalogTool()(query)
            for brain in brains:
                try:
                    ob = brain.getObject()
                except Exception, err:
                    logger.debug(
                        'WARNING: brain: %s, brain id: %s, getPath: %s, err: %s',
                        brain.absolute_url(), brain.data_record_id_,
                        brain.getPath(), err)
                    continue
                if ob is None:
                    logger.debug('WARNING: Broken brain: %s, id %s, getPath: %s',
                                 brain.absolute_url(), brain.data_record_id_,
                                 brain.getPath())
                    continue
                langs = str(getattr(ob, '_languages', '[no translations]'))
                try:
                    ob_info = {
                        'short_title': maxlen(ob.title_or_id(), 50),
                        'the_ob': ob,
                        'languages': langs,
                        }
                except:
                    # sometimes the wrong things get cataloged (e.g. methods)
                    logger.debug('WARNING: Object is not a valid content type: %s' % ob)
                    continue
                if langs not in overview:
                    overview[langs] = []
                overview[langs].append(ob_info)
            return overview

        def get_portal_output():
            for portal in get_portals(self):
                if portal_ids and portal.id not in portal_ids:
                    continue
                yield (portal.absolute_url(1), list_portal_objects(portal))

        def result(out={}):
            if REQUEST is None:
                return out
            else:
                return self._content_languages_html(REQUEST,
                    portals=portals, portal_output=out)

        if not action:
            return result()

        portal_output = dict(get_portal_output())

        if action == 'list objects':
            return result(portal_output)

        def modify_objects():
            for ob_info in portal_output[form_portal][form_langs]:
                ob = ob_info['the_ob']
                yield ob
                ob._p_changed = 1
                ob.recatalogNyObject(ob)

        form_portal = kwargs.get('portal')
        form_langs = kwargs.get('langs')
        if action == 'move':
            lang_from = kwargs['lang_from']
            lang_to = kwargs['lang_to']
            for ob in modify_objects():
                if lang_from not in ob._languages:
                    continue
                if lang_to not in ob._languages:
                    ob.add_language(lang_to)
                for prop_name in ob._local_properties:
                    prop_value = ob.getLocalProperty(prop_name, lang_from)
                    ob._setLocalPropValue(prop_name, lang_to, prop_value)
                    #ob._setLocalPropValue(prop_name, lang_from, '')
                ob.del_language(lang_from)
        elif action == 'delete':
            lang_delete = kwargs['lang_delete']
            for ob in modify_objects():
                ob.del_language(lang_delete)
        elif action == 'add':
            lang_add = kwargs['lang_add']
            for ob in modify_objects():
                ob.add_language(lang_add)

        #re-generate the output, since we've just changed it
        return result(dict(get_portal_output()))


def maxlen(s, l):
    if len(s) < l-3:
        return s
    else:
        return s[:l-3] + '...'
