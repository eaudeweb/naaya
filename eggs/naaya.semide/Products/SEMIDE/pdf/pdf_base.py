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

#Python imports
from StringIO                           import StringIO
from reportlab.lib.styles               import StyleSheet1, ParagraphStyle
from reportlab.lib.units                import inch
from reportlab.platypus                 import Frame, Paragraph, Spacer, Table, TableStyle, Image
from reportlab_rtl                      import ParagraphRTL
from reportlab.platypus.flowables       import Image as RLImage
from reportlab.lib.colors               import HexColor
from reportlab.pdfbase                  import pdfmetrics
from reportlab.pdfbase.ttfonts          import TTFont

# A small hack to support RTL

#Products imports
from constants                          import *
from Products.SEMIDE.constants          import *
from Products.NaayaCore.managers.utils  import utils, list_utils

#dimensions
A4_W =          8.2*inch
A4_H =          11.6*inch
PAGE_WIDTH =    A4_W - (2*inch)
PAGE_HEIGHT =   A4_H - (2*inch)


#styles
def registerUsedFonts():
    #register used fonts
    from os.path import join
    path = join(SEMIDE_PRODUCT_PATH, 'pdf', 'fonts')
    pdfmetrics.registerFont(TTFont('Arial', join(path, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', join(path, 'arialbd.ttf')))

TABLE_LTR = TableStyle([('BACKGROUND', (0,0), (-2,-1), HexColor(0xf0f0f0)),
                        ('BACKGROUND', (1,0), (-1,-1), HexColor(0xffffff)),
                        ('TEXTCOLOR', (0,0), (-1,-1), HexColor(0x000000)),
                        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT')])

TABLE_RTL = TableStyle([('BACKGROUND', (0,0), (-2,-1), HexColor(0xffffff)),
                        ('BACKGROUND', (1,0), (-1,-1), HexColor(0xf0f0f0)),
                        ('TEXTCOLOR', (0,0), (-1,-1), HexColor(0x000000)),
                        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('ALIGN', (0,0), (-1,-1), 'RIGHT')])

TABLE_FOOTER = TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor(0xf0f0f0)),
                           ('TEXTCOLOR', (0,0), (-1,-1), HexColor(0x000000)),
                           ('FONTNAME', (0,0), (-1,-1), 'Arial'),
                           ('FONTSIZE', (0,0), (-1,-1), 8),
                           ('ALIGN', (0,0), (-3,-1), 'LEFT'),
                           ('ALIGN', (1,0), (-2,-1), 'CENTER'),
                           ('ALIGN', (2,0), (-1,-1), 'RIGHT')])

TABLE_FOOTER_RTL = TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor(0xf0f0f0)),
                               ('TEXTCOLOR', (0,0), (-1,-1), HexColor(0x000000)),
                               ('FONTNAME', (0,0), (-1,-1), 'Arial'),
                               ('FONTSIZE', (0,0), (-1,-1), 8),
                               ('ALIGN', (0,0), (-3,-1), 'RIGHT'),
                               ('ALIGN', (1,0), (-2,-1), 'CENTER'),
                               ('ALIGN', (2,0), (-1,-1), 'RIGHT')])

def getPDFStyle():
    """Returns a stylesheet object"""
    PDFStyle = StyleSheet1()

    PDFStyle.add(ParagraphStyle(name='Normal',
                                fontName='Arial',
                                fontSize=10,
                                leading=12),
                alias='normal')

    PDFStyle.add(ParagraphStyle(name='Normal_RTL',
                                parent=PDFStyle['Normal'],
                                alignment=2),
                alias='normal_rtl')

    PDFStyle.add(ParagraphStyle(name='SiteTitle',
                                parent=PDFStyle['Normal'],
                                fontName = 'Arial-Bold',
                                fontSize=14,
                                leading=22,
                                textColor=HexColor(0x4B7DB2),
                                spaceAfter=6),
                alias='site_title')

    PDFStyle.add(ParagraphStyle(name='SiteTitle_RTL',
                                parent=PDFStyle['SiteTitle'],
                                alignment=2),
                alias='site_title_rtl')

    PDFStyle.add(ParagraphStyle(name='SiteSubTitle',
                                parent=PDFStyle['Normal'],
                                fontName = 'Arial-Bold',
                                fontSize=10,
                                leading=22,
                                spaceAfter=6),
                alias='site_subtitle')

    PDFStyle.add(ParagraphStyle(name='SiteSubTitle_RTL',
                                parent=PDFStyle['SiteSubTitle'],
                                alignment=2),
                alias='site_subtitle_rtl')

    PDFStyle.add(ParagraphStyle(name='Heading1',
                                parent=PDFStyle['Normal'],
                                fontName = 'Arial-Bold',
                                fontSize=18,
                                leading=22,
                                spaceAfter=6),
                alias='h1')

    PDFStyle.add(ParagraphStyle(name='Heading1_RTL',
                                parent=PDFStyle['Heading1'],
                                alignment=2),
                alias='h1_rtl')

    PDFStyle.add(ParagraphStyle(name='Heading2',
                                parent=PDFStyle['Normal'],
                                fontName = 'Arial-Bold',
                                textColor=HexColor(0x666666),
                                fontSize=14,
                                leading=22,
                                spaceAfter=1),
                alias='h2')

    PDFStyle.add(ParagraphStyle(name='Heading2_RTL',
                                parent=PDFStyle['Heading2'],
                                alignment=2),
                alias='h2_rtl')

    PDFStyle.add(ParagraphStyle(name='Heading3',
                                parent=PDFStyle['Normal'],
                                fontName = 'Arial-Bold',
                                textColor=HexColor(0x557BA1),
                                fontSize=12,
                                leading=22,
                                spaceAfter=1),
                alias='h3')

    PDFStyle.add(ParagraphStyle(name='Heading3_RTL',
                                parent=PDFStyle['Heading3'],
                                alignment=2),
                alias='h3_rtl')

    PDFStyle.add(ParagraphStyle(name='Li',
                                parent=PDFStyle['Normal'],
                                leading=35,
                                spaceAfter=1),
                alias='li')

    PDFStyle.add(ParagraphStyle(name='Li_RTL',
                                parent=PDFStyle['Li'],
                                alignment=2),
                alias='li_rtl')

    PDFStyle.add(ParagraphStyle(name='Link',
                                parent=PDFStyle['Normal'],
                                textColor=HexColor(0x0000ff)),
                alias='link')

    PDFStyle.add(ParagraphStyle(name='Link_RTL',
                                parent=PDFStyle['Link'],
                                alignment=2),
                alias='link_rtl')

    return PDFStyle

