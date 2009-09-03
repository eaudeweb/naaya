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