===============
Content Ratings
===============

This is a simple python package driven by Zope 3, which lets users
(including un-authenticated users) rate content.  It provides a set of
interfaces, adapters and views to allow the application of ratings to
any IAnnotatable object.

Dependencies:

BTrees
persistent
zope.annotations
zope.app.container
zope.app.testing
zope.interface
zope.component
zope.lifecycleevent
zope.location
zope.schema
zope.tales

All of these packages are included in Zope 2.10+ and Zope 3.2+.


Using contentratings in Your Packages or Products
=================================================

First install it somewhere in your *python path* (not in your Products
directory), $INSTANCE_HOME/lib/python may be a good place to start using it
with zope.  It can be installed as an egg from the Python Cheeseshop (PyPI).

You'll need to load the zcml for this package, so make sure that the
configure.zcml for your application contains::

 <include package="contentratings" />

If you want to allow some content to be rated you must mark it as
*annotatable*.  This is because the Rating Storage is contained in an
annotation on the content object.  The standard way to do this is to
to add the following to your product's configure.zcml::

 <content class=".content.MyContentClass">
   <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
 </content>


Rating Categories
=================

This package provides an infrastructure for defining `Rating
Categories`.  A `Rating Category` is an object implementing the
`IRatingCategory` interface, specifying a `title`, `description` (for
the UI), `view_name` (how the rating should be rendered and managed in
the UI), TALES expressions which determine when ratings can be viewed
or set (`read_expr` and `write_expr`), an `order` (for the UI), and
finally a `storage` (a factory which creates a persistent
implementation of a rating API to be stored in an annotation). All of
these attributes except `title` are optional, with sensible default
values provided.  Any object may have multiple Rating Categories
applied to it each registered with a unique `name`.


The Default Categories
----------------------

This package's default configuration provides two rating categories.
One for user ratings, and one for editorial ratings.  They are
registered for the marker interfaces `IUserRatable` and
`IEditorRatable` respectively.  The TALES expressions used to
determine when they apply are designed to work with objects contained
in a Zope 2 CMF application (primarily for backwards compatibility
with older versions of `contentratings` which used direct permission
checks). Unless they want to allow all users to set and
read the ratings, other applications will need to define categories with
custom conditions.

Let's demonstrate how these categories might be used.  We need to
create some content and mark it with our marker interface::

    >>> from zope.app.container.sample import SampleContainer
    >>> content = SampleContainer()
    >>> from contentratings.interfaces import IUserRatable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(content, IUserRatable)

Now we can adapt to the rating category using the IUserRating interface::

    >>> from contentratings.interfaces import IUserRating
    >>> adapted = IUserRating(content)
    >>> adapted.title
    u'User Rating'
    >>> float(adapted.averageRating)
    0.0
    >>> rating = adapted.rate(7.0)
    >>> float(adapted.averageRating)
    7.0
    >>> adapted.numberOfRatings
    1
    >>> rating = adapted.rate(8.0, 'me')
    >>> float(adapted.averageRating)
    7.5
    >>> adapted.numberOfRatings
    2

For more details on the IUserRating API see `tests/userstorage.txt`.

Editorial ratings are applied similarly, but have a much simpler
implementation::

    >>> from contentratings.interfaces import IEditorRatable, IEditorialRating
    >>> alsoProvides(content, IEditorRatable)
    >>> adapted = IEditorialRating(content)
    >>> adapted.title
    u'Editor Rating'
    >>> adapted.rating is None
    True
    >>> adapted.rating = 6.0
    >>> float(adapted.rating)
    6.0
    >>> adapted.rating = 8.0
    >>> float(adapted.rating)
    8.0

See `tests/editorialstorage.txt` for details on how the
IEditorialRating API works.

Let's remove these markers now so that we can examine custom
categories::

    >>> from zope.interface import noLongerProvides
    >>> noLongerProvides(content, IUserRatable)
    >>> noLongerProvides(content, IEditorRatable)
    >>> IUserRatable(content) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ...)
    >>> IEditorialRating(content) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ...)

Custom Rating Categories
------------------------

There are two ways to create a new rating category, declaratively
using ZCML, or programatically using the category factory directly
from python.  Let's look at the ZCML way first.  To make it work we
need to enable the zcml directive::

    >>> from zope.configuration import xmlconfig
    >>> import contentratings
    >>> context = xmlconfig.file('meta.zcml', contentratings)

Loading the package configuration will do the above automatically.

