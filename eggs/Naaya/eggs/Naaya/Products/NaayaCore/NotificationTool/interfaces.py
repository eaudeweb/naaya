# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

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
    """
    Marker interface - the object accepts subscriptions
    """
