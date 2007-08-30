NyMediaFile
===========
- A video file container, that display them using flash video player 
EdWideoPlayer (https://svn.eionet.europa.eu/repositories/Zope/trunk/EdWideoPlayer).

1 Features
==========
- Upload and play almost any video format in all browsers that support 
  adobe flash player 9 or greater;
- Store video files outside ZODB;
- Subtitles for every site language;
- Download video file.

2 Install
=========
The following products/tools are required in order to provide all the features:
  * ExtFile 1.5.6;
  * ffmpeg;
  * flvtool2;
If one of this is missing video conversion will not be supported (the users will
be able to upload only flash video files ".flv");

2.1 Install ExtFile:
--------------------
- Download it from provided URL and unpack into your zope instance:
    cd </path to my zope instance/>
    wget http://www.zope.org/Members/shh/ExtFile/1.5.6/ExtFile-1.5.6.tar.gz
    tar -zxvf ExtFile-1.5.6.tar.gz
    rm ExtFile-1.5.6.tar.gz
- Edit REPOSITORY_PATH in ExtFile/Config.py:
    REPOSITORY_PATH = ["var", "reposit"]

2.2 Install ffmpeg
------------------
- Download it from provided URL and unpack into tmp folder:
    cd /tmp
    wget http://ffmpeg.mplayerhq.hu/ffmpeg-checkout-snapshot.tar.bz2
    tar -xvf ffmpeg-checkout-snapshot.tar.bz2
    cd <ffmpeg-checkout-extract-folder>
- Ensure you have installed lame, lame-devel on your machine:
    (yum user): yum install lame lame-devel
    (apt user): apt-get install lame lame-devel
- Install:
    ./configure --enable-libmp3lame && make && sudo make install

2.3 Install flvtool2
--------------------
- Download it from provided URL and unpack into tmp folder:
    cd /tmp
    wget http://rubyforge.org/frs/download.php/17497/flvtool2-1.0.6.tgz
    tar -xvf flvtool2-1.0.6.tgz
    cd flvtool2-1.0.6
    ruby setup.rb config && ruby setup.rb setup && sudo ruby setup.rb install

2.4 Finish installation
-----------------------
- Restart zope;
- Login into ZMI, navigate to Naaya instance;
- Select Control Panel tab;
- Uninstall 'Naaya Media File' if installed;
- Install 'Naaya Media File';

3 Getting started
=================
- Login into your Naaya site and navigate to an existing Folder, or add one. 
  Add a new Media File. If all the required tools correctly installed, you'll
  be able to upload almost all known video formats
  (see http://en.wikipedia.org/wiki/FFmpeg for more details), if not, you'll 
  be able to upload only flash video files 
  (see http://en.wikipedia.org/wiki/Flv for more details).

- After the file was successfully uploaded, you can add subtitles in edit form 
  for every language that site supports. The subtitle format must be SubRip 
  (see http://en.wikipedia.org/wiki/Subrip for more details). You can easily 
  create SubRip subtitles for your movies using Subtitle Workshop
  (see http://www.urusoft.net/products.php?cat=sw&lang=1 for more details).

- As playing video files on web requires video conversion on server side, the 
  video will not be available until the conversion is complete, therefore a 
  message will annotate this.
  
- If any error occurs in video conversion process, a generic message will 
  annotate this. For more details about errors occurred check the conversion log 
  file located in the same directory as original video file.