PDFStyles = getPDFStyle()


#PDF page objects
def addFrame(x1, y1, width,height, leftPadding=6, bottomPadding=6, rightPadding=6,
             topPadding=6, id=None, showBoundary=0):
    #creates a Frame object
    return Frame(x1, y1, width, height, leftPadding, bottomPadding, rightPadding, topPadding, id, showBoundary)

def addSiteTitle(text, lang):
    #add an object like site title on PDF page
    return _addParagraph(text, 'SiteTitle', lang)

def addSiteSubTitle(text, lang):
    #add an object like site subtitle on PDF page
    return _addParagraph(text, 'SiteSubTitle', lang)

def addHeading1(text, lang):
    #add an object like H1 on PDF page
    res = testDisplaySpace(_addParagraph(text, 'Heading1', lang))
    return convertToList(res)

def addHeading2(text, lang):
    #add an object like H2 on PDF page
    res = testDisplaySpace(_addParagraph(text, 'Heading2', lang))
    return convertToList(res)

def addHTMLParagraph(text, lang):
    #creates an object like paragraph wich handles HTML data
    res = testDisplaySpace(_addParagraph(text, 'Normal', lang, 0))
    return convertToList(res)

def addParagraph(text, lang):
    #creates an object like paragraph
    res = testDisplaySpace(_addParagraph(text, 'Normal', lang))
    return convertToList(res)

def addLinkParagraph(text, lang):
    #creates an object like a HTML Link
    res = testDisplaySpace(_addParagraph(text, 'Link', lang))
    return convertToList(res)

def addLine(line_width=PAGE_WIDTH, line_height=1, upper_space=1):
    #creates an line
    line = Table([['']],
                       colWidths=[int(line_width)],
                       rowHeights=[int(upper_space)],
                       style=None,
                       splitByRow=1,
                       repeatRows=0,
                       repeatCols=0)
    line.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor(0xffffff)),
                              ('FONTSIZE', (0,0), (-1,-1), 1),
                              ('LINEBELOW', (0,0), (-1,-1), int(line_height), HexColor(0xf0f0f0))]))
    return convertToList(testDisplaySpace(line))

def addPropTable(data, lang):
    #creates an object like one row table
    table_style = TABLE_LTR
    l_measurements = [(2*PAGE_WIDTH)/9, (7*PAGE_WIDTH)/9]
    if isRTLLanguage(lang):
        table_style = TABLE_RTL
        l_measurements.reverse()
        data[0].reverse()

    prop_table = Table(data,
                       colWidths=l_measurements,
                       rowHeights=None,
                       style=None,
                       splitByRow=1,
                       repeatRows=0,
                       repeatCols=0)
    prop_table.setStyle(table_style)
    return convertToList(prop_table)

def addSpacer(width, height):
    #creates an object like spacer
    return convertToList(Spacer(width, height))

def addPILImage(img):
    #creates a PIL image
    if img is not None:
        try:
            img = RLImage(StringIO(str(img.data)))
        except:
            img = RLImage(StringIO(str(img)))
#OLD: create a PIL image
#        from PIL import Image as PILImage
#
#        img = PILImage.open(StringIO(str(img.data)))
#        if img.mode not in ("L", "RGB", "CMYK"):
#            img = img.convert("RGB")
        return img
    return None

def _addParagraph(text, style, lang, xml_enc=1):
    #create a Paragraph object
    if isRTLLanguage(lang):
        style = '%s_RTL' % style
        para = ParagraphRTL(formatText(text, xml_enc), PDFStyles[style])
    else:
        para = Paragraph(formatText(text, xml_enc), PDFStyles[style])
    return para

