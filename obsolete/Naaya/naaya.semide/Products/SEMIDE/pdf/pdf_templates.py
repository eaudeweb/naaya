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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Finsiel Romania

#Product imports
from pdf_base import *


class pdf_templates:
    """ """

    def __init__(self):
        """constructor"""
        pass

    #generate PDF content for site objects
    def _addPageHeader(self, canvas, lang):
        #add the header of the PDF pages
        logo_image = self.getLayoutTool()._getOb('left_logo.gif')
        img = addPILImage(logo_image)
        l_measurements = [(3*PAGE_WIDTH)/9, (6*PAGE_WIDTH)/9]
        l_align = 'LEFT'
        data = [[img, [addSiteTitle(self.site_title, lang),
                       addSiteSubTitle(self.site_subtitle, lang)]]]
        if isRTLLanguage(lang):
            l_align = 'RIGHT'
            l_measurements.reverse()
            data[0].reverse()

        doc_header = Table(data,
                           colWidths=l_measurements,
                           rowHeights=None,
                           style=None,
                           splitByRow=1,
                           repeatRows=0,
                           repeatCols=0)
        doc_header.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), l_align),
                                        ('VALIGN', (0,0), (-1,-1), 'TOP')]))
        return [doc_header]

    def _addPageFooter(self, page_index, p_releasedate, lang):
        #add the footer of the PDF pages
        getTranslation = self.getTranslation
        table_style = TABLE_FOOTER

        #page index
        data_pi = '%s: %s' % (getTranslation('page', lang), page_index)
        #last updated
        data_lu = '%s: %s' % (getTranslation('Last updated', lang), self.utShowDateTime(p_releasedate))
        #footer data
        data = [[addParagraph(data_pi, lang), ' ', addParagraph(data_lu, lang)]]

        if isRTLLanguage(lang):
            data[0].reverse()
            table_style = TABLE_FOOTER_RTL

        doc_footer = Table(data,
                           colWidths=(PAGE_WIDTH)/3,
                           rowHeights=None,
                           style=None,
                           splitByRow=1,
                           repeatRows=0,
                           repeatCols=0)
        doc_footer.setStyle(table_style)

        return [doc_footer]

    def _generate_container_info(self, p_obj, lang):
        #container info
        content = []
        add_content = content.extend

        add_content(addHeading1(p_obj.title, lang))
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 3))
        add_content(addLine())
        return content

    def _generate_container_view(self, p_obj, lang):
        #container's object
        content = []
        getTranslation = self.getTranslation
        add_content = content.extend

        add_content(addPropTable([[addParagraph(getTranslation(p_obj.meta_label, lang), lang),
                                   addParagraph(p_obj.title, lang)]], lang))
        add_content(addSpacer(0, 3))
        add_content(addPropTable([[addParagraph(getTranslation('Released', lang), lang),
                                   addParagraph(self.utShowDateTime(p_obj.releasedate), lang)]], lang))
        add_content(addSpacer(0, 3))
        add_content(addPropTable([[addParagraph(getTranslation('Description', lang), lang),
                                   addHTMLParagraph(p_obj.description, lang)]], lang))
        add_content(addLine(upper_space=10))

        return content

    def _generate_naaya_object(self, p_obj, lang):
        #generate the PDF content for any Naaya object
        content = []
        add_content = content.extend

        add_content(addHeading1(p_obj.title, lang))
        add_content(addHTMLParagraph(p_obj.description, lang))
        return content

    def _generate_semnews_object(self, p_obj, lang):
        #generate the PDF content for Semide News object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))

        #creator
        l_creator = '%s' % self.utToUtf8(p_obj.creator)
        if p_obj.creator_email: l_creator += ' (%s: %s)' % (getTranslation('email', lang), self.utToUtf8(p_obj.creator_email))
        add_content(addPropTable([[addParagraph(getTranslation('Creator', lang), lang),
                                   addParagraph(l_creator, lang)]], lang))
        add_content(addSpacer(0, 3))

        #contact
        l_contact = []
        l_contact_person = '%s' % self.utToUtf8(p_obj.contact_person)
        if p_obj.contact_email:
            l_contact_person += ' (%s: %s)' % (getTranslation('email', lang), self.utToUtf8(p_obj.contact_email))
        l_contact.extend(addParagraph(l_contact_person, lang))
        if p_obj.contact_phone:
            l_contact_ph = '%s: %s' % (getTranslation('Phone', lang), self.utToUtf8(p_obj.contact_phone))
            l_contact.extend(addParagraph(l_contact_ph, lang))
        add_content(addPropTable([[addParagraph(getTranslation('Contact', lang), lang), l_contact]], lang))
        add_content(addSpacer(0, 3))

        #news type
        add_content(addPropTable([[addParagraph(getTranslation('News type', lang), lang),
                                   addParagraph(getTranslation(p_obj.news_type, lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        #file link
        file_link = []
        file_link.extend(addLinkParagraph(p_obj.file_link, lang))
        if p_obj.file_link_local:
            file_link.extend(addLinkParagraph(p_obj.file_link_local, lang))
        add_content(addPropTable([[addParagraph(getTranslation('File link', lang), lang), file_link]], lang))
        add_content(addSpacer(0, 3))

        #source
        add_content(addPropTable([[addParagraph(getTranslation('Source', lang), lang),
                                   addParagraph(p_obj.source, lang)]], lang))
        add_content(addSpacer(0, 3))

        #subject(s)
        res = []
        if p_obj.subject:
            for x in p_obj.subject:
                if x:
                    theme_ob = self.getPortalThesaurus().getThemeByID(x, lang)
                    if theme_ob.theme_name:
                        res.extend(addParagraph(theme_ob.theme_name, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            if res:
                add_content(addPropTable([[addParagraph(getTranslation('Subject(s)', lang), lang), res]], lang))
                add_content(addSpacer(0, 3))

        #working languages
        res = []
        if p_obj.working_langs:
            for lang_id in self.convertToList(p_obj.working_langs):
                trans = self.getLanguagesGlossaryTrans(lang_id, self.gl_get_language_name(lang))
                if trans:
                    res.extend(addParagraph(trans, lang))
                else:
                    def_trans = self.getLanguagesGlossaryTrans(lang_id, self.gl_get_language_name(self.gl_get_default_language()))
                    if def_trans:
                        res.extend(addParagraph(def_trans, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            add_content(addPropTable([[addParagraph(getTranslation('Working language(s)', lang), lang), res]], lang))
            add_content(addSpacer(0, 3))

        #coverage
        add_content(addPropTable([[addParagraph(getTranslation('Location', lang), lang),
                                   addParagraph(p_obj.coverage, lang)]], lang))
        add_content(addSpacer(0, 3))

        #news date
        add_content(addPropTable([[addParagraph(getTranslation('News date', lang), lang),
                                   self.utShowDateTime(p_obj.news_date)]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))

        return content

    def _generate_semevent_object(self, p_obj, lang):
        #generate the PDF content for Semide Event object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #creator
        l_creator = '%s' % self.utToUtf8(p_obj.creator)
        if p_obj.creator_email: l_creator += ' (%s: %s)' % (getTranslation('email', lang), self.utToUtf8(p_obj.creator_email))
        add_content(addPropTable([[addParagraph(getTranslation('Creator', lang), lang),
                                   addParagraph(l_creator, lang)]], lang))
        add_content(addSpacer(0, 3))

        #contact
        l_contact = []
        l_contact_person = '%s' % self.utToUtf8(p_obj.contact_person)
        if p_obj.contact_email:
            l_contact_person += ' (%s: %s)' % (getTranslation('email', lang), self.utToUtf8(p_obj.contact_email))
        l_contact.extend(addParagraph(l_contact_person, lang))
        if p_obj.contact_phone:
            l_contact_ph = '%s: %s' % (getTranslation('Phone', lang), self.utToUtf8(p_obj.contact_phone))
            l_contact.extend(addParagraph(l_contact_ph, lang))
        add_content(addPropTable([[addParagraph(getTranslation('Contact', lang), lang), l_contact]], lang))
        add_content(addSpacer(0, 3))

        #event type
        add_content(addPropTable([[addParagraph(getTranslation('Event type', lang), lang),
                                   addParagraph(getTranslation(p_obj.event_type, lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        #file link
        file_link = []
        file_link.extend(addLinkParagraph(p_obj.file_link, lang))
        if p_obj.file_link_copy:
            file_link.extend(addLinkParagraph(p_obj.file_link_copy, lang))
        add_content(addPropTable([[addParagraph(getTranslation('File link', lang), lang), file_link]], lang))
        add_content(addSpacer(0, 3))

        #source
        add_content(addPropTable([[addParagraph(getTranslation('Source', lang), lang),
                                   addParagraph(p_obj.source, lang)]], lang))
        add_content(addSpacer(0, 3))

        #subject(s)
        res = []
        if p_obj.subject:
            for x in p_obj.subject:
                if x:
                    theme_ob = self.getPortalThesaurus().getThemeByID(x, lang)
                    if theme_ob.theme_name:
                        res.extend(addParagraph(theme_ob.theme_name, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            if res:
                add_content(addPropTable([[addParagraph(getTranslation('Subject(s)', lang), lang), res]], lang))
                add_content(addSpacer(0, 3))

        #coverage
        add_content(addPropTable([[addParagraph(getTranslation('Location', lang), lang),
                                   addParagraph(p_obj.coverage, lang)]], lang))
        add_content(addSpacer(0, 3))

        #organizer
        add_content(addPropTable([[addParagraph(getTranslation('Organizer', lang), lang),
                                   addParagraph(p_obj.organizer, lang)]], lang))
        add_content(addSpacer(0, 3))

        #address
        add_content(addPropTable([[addParagraph(getTranslation('Address', lang), lang),
                                   addParagraph(p_obj.address, lang)]], lang))
        add_content(addSpacer(0, 3))

        #geozone
        add_content(addPropTable([[addParagraph(getTranslation('Geozone', lang), lang),
                                   addParagraph(getTranslation(p_obj.geozone, lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        #duration
        add_content(addPropTable([[addParagraph(getTranslation('Duration', lang), lang),
                                   addParagraph(p_obj.duration, lang)]], lang))
        add_content(addSpacer(0, 3))

        #working languages
        res = []
        if p_obj.working_langs:
            for lang_id in self.convertToList(p_obj.working_langs):
                trans = self.getLanguagesGlossaryTrans(lang_id, self.gl_get_language_name(lang))
                if trans:
                    res.extend(addParagraph(trans, lang))
                else:
                    def_trans = self.getLanguagesGlossaryTrans(lang_id, self.gl_get_language_name(self.gl_get_default_language()))
                    if def_trans:
                        res.extend(addParagraph(def_trans, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            add_content(addPropTable([[addParagraph(getTranslation('Working language(s)', lang), lang), res]], lang))
            add_content(addSpacer(0, 3))

        #period
        period = ''
        if p_obj.start_date != p_obj.end_date and p_obj.end_date:
            period = '[%s - %s]' % (self.utShowDateTime(p_obj.start_date), self.utShowDateTime(p_obj.end_date))
        else:
            period = self.utShowDateTime(p_obj.start_date)
        add_content(addPropTable([[addParagraph(getTranslation('Period', lang), lang), period]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))

        return content

    def _generate_semproject_object(self, p_obj, lang):
        #generate the PDF content for Semide Project object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #project number
        add_content(addPropTable([[addParagraph(getTranslation('Project number', lang), lang),
                                   addParagraph(p_obj.pr_number, lang)]], lang))
        add_content(addSpacer(0, 3))

        #subjects
        res = []
        if p_obj.subject:
            for x in p_obj.subject:
                if x:
                    theme_ob = self.getPortalThesaurus().getThemeByID(x, lang)
                    if theme_ob.theme_name:
                        res.extend(addParagraph(theme_ob.theme_name, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            if res:
                add_content(addPropTable([[addParagraph(getTranslation('Subject(s)', lang), lang), res]], lang))
                add_content(addSpacer(0, 3))

        #acronym
        add_content(addPropTable([[addParagraph(getTranslation('Acronym', lang), lang),
                                   addParagraph(p_obj.acronym, lang)]], lang))
        add_content(addSpacer(0, 3))

        #budget
        add_content(addPropTable([[addParagraph(getTranslation('Budget (in &euro;)', lang), lang),
                                   addParagraph(p_obj.budget, lang)]], lang))
        add_content(addSpacer(0, 3))

        #programme
        add_content(addPropTable([[addParagraph(getTranslation('Programme', lang), lang),
                                   addParagraph(p_obj.programme, lang)]], lang))
        add_content(addSpacer(0, 3))

        #web site
        add_content(addPropTable([[addParagraph(getTranslation('Web site', lang), lang),
                                   addLinkParagraph(p_obj.resourceurl, lang)]], lang))
        add_content(addSpacer(0, 3))

        #objectives
        add_content(addPropTable([[addParagraph(getTranslation('Objectives', lang), lang), addSpacer(0, 1)]], lang))
        add_content(addHTMLParagraph(p_obj.objectives, lang))
        add_content(addSpacer(0, 3))

        #results
        add_content(addPropTable([[addParagraph(getTranslation('Results', lang), lang), addSpacer(0, 1)]], lang))
        add_content(addHTMLParagraph(p_obj.results, lang))
        add_content(addSpacer(0, 3))

        #period
        period = ''
        if p_obj.start_date != p_obj.end_date and p_obj.end_date:
            period = '[%s - %s]' % (self.utShowDateTime(p_obj.start_date), self.utShowDateTime(p_obj.end_date))
        else:
            period = self.utShowDateTime(p_obj.start_date)
        add_content(addPropTable([[addParagraph(getTranslation('Period', lang), lang), period]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))
        add_content(addSpacer(0, 15))

        #list partners
        partners_list = p_obj.getOrganisations()
        if partners_list:
            add_content(addHeading2(getTranslation('Partners', lang), lang))
            add_content(addLine())
            for part_obj in partners_list:
                #title
                add_content(addParagraph(part_obj.title, lang))
                add_content(addSpacer(0, 3))
                #description
                add_content(addHTMLParagraph(part_obj.description, lang))
                add_content(addSpacer(0, 3))
                #coordinator
                if part_obj.org_coord:
                    add_content(addPropTable([[addParagraph(getTranslation('Coordinator', lang), lang),
                                               addParagraph(getTranslation('acts as project coordinator', lang), lang)]], lang))
                    add_content(addSpacer(0, 3))
                #type
                if part_obj.org_type:
                    add_content(addPropTable([[addParagraph(getTranslation('Type', lang), lang),
                                               addParagraph(self.getOrganismTypeTitle(part_obj.org_type), lang)]], lang))
                    add_content(addSpacer(0, 3))
                #address
                add_content(addPropTable([[addParagraph(getTranslation('Address', lang), lang),
                                           addParagraph(part_obj.address, lang)]], lang))
                add_content(addSpacer(0, 3))
                #country
                add_content(addPropTable([[addParagraph(getTranslation('Country', lang), lang),
                                           addParagraph(part_obj.coverage, lang)]], lang))
                add_content(addSpacer(0, 3))
                #web site
                add_content(addPropTable([[addParagraph(getTranslation('Web site', lang), lang),
                                           addLinkParagraph(part_obj.org_url, lang)]], lang))
                add_content(addSpacer(0, 3))
                #contact
                l_contact = []
                l_contact.extend(addParagraph(part_obj.contact_title, lang))
                l_contact.extend(addParagraph(part_obj.contact_firstname, lang))
                l_contact.extend(addParagraph(part_obj.contact_lastname, lang))
                l_contact.extend(addParagraph('%s: %s' % (getTranslation('Position', lang), self.utToUtf8(part_obj.contact_position)), lang))
                l_contact.extend(addParagraph('%s: %s' % (getTranslation('Phone', lang), self.utToUtf8(part_obj.contact_phone)), lang))
                l_contact.extend(addParagraph('%s: %s' % (getTranslation('Email', lang), self.utToUtf8(part_obj.contact_email)), lang))
                add_content(addPropTable([[addParagraph(getTranslation('Contact', lang), lang),
                                           l_contact]], lang))
                add_content(addSpacer(0, 10))
            add_content(addSpacer(0, 5))

        #list funding sources
        fundings_list = p_obj.getFundings()
        if fundings_list:
            add_content(addHeading2(getTranslation('Funding sources', lang), lang))
            add_content(addLine())
            for fund_obj in fundings_list:
                #title
                add_content(addParagraph(fund_obj.title, lang))
                add_content(addSpacer(0, 3))
                #description
                add_content(addHTMLParagraph(fund_obj.description, lang))
                add_content(addSpacer(0, 3))
                #source
                add_content(addPropTable([[addParagraph(getTranslation('Source', lang), lang),
                                           addParagraph(fund_obj.funding_source, lang)]], lang))
                add_content(addSpacer(0, 3))
                #programme
                add_content(addPropTable([[addParagraph(getTranslation('Programme', lang), lang),
                                           addParagraph(fund_obj.funding_programme, lang)]], lang))
                add_content(addSpacer(0, 3))
                #funding type
                if fund_obj.funding_type:
                    add_content(addPropTable([[addParagraph(getTranslation('Funding type', lang), lang),
                                               addParagraph(self.getFundingTypeTitle(fund_obj.funding_type), lang)]], lang))
                    add_content(addSpacer(0, 3))
                #funding rate
                add_content(addPropTable([[addParagraph(getTranslation('Funding rate', lang), lang),
                                           addParagraph(fund_obj.funding_rate, lang)]], lang))
                add_content(addSpacer(0, 10))
            add_content(addSpacer(0, 5))

        #list field sites
        fields_list = p_obj.getFieldSites()
        if fields_list:
            add_content(addHeading2(getTranslation('Field sites', lang), lang))
            add_content(addLine())
            for field_obj in fields_list:
                #title
                add_content(addParagraph(field_obj.title, lang))
                add_content(addSpacer(0, 3))
                #description
                add_content(addHTMLParagraph(field_obj.description, lang))
                add_content(addSpacer(0, 3))
                #country
                add_content(addPropTable([[addParagraph(getTranslation('Country', lang), lang),
                                           addParagraph(field_obj.coverage, lang)]], lang))
                add_content(addSpacer(0, 3))
                #location
                add_content(addPropTable([[addParagraph(getTranslation('Location', lang), lang),
                                           addParagraph(field_obj.fieldsite_loc, lang)]], lang))
                add_content(addSpacer(0, 3))
                #river basin
                add_content(addPropTable([[addParagraph(getTranslation('River basin', lang), lang),
                                           addParagraph(field_obj.fieldsite_rb, lang)]], lang))
                add_content(addSpacer(0, 10))

        #list documents
        docs_list = p_obj.getDocuments()
        if docs_list:
            add_content(addHeading2(getTranslation('Documents', lang), lang))
            add_content(addLine())
            for doc_obj in docs_list:
                add_content(self._generate_semdocument_object(doc_obj, lang))

        return content

    def _generate_semdocument_object(self, p_obj, lang):
        #generate the PDF content for Semide Document object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #creator
        l_res = ''
        l_creator = self.utToUtf8(p_obj.creator)
        l_creator_email = self.utToUtf8(p_obj.creator_email)
        if l_creator_email and l_creator:
            l_res = '%s (%s: %s)' % (l_creator, getTranslation('email', lang), l_creator_email)
        elif (not l_creator) and l_creator_email:
            l_res = '%s: %s' % (getTranslation('email', lang), l_creator_email)
        elif (not l_creator) and (not l_creator_email):
            l_res = getTranslation('n/a', lang)
        add_content(addSpacer(0, 3))

        #publisher
        add_content(addPropTable([[addParagraph(getTranslation('Publisher', lang), lang),
                                   addParagraph(p_obj.publisher, lang)]], lang))
        add_content(addSpacer(0, 3))

        #type of document
        l_dtype = p_obj.document_type
        if l_dtype: l_dtype = getTranslation(l_dtype, lang)
        else: l_dtype = getTranslation('n/a', lang)
        add_content(addPropTable([[addParagraph(getTranslation('Type of document', lang), lang), addParagraph(l_dtype, lang)]], lang))
        add_content(addSpacer(0, 3))

        #rights
        add_content(addPropTable([[addParagraph(getTranslation('Rights', lang), lang),
                                   addParagraph(getTranslation(p_obj.rights, lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        #file link
        l_res = []
        l_file_link = self.convertToFullURL(p_obj.file_link)
        l_file_link_local = self.convertToFullURL(p_obj.file_link_local)
        if l_file_link:
            l_res.extend(addLinkParagraph(l_file_link, lang))
        if l_file_link_local:
            l_res.extend(addLinkParagraph('%s (%s)' % (self.utToUtf8(l_file_link), getTranslation('copy', lang)), lang))
        if not(l_file_link or l_file_link_local):
            l_res.extend(addParagraph(getTranslation('n/a', lang), lang))
        add_content(addPropTable([[addParagraph(getTranslation('File link', lang), lang), l_res]], lang))
        add_content(addSpacer(0, 3))

        #source of information
        l_res = []
        l_source_link = self.convertToFullURL(p_obj.source_link)
        l_source = self.utToUtf8(p_obj.source)
        if l_source_link or l_source:
            if l_source_link and l_source:
                l_res.extend(addParagraph(l_source, lang))
                l_res.extend(addLinkParagraph(l_source_link, lang))
            elif l_source and (not l_source_link):
                l_res.extend(addParagraph(l_source, lang))
            elif (not l_source) and l_source_link:
                l_res.extend(addLinkParagraph(l_source_link, lang))
            add_content(addPropTable([[addParagraph(getTranslation('Source of information', lang), lang),
                                       l_res]], lang))
            add_content(addSpacer(0, 3))

        #keyword(s)
        add_content(addPropTable([[addParagraph(getTranslation('Keyword(s)', lang), lang),
                                   addParagraph(p_obj.keywords, lang)]], lang))
        add_content(addSpacer(0, 3))

        #subject(s)
        res = []
        if p_obj.subject:
            for x in p_obj.subject:
                if x:
                    theme_ob = self.getPortalThesaurus().getThemeByID(x, lang)
                    if theme_ob.theme_name:
                        res.extend(addParagraph(theme_ob.theme_name, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            if res:
                add_content(addPropTable([[addParagraph(getTranslation('Subject(s)', lang), lang), res]], lang))
                add_content(addSpacer(0, 3))

        #relation
        add_content(addPropTable([[addParagraph(getTranslation('Relation', lang), lang),
                                   addLinkParagraph(p_obj.relation, lang)]], lang))
        add_content(addSpacer(0, 3))

        #geographical coverage
        l_coverage = p_obj.coverage
        if not l_coverage:
            l_coverage = getTranslation('n/a', lang)
        add_content(addPropTable([[addParagraph(getTranslation('Geographical coverage', lang), lang),
                                   addParagraph(l_coverage, lang)]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))

        return content

    def _generate_semtextlaws_object(self, p_obj, lang):
        #generate the PDF content for Semide Text of Laws object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #type
        l_type = p_obj.type_law
        if l_type: l_type = getTranslation(l_type, lang)
        else: l_type = getTranslation('n/a', lang)
        add_content(addPropTable([[addParagraph(getTranslation('Type of document', lang), lang), addParagraph(l_type, lang)]], lang))
        add_content(addSpacer(0, 3))

        #file link
        l_res = []
        l_file_link = self.convertToFullURL(p_obj.file_link)
        l_file_link_local = self.convertToFullURL(p_obj.file_link_local)
        if l_file_link:
            l_res.extend(addLinkParagraph(l_file_link, lang))
        if l_file_link_local:
            l_res.extend(addLinkParagraph('%s (%s)' % (self.utToUtf8(l_file_link), getTranslation('copy', lang)), lang))
        if not(l_file_link or l_file_link_local):
            l_res.extend(addParagraph(getTranslation('n/a', lang), lang))
        add_content(addPropTable([[addParagraph(getTranslation('File link', lang), lang), l_res]], lang))
        add_content(addSpacer(0, 3))

        #official journal reference
        add_content(addPropTable([[addParagraph(getTranslation('Official journal reference', lang), lang),
                                   addParagraph(p_obj.official_journal_ref, lang)]], lang))
        add_content(addSpacer(0, 3))

        #source
        l_res = []
        l_source_link = self.convertToFullURL(p_obj.source_link)
        l_source = self.utToUtf8(p_obj.source)
        if l_source_link or l_source:
            if l_source_link and l_source:
                l_res.extend(addParagraph(l_source, lang))
                l_res.extend(addLinkParagraph(l_source_link, lang))
            elif l_source and (not l_source_link):
                l_res.extend(addParagraph(l_source, lang))
            elif (not l_source) and l_source_link:
                l_res.extend(addLinkParagraph(l_source_link, lang))
            add_content(addPropTable([[addParagraph(getTranslation('Source', lang), lang),
                                       l_res]], lang))
            add_content(addSpacer(0, 3))

        #subject(s)
        res = []
        if p_obj.subject:
            for x in p_obj.subject:
                if x:
                    theme_ob = self.getPortalThesaurus().getThemeByID(x, lang)
                    if theme_ob.theme_name:
                        res.extend(addParagraph(theme_ob.theme_name, lang))
                    else:
                        res.extend(addParagraph(getTranslation('no translation available', lang), lang))
            if res:
                add_content(addPropTable([[addParagraph(getTranslation('Subject(s)', lang), lang), res]], lang))
                add_content(addSpacer(0, 3))

        #relation
        add_content(addPropTable([[addParagraph(getTranslation('Relation', lang), lang),
                                   addLinkParagraph(p_obj.relation, lang)]], lang))
        add_content(addSpacer(0, 3))

        #geographical coverage
        add_content(addPropTable([[addParagraph(getTranslation('Geographical coverage', lang), lang),
                                   addParagraph(p_obj.coverage, lang)]], lang))
        add_content(addSpacer(0, 3))

        #geozone
        l_geozone = p_obj.geozone
        if l_geozone: l_geozone = getTranslation(l_geozone, lang)
        else: l_geozone = getTranslation('n/a', lang)
        add_content(addPropTable([[addParagraph(getTranslation('Geozone', lang), lang), addParagraph(l_geozone, lang)]], lang))
        add_content(addSpacer(0, 3))

        #statute
        l_statute = p_obj.statute
        if l_statute: l_statute = getTranslation(l_statute, lang)
        else: l_statute = getTranslation('n/a', lang)
        add_content(addPropTable([[addParagraph(getTranslation('Statute', lang), lang), addParagraph(l_statute, lang)]], lang))
        add_content(addSpacer(0, 3))

        #original language
        l_orig_lang = p_obj.original_language
        if l_orig_lang:
            lang_name = self.gl_get_language_name(self.gl_get_selected_language())
            trans = self.getLanguagesGlossaryTrans(l_orig_lang, lang_name)
            if trans: res = trans
            else:
                lang_name = self.gl_get_language_name(self.gl_get_default_language())
                trans = self.getLanguagesGlossaryTrans(l_orig_lang, lang_name)
                if trans: res = trans
                else: res = getTranslation('no translation available', lang)

            add_content(addPropTable([[addParagraph(getTranslation('Original language', lang), lang),
                                       addParagraph(res, lang)]], lang))
            add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))

        return content

    def _generate_document_object(self, p_obj, lang, type=''):
        #generate the PDF content for HTML Document object
        #   @param p_obj: the HTML Document object
        #   @param lang:  document language
        #   @param type:  normal or eFlash generated object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #released
        add_content(addPropTable([[addParagraph(getTranslation('Released', lang), lang),
                                   addParagraph(self.utShowDateTime(p_obj.releasedate), lang)]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        #body
        flash_marker = '<!--PDF_GENERATOR_FOOTER_MARKER-->'
        if type == 'flash':
            if not flash_marker in p_obj.body: type = ''
        if type == 'flash':
            #eflash view
            add_content(addHTMLFlash(p_obj.body, lang))
        else:
            #normal view
            add_content(addHTMLParagraph(p_obj.body, lang))

        return content

    def _generate_country_object(self, p_obj, lang):
        #generate the PDF content for Country Folder object
        content = []
        add_content = content.extend
        getTranslation = self.getTranslation

        #title
        add_content(addHeading1(p_obj.title, lang))

        #description
        add_content(addHTMLParagraph(p_obj.description, lang))
        add_content(addSpacer(0, 5))

        #geographical coverage
        add_content(addPropTable([[addParagraph(getTranslation('Geographical coverage', lang), lang),
                                   addParagraph(p_obj.coverage, lang)]], lang))
        add_content(addSpacer(0, 3))

        #flag
        if p_obj.hasSmallFlag():
            flag_img = addPILImage(p_obj.getSmallFlag())
        else: flag_img = addParagraph(getTranslation('n/a', lang), lang)
        add_content(addPropTable([[addParagraph(getTranslation('Flag', lang), lang), flag_img]], lang))
        add_content(addSpacer(0, 3))

        #NFP
        l_res = []
        l_nfp_label = p_obj.getLocalProperty('nfp_label')
        l_nfp_url = self.convertToFullURL(p_obj.getLocalProperty('nfp_url'))
        if l_nfp_label: l_res.extend(addParagraph(l_nfp_label, lang))
        if l_nfp_url:   l_res.extend(addLinkParagraph(l_nfp_url, lang))
        if not (l_nfp_label or l_nfp_url):
            l_res.extend(addParagraph(getTranslation('n/a', lang), lang))

        add_content(addPropTable([[addParagraph(getTranslation('NFP', lang), lang), l_res]], lang))
        add_content(addSpacer(0, 3))

        #Institutions URL
        add_content(addPropTable([[addParagraph(getTranslation('Institutions URL', lang), lang),
                                   addLinkParagraph(p_obj.getLocalProperty('link_ins'), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Documentation URL
        add_content(addPropTable([[addParagraph(getTranslation('Documentation URL', lang), lang),
                                   addLinkParagraph(p_obj.getLocalProperty('link_doc'), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Training URL
        add_content(addPropTable([[addParagraph(getTranslation('Training URL', lang), lang),
                                   addLinkParagraph(p_obj.getLocalProperty('link_train'), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Research & Development URL
        add_content(addPropTable([[addParagraph(getTranslation('Research and Development URL', lang), lang),
                                   addLinkParagraph(p_obj.getLocalProperty('link_rd'), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Data management URL
        add_content(addPropTable([[addParagraph(getTranslation('Data management URL', lang), lang),
                                   addLinkParagraph(p_obj.getLocalProperty('link_data'), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Legislation on Water RSS feed URL
        add_content(addPropTable([[addParagraph(getTranslation('Legislation on Water RSS feed URL', lang), lang),
                                   addLinkParagraph(p_obj.get_rc_legislation_url(), lang)]], lang))
        add_content(addSpacer(0, 3))

        #Project Water RSS feed URL
        add_content(addPropTable([[addParagraph(getTranslation('Project Water RSS feed URL', lang), lang),
                                   addLinkParagraph(p_obj.get_rc_project_url(), lang)]], lang))
        add_content(addSpacer(0, 3))

        #language
        add_content(addPropTable([[addParagraph(getTranslation('Language', lang), lang),
                                   getTranslation(self.gl_get_language_name(lang), lang)]], lang))
        add_content(addSpacer(0, 3))

        return content

    def getTranslation(self, text, lang):
        """return translation for given text"""
        return self.utToUtf8(self.getPortalI18n().get_translation(text))