CHM Portal Toolkit
==================

Buildout-based installation of the CHM PTK, with current packages as of
November 2011. Based on Zope 2.12.18. Packages are installed from PyPI_
and the Eau de Web package repository_.

.. _PyPI: http://pypi.python.org/pypi
.. _repository: http://eggshop.eaudeweb.ro/


Installation on Windows
-----------------------

1. Install `Python 2.6`_, PyWin32_ and `PIL 1.1.7`_.

2. Download and unzip the `chm-ptk archive`_.

3. In a command prompt, run the following commands, from inside the
   ``chm-ptk`` folder. They will take a few minutes but should complete
   without error::

    \Python26\python.exe bootstrap.py -d
    bin\buildout.exe

4. If the previous step completed successfully, install Zope as a
   Windows service, and start it::

    bin\zope-instance.exe install
    bin\zope-instance.exe start

.. _`Python 2.6`: http://www.python.org/ftp/python/2.6.6/python-2.6.6.msi
.. _PyWin32: http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download
.. _`PIL 1.1.7`: http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe
.. _`chm-ptk archive`: http://eggshop.eaudeweb.ro/chm-ptk-2011-11.zip
