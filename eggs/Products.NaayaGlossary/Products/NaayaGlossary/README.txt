NaayaGlossary
  This product is used in the Naaya architecture to store and handle
  glossaries of terms.

Prerequisites

    In order to use this product, you should have a Naaya compliant site.

Installation

  Installation of NaayaGlossary is the same as for any other Zope product. You
  just need to untar the package into the Products directory of your
  Zope installation. Consult the Zope documentation if you need further
  information.

  For Windows, you can use Winzip or any similar utility to open the
  NaayaGlossary-x-x-x.tar.gz package (where NaayaGlossary-x-x-x.tar.gz is the
  name of the NaayaGlossary package you downloaded) and extract all the files
  into the appropriate directory.  For Linux and other Unix systems, cd
  to the appropriate directory and do a tar xvzf NaayaGlossary-x-x-x.tar.gz
  (where NaayaGlossary-x-x-x.tar.gz is the name of the NaayaGlossary package
  you downloaded).

  After installing the NaayaGlossary, restart Zope.

Usage

  Open the Zope management interface in a web browser (e.g. go to
  http://your-zope-server/manage) and select the 'Naaya Glossary'
  option from the pull-down menu labeled 'Select type to add...'
  and create a new NaayaGlossary instance.

  After creation, each NaayaGlossary has the following tabs:
  "Contents", "Properties", "Languages", "Themes", "View", "Export", "Import",
  "Management" and "Undo". From "Import" and "Export" tabs you can import/export
  terms and their translations from/in XLIFF (XML Localization Interchange File Format )
  and TMX (Translation Memory eXchange) formats. From the 'Languages' tab you
  can manage the glossary's internal languages. 'Themes' tab provide the management
  of the themes used.

  That's it. Your glossary should now be ready to be filled.

  The Naaya Glossary Folders and Naaya Glossary Elements content can be translated
  via the 'Translation' tabs. In addition, the element's definitions
  can be translated from the same tab.

  Views exposed by Naaya glossary:

  - structural map of the folders and terms - used in portal pages: 'index_html' or 'map_structural_html'
  - alphabetical map of the terms - used in portal pages: 'map_alphabetical_html'
  - structural map page of the folders and terms - used for picklists: 'GlossMap_html'
  - alphabetical map of the terms - used for picklists: 'GlossMapAlph_html'
