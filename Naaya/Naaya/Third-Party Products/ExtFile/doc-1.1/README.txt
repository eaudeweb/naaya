ExtFile/ExtImage Product, Version 1.1.x
Copyright (c) 2001 Gregor Heine (mac.gregor@gmx.de). All rights reserved.
ExtFile Home: http://www.zope.org/Members/MacGregor/ExtFile/index_html


=============================
Contents
=============================

1. Product Description
2. Requirements
3. Installation Instructions
4. Usage
   4.1. Creation of an ExtFile/ExtImage object
   4.2. Public methods ('View' permission)
   4.3. Management methods
   4.4. The 'Download ExtFile/ExtImage' permission
5. Additional settings
   5.1. Directory structure 
   5.2. Filename generation
   5.3. Undo handling
6. Method appendix
   6.1. ExtFile/ExtImage public methods
   6.2. Additional public methods for ExtImage
7. Supported image formats


=============================
1. Product Description
=============================

The ExtFile Product stores large files in an external file-repository and is 
able to display icons for different MIME-Types. 
The ExtImage Product additionally creates preview-thumbnails from various 
images and displays them.

ExtFile and ExtImage basically work like the Zope File and Image products. The 
difference is, that the File/Image Products stores the (binary) file inside the 
ZODB, wheras ExtFile/ExtImage stores it externally in a repository directory 
(default: <zope-dir>/var/reposit). Only meta data (like title and description) 
are stored in the Database. This prevents the Database swelling up quickly, 
when many large files are uploaded and thus increasing database performance.

And what about LocalFS? Doesn't it do the same thing?
The difference between ExtFile/ExtImage and LocalFS is that you create one 
LocalFS object to access many files, whereas you create one ExtFile object per 
file. LocalFS works like a window through which you get access to files outside 
the Database. ExtFile/ExtImage on the other hand has a one-to-one relation 
between files and objects - you create one ExtFile/ExtImage object for each 
file.

ExtFile/ExtImage has full Zope Cut/Copy/Paste and Undo Support.


=============================
2. Requirements
=============================

