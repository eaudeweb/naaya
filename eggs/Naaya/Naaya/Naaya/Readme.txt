Naaya


Installation instructions for Naaya

Requirements
- Zope version 2.7.6 with Python version 2.3.5

Installation steps

1. Download the following Python modules:
	feedparser: http://prdownloads.sourceforge.net/feedparser/feedparser-3.3.zip?download
	itools & Localizer: http://www.ikaaro.org/download/localizer/Localizer-1.1.0-metapackage.tar.gz
	PIL: http://effbot.org/downloads/Imaging-1.1.5.tar.gz
	MX: 
		http://www.egenix.com/files/python/egenix-mx-base-2.0.6.tar.gz
		http://www.egenix.com/files/python/egenix-mx-experimental-0.9.0.tar.gz

2. Using the Zope's Python, compile and install the above modules:
	- Extract in a new directory the content of each archive
	- Change the current directory to the new created folder (for the Localizer package change directory to "../Localizer-1.1.0-metapackage/itools-0.7.4.")
	- Build and install the python modules:
		<Zope-path>/bin/python ./setup.py build
		<Zope-path>/bin/python ./setup.py install

3. Copy the "Localizer" and "iHotfix" folders from "Localizer-1.1.0-metapackage.tar.gz" archive inside the Products folder of your Zope instance. Rename the "Localizer-1.1.0" folder as "Localizer"

4. Download the following into the Products folder of your Zope instance:
	http://svn.eionet.europa.eu/repositories/Zope/trunk/ChangeNotification/,
	http://svn.eionet.europa.eu/repositories/Zope/trunk/MessageBoard/,
	http://svn.eionet.europa.eu/repositories/Zope/branches/chm_related/CHMGlossary/,
	http://svn.eionet.europa.eu/repositories/Zope/trunk/HelpDeskAgent/,
	and all products from http://svn.eionet.europa.eu/repositories/Zope/trunk/Naaya/

	Note: the products from the SVN server should be downloaded using a SVN client

5. Download and unpack the archive http://mjablonski.zope.de/Epoz/releases/Epoz-2.0.0.tar.gz 
into the Products folder of your Zope installation.
Move the content of the folder "Products/Epoz_18n" inside the "Products/Epoz/epoz/epoz_i18n" folder.
Delete the folder Epoz_18n from Products.

6. Download and unpack http://prdownloads.sourceforge.net/textindexng/TextIndexNG-2.2.0.tar.gz?download. 
Rename the folder "TextIndexNG-2.2.0" as "TextIndexNG". Using Zope's Python:
	cd <Zope-path>Products/TextIndexNG
	<Zope-path>/bin/python ./setup.py build
	<Zope-path>/bin/python ./setup.py install

7. Restart the Zope server and go to the Zope Management Console. Create a "CHM site". Start working.
