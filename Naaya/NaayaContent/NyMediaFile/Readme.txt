NyMediaFile
===========
- A video file container, that display them using flash video player 
EdWideoPlayer (https://svn.eionet.europa.eu/repositories/Zope/trunk/EdWideoPlayer).

1 Install
=========
The following products/tools are required in order to provide all the features:
  * ExtFile 1.5.6;
  * ffmpeg;
  * flvtool2;
If one of this is missing video conversion will not be supported (the users will
be able to upload only flash video files ".flv");

1.1 Install ExtFile:
--------------------
- Download it from provided URL and unpack into your zope instance:
    cd </path to my zope instance/>
    wget http://www.zope.org/Members/shh/ExtFile/1.5.6/ExtFile-1.5.6.tar.gz
    tar -zxvf ExtFile-1.5.6.tar.gz
    rm ExtFile-1.5.6.tar.gz
- Edit REPOSITORY_PATH in ExtFile/Config.py:
    REPOSITORY_PATH = ["var", "reposit"]

1.2 Install ffmpeg
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

1.3 Install flvtool2
--------------------
- Download it from provided URL and unpack into tmp folder:
    cd /tmp
    wget http://rubyforge.org/frs/download.php/17497/flvtool2-1.0.6.tgz
    tar -xvf flvtool2-1.0.6.tgz
    cd flvtool2-1.0.6
    ruby setup.rb config && ruby setup.rb setup && sudo ruby setup.rb install

1.4 Finish installation
-----------------------
- Restart zope;
