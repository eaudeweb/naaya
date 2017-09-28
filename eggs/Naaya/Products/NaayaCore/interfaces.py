from zope.interface import Interface, Attribute

class ILinksList(Interface):
    """ Interface for LinksList"""
    pass

class ILocalChannel(Interface):
    """ Interface for LocalChannel"""
    pass

class IRemoteChannel(Interface):
    """ Interface for RemoteChannel"""
    pass

class IRemoteChannelFacade(Interface):
    """ Interface for RemoteChannelFacade"""
    pass

class IScriptChannel(Interface):
    """ Interface for ScriptChannel"""
    pass

class IChannelAggregator(Interface):
    """ Interface for ChannelAggregator"""
    pass

class IDynamicPropertiesItem(Interface):
    """ Interface for DynamicPropertiesItem"""
    pass

class ICSVImportExtraColumns(Interface):
    """
    When bulk-uploading CSV data, columns are mapped to schema
    properties. Some columns may not map to anything, and they would
    be ignored. For each row, if we can find an adapter that provides
    this interface, it will receive the additional CSV data.
    """

    def handle_columns(extra_properties):
        """ Handle extra CSV data columns """

class ICSVImportEvent(Interface):
    """ An event triggered after a CSV import
    """
    context = Attribute("The containing folder")
    ids = Attribute("List containing the ids of the newly added objects")

class IZipImportEvent(Interface):
    """ Event triggered after a successful Zip upload
    """
    context = Attribute("Containing folder")
    zip_contents = Attribute("Zip contents list (zip.namelist())")

class ICaptcha(Interface):
    """ Captcha functionality: display a challenge; verify the response """

    # `is_available` exists for backwards compatibility. At some point we
    # should roll the old PyCaptcha code into ICaptcha, and `is_available` will
    # always be `True`.
    is_available = Attribute("Is Captcha functionality available?")

    def render_captcha():
        """ Return HTML code to be presented to the user as challenge. """

    def is_valid_captcha(request):
        """ Check if the user solved the captcha correctly. """
