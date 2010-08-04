__doc__ = """ Initiailization of ZOpenArchives Components """

def initialize(context):
    """ """

    #Server products
    import OAIServer
    import ZCatalogHarvester

    #Aggregator (client) products
    import OAIAggregator
    import OAIHarvester

    #Main products
    import OAIRecord
    import OAIToken
    import OAINamespace

    context.registerClass(
        OAIServer.OAIServer,
        constructors = (OAIServer.manage_addOAIServerForm,
                         OAIServer.manage_addOAIServer, ),
        icon='www/icon_object.gif'
    )

    context.registerClass(
        ZCatalogHarvester.ZCatalogHarvester,
        constructors = (ZCatalogHarvester.manage_addZCatalogHarvesterForm,
                         ZCatalogHarvester.manage_addZCatalogHarvester, ),
        icon='www/icon_site.gif',
        visibility=None
    )

    context.registerClass(
        OAIAggregator.OAIAggregator,
        constructors = (OAIAggregator.manage_addOAIAggregatorForm,
                         OAIAggregator.manage_addOAIAggregator, ),
        icon='www/icon_object.gif'
    )

    context.registerClass(
        OAIHarvester.OAIHarvester,
        constructors = (OAIHarvester.manage_addOAIHarvesterForm,
                         OAIHarvester.manage_addOAIHarvester, ),
        icon='www/icon_site.gif',
        visibility=None
    )

    context.registerClass(
        OAIRecord.OAIRecord,
        constructors = (OAIRecord.manage_addOAIRecord, ),
        icon='www/icon_record.gif',
        visibility=None
    )

    context.registerClass(
        OAINamespace.OAINamespace,
        constructors = (OAINamespace.manage_addOAINamespace, ),
        icon='www/icon_site.gif'
    )

    context.registerClass(
        OAIToken.OAIToken,
        constructors = (OAIToken.manage_addOAIToken, ),
        icon='www/icon_record.gif',
        visibility=None
    )