def addHTMLFlash(text, lang):
    #creates an object like paragraph wich handles eFlash generated HTML
    res = []

    #eliminate footer
    text = text.split('<!--PDF_GENERATOR_FOOTER_MARKER-->')[0] #document footer

    #split content
    l_content = text.split('</h1>')
    l_header = l_content[0] + '</h1>' #eFlash title
    res.extend(convertToList(testDisplaySpace(_addParagraph(l_header, 'Heading1', lang, 0))))
    
    l_rest = ''
    if len(l_content) > 1:
        l_rest = l_content[1]

    l_content = l_rest.split('<!--PDF_GENERATOR_MENU_MARKER-->')
    l_menu = l_content[0] + '</ul>' #eFlash menu
    l_items = l_menu.split('</li>')

#menu rendering, not shown
#    if len(l_items) > 1:
#        for k in l_items:
#            res.extend(convertToList(testDisplaySpace(_addParagraph(k, 'Li', lang, 0))))
#    else:
#        res.extend(convertToList(testDisplaySpace(_addParagraph(l_items, 'Li', lang, 0))))
    if len(l_content) > 1:
        l_rest = l_content[1]

    l_content = l_rest.split('<h2') #list of paragraphs
    if l_content == ['']: l_content = []
    for k in l_content:
        k = '<h2' + k
        if list_utils().stripHTMLTags(k).split():
            l_para = k.split('</h2>')

            if len(l_para) > 1:
                l_h2 = l_para[0] #<h2>
                res.extend(addSpacer(0, 13))
                res.extend(convertToList(testDisplaySpace(_addParagraph(l_h2, 'Heading2', lang, 0))))
                l_p = l_para[1] #paragraph content

                if list_utils().stripHTMLTags(l_p).split():
                    l_para = l_p.split('</h3>')
                    if len(l_para) > 1:
                        l_h3 = l_para[0] #<h3>
                        res.extend(convertToList(testDisplaySpace(_addParagraph(l_h3, 'Heading3', lang, 0))))
                        l_pp = l_para[1] #<p>
                        res.extend(convertToList(testDisplaySpace(_addParagraph(l_pp, 'Normal', lang, 0))))
                    else:
                        res.extend(convertToList(testDisplaySpace(_addParagraph(l_para, 'Normal', lang, 0))))

                    res.extend(convertToList(testDisplaySpace(_addParagraph(l_p, 'Normal', lang, 0))))
            else:
                res.extend(convertToList(testDisplaySpace(_addParagraph(l_para[0], 'Heading2', lang, 0))))

    return res


#################
#   utils       #
#################
def formatText(l_text, xml_enc):
    #format the text to be added on PDFs
    if not l_text: l_text = ' '
    res = utils().utToUtf8(l_text)
    res = list_utils().stripHTMLTags(res)

    if xml_enc: return utils().utXmlEncode(res)
    else:       return res

def testDisplaySpace(pdf_obj, w=PAGE_WIDTH, h=PAGE_HEIGHT):
    #Test if the pdf object to be written has sufficient space on canvas.
    w = float(w)
    h = float(h)
    obj_w, obj_h = pdf_obj.wrap(w, h)
    obj_w = float(obj_w)
    obj_h = float(obj_h)

    if obj_w <= w and obj_h <= 100:
        return pdf_obj
    else:
        if not obj_w <= w and obj_h <= 100:
            msg = MSG_WIDTH
        elif not obj_h <= 100 and obj_w <= w:
            msg = MSG_HEIGHT
        else:
            msg = '%s, %s' % (MSG_WIDTH, MSG_HEIGHT)

        res = []
        if msg == MSG_HEIGHT:
            l_split = pdf_obj.split(30, 100)
            res.extend([l_split[0]])
            l_width, l_height = l_split[-1].wrap(w, h)

            while l_height > 100:
                l_split = l_split[-1].split(30, 100)
                res.extend([l_split[0]])
                l_width, l_height = l_split[-1].wrap(w, h)

            return res

        elif msg == MSG_WIDTH:
            return pdf_obj.split(200, 12)
        else:
            return pdf_obj
            #return _addParagraph(msg, 'Normal', lang)

def isRTLLanguage(lang):
    #Test if is a RTL language.
    #Arabic          [AR]
    #Azerbaijani     [AZ]
    #Persian         [FA]
    #Javanese        [JV]
    #Kashmiri        [KS]
    #Kazakh          [KK]
    #Kurdish         [KU]
    #Malay           [MS]
    #Malayalam       [ML]
    #Pashto          [PS]
    #Punjabi         [PA]
    #Sindhi          [SD]
    #Somali          [SO]
    #Turkmen         [TK]
    #Hebrew          [HE]
    #Yiddish         [YI]
    #Urdu            [UR]
    return lang in ['ar', 'az', 'fa', 'jv', 'ks', 'kk', 'ku', 'ms', 'ml',\
                    'ps', 'pa', 'sd', 'so', 'tk', 'he', 'yi', 'ur']

def convertToList(param):
    #Convert to list.
    if type(param) != type([]):
        param = [param]
    return param