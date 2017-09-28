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
# Alexandru Plugaru, Eau de Web

#Python imports
import reportlab.rl_config
#TODO: _rl_accel module should be added for improve performace on writing and size
from StringIO                   import StringIO
from reportlab.pdfgen.canvas    import Canvas
from reportlab.lib.units        import inch
from reportlab.platypus         import Table, TableStyle
from reportlab.lib.colors       import HexColor
from reportlab.lib.units        import inch

#Product imports
from pdf_base                   import *
from pdf_templates              import pdf_templates
from Products.Naaya.constants   import *

# Content types constants
from naaya.content.document.document_item import config; METATYPE_NYDOCUMENT = config['meta_type']
from naaya.content.semide.country.country_item import METATYPE_OBJECT as METATYPE_NYCOUNTRY
from naaya.content.semide.document.semdocument_item import METATYPE_OBJECT as METATYPE_NYSEMDOCUMENT
from naaya.content.semide.news.semnews_item import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from naaya.content.semide.project.semproject_item import METATYPE_OBJECT as METATYPE_NYSEMPROJECT
from naaya.content.semide.textlaws.semtextlaws_item import METATYPE_OBJECT as METATYPE_NYSEMTEXTLAWS
from naaya.content.semide.event.semevent_item import METATYPE_OBJECT as METATYPE_NYSEMEVENT

class export_pdf(pdf_templates):

    def __init__(self):
        """ constructor """
        pass

    #create the PDF document
    def _generate_pdf_content(self, canvas, p_container, type, lang):
        #write to PDF
        reportlab.rl_config.warnOnMissingFontGlyphs = 0
        l_content = []
        content_add = l_content.append
        content_extend = l_content.extend

        registerUsedFonts()
        canvas.setFont("Arial", 12)

        #cycle objects inside container
        if p_container.meta_type == METATYPE_FOLDER:
            obj_list = p_container.getObjects()
            for x in self._generate_container_info(p_container, lang):
                content_add(x)
            for sem_ob in obj_list:
                content_extend(addSpacer(0, 15))
                l_content.extend(self._generate_container_view(sem_ob, lang))
        else:
            if p_container.meta_type == METATYPE_NYSEMNEWS:
                for x in self._generate_semnews_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYSEMEVENT:
                for x in self._generate_semevent_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYSEMPROJECT:
                for x in self._generate_semproject_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYSEMDOCUMENT:
                for x in self._generate_semdocument_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYSEMTEXTLAWS:
                for x in self._generate_semtextlaws_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYCOUNTRY:
                for x in self._generate_country_object(p_container, lang):
                    content_add(x)
            elif p_container.meta_type == METATYPE_NYDOCUMENT:
                for x in self._generate_document_object(p_container, lang, type):
                    content_add(x)
            else:
                for x in self._generate_naaya_object(p_container, lang):
                    content_add(x)
        return l_content

    def create_pdf(self, p_container, type, lang, req):
        # Create the document
        output = StringIO()
        pdf_canvas = Canvas(output)

        pdf_content = []
        pdf_content.extend(self._generate_pdf_content(pdf_canvas, p_container, type, lang))

        i = 0
        while pdf_content:
            i += 1
            #old 3-Frames implementation
            #header =    addFrame(1*inch, A4_H - 1.5*inch,  PAGE_WIDTH, 1*inch,                 showBoundary=0)
            #body =      addFrame(1*inch, 1.5*inch,         PAGE_WIDTH, PAGE_HEIGHT - 1*inch,   showBoundary=0)
            body =      addFrame(1*inch, 1.5*inch,    PAGE_WIDTH, PAGE_HEIGHT,    showBoundary=0)
            footer =    addFrame(1*inch, 1*inch,    PAGE_WIDTH, 0.5*inch,       showBoundary=0)

            #old 3-Frames implementation
            #header.addFromList(self._addPageHeader(pdf_canvas, lang), pdf_canvas)

            #add header
            body.addFromList(self._addPageHeader(pdf_canvas, lang), pdf_canvas)
            #add body
            body.addFromList(pdf_content, pdf_canvas)
            #add footer
            footer.addFromList(self._addPageFooter(i, p_container.releasedate, lang), pdf_canvas)
            pdf_canvas.showPage()
        pdf_canvas.save()

        # Return the rendered page content.
        content = output.getvalue()
        req.RESPONSE.setHeader('Content-Type', 'application/pdf')
        req.RESPONSE.setHeader('Content-Length', str(len(content)))
        pdf_title = self.utToUtf8(p_container.title)

        if not pdf_title: pdf_title = 'SEMIDE'
        req.RESPONSE.setHeader('Content-Disposition', 'inline; filename="%s.pdf"' % pdf_title)
        return content

    def generate_pdf(self, url='', lang='', REQUEST=None):
        """ returns the PDF document for the requested URL """
        type = ''
        if not lang: lang=self.gl_get_selected_language()
        try:
            try:
                if url.split('/')[-2] == 'eflash': type = 'flash'
            except:
                pass
            obj_container = self.unrestrictedTraverse(url)
            return self.create_pdf(obj_container, type, lang, REQUEST)
        except:
            self.setSessionErrorsTrans('The PDF document could not be generated.')
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