Any Zope 2.x will do. (Tested with 2.1.6, 2.2.2 and 2.3.0)
The ExtImage Product requires PIL (Python Imaging Library, 
http://www.pythonware.com/products/pil/index.htm) to create preview-images.


=============================
3. Installation Instructions
=============================

Unzip the tarball in your Products directory and restart zope.
If you like to  configure the handling and structuring of the external files in 
the repository see 5. Additional settings


=============================
4. Usage
=============================

4.1. Creation of an ExtFile/ExtImage object
Create an instance of ExtFile or ExtImage by adding an ExtFile-item (resp. 
ExtImage) in the Zope management screen.
Choose a file (required) and enter an id, a title and a description (optional).
If no id is entered, the filename is used as id.
For ExtImage you can choose, if you do not want any preview, if ExtImage shold 
generate a preview image from the given file or if you want to specify a second
file, which is used as the preview image. In that case you can either use this 
image as it is or you can let ExtImage resize it to a different size.
If you want the preview image to be generated, you must enter its (x,y)size and 
choose, if you want to keep the aspect ratio of the image for the preview-image 
or if you want it scaled to the exact size entered.
To set an extra permission check for the download of the file, enable 
"Use 'Download ExtFile/ExtImage' permission" (see 4.4.)

4.2. Public methods ('View' permission)
The raw file is called through the 'index_html' method, the icon by the 
'icon_gif' method and the preview image by the 'preview' method (only available
in ExtImage). To view the meta data of a file, call the 'view' method.
For a complete list of all public methods and attributes, see 4.6. and 4.7

4.3. Management methods
To be able to fully access and use the management methods the permissions 
'View management screens', 'Change ExtFile/ExtImage' and 'FTP access' must be
enabled.
In the upload-tab of the management screen you can upload a new version of the 
file (or the preview in ExtImages) via local upload or http upload.

4.4. The 'Download ExtFile/ExtImage' permission
Usually, you want everybody with the 'View' permission to be able to download
the file (or view the image) stored in an ExtFile/ExtImage object.
In some cases (e.g. commercial websites) the administrator would want to let
people with 'View' permission only to see the preview image, or the 
meta-information of the file, or an icon for it and allow only users with a 
special permission to view/download the file itself.
In these cases, enable the "Use 'Download ExtFile/ExtImage' permission" while
creating a new ExtFile/ExtImage object and set that permission for the role,
you want to give access to the file. You enable/disable this permission check
later by setting 'use_download_permission_check' in the properties tab to 
either 1 (enabled) or 0 (disbaled).

=============================
5. Additional settings
=============================

5.1. Directory structure 
At the moment there are three ways to structure the files in the repository.
You can switch between those modes by setting the constant 'REPOSITORY' (in 
line 69 of ExtFile.py) to the respective value.
- FLAT (default): The 'classic mode'. All files are stored in one single 
  directory which is by default var/reposit/
- SYNC_ZODB: Starting from the base repository dir (default is var/reposit) the
  file is stored in a directory that corresponds to the url of its object.
  E.g. if you add an ExtFile object in the folder spamFolder/eggsFolder, the 
  file goes to var/reposit/spamFolder/eggsFolder.
  Please note, that this does not mean, that the directory structure of the 
  repository is kept in sync with the ZODB afterwards. Renaming a parent folder 
  or moving the ExtFile object to a different folder has no effect on the files
  in the repository. They stay where they are, troughout the lifetime of the
  object.
- SLICED: The first two characters of the filename (resp. the id) determine
  in which sub-directory (starting from the base repository directory) the file 
  is stored. E.g. the file spam.txt is stored in var/reposit/s/p/, 
  eggs.txt is stored as var/reposit/e/g/.
  This gives you up to approx. 70 subdirecories in the base repository, each
  containing up to approx. 70 subdirecories in wich the files are stored.

5.2. Filename generation
You can customize the filename of the files in the repository. A unique 
filename is generated, each time an ExtFile/ExtImage object is added. 
The format of this filename is specified by a format string stored in the
constant FILE_FORMAT in line 73 of ExtFile.py. 
It may contain the following elements:
%u - The name of the user, that adds the object.
%p - The relative-url-path of the object, separated by underscores. E.g. if you 
     add an ExtFile object in the folder spamFolder/eggsFolder, %p is expanded 
     to 'spamFolder_eggsFolder'.
%n - The name of the added file (or the id of the object), without the 
     extension. E.g. if the id is spam.txt, %n is expanded to 'spam'.
%e - The extension of the added file including the dot, e.g. '.txt'.
%c - A counter starting at 0
%t - The current date and time as a 10 digit number (mmddHHMMSS)
The format string may contain any of the first four elements and must contain
one of the two last elements (counter or time). The last two elements are used
to generate a unique filename, simply by increasing the value as long as a file
with that name already exists.
Examples:
%n%c%e     -> spam.txt, eggs1.txt, multiple.dots23.txt, ... (default)
%t%n%e     -> 0101000001spam.txt, 1231235959eggs.txt, ... (classic)
%n(%u)%c%e -> spam(gregor).txt, eggs(a_user)100.txt, ...
%p_%n%c%e  -> folder1_folder2_spam.txt, folderA_folderB_eggs1.txt, ...

5.3. Undo handling
To be able to support Zope's undo functionality, the external file is not 
deleted, when the object is deleted in the Zope management interface, but it is 
renamed to 'filename.undo'.
You can set a 'level of undo' which determines in wich cases the external file 
is overwritten/deleted or renamed to '.undo'.
The constant UNDO_POLICY in line 75 of ExtFile.py can be set to one of the 
following values:
- NO_BACKUPS: ExtFile/ExtImage never makes '.undo' files. If you delete an 
  object, the file in the repository is deleted aswell, if you upload a new 
  version of the file, the old version is overwritten. In this case an undo
  of a deleted object causes a broken ExtFile object because the external file
  doen't exist any more. (This option has been removed, because it produced 
  broken objects after a cut/paste or rename operation.)
