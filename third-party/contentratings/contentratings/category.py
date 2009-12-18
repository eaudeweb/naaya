from persistent import Persistent
from zope.interface import implements, Interface, alsoProvides
from zope.component import adapts, queryMultiAdapter, getMultiAdapter
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.interface import queryType
from zope.app.container.contained import contained
from zope.event import notify
from zope.tales.engine import Engine
from BTrees.OOBTree import OOBTree
try:
    from Acquisition import aq_base
except ImportError:
    # Do nothing
    aq_base = lambda x: x
from contentratings.interfaces import (
    IRatingType,
    IRatingCategory,
    IRatingManager,
    IRatingStorage,
    IRatingStorageMigrator,
    _,
    )
from contentratings.events import ObjectRatedEvent
from contentratings.storage import UserRatingStorage

BASE_KEY = 'contentratings.userrating'

def expression_property(name):
    """A closure for creating properties which invalidate an _v_cache
    when changed.  Used to ensure that the complied version is
    up-to-date."""
    def _get(self):
        return getattr(self, '_expr_' + name)
    def _set(self, val):
        setattr(self, '_expr_' + name, val)
        # Remove the cache if it exists
        cache_name = '_v_' + name
        if hasattr(self, cache_name):
            delattr(self, cache_name)
    return property(_get, _set)

class RatingsCategoryFactory(Persistent):
    """Contains all settings for a rating category"""
    implements(IRatingCategory)
    storage = UserRatingStorage
    # compiled expressions

    def __init__(self, title=u'', name=u'', view_name=u'ratings_view',
                 description=u'', read_expr=None,
                 write_expr=None, storage=None, order=100):
        """Sets the category properties and compiles the expressions"""
        self.name = name
        self.title = title
        self.view_name = view_name
        self.description = description
        self.order = order
        self.read_expr = read_expr
        self.write_expr = write_expr
        if storage is not None:
            self.storage = storage

    @property
    def __name__(self):
        # Use Zope 3 convention
        return self.name

    # expressions which invalidate cache on set
    read_expr = expression_property('read')
    write_expr = expression_property('write')

    # Read-only properties containing a cached compiled TALES expression
    @property
    def read(self):
        if not self.read_expr:
            return None
        if not hasattr(self, '_v_read'):
            self._v_read = Engine.compile(self.read_expr)
        return self._v_read
    @property
    def write(self):
        if not self.write_expr:
            return None
        if not hasattr(self, '_v_write'):
            self._v_write = Engine.compile(self.write_expr)
        return self._v_write

    def __call__(self, context):
        """Returns the rating manager for self, context, or None if
        one is not found"""
        return queryMultiAdapter((self, context), IRatingManager)


def expression_runner(name):
    """Closure for generating a property which runs an expression"""
    @property
    def runner(self):
        """Returns the result of the desired TALES expression"""
        expr = getattr(self.category, name, None)
        if expr is not None:
            try:
                res = expr(self._getExprContext())
                if isinstance(res, Exception):
                    # raise any excpetions returned by the expression
                    raise res
            except AttributeError, e:
                # prevent uninformative errors during property lookup,
                # by wrapping AttributeErrors
                raise RuntimeError(e)
            return res
        return True
    return runner

