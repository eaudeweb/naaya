- start open office service to accept calls (from graphical interface on linux)
	e.g soffice -accept="socket,port=8100;urp;"
- must have libcurl installed (curl-7.19.6-devel-mingw32)
- must have BeautifulSoup-3.1.0.1, soupselect, pycurl-7.19.0

1. Run the DocumentConverter (.doc -> .pdf + .html & images)
	e.g. andrei@pivo:~/dev/DocumentConverter$ python MultiDocumentConverter.py input output
2. Do the sections by hand or use splitter if the converter can not split in sections properly
	- split by section titles
	- insert the footnotes in the proper section
	- clear footnotes (currently the remove from last section does not work)
3. Make Consultation with the info
	- needs a 'Information for Reviewers & Table of contents' first section
	- needs a 'References' last section
4. Run image_pycurl.py to upload the images in the folder.
	e.g. C:\Zope\2.10.6\Python>python image_pycurl.py D:\dev\DocumentConverter\output\WaterQuality_2ndDraft

If can not connect with socket
	soffice "-accept=socket,port=8100;urp;"
	context = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % port)
try:
	soffice "-accept=pipe,name=pypipe;urp;StarOffice.ServiceManager"
	context = resolver.resolve("uno:pipe,name=pypipe;urp;StarOffice.ComponentContext")
- upload on stingray:
	put zexps in:
		/var/local/ew-sites-buildout/buildout/parts/zope-instance-ew/
	import zexps from zmi
	upload images
	upload pdf-s as a naaya file in a "download" folder
