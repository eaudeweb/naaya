HOW TO CREATE THE INSTALLER:

1. copy the SEMIDE_KIT_FILES folder to a new location
2. delete all SVN related files
3. extract files from the zope.zip file found in SEMIDE_KIT_FILES/zope in the same location,  
SEMIDE_KIT_FILES/zope and then delete the zope.zip file
4. copy into /instance/Products all necessary products for SEMIDE
5. replace the files found in the original SEMIDE_KIT_FILES/instance/Products with the new  
one (this are custom files for the SEMIDE toolkit)
6. delete all portlets related to NyCountry objects from SEMIDE/skel/portlets
7. delete NyCountry from NaayaContent

that's all !