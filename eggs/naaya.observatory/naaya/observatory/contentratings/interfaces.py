from zope.interface import Interface

class IObservatoryRatable(Interface):
    """Marker interface that promises that an implementing object may be
    rated by users.
    """

