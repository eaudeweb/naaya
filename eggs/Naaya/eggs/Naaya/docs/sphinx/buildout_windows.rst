Buildout on windows
===================

.. toctree::
    :hidden:

    ldap_windows

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
4. Subversion command line client (`Binary packages
   <http://subversion.apache.org/packages.html>`_)
   The "bin" folder (e.g. ``C:\Program Files\Subversion Client``) should be added
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

6. The 5 DLL files from `this archive <http://eggshop.eaudeweb.ro/glib-dlls.zip>`_
   should be copied into the Windows\System32 folder.

Configurations, build
---------------------
By default the buildout comes with configuration files for Naaya (``naaya.cfg``).
These steps refer to ``naaya.cfg`` but the same can be applied to other possible configuration files,
e.g.: ``chm.cfg``, ``ew.cfg``.

1. Checkout the Naaya buildout (e.g. into the folder ``D:\Naaya``) from
   https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk

2. Changes to ``naaya.cfg``:

  * If you wish to install separate products, you should create a Products folder
    and add the path to it within the section ``[zope-instance]``, e.g.::

        [zope-instance]
        ...
        products =
            ...
            D:\\Naaya\\Products

3. Open a command prompt, change to the Naaya buildout checkout folder, and run::

       python bootstrap.py -c naaya.cfg
       bin\buildout -c naaya.cfg -v

4. After installation you can start the Zope instance with::

       trunk\bin\zope-instance.exe

Installing LDAP User Folder
---------------------------
If you need to use Python LDAP, please check the installation instructions at :doc:`ldap_windows`.
