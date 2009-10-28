- start open office service to accept calls (from graphical interface on linux)
	e.g soffice -accept="socket,port=8100;urp;"
- must have libcurl installed (curl-7.19.6-devel-mingw32)
- must have BeautifulSoup-3.1.0.1, soupselect, pycurl-7.19.0

1. Run the DocumentConverter (.doc -> .html & images)
	e.g. ~/dev/DocumentConverter$ python MultiDocumentConverter.py input output
2. Run Converter2 (.html -> title, sections .html)
	e.g. D:\dev\DocumentConverter>python Convertor2.py WaterQuality_2ndDraft.html test.html
	e.g. D:\dev\DocumentConverter>python splitter.py test.html
3. Make Consultation with the info from Converter2
4. Make the image folder based on Consultation Id
5. ReRun Converter2 with the proper image folder. (maybe use splitter if the converter can not split in sections properly)
6. Run image_pycurl.py to upload the images in the folder.
	e.g. C:\Zope\2.10.6\Python>python image_pycurl.py D:\dev\DocumentConverter\output\WaterQuality_2ndDraft

If can not connect with socket
	soffice" -accept="socket,port=8100;urp;"
	context = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % port)
try:
	soffice "-accept=pipe,name=pypipe;urp;StarOffice.ServiceManager"
	context = resolver.resolve("uno:pipe,name=pypipe;urp;StarOffice.ComponentContext")

