#####
###  Epoz - a cross-browser-wysiwyg-editor for Zope
##   Copyright (C) 2005 Maik Jablonski (maik.jablonski@uni-bielefeld.de)
#
#    All Rights Reserved.
#
#    This software is subject to the provisions of the Zope Public License,
#    Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
#    THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
#    WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##   WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
###  FOR A PARTICULAR PURPOSE.
####

import re
import urlparse
import cgi
import sys

# try to import mxTidy as default
try:
    from mx import Tidy
    mxTidyIsAvailable = 1
except:
    mxTidyIsAvailable = 0

# try to import uTidylib as fallback
try:
    import tidy
    uTidyIsAvailable = 1
except ImportError:
    uTidyIsAvailable = 0

# try to import word_unmunger
try:
    from plugins.word_unmunger import unmungeString
    uWordUnmunger = 1
except:
    uWordUnmunger = 0

import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ImageFile import ImageFile

# Regexp for snipping the body of a document
HTML_BODY = re.compile('<body[^>]*?>(.*)</body[^>]*?>', re.DOTALL|re.IGNORECASE)
MSO_CLASS = re.compile(r'<(\w+)\W+(class="Mso.*?")>', re.IGNORECASE)
EPOZ_SCRIPT = re.compile(r'<epoz:script (style="[^"]*")? ?')

