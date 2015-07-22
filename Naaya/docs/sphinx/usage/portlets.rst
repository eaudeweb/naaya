Portlets
========

Portlets represent pieces of content that help make up the pages in a
Naaya site. They show up at the left or right side of the main content,
or just below it. Portlets can be assigned to any folder or content
item, and may or may not be inherited by subobjects.

Portlets are part of :ref:`portlets-tool` and can be managed either from
:term:`ZMI` or from the :ref:`administration-section`


Creating portlets
-----------------

The division of some parts of the layout into portlets is made available
for its easy customisation by portal administrators, who can create and
move around boxes of information that are relevant for that particular
portal.

In the *Portlets -> Manage* administration page, it is possible to
create several kinds of portlets. There are pre-defined templates for
remote channel portlets (which display syndicated news/events from
remote RSS feeds), local channel portlets (same for locally-generated
feeds), folders (showing the contents of a folder), lists of links
(showing links defined from the *Administration -> Lists of links*
page). Administrators can also create portlets with static HTML content.

1. Portlet from *Remote channels*

   Such portlet will display the items of the selected remote channel
   (e.g. the news from another biodiversity website), showing their
   titles and the links to the corresponding page on the remote website.

   Administrators can choose to create a portlet from a remote channel,
   if a portlet is not already defined for that channel. As a reminder,
   when users create a remote channel, they can choose to also create a
   portlet for it. If they don't at that stage, they can choose to
   create a portlet from here.

2. Portlet from *Local channels*

   As in the case of remote channels, portlets created from a local
   channel display titles and links of the items included in that local
   channel. For instance, if you want to publish the latest news on
   front page, you will have to create a portlet from the local channel
   *Latest news*.

   Similar to the remote channels, it is also possible to create
   portlets for local channels at the moment of their adding.

   The maximum number of items that this portlet displays is set when
   creating the local channel.

3. Portlet for *Folders*

   This type of portlet is created as a quick link to the folder in the
   portal. Portal administrators choose the folder from a small sitemap
   displayed in this page, and the portlet generated will contain the
   title of the folder and its description, with a link to the folder
   itself.

   Such portlet is useful when administrators want to emphasise from the
   front page a folder where important documents are published.

4. Portlet from *Lists of links*

   The lists of links can be created from the *Lists of links*
   administrative page, and they are used to put together a collection
   of entry points - from the current website or external - useful to
   certain topics.

   As in the case of channels, this page offers the possibility to
   choose a list of links from the existing ones and creates a portlet
   with that list.

5. Portlet as *Static HTML*

   This type of portlet has static text, images and links, that
   administrators compose using the friendly HTML editor, the same
   editor used to add and edit the various content types. It is also
   possible to include films or other Flash or Javascript-based code
   taken from the local or remote websites by editing the HTML source of
   the portlet and pasting the corresponding HTML or Javascript code.

   As opposed to the above-mentioned types of portlets, this one is
   multilingual and its title and body can be translated in all the
   languages available in the portal.

   Additionally, the *Manage portlets* page lists a few portlets defined
   in the system that cannot be changed or deleted by administrators.
   These portlets are called *special* and Naaya portals need them in
   order to work properly.

   When administrators need to create other types of portlets that
   require computation, for instance the items in the portal that are
   tagged with certain keywords or that have a certain geographical
   coverage, technical managers can create these portlets from the ZMI,
   using TAL and Python.


Arranging portlets
------------------

Portlet assignments are configured from the *Portlets -> Arrange*
administration page. In order to create a new assignment, select its
position, the portlet, whether it should be inherited, and  then select
its location (e.g. a folder).

It is also possible to change the ordering of existing portlets by
clicking and dragging the colored *position* field in the assigned
portlets table. In this table, administrators can also choose not to
have displayed certain portlets, by pressing on the *Remove* button.

In the *Arrange portlets* form, administrators can choose where to
display portlets. Portlets can be shown on the left side, right side, or
center (below the page content).

Portlets can also be assigned to the entire portal or to a folder, and
they can be inherited (shown also in sub-folders) or non-inherited. For
example, assigning a portlet on the site, non-inherited, will cause it
to be shown just on the homepage, while assigning the portlet as
inherited will display it on all pages in the site.

There is a further restriction: right-side and center portlets are only
shown on homepage and folder index pages.

The listing of the assigned portlets allows executing management
operations like:

* changing the order the portlets are shown in a certain location, by
  dragging and dropping the corresponding row up and down. For the drag
  and drop operation, the mouse has to be positioned on the *Position*
  column

* deciding to display each portlet

  * only in the specified location (home page or a folder) or
  * also in the subfolders of that location.

  This is done by choosing *yes* or *no* in the inherit column of the
  table. For instance, if you want the left portlets to be shown on all
  the portal pages, you will choose them to be displayed on the front
  page and then set *Inherit* attribute to *yes*.

* removing portlets from the locations (which does not result in
  deletion of the portlet, just not displaying it in that location)

*Note* that portlets inherited from parent folders will always be
displayed above portlets in sub-folders.
