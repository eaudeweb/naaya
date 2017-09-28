# -*- coding=utf-8 -*-

import re

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.utils import add_admin_entry, get_portals

class UpdatePortletAdministrationAddEntries(UpdateScript):
    """ Add new entries in portal administration portlet """
    title = 'Add new entries in portal administration portlet'
    authors = [u'Bogdan Tănase']
    description = '(API Keys status, Manage content comments)'
    creation_date = 'Mar 28, 2012'
    priority = PRIORITY['HIGH']
    security = ClassSecurityInfo()

    def clean_up(self, text):
        return re.sub(r'[\r\n\t]', '', text)

    def portal_portlet(self, portal):
        return portal.getPortletsTool().getPortletById('portlet_administration')

    def get_texts(self, markup):
        return [line for line in (re.sub(r'[\n\r\t]', '', text) for text in re.findall('[^><]+?(?=<|$)', markup)) if line]

    security.declarePrivate('_update')
    def pre_update_hook(self):
        """
        """

        portals = get_portals(self)
        portlets = [(portal, self.portal_portlet(portal)) for portal in portals]

        unique_sections = []
        portals_per_sections = []
        portals_sections = {}
        for portal_port in portlets:
            portal, portlet = portal_port
            if not hasattr(portlet, 'portlet'):
                markup = portlet.read()
                lines = markup.split('\n');
                portlet_text_only = self.get_texts(markup)
                sections = []
                for line in lines:
                    for section in portlet_text_only:
                        section_details = ()
                        if ('>' + section + '</a>') in line and '<li' in line:
                            section_details = (lines.index(line), section)
                            sections.append(section_details)

                if sections not in unique_sections:
                    unique_sections.append(sections)

                portals_sections[''.join(portal.getPhysicalPath())] = sections

        for section in unique_sections:
            section_portals = []
            for portal in portals_sections:
                if portals_sections[portal] == section:
                    section_portals.append(portal)
            portals_per_sections.append(section_portals)

        return {
            'unique_sections': unique_sections,
            'portals_per_sections': portals_per_sections
        }

    def get_section_markup_index(self, lines, section):
        """
        """
        index = 0
        for line in lines:
            if ('>' + section + '<' in line) and '<li' in line:
                index = lines.index(line)

        return index

    security.declarePrivate('_update')
    def _update(self, portal):
        """
        """
        portal_path = "".join(portal.getPhysicalPath())
        portlet = self.portal_portlet(portal)

        form = self.REQUEST.form
        all_sections = form.get('sections', '')
        new_sections_markup = form.get('new-sections', [])
        all_portals = form.get('sections-portals', '')
        exists = [all_portals.index(portals_list) for portals_list in all_portals if portal_path in portals_list.split(', ')]
        try:
            sections = all_sections[exists[0]]
        except IndexError:
            self.log.error('No sections identified for this portal. '
                           'Administration portlet could not be updated. '
                           'Maybe the portlet is saved on the disk')
            return False

        sections = sections.split(',')
        portlet_markup = portlet.read()
        portlet_lines = portlet_markup.split('\n')
        portlet_text_only = self.get_texts(portlet_markup)
        new_sections_label = list(set(sections) - set(portlet_text_only))
        total_new_sections = 0

        for section_label in new_sections_label:
            try:
                after_index = (sections.index(section_label) - 1)
            except ValueError:
                after_index = 0
            after_section = sections[after_index]

            try:
                before_index = (sections.index(section_label) + 1)
            except ValueError:
                before_index = len(sections) - 1
            before_section = sections[before_index]

            after_markup_index = self.get_section_markup_index(portlet_lines, after_section) + 1
            for new_section_markup in new_sections_markup:
                new_section_markup = '\t' + new_section_markup + '\r'
                if ('>' + section_label + '<') in new_section_markup:
                    if new_section_markup not in portlet_lines:
                        portlet_lines.insert(after_markup_index, new_section_markup)
                        total_new_sections += 1
                        self.log.debug('New markup added to portal '
                                       '"%s": "%s"' %
                                       (portal_path, new_section_markup))
                        self.log.debug('Section "%s" was added before '
                                       '"%s" and after "%s"' %
                                       (section_label, before_section, after_section))
                    else:
                        self.log.debug('Section "%s" already exists in '
                                       'administration portlet' %
                                       section_label)

        if total_new_sections:
            new_markup = "\n".join(portlet_lines)
            portlet.pt_edit(text=new_markup, content_type='text/html')
            self.log.debug('Administration portlet for "%s" updated with %d'
                           ' new section/s.' %
                           (portal_path, total_new_sections))

        return True

    update_template = PageTemplateFile('zpt/update_portlet_administration_add_entries', globals())
    update_template.default = UpdateScript.update_template