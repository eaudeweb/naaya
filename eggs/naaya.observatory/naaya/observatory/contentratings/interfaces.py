from zope.annotation.interfaces import IAnnotatable

class IObservatoryRatable(IAnnotatable):
    """Marker interface that promises that an implementing object may be
    rated by users using the IUserRating interface.
    """

