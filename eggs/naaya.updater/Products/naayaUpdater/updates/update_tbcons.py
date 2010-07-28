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
# David Batranu, Eau de Web


#Python imports
import re
from copy import copy

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.NaayaBase.NyImageContainer import NyImageContainer
try:
    from Products.NaayaContent.NyTalkBackConsultation.invitations import InvitationsContainer
except:
    pass

class UpdateTalkBackCons(UpdateScript):
    """ TalkBack Consultation update """
    title = ' TalkBack Consultation update'
    creation_date = 'Oct 15, 2009'
    authors = ['David Batranu']
    description = 'Updates TalkBack Consultation objects to the new version.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        for cons in portal.getCatalogedObjects('Naaya TalkBack Consultation'):
            self.update_cons(cons)
        for skin in portal['portal_layout'].objectValues('Naaya Skin'):
            self.update_site_header(skin['site_header'])
        return True

    def update_cons(self, cons):
        self.set_attr(cons, 'invitations', InvitationsContainer('invitations'))
        sections = cons.objectValues('Naaya TalkBack Consultation Section')
        paragraphs = []
        for sec in sections:
            paragraphs.extend(sec.objectValues('Naaya TalkBack Consultation Paragraph'))
        for par in paragraphs:
            self.update_paragraph(par)

    def update_paragraph(self, par):
        self.set_attr(par, 'imageContainer', NyImageContainer(par, None))
        for com in par.objectValues('Naaya TalkBack Consultation Comment'):
            self.update_comment(com)

    def update_comment(self, com):
        # get contributor name without the userid parantheses
        actual_name = re.sub(r'\s*\(\w+\)$', '', com.get_contributor_name())
        contributor_name = getattr(com, 'contributor_name', '')
        if contributor_name and actual_name != contributor_name:
            # 'contributor_name' field was probably used
            # to comment on behalf of someone else
            added_text = "<p><em>%s:</em></p>" % contributor_name
            com.message = added_text + com.message
            self.log.debug("Marked comment %s as being on behalf of %s" % (com.absolute_url(1), contributor_name))
        if com.__dict__.has_key('title'):
            del com.__dict__['title']
            self.log.debug("Deleted 'title' from %s" % com.absolute_url(1))
        self.del_attr(com, 'contributor_name')
        self.set_attr(com, 'reply_to', None)

    def set_attr(self, ob, attr, val):
        if not hasattr(ob.aq_self, attr):
            setattr(ob.aq_self, attr, val)
            self.log.debug("Added '%s' to %s" % (attr, ob.absolute_url(1)))

    def del_attr(self, ob, attr):
        if hasattr(ob.aq_self, attr):
            delattr(ob.aq_self, attr)
            self.log.debug("Deleted %s from %s" % (attr, ob.absolute_url(1)))

    def update_site_header(self, header):
        content = header.read()
        new_head = '<head tal:define="layout_path python:here.getSite().getLayoutTool().absolute_url()">'
        new_link = '\t<link rel="stylesheet" type="text/css" media="screen" tal:attributes="href string:${layout_path}/additional_style_css" />'
        updated = False
        if new_head not in content:
            content = content.replace('<head>', new_head)
            updated = True

        if new_link not in content:
            content_lines = content.split('\n')
            content_lines.reverse()
            for line in copy(content_lines):
                if '<link rel="stylesheet" type="text/css"' in line:
                    content_lines.insert(content_lines.index(line)-1, new_link)
                    break
            content_lines.reverse()
            content = '\n'.join(content_lines)
            updated = True
        if updated:
            header.pt_edit(text=content, content_type='text/html')
            self.log.debug('Updated %s' % header.absolute_url(1))