misc_ = {
 # The Format-Controls
'epoz_script_main.js':ImageFile('epoz/epoz_core/epoz_script_main.js.dtml', globals()),

 # Rendering of the widget
'epoz_script_widget.js':ImageFile('epoz/epoz_core/epoz_script_widget.js.dtml', globals()),

 # Browser-detection
'epoz_script_detect.js':ImageFile('epoz/epoz_core/epoz_script_detect.js.dtml', globals()),

 # Code for the color-selection-popup
'epoz_script_color.html':ImageFile('epoz/epoz_core/epoz_script_color.html.dtml', globals()),

 # Code for the table-popup
'epoz_script_table.html':ImageFile('epoz/epoz_core/epoz_script_table.html.dtml', globals()),

 # The XMLRPC-handler
'vcXMLRPC.js':ImageFile('epoz/epoz_core/vcXMLRPC.js.dtml', globals()),

# Multi-Epoz
'epoz_redirect.js':ImageFile('epoz/epoz_core/epoz_redirect.js.dtml', globals()),
'epoz_iframe_trigger.js':ImageFile('epoz/epoz_core/epoz_iframe_trigger.js.dtml', globals()),

## CHM specific
# Help Form
'epoz_help.html':ImageFile('epoz/epoz_core/epoz_help.html.dtml', globals()),


 # The Epoz-Language-Files
'epoz_lang_da.js':ImageFile('epoz/epoz_i18n/epoz_lang_da.js.dtml', globals()),
'epoz_lang_de.js':ImageFile('epoz/epoz_i18n/epoz_lang_de.js.dtml', globals()),
'epoz_lang_en.js':ImageFile('epoz/epoz_i18n/epoz_lang_en.js.dtml', globals()),
'epoz_lang_es.js':ImageFile('epoz/epoz_i18n/epoz_lang_es.js.dtml', globals()),
'epoz_lang_fi.js':ImageFile('epoz/epoz_i18n/epoz_lang_fi.js.dtml', globals()),
'epoz_lang_fr.js':ImageFile('epoz/epoz_i18n/epoz_lang_fr.js.dtml', globals()),
'epoz_lang_hu.js':ImageFile('epoz/epoz_i18n/epoz_lang_hu.js.dtml', globals()),
'epoz_lang_it.js':ImageFile('epoz/epoz_i18n/epoz_lang_it.js.dtml', globals()),
'epoz_lang_nl.js':ImageFile('epoz/epoz_i18n/epoz_lang_nl.js.dtml', globals()),
'epoz_lang_no.js':ImageFile('epoz/epoz_i18n/epoz_lang_no.js.dtml', globals()),
'epoz_lang_pl.js':ImageFile('epoz/epoz_i18n/epoz_lang_pl.js.dtml', globals()),
'epoz_lang_pt.js':ImageFile('epoz/epoz_i18n/epoz_lang_pt.js.dtml', globals()),
'epoz_lang_pt-br.js':ImageFile('epoz/epoz_i18n/epoz_lang_pt-br.js.dtml', globals()),
'epoz_lang_ru.js':ImageFile('epoz/epoz_i18n/epoz_lang_ru.js.dtml', globals()),
'epoz_lang_sk.js':ImageFile('epoz/epoz_i18n/epoz_lang_sk.js.dtml', globals()),
'epoz_lang_zh-cn.js':ImageFile('epoz/epoz_i18n/epoz_lang_zh-cn.js.dtml', globals()),

 # The Epoz-Buttons
'epoz_button_anchor.gif':ImageFile('epoz/epoz_images/epoz_button_anchor.gif', globals()),
'epoz_button_bgcolor.gif':ImageFile('epoz/epoz_images/epoz_button_bgcolor.gif', globals()),
'epoz_button_bold.gif':ImageFile('epoz/epoz_images/epoz_button_bold.gif', globals()),
'epoz_button_centre.gif':ImageFile('epoz/epoz_images/epoz_button_centre.gif', globals()),
'epoz_button_hr.gif':ImageFile('epoz/epoz_images/epoz_button_hr.gif', globals()),
'epoz_button_hyperlink.gif':ImageFile('epoz/epoz_images/epoz_button_hyperlink.gif', globals()),
'epoz_button_image.gif':ImageFile('epoz/epoz_images/epoz_button_image.gif', globals()),
'epoz_button_indent.gif':ImageFile('epoz/epoz_images/epoz_button_indent.gif', globals()),
'epoz_button_italic.gif':ImageFile('epoz/epoz_images/epoz_button_italic.gif', globals()),
'epoz_button_left_just.gif':ImageFile('epoz/epoz_images/epoz_button_left_just.gif', globals()),
'epoz_button_list.gif':ImageFile('epoz/epoz_images/epoz_button_list.gif', globals()),
'epoz_button_numbered_list.gif':ImageFile('epoz/epoz_images/epoz_button_numbered_list.gif', globals()),
'epoz_button_outdent.gif':ImageFile('epoz/epoz_images/epoz_button_outdent.gif', globals()),
'epoz_button_redo.gif':ImageFile('epoz/epoz_images/epoz_button_redo.gif', globals()),
'epoz_button_right_just.gif':ImageFile('epoz/epoz_images/epoz_button_right_just.gif', globals()),
'epoz_button_strikethrough.gif':ImageFile('epoz/epoz_images/epoz_button_strikethrough.gif', globals()),
'epoz_button_subscript.gif':ImageFile('epoz/epoz_images/epoz_button_subscript.gif', globals()),
'epoz_button_superscript.gif':ImageFile('epoz/epoz_images/epoz_button_superscript.gif', globals()),
'epoz_button_table.gif':ImageFile('epoz/epoz_images/epoz_button_table.gif', globals()),
'epoz_button_textcolor.gif':ImageFile('epoz/epoz_images/epoz_button_textcolor.gif', globals()),
'epoz_button_tools.gif':ImageFile('epoz/epoz_images/epoz_button_tools.gif', globals()),
'epoz_button_underline.gif':ImageFile('epoz/epoz_images/epoz_button_underline.gif', globals()),
'epoz_button_undo.gif':ImageFile('epoz/epoz_images/epoz_button_undo.gif', globals()),
'epoz_button_unformat.gif':ImageFile('epoz/epoz_images/epoz_button_unformat.gif', globals()),
#CHM CUSTOM
'epoz_button_relativelink.gif':ImageFile('epoz/epoz_images/epoz_button_hyperlink.gif', globals()),
'epoz_button_help.gif':ImageFile('epoz/epoz_images/epoz_button_help.gif', globals()),
'epoz_button_more.gif':ImageFile('epoz/epoz_images/epoz_button_more.gif', globals()),
'epoz_button_readmore.gif':ImageFile('epoz/epoz_images/epoz_button_readmore.gif', globals()),
#end CHM CUSTOM
}


