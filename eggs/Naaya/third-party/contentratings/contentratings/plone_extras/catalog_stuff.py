# This file contains methods useful for indexing the ratings in your
# plone portal_catalog
from zope.component.exceptions import ComponentLookupError
from contentratings.interfaces import IUserRating
from contentratings.interfaces import IEditorialRating
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.CMFCore.utils import getToolByName

# Some example indexableAttribute extensions for the Plone portal_catalog for
# indexing the ratings and/or storing them as metadata.

# This method just stores the average user rating, which may be sufficient for
# many cases, but generally storing a tuple (avg, num) makes more sense but is
# slightly less efficient.  Uncomment the registration below, and comment the
# one for the tuple if you prefer indexing just the average.
def z3_user_rating_avg(object, portal, **kwargs):
    try:
        rated = IUserRating(object)
        return rated.averageRating
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

# registerIndexableAttribute('user_rating_avg', z3_user_rating_avg)

# Storing the average and number as a tuple allows for quick sorting and easy
# access, while still allowing range searches on the average rating.
# This is probably the way to go if you care about both values.
def z3_user_rating_tuple(object, portal, **kwargs):
    try:
        rated = IUserRating(object)
        return (rated.averageRating, rated.numberOfRatings)
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('user_rating_tuple', z3_user_rating_tuple)

def z3_editorial_rating(object, portal, **kwargs):
    try:
        rated = IEditorialRating(object)
        return rated.rating
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('editorial_rating', z3_editorial_rating)

# Example code for adding a new index and metadata to your catalog, call this
# from your Extensions/Install.py, or use GenericSetup to add the desired
# indexes/columns:

def addRatingIndexesToCatalog(portal,
                             indexes=('editorial_rating','user_rating_tuple'),
                             catalog='portal_catalog'):
    """Adds the specified indices as FieldIndexes to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for index in indexes:
            if index in cat.indexes():
                continue

            cat.addIndex(index, 'FieldIndex')
            reindex.append(index)
        if reindex:
            cat.manage_reindexIndex(reindex)

def addRatingMetadataToCatalog(portal,
                             metadata=('editorial_rating','user_rating_tuple'),
                             catalog='portal_catalog'):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
    cat = getToolByName(portal, catalog, None)
    reindex = []
    if cat is not None:
        for column in metadata:
            if column in cat.schema():
                continue
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()

index_mapping = {'editorial_rating':
                    {'name': 'Editorial Rating',
                     'description': 'The rating given by the site editors',
                     'enabled': True,
                     'criteria': ('ATSimpleIntCriterion',)},
                 'user_rating_tuple':
                    {'name': 'User Rating (weighted)',
                     'description': 'Average rating given by users, along '
                                    'with the number of users who made '
                                    'ratings',
                     'enabled': True,
                     'criteria': ()},
                 'user_rating_avg':
                    {'name': 'User Rating',
                     'description': 'Average rating given by users',
                     'enabled': True,
                     'criteria': ('ATSimpleIntCriterion',)},
                 }

def addSmartFolderIndexAndMetadata(portal,
                                   indexes=('editorial_rating',
                                            'user_rating_tuple')):
    """Adds the default indexes to be available from smartfolders"""
    atct_config = getToolByName(portal, 'portal_atct', None)
    if atct_config is not None:
        for index in indexes:
            index_info=index_mapping[index]
            atct_config.updateIndex(index, friendlyName=index_info['name'],
                                 description=index_info['description'],
                                 enabled=index_info['enabled'],
                                 criteria=index_info['criteria'])
            atct_config.updateMetadata(index, friendlyName=index_info['name'],
                                 description=index_info['description'],
                                 enabled=True)
