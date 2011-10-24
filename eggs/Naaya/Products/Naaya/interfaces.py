from zope.interface import Interface, Attribute

# import for compatibility
from naaya.core.interfaces import IHeartbeat

class INySite(Interface):
    """ Interface for NySite"""
    pass

class INyFolder(Interface):
    """ Interface for NyFolder"""
    pass

class IObjectView(Interface):
    """ Provide information about an object, to be shown in folder listing """
    def version_status():
        """ Returns tuple (versionable, editable) """

    def get_modification_date():
        """
        Modification date as `datetime.datetime` object. For most objects this
        will actually be their `releasedate` property.
        """

    def get_info_text():
        """
        Returns an info text that is displayed next to the item's title. Can
        be an empty string if there is nothing interesting to display.
        """

    def get_icon():
        """
        Returns a dictionary with the following keys:
            `url`
                address of image to be displayed
            `title`
                title of image (used for title and alt text)
        """

    def get_size():
        """
        Returns a description of size. Can be file size, number of items, etc.
        """

class IActionLogger(Interface):
    """ Action logging utility for Naaya """

    def append():
        """ Add an ``IActionLogger`` """

class IActionLogItem(Interface):
    """ Where actual log data resides """

    type = Attribute('type', u'Type of log item')
    created_datetime = Attribute('created_datetime', u"Created datetime")

class INyPluggableItemInstalled(Interface):
    """ A pluggable item was installed """

    context = Attribute('context', "Portal where pluggable item was installed")
    meta_type = Attribute('meta_type', "meta_type of pluggable item")

class ISkelLoad(Interface):
    """ Skel is being loaded """

    site = Attribute('site', "Portal that is being created")
    skel_handler = Attribute('skel_handler', "Instance of SkelTree")
