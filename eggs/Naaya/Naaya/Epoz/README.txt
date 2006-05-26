Epoz - a cross-browser-wysiwyg-editor for Zope

 Epoz allows you to edit Zope-objects with a wysiwyg-editor. No
 plugins are required. You only have to use a recent browser (IE >=
 5.5, Mozilla >= 1.3.1, Netscape >= 7.1, Firebird >= 0.7) that
 supports Rich-Text-controls (called Midas for Mozilla).

 Please read the CHANGES.txt before upgrading Epoz.

 To use Epoz, simply install it into your Products-directory of your
 Zope-Server and restart the server. If you want to get nice
 formatted and xhtml-compatible html-code from Epoz, you should also
 install "mxTidy":http://www.lemburg.com/files/python/mxTidy.html or
 "uTidylib":http://utidylib.sourceforge.net on your server.

 Documentation about Epoz for end-users is provided by Tom Purl (see
 "EpozBook":http://zopewiki.org/EpozBook). Thanks Tom!

 Epoz talks over XMLRPC to the Zope-Server to clean up the html-code.
 After the processing of mxTidy, Epoz tries to call an additional hook
 (EpozPostTidy) which can do postprocessings on the html-source.

 If you want to use the EpozPostTidy-Hook for getting relative urls from
 Epoz out of the box, create an External Method in the root of the ZMI or
 your Plone-Site with id=EpozPostTidy,  Module Name=Epoz.EpozPostTidy,
 Function Name=EpozPostTidy.

 If you want to use the EpozPostTidy-Hook for customized tasks, please
 have a look at Epoz/Extensions/EpozPostTidy.py on how to build an
 EpozPostTidy-hook. To use the EpozPostTidy-Hook for your
 own applications, create an external method or a python-script with
 id=EpozPostTidy in the root of your site, which expects three parameters
 'self' (=server context), 'html' (=only htmlbody) and 'pageurl' (=the "real" base
 url of current page, use it to traverse the object, rewrite urls, etc.).
 It should return a new html-body.

 If you want to use Epoz with Plone use the CMFQuickInstaller or
 create an External Method with id=Install in your Plone-Site.
 Then edit the newly created External Method, set
 Module Name = Epoz.Install, Function Name = install and
 click on 'Test'. Now you can select Epoz as default editor in "your
 preferences" of the Plone-Site. Please read the FAQ.txt on how to
 customize the widget-buttons. Epoz is shipped with a
 default toolbox for Plone (icon with folder on it). You can insert links
 (please highlight text before inserting a link) and images by
 searching / navigating through your site and simply click
 "Insert Link/Image".

 If you want to use Epoz with native Zope applications, you have to
 create a customized edit-script. Because there is no unique
 interface for editing Zope-Objects, I did not include a
 "manage_edit_all"-script for Epoz. You have to create it yourself!!!
 To start working with Epoz, simply create a DTML-Method with
 id=edit::

  <dtml-var standard_html_header>
  <dtml-if html>
    <dtml-call "manage_edit('', content_type='text/html', filedata=_.str(html))">
  </dtml-if>

  <p><a href="<dtml-var URL1>">View Document</a></p>

  <form action="<dtml-var URL>" method="post">
   <dtml-var "Epoz('html:string', data=this().data,
                           toolbox='/toolbox',
                           lang='en',
                           style='width: 620px; height: 250px; border: 1px solid #000000;')">
   <input type="submit" name="submit" value=" Save Changes " >
  </form>
  <dtml-var standard_html_footer>


 Then create an empty File with id=test and point your
 browser to http://yourServer/test/edit. That's all...:) Please note:
 Epoz is a pure HTML-editor and can't edit any ZPT-or-DTML-Tags!

 To create an Epoz-Rich-Text-Editor from your own
 Products/Scripts/Methods/ZPT, you have to call it with one fixed and several
 optional paramters::

 Epoz(self, name, data='', toolbox='', lang='en',
            path='', widget='',
            style='width: 600px; height: 250px; border: 1px solid #000000;',
            button='background-color: #EFEFEF; border: 1px solid #A0A0A0; cursor: pointer; margin-right: 1px; margin-bottom: 1px;',
            css='', customcss='', charset='utf-8', pageurl=''):
    """ Create an Epoz-Wysiwyg-Editor.

        name : the name of the form-element which submits the data
        data : the data to edit
        toolbox : a link to a HTML-Page which delivers additional tools
        lang: a code for the language-file (en,de,...)
        path : path to Epoz-Javascript. Needed mainly for Plone (portal_url).
        widget: You can specify a path to an alternative JavaScript for
                epoz_script_widget.js
        style : style-definition for the editor-area
        button : style-definiton for buttons
        css : url to a global css which should be used for rendering
                content in editor-area
        customcss : url to a customized css which should be used for rendering
                         content in editor-area
        charset : charset which is edited in the editor-area
        pageurl: the base-url for the edited page

        If Epoz can't create a Rich-Text-Editor, a simple textarea is created.
    """

 Epoz is shipped with a very nice additional feature. Besides the
 rich-text-controls you can set up a customized toolbox. This is
 simply an URL which provides a popup-window with special functions.
 To get the idea, create a DTML-Method with id=toolbox in your Zope-Root
 and enter something like::

  <html>
  <head><title>Epoz-Toolbox</title></head>
  <body onload="this.focus();">

  <h1>Images</h1>

  <dtml-in "PYTHONPATH.TO.IMAGES.objectValues(['Image'])">
   <img src="<dtml-var absolute_url>"
        border="0"
        width="16"
        height="16"
        alt="<dtml-var title_or_id>"
        style="cursor: pointer;"
        onclick="window.opener.CreateImage('<dtml-var absolute_url>'); window.close();">
  </dtml-in>

  <hr />

  <h1>Links</h1>

  <dtml-tree "PYTHONPATH.TO.CONTENT" branches_expr="objectValues(['Folder','File'])"  nowrap=1>
   <a href="#"
      style="cursor: pointer;"
      onclick="window.opener.CreateLink('<dtml-var absolute_url>'); window.close();" ><dtml-var title_or_id></a>
  </dtml-tree>

  </body>
  </html>

 Now you can click onto the little icon with the folder on it and get a
 popup, which provides images (simply click) and links (select text in
 Epoz-window, then click onto link).

 If you want to translate Epoz into your own language, have a look at
 epoz/epoz_i18n/epoz_lang_en.js.dtml. It would be nice if you want to share
 your translation with me.

 I hope you'll enjoy Epoz. For me Epoz is the missing link to Zope.
 If you consider using Epoz, please write me a short mail about your
 use-case.

 Bug-reports & patches are welcome. Please send them to:
 maik.jablonski@uni-bielefeld.de