Now we register our rating category using the
`contentratings:category` directive::

    >>> context = xmlconfig.string("""
    ... <configure
    ...    xmlns:contentratings="http://namespaces.plone.org/contentratings">
    ...  <contentratings:category
    ...      for="zope.app.container.sample.SampleContainer"
    ...      title="My Rating Category"
    ...      />
    ... </configure>""", context=context)


Here we have made use of all of the category default values.  As a
result we have registered a category which uses the default ZODB
storage and `IUserRating` API, with no restrictions on who can get
and set ratings.  We can verify this easily since the categories are
simply adapters providing the rating interface provided by the
(default) storage::

    >>> from contentratings.interfaces import IUserRating
    >>> from zope.app.container.sample import SampleContainer
    >>> content = SampleContainer()
    >>> adapted = IUserRating(content)
    >>> IUserRating.providedBy(adapted)
    True
    >>> adapted.context is content
    True
    >>> adapted.title
    u'My Rating Category'

Note that because we provided no name in the configuration, the
adapter was registered as the default (unnamed) adapter.  The name of
the category is the name under which the adapter is registered and it
is stored in the category's name attribute::

    >>> adapted.name
    ''

To provide multiple categories, just register them with unique names::

    >>> context = xmlconfig.string("""
    ... <configure
    ...    xmlns:contentratings="http://namespaces.plone.org/contentratings">
    ...  <contentratings:category
    ...      for="zope.app.container.sample.SampleContainer"
    ...      title="My Other Rating Category"
    ...      name="other"
    ...      />
    ... </configure>""", context=context)
    >>> from zope.component import getAdapter
    >>> adapted = getAdapter(content, IUserRating, name=u'other')
    >>> adapted.title
    u'My Other Rating Category'
    >>> adapted.name
    u'other'

If we wanted to accomplish the same thing programatically, we could
instantiate the factory directly and register it as an adpater::

    >>> from contentratings.category import RatingsCategoryFactory
    >>> category = RatingsCategoryFactory(title=u'Another Title', name=u'another')
    >>> from zope.component import provideAdapter
    >>> provideAdapter(category, adapts=(SampleContainer,), provides=IUserRating,
    ...                name=u'another')
    >>> adapted = getAdapter(content, IUserRating, name=u'another')
    >>> adapted.title
    u'Another Title'
    >>> adapted.name
    u'another'

This involves some redundancy, since the interface provided by the
storage has to be explicitly declared, and the category name has to be
provided twice.  Otherwise they are equivalent.

Note that categories are adapters, and adapters may only be registered under
the same name for different interfaces/classes.  As usual, for a given name,
the adapter registered for the most specific interface will be chosen.

The Rating Manager
==================

When the adapter corresponding to a given rating category is
queried, the object returned is not actually a `Rating Category`
itself, but a `Rating Manager`::

    >>> adapted # doctest: +ELLIPSIS
    <contentratings.category.RatingCategoryAdapter ...>
    >>> from contentratings.interfaces import IRatingManager
    >>> IRatingManager.providedBy(adapted)
    True
    
The Rating Manager provides the API of the storage, and also many of
the attributes of the category.  It protects direct access to the
storage by checking the expressions specified for the category.  The
manager is implemented as a multi-adapter on the category and the
context, but generally it should not be retrieved directly.  The
category adapter is responsible for retrieving it.  The manager is
responsible for setting up the category specific storage on the
content object.

    >>> adapted.category # doctest: +ELLIPSIS
    <contentratings.category.RatingsCategoryFactory ...>
    >>> adapted.context # doctest: +ELLIPSIS
    <zope.app.container.sample.SampleContainer ...>
    >>> adapted.storage # doctest: +ELLIPSIS
    <contentratings.storage.UserRatingStorage ...>
    >>> isinstance(adapted.storage, adapted.category.storage)
    True

Since the rating manager is responsible for security checks and
populating the TALES expression context, it is very likely that
applications will want to replace this component (locally or for
specific content) with a subclass to provide application specific
security.

The Views
=========

The Rating Views
----------------

Each category has an associated `view_name` which is simply the name
of a view registered for the rating interface (e.g. IUserRating) to be
used when rendering the category in the UI.  These are looked up on
the Rating Manager and have access to the `IRatingManager` API, as
well as the protected rating storage API, as provided by the
manager (e.g. IUserRating).

