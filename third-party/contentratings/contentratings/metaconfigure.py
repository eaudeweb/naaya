from zope.configuration.exceptions import ConfigurationError
from zope.component.zcml import handler, provideInterface
from zope.interface import implementedBy
from contentratings.category import RatingsCategoryFactory
from contentratings.interfaces import IRatingType

def category(_context, for_, title, name='', view_name='ratings_view',
             description=u'', read_expr=None, write_expr=None,
             storage=None, order=100):
    """Creates and registers a rating category"""
    factory = RatingsCategoryFactory(title, name=name, view_name=view_name,
                                     read_expr=read_expr, write_expr=write_expr,
                                     storage=storage, order=order)

    # the resulting storage must have an IRatingType interface
    implemented = implementedBy(factory.storage)
    provides = None
    for possible in implemented:
        if IRatingType.providedBy(possible):
            provides = possible
    if provides is None:
        raise ConfigurationError('The storage factory must provide an '
                                 'IRatingType interface.')

    # register our adapter
    _context.action(
        discriminator=('category', for_, name, provides),
        callable = handler,
        args= ('registerAdapter',
                factory, (for_,), provides, name, _context.info)
        )

    # Register the interfaces infvolved globally
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
