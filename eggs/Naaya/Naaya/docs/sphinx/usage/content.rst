Content types
=============

When you have a piece of information that you want to see published in the
portal, the first step is to decide what type of content would better
accommodate it. It is important to put the data in the right format because
each type of content has a different set of attributes which can later be
used to correctly index and categorize it.

What is a :term:`content type`?
---------------------------------

All types of content have a common set of attributes that generically describe
resources. They are called metadata. Since fully defining a resource implies
generically describing it and also describing its custom characteristics, all **Naaya** content types have:

* a common set of properties (e.g. title, description, release date, contributor)
* a custom set of properties (e.g. *location* for *events*, *expiration date* for *news*)

Administrators can view and configure all these attributes, or properties, in
the :doc:`admin` *Manage content types*. It is also here that they can decide whether the content types available in the portal can be geo-tagged or
ratable. Depending on the setup chosen by administrators in terms of
geo-taggable content types, such content types can be geotagged by users.

When adding or editing a content type, users can feel in a description of
the content type by means of an easy to use, :term:`WYSIWYG` web editor.

What content types are available?
---------------------------------

Folder
  Folders are containers of information, similar to the ones found
  in operating systems. They have metadata attached, in order to
  help describe and index the data inside them.

File
  A standard file, briefly described by its metadata.
  The file types (PDF, Word, PPT) are automatically recognised by
  the system in most cases and the corresponding icon appears
  next to them. It is possible to keep old versions of Naaya files
  for user consultation.

HTML document
  You can use this content type to build a generic Web page.
  The user-friendly integrated web editor will help you compose the
  pages, without having to actually write HTML code.

Media file
  When you need to display films, presentations, audio tracks or
  other multimedia materials inside the portal pages, you can use
  this content type to upload the film file in any format.

News
  The news item is a short piece of information with a limited
  duration of life. It is very simple to display news from remote
  sources of information in the portal pages and also to allow other
  websites to pick up the latest news from Naaya portals.

Event
  This content type stores information about an event, a meeting, a
  conference, etc. The events are syndicated by default and can be
  shown under the form of an events calendar. The RDF calendar can
  expose events from various sources of information, including the
  local portal.

Story
  The story is somewhat similar to the news, but with an unlimited
  period of relevancy. Stories can contain a longer body, have
  pictures inserted in them and a small image to be displayed on
  the front page if necessary.

URL
  URL objects contain links to remote pages. They are easy to check at
  regular intervals using an automatic link checker and can be described
  by the metadata.

Geo Point
  This content type stores data about certain locations, which are then
  shown on an interactive map.

Pointer
  Pointers are links to internal portal pages. When adding a pointer, a
  sitemap is displayed to pick from.

How to add an object?
-----------------------------------------------------

After having chosen the location where you want to create an instance of a 
content type / an object, and after having chosen the content type you want to
add, there is a sequence of steps you need to follow:

    go to a folder -> choose on the right of *Submit* the type of content you want
    to add -> fill in the form that opens with: Title, Description,
    geographical coverage, keywords, sort order, release date, choose whether
    the object is *open for comments* or not, maintainer email, etc.

    When you've filled in the requested information, you can push the
    *Submit* button, to save the information. Once the object was added,
    you can go back to the folder to edit it.

How to search for content types?
--------------------------------

Content types are pluggable
---------------------------

How to customize a content type?
--------------------------------

Why can't I add an object of a specific content type?
-----------------------------------------------------
There is a global list of allowed content types configurable in
:doc:`Administration, Folder subobjects <admin>`. All folders inspect that list when they
show you the selection list of available content types for new objects.

However, a folder can be customized by using its own list of subobjects;
a manager can click *Edit subobjects* inside a folder and choose to
select a particular list of content types or check *Use defaults*. There
is also an option to make changes easier: recursively apply selected settings
to all subfolders (be it content type customization or `use defaults` setting).