Resuable base classes for rating views are provided in
`browser/basic.py` (`BasicUserRatingView` and
`BasicEditorialRatingView`).  These views use a named vocabulary to
validate input and use the IRatingManager API to determine who can and
cannot rate content.  The package configuration provides a few rating
views by default::

  ratings_view (default):  A rating using 1-5 large (25px) stars
  small_stars: A rating using 1-5 small (10px) stars
  three_small_stars: A rating using 1-3 small (10px) stars

These are each highly customizable using CSS. They are all registered
for IUserRating.  Additionally, there is a `rating_view` is registered
for IEditorialRating.

The views are responsible for looking up a rating vocabulary and
validating user input, as well as rendering the user interface.  The
security is enforced by the `Rating Manager` used by the view, however
the view may go directly to the storage from rating manager if it
wants to override the expression checking (e.g. showing a user their
own ratings, though they cannot see others).  Creating new views
(e.g. non-starred ratings) is quite simple.

A utility is provided for efficiently determining a reusable session
key in a generic manner.  This can be used to prevent repeat voting
from anonymous users.  Applications which implement their own
anonymous session tracking mechanisms may override this utility
locally if desired.

The Aggregator Views
--------------------

There are also views which find all the rating categories available on
the content object being viewed, rendering them in order.  These are
intended to be used within a viewlet, portlet, macro, or similar.  The
aggregator view for user ratings is called `user-ratings` and the one
for editorial ratings is called `editorial-ratings`.


The Storage
===========

Though the `UserRatingStorage` should be sufficient fr most usecases,
this package provides a simplemechanism for using custom objects for
storing ratings.  Two storage factory implementations are included,
both of which use the ZODB for storing ratings: one implementing the
`IUserRating` interface and the other the `IEditorialRating`
interface.  The former is intended to be used for any content which
will be rated (or voted on) by multiple users.  The latter stores a
single "editorial" rating on content, and exists primarily for
backwards compatibility.

A custom sotrage factory (possibly sub-classed from one of the included
implementations), can be specified using the `storage` attribute of
the zcml directive, or `storage` parameter of the rating category factory.

Not only are the storages replaceable, they can implement completely
custom APIs for managing ratings.  Though the need for this is is
probably limited, you may create a custom storage API by making an
interface for managing ratings, and having that interface provide
`IRatingType`.  See the storage documentation in `tests/` for more
information.


Why a New Rating Package
========================

There are already the `ATRatings`, `lovely.rating`, `iqpp.rating`, and
`iqpp.plone.rating` packages, why do we need another package?

First, contentratings preceeds all of those except ATRatings, which is
useful only under Plone with Archetypes content.  `contentratings` was
originally a very simple package intended to make it easy for
developers to add ratings to their products and applications.
However, there appears to be much demand for an end-user product to
facilitate adding ratings to existing content objects.

Unfortunately, none of these packages offer direct support for
multiple ratings on a single content object, which appears to be a
common need.  It also (along with `lovely.rating`) decouples the
rating scoring system from the view in a manner which is probably
undesirable for a product which wants to allow user customization of
ratings.  Changing these packages to support these use-cases would
have required a complete rewrite.  As a result, I rewrote the simplest
(and most familiar) of these rating packages to support these
usecases, and also created a new package to integrate this new
functionality for Plone end-users (see `plone.contentratings`).

ToDo
====

* Provide view customization examples
* Make the views work with Zope 3 authentication
* Port the KSS view from plone.contentratings into contentratings (it
  currently depends on some plone KSS commands)


Credits
=======

Author:
-------

* **Alec Mitchell** <apm13@columbia.edu>


Contributors:
-------------

* **Maurizio Delmonte**

(feel free to add your name above if you have made significant contributions)

Thanks To:
----------

* **Geoff Davis** author of `ATRatings` from which icons and ideas were
  stolen.

* **Philipp von Weitershausen** author of
  `Web Component Development with Zope 3`_ which provides a nice example
  of an annotation based rating product, which was the starting point for
  this implementation.

* **Kai Diefenbach** author of `iqpp.plone.rating` from which other icons
  and UI ideas were stolen.

* Some icons are from **Mark James'** `Silk icon set 1.3`_

* The star rating is based on `CSS Star Rating Redux`_ via `iqpp.plone.rating`

.. _`Web Component Development with Zope 3`: http://www.worldcookery.com/
.. _`Silk icon set 1.3`: http://www.famfamfam.com/lab/icons/silk/
.. _`CSS Star Rating Redux`: http://komodomedia.com/blog/index.php/2007/01/20/css-star-rating-redux/
