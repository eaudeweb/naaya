Buildout on windows
===================

Prerequisites (software, settings)
----------------------------------

1. Python 2.4.4 (`python-2.4.4.msi
   <http://www.python.org/ftp/python/2.4.4/python-2.4.4.msi>`_)

    The main installation folder (e.g. ``C:\Python24``) and the "Scripts" folder
    (e.g. ``C:\Python24\Scripts``) should be added to the **PATH** system variable.
2. Pywin32 extensions (`pywin32-214.win32-py2.4.exe
   <http://downloads.sourceforge.net/project/pywin32/pywin32/Build%20214/pywin32-214.win32-py2.4.exe>`_)
3. Python imaging library (`PIL-1.1.6.win32-py2.4.exe
   <http://effbot.org/downloads/PIL-1.1.6.win32-py2.4.exe>`_)
4. Subversion 1.6.5 (`Setup-Subversion-1.6.5.msi
   <http://subversion.tigris.org/files/documents/15/46531/Setup-Subversion-1.6.5.msi>`_)
   The "bin" folder (e.g. ``C:\Program Files\Subversion\bin``) should be added
   to the **PATH** system variable.
5. MinGW (`MinGW-5.1.6.exe
   <http://downloads.sourceforge.net/project/mingw/Automated%20MinGW%20Installer/MinGW%205.1.6/MinGW-5.1.6.exe>`_)

    * Choose an installation folder (e.g. ``C:\MinGW``)
    * At least the packages "base" and "make" must be selected for installation
    * After installation, ``cc1.exe`` and ``collect2.exe`` must be copied from
      the folder ``C:\MinGW\libexec\gcc\mingw32\3.4.5`` to the folder ``C:\MinGW\bin``
    * The "bin" folder should be added to the **PATH** system variable.
    * In the folder ``C:\Python24\Lib\distutils`` must be created a file
      ``distutils.cfg`` with the content::

        [build]
        compiler=mingw32

6. The 5 DLL files from `this archive <http://naaya.eaudeweb.ro/eggshop/glib-dlls.zip>`_
   should be copied into the Windows\System32 folder.

Configurations, build
---------------------

1. Checkout the Naaya buildout (e.g. into the folder ``D:\Naaya``) from
   https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk

2. If you make Naaya development, checkout Naaya from
   https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/Naaya
   into a subfolder (e.g. ``D:\Naaya\Naaya210``)

3. Changes to buildout.cfg:
    * If you make Naaya development you should add the path to the chosen Naaya
      checkout folder within the section ``[buildout]``, e.g.::

          [buildout]
          ...
          develop = 
              D:\\Naaya\\Naaya210

    * If you wish to install separate products, you should create a Products folder
      and add the path to it within the section ``[zope-instance]``, e.g.::

          [zope-instance]
          ...
          products =
              ...
              D:\\Naaya\\Products

4. Open a command prompt, change to the Naaya buildout checkout folder, and run::

       python bootstrap.py
       bin\buildout -v

5. After installation you can start the Zope instance with::

       trunk\bin\zope-instance.exe

   or::

       parts\zope-instance\bin\runzope.bat

Installing LDAP User Folder
---------------------------

1. Install Python LDAP User Folder::

    easy_install Products.LDAPUserFolder

   This will install LDAP User Folder *and Python-ldap as a dependency*. The package
   Python-ldap 2.3.10 installed by easy_install is defective and it will fail to load.

2. Open ``Python\Lib\site-packages``, remove the folder
   ``python_ldap-2.3.10-py2.4-win32.egg`` and edit the file ``easy-install.pth``
   removing the line::

       ./python_ldap-2.3.10-py2.4-win32.egg

3. Download and install Python-ldap 2.3.10 (`python-ldap-2.3.10.win32-py2.4.exe
   <http://pypi.python.org/packages/2.4/p/python-ldap/python-ldap-2.3.10.win32-py2.4.exe#md5=ee8e7fce5c29203de4f625b33a3d0cd6>`_)