def Epoz(self, name, data='', toolbox='', lang='en',
               path='', widget='',
               style='width: 600px; height: 250px; border: 1px solid #000000;',
               textstyle='width: 600px; height: 280px; border: 1px solid #000000;',
               epoz_toolbar_style = 'width:602px',
               button='background-color: #EFEFEF; border: 1px solid #A0A0A0; cursor: pointer; margin-right: 1px; margin-bottom: 1px;',
               css='', customcss='', charset='utf-8', pageurl=''):
    """ Create an Epoz-Wysiwyg-Editor.

        name : the name of the form-element which submits the data
        data : the data to edit
        toolbox : a link to a HTML-Page which delivers additional tools
        lang: a code for the language-file (en,de,...).
        path : path to Epoz-Javascript. Needed mainly for Plone (portal_url).
        widget: You can specify a path to an alternative JavaScript for
                epoz_script_widget.js
        style : style-definition for the editor-area
        button : style-definiton for buttons
        css : url to a global css which should be used for rendering
               content in editor-area
        customcss: url to a customized css which should be used for rendering
                        content in editor-area
        charset : charset which is edited in the editor-area
        pageurl: the base-url for the edited page

        If Epoz can't create a Rich-Text-Editor, a simple textarea is created.
    """

    if data is None:
        data=''

    js_data = data
    data = cgi.escape(data)

    # hide scripts without removing them
    js_data = js_data.replace('<script', '<epoz:script style="display: none;"')
    js_data = js_data.replace('</script>', '</epoz:script>')
    js_data = js_data.replace('<SCRIPT', '<epoz:script style="display: none;"')
    js_data = js_data.replace('</SCRIPT>', '</epoz:script>')

    # Quote newlines and single quotes, so the Epoz-JavaScript won't break.
    # Needs to be a list and no dictionary, cause we need order!!!

    quotes = (("\\","\\\\"), ("\n","\\n"), ("\r","\\r"), ("'","\\'"))

    for item in quotes:
        js_data = js_data.replace(item[0], item[1])

    # Determine the correct path for VirtualHostMonsters & PCGI & etc.pp.
    if not path:
        path = "%s/misc_/Epoz/" % (self.REQUEST.get('BASEPATH1',''),)

    if not pageurl:
        pageurl = self.REQUEST.get('URL1','')

    i18n='<script language="JavaScript" type="text/javascript" src="%sepoz_lang_en.js"></script>' % (path,)
    if lang<>'en':
        i18n += '<script language="JavaScript" type="text/javascript" src="%sepoz_lang_%s.js"></script>' % (path, lang)

    if not widget:
       widget = "%sepoz_script_widget.js" % path

    # This is just a dummy page for test-iframe
    # to prevent IE complaining when using Epoz via https
    iframesrc = pageurl+'/epoz_blank_iframe.html'

    # Return the HTML-Code for the Epoz-Rich-Text-Editor
    return """
%(i18n)s
<script language="JavaScript" type="text/javascript" src="%(widget)s"></script>
<script language="JavaScript" type="text/javascript" src="%(path)svcXMLRPC.js"></script>
<script language="JavaScript" type="text/javascript" src="%(path)sepoz_script_detect.js"></script>
<script language="JavaScript" type="text/javascript" src="%(path)sepoz_script_main.js" charset="utf-8"></script>
<script language="JavaScript" type="text/javascript" src="%(path)sepoz_redirect.js"></script>
<script language="JavaScript" type="text/javascript">
<!--
  InitIframe('%(name)s','%(js_data)s','%(path)s','%(toolbox)s','%(style)s','%(textstyle)s','%(epoz_toolbar_style)s','%(button)s','%(css)s','%(customcss)s','%(charset)s', '%(pageurl)s');
//-->
</script>
<noscript><textarea name="%(name)s" style="%(style)s">%(data)s</textarea></noscript>
""" % {
       'i18n': i18n,
       'widget':  widget,
       'path':    path,
       'name':    name,
       'js_data': js_data,
       'toolbox': toolbox,
       'style':   style,
       'textstyle': textstyle,
       'epoz_toolbar_style': epoz_toolbar_style,
       'button':  button,
       'css': css,
       'customcss': customcss,
       'charset': charset,
       'data':    data,
       'pageurl': pageurl,
       'iframesrc': iframesrc
      }



def EpozTidy(self, html, pageurl):
    """ Take html and deliver xhtml if mxTidy is installed;
        call EpozPostTidy for html-postprocessings before returning the result
    """

    errors = 0
    output = html
    errordata = ""

    input = html.encode("utf-8")
    input = EPOZ_SCRIPT.sub('<script ', input)
    input = input.replace('</epoz:script>', '</script>')

    if uWordUnmunger:
        input = unmungeString(input)

    if mxTidyIsAvailable:
        (errors, warnings, output, errordata) = Tidy.tidy(
            input, drop_empty_paras=1, logical_emphasis=1, indent_spaces=1,
            indent="no", output_xhtml=1, word_2000=1, wrap=0, alt_text='',
            char_encoding="utf8")