class RatingCategoryAdapter(object):
    """A multiadapter which takes the rating settings, the rating
    storage, and the context and implements basic ratings
    functionality"""
    implements(IRatingManager)
    adapts(IRatingCategory, Interface)

    def __init__(self, category, context):
        self.category = category
        self.context = context
        self.storage = self._lookup_or_create_storage()
        # We dynamically provide all the rating methods
        # of our underlying storage
        rating_type = queryType(self.storage, IRatingType)
        alsoProvides(self, rating_type)

    def _lookup_or_create_storage(self):
        category = self.category
        context = self.context
        # lookup the key directly on the category if set (this used for BBB)
        if hasattr(category, 'key'):
            key = category.key
        else:
            # Get the key from the storage, or use a default
            key = getattr(category.storage, 'annotation_key', BASE_KEY)
            # Append the category name to the dotted annotation key name
            if category.name:
                key = str(key + '.' + category.name)
        # Retrieve the storage from the annotation, or create a new one
        annotations = IAnnotations(context)
        try:
            storage = annotations[key]
        except KeyError:
            storage = annotations[key] = category.storage()
            # set containment for the ratings storage
        if not isinstance(storage, category.storage):
            # if the storage is not an instance of the category
            # storage, attempt to migrate it.  This check
            # requires that storage factories be implemented
            # as standard class.
            orig_storage = storage
            storage = category.storage()
            migrator = getMultiAdapter((orig_storage, storage),
                                       IRatingStorageMigrator)
            storage = migrator.migrate()
            # the migrator may have returned a different object
            # or it may have accepted the original storage
            if annotations[key] is not storage:
                annotations[key] = storage
        # Use the unwrapped context as container, so that
        # this doesn't mutate the storage everytime when
        # context changes due to wrapping.  This should
        # only have an effect when the storage is new.
        return contained(storage, aq_base(context), key)

    @property
    def title(self):
        """Returns the rating title"""
        return self.category.title

    @property
    def description(self):
        """Returns the rating title"""
        return self.category.description

    @property
    def order(self):
        """Returns the rating title"""
        return self.category.order

    @property
    def name(self):
        """Returns the rating title"""
        return self.category.name

    @property
    def view_name(self):
        """Returns the rating title"""
        return self.category.view_name

    def _get_user(self):
        """Not Implemented, please override"""
        return None

    @property
    def userid(self):
        """This will need to be overridden for some auth systems"""
        user = self._get_user()
        if hasattr(user, 'getId'):
            return user.getId()

    def _getExprContext(self):
        """Dumb tal expression context, please override"""
        return Engine.getContext({'context': self.context,
                                  'user': self._get_user()})

    # Expressions which evaluate the complied expressions from the category
    can_read = expression_runner('read')
    can_write = expression_runner('write')

    # Magic to ensure we implement the desired Rating interface
    def __getattr__(self, name):
        """If name is part of our storage interface, return the
        attribute from the storage, checking the read_expr first.
        """
        rating_type = queryType(self, IRatingType)
        # make sure it works even if the rating type isn't set yet
        if rating_type and name in rating_type.names(True):
            assert self.can_read
            return getattr(self.storage, name)
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        """If name is part of our storage interface, set the
        attribute from the storage, checking the write_expr first.
        """
        rating_type = queryType(self, IRatingType)
        # make sure it works even if the rating type isn't set yet
        if rating_type and name in rating_type.names(True):
            assert self.can_write
            # special handling for the "rating" atribute from
            # EditorialRatingStorage
            if name =='rating':
                self._rating_set(value)
            else:
                setattr(self.storage, name, value)
        else:
            super(RatingCategoryAdapter, self).__setattr__(name, value)

    # Special attributes 'rate', 'rating', and '__setitem__' which
    # are used to set ratings.
    # Custom IRatingType/Storages should implement one of
    # these attributes, fire their own events, or use a custom RatingManager.
    def rate(self, *args, **kw):
        """Uses the rate method of the underlying storage"""
        assert self.can_write
        storage = self.storage
        result = storage.rate(*args, **kw)
        rating = result
        if rating is None and hasattr(storage, 'most_recent'):
            rating = storage.most_recent
        if rating is not None:
            # we assume the return value, if it exists is a rating useful
            # for the event
            notify(ObjectRatedEvent(self.context, rating, self.name))
        return result

    def __setitem__(self, name, val):
        """The default storages do not provide a dictionary API, but this may
        be useful for custom rating types."""
        assert self.can_write
        storage = self.storage
        storage[name] = val
        if name is not None or not hasattr(storage, 'most_recent'):
            rating = storage[name]
        else:
            rating = storage.most_recent
        notify(ObjectRatedEvent(self.context, rating, self.name))

    def _rating_set(self, value):
        """Uses the rate method of the underlying storage and fires an event"""
        self.storage.rating = value
        notify(ObjectRatedEvent(self.context, self.storage.rating,
                                self.name))

    # Lame BBB for Five i18n
    @property
    def REQUEST(self):
        return getattr(self.context, 'REQUEST', None)
