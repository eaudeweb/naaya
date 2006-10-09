Naaya

License
-------

This package is subject to the Mozilla Public License Version 1.1
(the "License"); you may not use these sources except in compliance
with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/.

Software distributed under the License is distributed on an "AS
IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
implied. See the License for the specific language governing
rights and limitations under the License.

The Initial Owner of the Original Code is European Environment
Agency (EEA).  Portions created by Finsiel Romania are
Copyright (C) European Environment Agency.  All
Rights Reserved.

Authors: Finsiel Romania



Installation instructions for Naaya

Requirements
- Zope version 2.7.6 with Python version 2.3.5

Installation steps

1. Download the following Python modules:
	- feedparser: http://prdownloads.sourceforge.net/feedparser/feedparser-3.3.zip?download
	- itools & Localizer: http://www.ikaaro.org/download/localizer/Localizer-1.1.0-metapackage.tar.gz
	- PIL: http://effbot.org/downloads/Imaging-1.1.5.tar.gz
	- Egenix MX base and experimental: 
		http://www.egenix.com/files/python/egenix-mx-base-2.0.6.tar.gz
		http://www.egenix.com/files/python/egenix-mx-experimental-0.9.0.tar.gz

2. Using the Zope's Python, compile and install the above modules:
	- Extract in a new directory the content of each archive
	- Change the current directory to the new created folder (for the Localizer package change directory to "../Localizer-1.1.0-metapackage/itools-0.7.4.")
	- Build and install the python modules:
		<Zope's-python>/python ./setup.py build
		<Zope's-python>/python ./setup.py install

3. Copy the "Localizer" and "iHotfix" folders from "Localizer-1.1.0-metapackage.tar.gz" archive inside the Products folder of your Zope instance. Rename the "Localizer-1.1.0" folder as "Localizer"

4. Download the following into the Products folder of your Zope instance:
	- Naaya: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/Naaya
	- NaayaBase: https://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaBase
	- NaayaContent: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaContent
	- NaayaCore: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaCore
        - Epoz: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/Epoz
        - naayaHotfix: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/naayaHotfix

        Also, additional features can be installed:
        - NaayaCalendar: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaCalendar
        - NaayaForum: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaForum
        - NaayaGlossary: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaGlossary
        - NaayaLinkChecker: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaLinkChecker
        - NaayaPhotoArchive: http://svn.eionet.eu.int/repositories/Zope/trunk/Naaya/NaayaPhotoArchive

	Note: the products from the SVN server should be downloaded using a SVN client

5. Download and unpack http://prdownloads.sourceforge.net/textindexng/TextIndexNG-2.2.0.tar.gz?download. 
Rename the folder "TextIndexNG-2.2.0" as "TextIndexNG". Using Zope's Python:
	cd <Zope-path>Products/TextIndexNG
	<Zope's-python>/python ./setup.py build
	<Zope's-python>/python ./setup.py install

6. Converters:
    The converter is selected based on the mime-type and the extension of the object. The following formats are converted:
          - PDF (requires xpdf)
          - Postscript (requires ghostscript)
          - WinWord (requires wvWare)
          - PowerPoint (requires pphtml from xlhtml package)
          - Excel (requires xls2csv from the catdoc package)

7. Cron jobs:
    * update RDF channels - the following URL must be accessed:http://server_name:HTTP_port_number/naaya_site/updateRemoteChannels?uid=<portal UID>

    * clean up portal - the following URL must be accessed:http://server_name:HTTP_port_number/naaya_site/cleanupUnsubmittedObjects?uid=<portal UID>

    * check broken links (if NaayaLinkChecker is installed) - the following URL must be accessed:http://server_name:HTTP_port_number/naaya_site/LinkChecker/runChecker

8. Restart the Zope server and go to the Zope Management Console. Create a "Naaya Site". Start working.




