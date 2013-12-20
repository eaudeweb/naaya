===================
Buildout on windows
===================

.. toctree::
    :hidden:

    ldap_windows


Using Zope 2.12
===============

The buildout with Zope 2.12 has few dependencies. First, install `Python
2.6`_, PyWin32_ and `PIL 1.1.7`_. Then download the `default buildout
configuration`_ and, from inside, run the following commands::

    \Python26\python.exe bootstrap.py -d
    bin\buildout.exe

If all works fine you should be able to start Zope::

    bin\zope-instance.exe fg

.. _`Python 2.6`: http://www.python.org/ftp/python/2.6.6/python-2.6.6.msi
.. _PyWin32: http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download
.. _`PIL 1.1.7`: http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe
.. _`default buildout configuration`: https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/zope212/


Using Zope 2.10 (legacy)
========================

Prerequisites (software, settings)
----------------------------------

1. Python 2.4.4 (`python-2.4.4.msi
   <http://www.python.org/ftp/python/2.4.4/python-2.4.4.msi>`_)

   The main installation folder (e.g. ``C:\Python24``) and the "Scripts" folder
   (e.g. ``C:\Python24\Scripts``) should be added to the **PATH** system variable.
2. Pywin32 extensions (`pywin32-216.win32-py2.4.exe
   <http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.4.exe>`_)
3. Python imaging library (`PIL-1.1.6.win32-py2.4.exe
   <http://effbot.org/downloads/PIL-1.1.6.win32-py2.4.exe>`_).
   **Important**. While some of the these prerequisites can also be
   installed in newer versions, the Python imaging library **must be kept
   at version 1.1.6** (although 1.1.7 is released already).
4. Subversion command line client (`Binary packages
   <http://www.sliksvn.com/en/download>`_)
   The "bin" folder (e.g. ``C:\Program Files\Subversion Client``) should be added
   to the **PATH** system variable.
5. MinGW (`MinGW
   <http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/mingw-get-inst/mingw-get-inst-20110802/mingw-get-inst-20110802.exe>`_)

  * Choose an installation folder (e.g. ``C:\MinGW``)
  * At least the package "C Compiler" must be selected for installation
    (default setting)
  * After installation, ``cc1.exe`` and ``collect2.exe`` must be copied from
    the folder ``C:\MinGW\libexec\gcc\mingw32\<version>`` to the folder ``C:\MinGW\bin``
  * The "bin" folder should be added to the **PATH** system variable.
  * In the folder ``C:\Python24\Lib\distutils`` must be created a file
    ``distutils.cfg`` with the content::

      [build]
      compiler=mingw32

6. The 5 DLL files from `this archive <http://eggshop.eaudeweb.ro/glib-dlls.zip>`_
   should be copied into the Windows\System32 folder (**and
   Windows\SysWOW64 if on Windows 7 64bit**).

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

       bin\zope-instance.exe fg

Installing LDAP User Folder
---------------------------
If you need to use Python LDAP, please check the installation instructions at :doc:`ldap_windows`.
