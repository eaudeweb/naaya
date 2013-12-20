About Naaya
===========

History
-------
Naaya was originally developed by Finsiel, Romania.
Today’s version of Naaya is written as a set of Python products for Zope. 
Around 9 years ago, the need was expressed in the European Environment Agency to have a portal toolkit
easy to install and handle by non-technical administrators. The first toolkit was a simple ZClasses Zope
product with multiple types of content, such as news, events, documents and links. Due to its popularity,
new features were constantly added, mostly by developers now working in Eau de Web, and the technological
solution was enhanced to a set of Zope products, today called Naaya.


This portal toolkit was built to respond to the needs of Web applications for European  and global
institutions, and then continuously fine tuned to use common standards and include modern technologies.
Although most of the features are generic for a multilingual content management system, some of them are 
custom designed to fit the profile of public administration portals. 


Moreover, Naaya is used not only in stand alone websites, but more often in networks of portals. 
Some such communities are:

 * European Community Clearing House Mechanism portal, national portal and portal toolkit, `European CHM`_ - currently over 40 national portals worldwide
 * EnviroWindows network of portals, `EnviroWindows`_, an EEA platform for knowledge sharing and development - currently over 40 national portals worldwide
 * Euro-Mediterranean Information System on Know-How in the Water Sector portal, toolkit and national portals, `Semide`_ - currently 4 portals from the Mediterranean area 
 * SMAP Clearing House, portal toolkit for the national nodes with support for online and offline content management, `SMAP`_ - currently 3 portals from the Mediterranean area
 * Danish Biodiversity Information Facility portal, `DanBIF`_ - Danish biodiversity research platform, International School of Biodiversity Sciences, Entomologisk forening, Naturhistorisk Guide, currently 10 Danish biodiversity portals
 * `DestiNET`_, a network for sustainable tourism information – currently 7 European portals
 * INOGATE energy portal, `Inogate`_

 
Over the years, Eau de Web’s team received feedback from these communities of users, which led to 
regular fixes, extensions, enhancements, that made the tools more modern and user friendly. Several 
custom products have been built for each of these communities, in order to respond to specific 
requirements such as new content types and integration with external databases. 


Requirements
------------
Source code for Naaya is freely available under the Mozilla Public License, and
runs on top of an open source stack, there is no need for any license. The
platform of choice is Linux but Mac OS and Windows are fully supported. Naaya
is not suited for shared-hosting enviromnents; recommended minimum hardware is
a virtual machine with 256MB of RAM.

Naaya stores data in the Zope database (ZODB) which is stored in a file on the
filesystem, so there is no need for an SQL database. Typically there would be
an Apache (or Nginx, etc) front-end web server that proxies requests to Naaya's
Zope server. Apart from that it requires a few commonly-available libraries
(zlib, glib, libxml, libpng, libjpeg).

Installation is performed using Buildout. Given a fresh install of a recent
Linux distribution, one can install Naaya in about 10 minutes, as most of the
process is automated. See the installation documentation for more details:
http://naaya.eaudeweb.ro/docs/getting_started/installation.html

Most administrative tasks are performed through-the-web: setting up portals,
configuring user permissions, customizing the look-and-feel, managing content,
translating messages, and even simple tweaks to functionality (e.g. HTML page
templates).


Releases
--------

*Naaya* has a one month release cycle. Every month we release a new stable
version. For example, *2.11.03* means that the major version of Naaya is *2*,
the year of the release is *2011*, and the *03* is the month.

The decision behind this is that we update *Naaya* very often and there aren't
really many major releases, thus making the update cycle smoother.

What would count as a major release is the switch to a newer version of Zope2
or other major changes that will possibly break old code.


Is Naaya for me?
----------------

If you need a solid CMS based on Zope2...

License
-------
::

    The contents of this package are subject to the Mozilla Public
    License Version 1.1 (the "License"); you may not use this package
    except in compliance with the License. You may obtain a copy of
    the License at http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS
    IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
    implied. See the License for the specific language governing
    rights and limitations under the License.

    The Original Code is Naaya version 1.0

    The Initial Owner of the Original Code is European Environment
    Agency (EEA). Portions created by Finsiel Romania and Eau de Web
    are Copyright (C) European Environment Agency. All Rights Reserved.


Authors
-------
::

    Alec Ghica (Finsiel Romania, Eau de Web)
    Alex Morega (Eau de Web)
    Alexandru Plugaru (Eau de Web)
    Alin Voinea (Eau de Web)
    Andrei Laza (Eau de Web)
    Anton Cupcea (Finsiel Romania, Eau de Web)
    Cornel Nițu (Finsiel Romania, Eau de Web)
    Cristian Ciupitu (Eau de Web)
    Cristian Romanescu (Eau de Web)
    David Bătrânu (Eau de Web)
    Dragoș Chirilă (Finsiel Romania)
    Miruna Badescu (Finsiel Romania, Eau de Web)
    Valentin Dumitru (Eau de Web)

.. _`European CHM`: http://biodiversity-chm.eea.europa.eu/ptk	
.. _`EnviroWindows`: http://ew.eea.europa.eu
.. _`Semide`: http://www.semide.net/ptk
.. _`SMAP`: http://smap.ew.eea.europa.eu/ptk
.. _`DanBIF`: http://www.danbif.dk
.. _`DestiNET`: http://destinet.eu/
.. _`Inogate`: http://www.inogate.org/
