ExtFile/ExtImage Product, Version 1.1.x
Copyright (c) 2001 Gregor Heine (mac.gregor@gmx.de). All rights reserved.
ExtFile Home: http://zope.org/Members/MacGregor/ExtFile
License: See doc-1.1/LICENSE.txt

ExtFile/ExtImage, Version 2.0.2
Copyright (c) 2002-2007 Stefan H. Holek, stefan@epy.co.at
ExtFile Home: http://zope.org/Members/shh/ExtFile
License: ZPL
Zope: 2.9-2.11

This product includes software developed by Zope Corporation
for use in the Z Object Publishing Environment (http://www.zope.org/).


Product Description
===================

Requires PIL 1.1.5 or higher.
Requires Zope 2.9.6 or higher.

This product offers replacements for Zope's File and Image content types.
ExtFiles and ExtImages store their data in a repository directory on the
filesystem, not in the ZODB.


Available Documentation
=======================

Directory doc-1.1/ contains README.txt, CHANGES.txt, and LICENSE.txt that
shipped with version 1.1.3 of ExtFile/ExtImage. The README, while a little
outdated, does a good job at explaining the goals of ExtFile. A must read
if you don't know what this is all about.

Directory doc-1.5/ contains README.txt, CHANGES.txt, and UPGRADE.txt that
shipped with version 1.5.6 of ExtFile/ExtImage. See doc-1.5/CHANGES.txt for
a detailed record of improvments made to the ExtFile product over the years.

See CHANGES.txt in this directory for what is new in ExtFile 2.0.x.

ExtFile/ExtImage interfaces are defined in file interfaces.py.

ExtFile can be used to serve files and images directly out of the repository,
bypassing Zope. All you need is an Apache rewrite rule. For details please
refer to: http://zope.org/Members/shh/ExtFile/UsingStaticURLs.


Installation Instructions
=========================

As the directory layout has changed, you must delete an existing installation
of ExtFile <= 1.5.6 before installing ExtFile 2.0.2. You will want to keep
a copy of Config.py to be able to convert the repository configuration.

Untar ExtFile-2.0.2.tar.gz into the Products directory of your Zope instance.

Repository settings are kept in a configuration file, extfile.ini. Copy the
file to INSTANCE_HOME/etc/extfile.ini if you want to make modifications.

The configuration file is well commented, and converting Config.py settings
should be straight-forward. It is a good idea to at least review extfile.ini,
as some defaults have changed and may no longer suit you.

Once you are happy with your settings, restart Zope.


/etc/mime.types
===============

For proper operation, ExtFile relies on the system's mimetype configuration
being in good shape. Mimetypes are typically configured in file
/etc/mime.types, and picked up by Python's mimetypes module on startup.

On Mac OS X, the mime.types file lives in /etc/httpd/mime.types and is thus
not found by the Python interpreter. Mac OS X users have to symlink that file
into the /etc directory for Python (and ExtFile) to work as intended::

    $ cd /etc
    $ sudo ln -s /etc/httpd/mime.types

You can use the [mimetypes] section in extfile.ini to disambiguate and/or
override content-type -> extension mappings.