- BACKUP_ON_DELETE (default): When an object is deleted, the external file is
  renamed to '<filename>.undo'. This guarantees, that objects always have a 
  valid reference to a file in the repository even if they are deleted this
  transaction is undo'ed afterwards. But if you update the file with a new 
  version, the old version is overwritten and even if the update operation is
  undo'ed, the object still references the new version of the file.
- ALWAYS_BACKUP: On every transaction that alters the external file, a backup
  of the original file is left in the repository. So if you upload a new
  version and then undo this transaction the object references the old version
  of the file again. On the other hand, this can lead to unreferenced non-undo
  files in the repository.
You should occasionally (e.g. when packing the ZODB) delete the '.undo' files 
in the repository directory (default: var/reposit).
Thou it is possible to upload a new version of the file, this is only 
recommended, when you want to update the file with a new version. Don't use the 
upload function to replace the file with a completely different one, because 
the id of the objects remains the same. 

=============================
6. Method appendix
=============================

6.1. ExtFile/ExtImage public methods

  - index_html(): 
    Returns the (binary) file
  
  - icon_gif(), index_html(icon=1): 
    Returns the icon for the file's MIME-Type
  
  - link(text=self.title_or_id, **args): 
    Return a HTML link tag to the file: <a href="link/to/object">text</a>, 
    **args are all other parameters for the <a> tag.
  
  - icon_html(): 
    HTML '<img>' tag wrapper around icon_gif with a link to index_html:
    <a href="link/to/object"><img src="link/to/object/icon_gif"></a>
  
  - is_broken(): 
    Returns true if external file is 'broken', otherwise 1 
    (this can happen, when a file in the repository direcory was accidentially 
    deleted or a database undo was performed, after the .undo file was deleted)
  
  - getContentType: 
    Returns the MIME-Type of the file.
  
  - rawsize(), get_size(), getSize(): 
    returns the size of the file in bytes.
  
  - size():
    returns a 'stringified' filesize (e.g. '1.23 MB')

6.2. Additional public methods for ExtImage

  - preview(), index_html(preview=1): 
    Returns the binary preview image.
  
  - tag(preview=0, height=None, width=None, alt=None, scale=0, xscale=0, 
    yscale=0, border="0", **args): 
    Generate an HTML IMG tag for this image, with customization. Arguments to 
    tag() can be any valid attributes of an IMG tag.'src' is always the 
    absolute pathname of the object. 'preview' is either 0 for the image or 1 
    for the preview. Defaults are applied intelligently for 'height', 'width', 
    and 'alt'. If specified, the 'scale', 'xscale', and 'yscale' keyword 
    arguments will be used to automatically adjust the output height and width 
    values of the image tag. **args are all other parameters for the <img> tag.
  
  - preview_html(): 
    Same as tag(preview=1)
  
  - width(), height(), prev_width(), prev_height():
    The dimensions (in pixel) of the image or the preview.
  
  - prev_rawsize(), prev_size():
    Same methods for the preview as for the image.
  
  - is_webviewable(): 
    Returns 1 if the image is viewable in a webbrowser (gif, jpeg or png), 
    otherwise 0
  

=============================
7. Supported image formats
=============================

The ExtImage product can create a preview from the image you upload. To be able
to do this, it requires Python Imaging Library (PIL) installed and working.
Depending on your PIL configuration most common image file formats are 
supported. In short: every image file format that can be read by your PIL 
installation can be used by ExtImage to create preview images.
These are (to name the most common): BMP, GIF, JPEG, TIFF, PNG, PCX, PNG, PSD
The preview image is always created in the JPEG format.
