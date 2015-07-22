Layout
======

Naaya layout is completly customizable.

* Some basic info about the :term:`TAL` and :term:`ZPT`
* Why :term:`TAL` and not X templating system?
* What is standard template? What is portlet_main?

Since the content is separated from the presentation and from the application 
logic, it is possible to create other layouts by accessing the *ZMI -> 
portal_templates*. In here, you'll find the portal layout, containing 
templates for the header, footer, left/center/right portlets and colour 
schemes. Changing the template requires knowledge of TAL and METAL.

Creating or changing a colour scheme is however very simple for the web 
designers since they need to make a copy of an existing one and edit the CSS 
files and/or replace the few images used in designing the template.

For each portal, new layouts can be created and the existing ones can be 
changed from the Zope Management Interface by entering the *portal_layout* 
object from the corresponding *Site* object. The easiest way to create a new 
layout is to copy the existing one and to start modifying the *Naaya Template* 
inside:

* *portlet_center_macro*, the template for the central portlets that appear on the front page
* *portlet_left_macro*, the template for the left-side portlets
* *portlet_right_macro*, the template for the right-side portlets
* *standard template*, the customized standard template

Icons for content types
-----------------------

Content objects display an icon on their `index` page. By default, this is the
icon registered with Zope, which is also shown in the ZMI. The icon can be
customized: if there is an image in the current layout color scheme, named
``Naaya_Folder-icon`` or ``Naaya_Folder-icon-marked`` (replace ``Naaya_Folder``
with any other meta type), it will be used instead. Note however that this
customization does not affect object listings in folders - perhaps it should.
