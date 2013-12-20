from zope import interface

class ISubscriptionContainer(interface.Interface):
    """
    Provides the list of people who have subscribed to notifications
    on an object.
    """

    def add(subscription):
        """ Add a subscription to the list """

    def remove(sub_id):
        """
        Remove a subscription from the list, given its ID (as
        returned by `list_with_keys()`)
        """

    def list_with_keys():
        """
        Iterare through subscriptions and their IDs. Yields tuples
        in the form of `(key, subscription)`.
        """

    def __iter__():
        """ Iterate through subscriptions stored here """

class ISubscription(interface.Interface):
    """
    Data for a subscription
    """

    notif_type = interface.Attribute("Type of notification. One of "
                    "`('instant', 'daily', 'weekly', 'monthly')`")

    lang = interface.Attribute("Preferrd language of notification messages")

    def check_permission(obj):
        """
        Check if the subscriber should receive notifications for
        changes on `obj`. Returns `True` or `False`.
        """

    def get_email(obj):
        """
        Return the subscriber's e-mail address. If not found,
        return None, and the notification message will be skipped.

        The `obj` parameter exists because subscriptions have no
        awearness of their context; some of them (e.g. the Naaya
        `AccountSubscription`) need to access the site in order to
        find the email address. `obj` is the subject of the current
        notification (the object that has been created/changed).
        """

    def to_string(obj):
        """
        Representation of this subscription, suitable for the admin
        page. The `obj` parameter is the same as for the `get_email`
        method.
        """

class ISubscriptionTarget(interface.Interface):
    """ Marker interface - a user can subscribe to this object.

    Usually folders, message forums and portals

    """