#        (errors, warnings, output, errordata) = Tidy.tidy(
#            input, drop_empty_paras=1, indent_spaces=1, indent="auto",
#            output_xhtml=1, word_2000=1, wrap=79, char_encoding="utf8")
        if errors:
            output = html
    elif uTidyIsAvailable:
        parsed = tidy.parseString(
            input, drop_empty_paras=1, indent_spaces=1, indent="auto",
            output_xhtml=1, word_2000=1, wrap=79, char_encoding="utf8",
            add_xml_decl=0, doctype="omit", indent_attributes=1,
            drop_proprietary_attributes=1, bare=1, clean=1,
            enclose_text=1, tidy_mark=0)
        reports = parsed.get_errors()
        all_errors = [str(x) for x in reports if x.severity != 'W']
        errors = len(all_errors)
        errordata = '\n'.join(all_errors)
        if errors:
            output = html
        else:
            output = str(parsed)

    output = MSO_CLASS.sub(r"<\1>", output)
    result = HTML_BODY.search(output)
    if result:
        output = result.group(1)

    # Call External Method / PythonScript for postprocessing
    # The script should expect two parameters:
    # self = called context (=server)
    # html = the htmlbody to postprocess
    # pathname = path of edited object (maybe with template!)
    # The script should return the new htmlbody

    EpozPostTidy = getattr(self, 'EpozPostTidy', None)
    if EpozPostTidy is not None:
        output = EpozPostTidy(self, output, pageurl)

    return (errors, output, errordata)


def EpozGetRelativeUrl(self, pageUrl, targetUrl):
    """ Returns relative path from targetUrl to pageUrl. """

    # Just some shortcuts...
    SCHEME, HOSTNAME, PATH, PARAMS, QUERY, FRAGMENT = range(6)

    pageUnits = urlparse.urlparse(pageUrl)
    targetUnits = urlparse.urlparse(targetUrl)

    if pageUnits[:PATH] != targetUnits[:PATH]:
        # Scheme (http) or host:port (www.comain.com) are different
        # -> no possible relative URL
        return targetUrl

    afterPath = targetUnits[PARAMS:]

    pagePath = pageUnits[PATH].split('/')
    pagePath.reverse()

    targetPath = targetUnits[PATH].split('/')
    targetPath.reverse()

    # Remove parts which are equal (['a', 'b'] ['a', 'c'] --> ['c'])
    while (len(pagePath) > 0
       and len(targetPath) > 0
       and pagePath[-1] == targetPath[-1]):
        pagePath.pop()
        last_pop = targetPath.pop()
    if len(pagePath) == 0 and len(targetPath) == 0:
        # Special case: link to itself (http://foo/a http://foo/a -> a)
        targetPath.append(last_pop)
    if len(pagePath) == 1 and pagePath[0] == "" and len(targetPath) == 0:
        # Special case: (http://foo/a/ http://foo/a -> ../a)
        pagePath.append(last_pop)
        targetPath.append(last_pop)

    targetPath.reverse()

    relativeUrl = ['..'] * (len(pagePath) -1)
    relativeUrl = ('', '', '/'.join(relativeUrl + targetPath)) + tuple(afterPath)

    return urlparse.urlunparse(relativeUrl)


# Make sure the Epoz method is replaceable in the Products folder
Epoz.__replaceable__ = Globals.REPLACEABLE

# Register Epoz as global method
# Register EpozTidy as global method for XMLRPC
# Register EpozGetRelativeUrl as global method
# Register epoz_blank_iframe.html as global PageTemplate

methods = {
'Epoz': Epoz,
'Epoz__roles__': None,

'EpozTidy': EpozTidy,
'EpozTidy__roles__': None,

'EpozGetRelativeUrl': EpozGetRelativeUrl,
'EpozGetRelativeUrl__roles__': None,

'epoz_blank_iframe.html': PageTemplateFile('epoz/epoz_core/epoz_blank_iframe.html.pt', globals()),
'epoz_blank_iframe.html__roles__': None,
}


# And now try to register Epoz for CMF/Plone

try:
    from Products.CMFCore.DirectoryView import registerDirectory

    global cmfepoz_globals
    cmfepoz_globals=globals()

    def initialize(context):
        registerDirectory('epoz', cmfepoz_globals)
except:
    pass
