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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

from os.path import join

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

from Products.Naaya.NySite import NAAYA_PRODUCT_PATH

class CustomContentUpdater(NaayaContentUpdater):
    """ Update sites to use the new SchemaTool """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya site to use Schemas'
        self.description = 'Add portal_schemas in NySite; update relevant forms in portal_forms'

    def _list_updates(self):
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals()
        for portal in portals:
            if 'portal_schemas' not in portal.objectIds():
                yield portal

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            logger.debug('Updating site: %s', update.absolute_url())
            self._update_portal(update)
            logger.debug('--- done ---')

    def _update_portal(self, portal):
        from Products.NaayaCore.constants import METATYPE_SCHEMA
        from Products.NaayaCore.SchemaTool.SchemaTool import manage_addSchemaTool
        # step 1: add schema tool
        manage_addSchemaTool(portal)
        logger.debug("Created portal_schemas")
        logger.debug("NOTE: add/edit forms need to be updated, e.g. by reinstalling content types")
        logger.debug("NOTE: the 'admin_properties_html' form needs to be updated")

        # step 1.1: set keywords and coverage glossaries
        schema_tool = portal.portal_schemas
        if portal.keywords_glossary:
            for schema in schema_tool.objectValues([METATYPE_SCHEMA]):
                schema._getOb('keywords-property').glossary_id = portal.keywords_glossary
            logger.debug("Set keywords glossary_id to \"%s\"", portal.keywords_glossary)
        if portal.coverage_glossary:
            for schema in schema_tool.objectValues([METATYPE_SCHEMA]):
                schema._getOb('coverage-property').glossary_id = portal.coverage_glossary
            logger.debug("Set coverage glossary_id to \"%s\"", portal.coverage_glossary)

        # step 2: add new forms
        new_forms = {
            'site_macro_schema_add': "Macro for add forms using schemas",
            'site_macro_schema_edit': "Macro for edit forms using schemas",
        }
        skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
        formstool_ob = portal.getFormsTool()
        for form_id, form_title in new_forms.iteritems():
            content = portal.futRead(join(skel_path, 'forms', '%s.zpt' % form_id), 'r')
            form_ob = formstool_ob._getOb(form_id, None)
            if form_ob is None:
                formstool_ob.manage_addTemplate(id=form_id, title=form_title, file='')
                form_ob = formstool_ob._getOb(form_id, None)
            form_ob.pt_edit(text=content, content_type='')

        # step 3: update portlet_administration
        new_line = u'\t<li tal:condition="canPublish">' \
                '<a tal:attributes="href string:${site_url}' \
                '/portal_schemas/admin_html" title="Content ' \
                'type property definitions" i18n:attributes="title" ' \
                'i18n:translate="">Manage content types</a></li>'
        portlets_tool = portal.getPortletsTool()
        admin_portlet = portlets_tool._getOb('portlet_administration')
        text = admin_portlet._text.split('\n')
        for c in range(len(text)):
            if '/admin_translations_html"' in text[c]:
                text[c:c] = [new_line]
                break
        admin_portlet.pt_edit(text='\n'.join(text).encode('utf-8'), content_type='')

def register(uid):
    return CustomContentUpdater(uid)
