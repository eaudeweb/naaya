from App.ImageFile import ImageFile

import Products.Naaya
from constants import *

try:
    import GeoMapTool
    geo_installed = True
except ImportError:
    geo_installed = False

def initialize(context):
    """ """

    # don't think about importing these top-level like this because
    # they mess up modules' paths
    from CatalogTool import CatalogTool
    from EmailTool import EmailTool
    from SyndicationTool import SyndicationTool
    from AuthenticationTool import AuthenticationTool
    from PropertiesTool import PropertiesTool
    from DynamicPropertiesTool import DynamicPropertiesTool
    from PortletsTool import PortletsTool
    from FormsTool import FormsTool
    from LayoutTool import LayoutTool
    from NotificationTool import NotificationTool
    from EditorTool import EditorTool
    from SchemaTool import SchemaTool
    from GoogleDataTool import AnalyticsTool
    from GeoMapTool import GeoMapTool

    context.registerClass(
        PropertiesTool.PropertiesTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                PropertiesTool.manage_addPropertiesTool,
                ),
        icon = 'PropertiesTool/www/PropertiesTool.gif'
        )
    context.registerClass(
        CatalogTool.CatalogTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                CatalogTool.manage_addCatalogTool,
                ),
        icon = 'CatalogTool/www/CatalogTool.gif'
        )
    context.registerClass(
        EmailTool.EmailTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                EmailTool.manage_addEmailTool,
                ),
        icon = 'EmailTool/www/EmailTool.gif'
        )
    context.registerClass(
        SyndicationTool.SyndicationTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                SyndicationTool.manage_addSyndicationTool,
                ),
        icon = 'SyndicationTool/www/SyndicationTool.gif'
        )
    context.registerClass(
        AuthenticationTool.AuthenticationTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                AuthenticationTool.manage_addAuthenticationTool,
                ),
        icon = 'AuthenticationTool/www/AuthenticationTool.gif'
        )
    context.registerClass(
        DynamicPropertiesTool.DynamicPropertiesTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                DynamicPropertiesTool.manage_addDynamicPropertiesTool,
                ),
        icon = 'DynamicPropertiesTool/www/DynamicPropertiesTool.gif'
        )
    context.registerClass(
        FormsTool.FormsTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                FormsTool.manage_addFormsTool,
                ),
        icon = 'FormsTool/www/FormsTool.gif'
        )
    context.registerClass(
        PortletsTool.PortletsTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                PortletsTool.manage_addPortletsTool,
                ),
        icon = 'PortletsTool/www/PortletsTool.gif'
        )
    context.registerClass(
        LayoutTool.LayoutTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                LayoutTool.manage_addLayoutTool,
                ),
        icon = 'LayoutTool/www/LayoutTool.gif'
        )
    context.registerClass(
        NotificationTool.NotificationTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                NotificationTool.manage_addNotificationTool,
                ),
        icon = 'NotificationTool/www/NotificationTool.gif'
        )
    context.registerClass(
        EditorTool.EditorTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                EditorTool.manage_addEditorTool,
                ),
        icon = 'EditorTool/www/EditorTool.gif'
        )
    context.registerClass(
        SchemaTool.SchemaTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                SchemaTool.manage_addSchemaTool,
                ),
        icon = 'SchemaTool/www/SchemaTool.gif'
        )
    context.registerClass(
        AnalyticsTool.AnalyticsTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                AnalyticsTool.manage_addAnalyticsTool,
                ),
        icon = 'GoogleDataTool/www/AnalyticsTool.gif'
        )

    if geo_installed:
        context.registerClass(
            GeoMapTool.GeoMapTool,
            permission = PERMISSION_ADD_NAAYACORE_TOOL,
            constructors = (
                    GeoMapTool.manage_addGeoMapTool,
                    ),
            icon = 'GeoMapTool/www/GeoMapTool.gif'
            )

misc_ = {
    'PropertiesTool.gif':ImageFile('PropertiesTool/www/PropertiesTool.gif', globals()),
    'CatalogTool.gif':ImageFile('CatalogTool/www/CatalogTool.gif', globals()),
    'EmailTool.gif':ImageFile('EmailTool/www/EmailTool.gif', globals()),
    'EmailTemplate.gif':ImageFile('EmailTool/www/EmailTemplate.gif', globals()),
    'SyndicationTool.gif':ImageFile('SyndicationTool/www/SyndicationTool.gif', globals()),
    'RemoteChannel.gif':ImageFile('SyndicationTool/www/RemoteChannel.gif', globals()),
    'RemoteChannelFacade.gif':ImageFile('SyndicationTool/www/RemoteChannelFacade.gif', globals()),
    'LocalChannel.gif':ImageFile('SyndicationTool/www/LocalChannel.gif', globals()),
    'ScriptChannel.gif':ImageFile('SyndicationTool/www/ScriptChannel.gif', globals()),
    'ChannelAggregator.gif':ImageFile('SyndicationTool/www/ChannelAggregator.gif', globals()),
    'AuthenticationTool.gif':ImageFile('AuthenticationTool/www/AuthenticationTool.gif', globals()),
    'User.gif':ImageFile('AuthenticationTool/www/User.gif', globals()),
    'Permission.gif':ImageFile('AuthenticationTool/www/Permission.gif', globals()),
    'Role.gif':ImageFile('AuthenticationTool/www/Role.gif', globals()),
    'DynamicPropertiesTool.gif':ImageFile('DynamicPropertiesTool/www/DynamicPropertiesTool.gif', globals()),
    'DynamicPropertiesItem.gif':ImageFile('DynamicPropertiesTool/www/DynamicPropertiesItem.gif', globals()),
    'PortletsTool.gif':ImageFile('PortletsTool/www/PortletsTool.gif', globals()),
    'EditorTool.gif':ImageFile('EditorTool/www/EditorTool.gif', globals()),
    'Portlet.gif':ImageFile('PortletsTool/www/Portlet.gif', globals()),
    'HTMLPortlet.gif':ImageFile('PortletsTool/www/HTMLPortlet.gif', globals()),
    'LinksList.gif':ImageFile('PortletsTool/www/LinksList.gif', globals()),
    'RefList.gif':ImageFile('PortletsTool/www/RefList.gif', globals()),
    'RefTree.gif':ImageFile('PortletsTool/www/RefTree.gif', globals()),
    'RefTreeNode.gif':ImageFile('PortletsTool/www/RefTreeNode.gif', globals()),
    'FormsTool.gif':ImageFile('FormsTool/www/FormsTool.gif', globals()),
    'LayoutTool.gif':ImageFile('LayoutTool/www/LayoutTool.gif', globals()),
    'Skin.gif':ImageFile('LayoutTool/www/Skin.gif', globals()),
    'Template.gif':ImageFile('LayoutTool/www/Template.gif', globals()),
    'Scheme.gif':ImageFile('LayoutTool/www/Scheme.gif', globals()),
    'Style.gif':ImageFile('LayoutTool/www/Style.gif', globals()),
    'DiskFile.gif':ImageFile('LayoutTool/www/DiskFile.gif', globals()),
    'DiskTemplate.gif':ImageFile('LayoutTool/www/DiskTemplate.gif', globals()),
    'checkered.png':ImageFile('LayoutTool/www/checkered.png', globals()),
    'NotificationTool.gif':ImageFile('NotificationTool/www/NotificationTool.gif', globals()),
    'xml.png':ImageFile('SyndicationTool/www/xml.png', globals()),
    'xml-blue.jpg':ImageFile('SyndicationTool/www/xml-blue.jpg', globals()),
    'SchemaTool.gif': ImageFile('SchemaTool/www/SchemaTool.gif', globals()),
    'AnalyticsTool.gif': ImageFile('GoogleDataTool/www/AnalyticsTool.gif', globals()),
#     'Schema.gif': ImageFile('SchemaTool/www/Schema.gif', globals()),
#     'PropertyDefinition.gif': ImageFile('SchemaTool/www/PropertyDefinition.gif', globals()),
}
if geo_installed:
    gmisc_ = {
    'GeoMapTool.gif':ImageFile('GeoMapTool/www/GeoMapTool.gif', globals()),
    'progress.gif':ImageFile('GeoMapTool/www/progress.gif', globals()),
    'shadow.png':ImageFile('GeoMapTool/www/shadow.png', globals()),
    'geomaptool.js':ImageFile('GeoMapTool/www/geomaptool.js', globals()),

    'pin1.png':ImageFile('GeoMapTool/images/pin1.png', globals()),
    'pin2.png':ImageFile('GeoMapTool/images/pin2.png', globals()),
    'pin3.png':ImageFile('GeoMapTool/images/pin3.png', globals()),
    'pin4.png':ImageFile('GeoMapTool/images/pin4.png', globals()),
    'pin5.png':ImageFile('GeoMapTool/images/pin5.png', globals()),
    'pin6.png':ImageFile('GeoMapTool/images/pin6.png', globals()),
    'pin7.png':ImageFile('GeoMapTool/images/pin7.png', globals()),
    'pin8.png':ImageFile('GeoMapTool/images/pin8.png', globals()),
    'pin9.png':ImageFile('GeoMapTool/images/pin9.png', globals()),
    'pin10.png':ImageFile('GeoMapTool/images/pin10.png', globals()),
    'pin11.png':ImageFile('GeoMapTool/images/pin11.png', globals()),
    'pin12.png':ImageFile('GeoMapTool/images/pin12.png', globals()),
    'pin13.png':ImageFile('GeoMapTool/images/pin13.png', globals()),
    'pin14.png':ImageFile('GeoMapTool/images/pin14.png', globals()),
    'pin15.png':ImageFile('GeoMapTool/images/pin15.png', globals()),
    'pin16.png':ImageFile('GeoMapTool/images/pin16.png', globals()),
    'pin17.png':ImageFile('GeoMapTool/images/pin17.png', globals()),
    'pin18.png':ImageFile('GeoMapTool/images/pin18.png', globals()),
    'pin19.png':ImageFile('GeoMapTool/images/pin19.png', globals()),
    'pin20.png':ImageFile('GeoMapTool/images/pin20.png', globals()),

    'pin_22_1.png':ImageFile('GeoMapTool/images/pin_22_1.png', globals()),
    'pin_22_2.png':ImageFile('GeoMapTool/images/pin_22_2.png', globals()),
    'pin_22_3.png':ImageFile('GeoMapTool/images/pin_22_3.png', globals()),
    'pin_22_4.png':ImageFile('GeoMapTool/images/pin_22_4.png', globals()),
    'pin_22_5.png':ImageFile('GeoMapTool/images/pin_22_5.png', globals()),
    'pin_22_6.png':ImageFile('GeoMapTool/images/pin_22_6.png', globals()),
    'pin_22_7.png':ImageFile('GeoMapTool/images/pin_22_7.png', globals()),
    'pin_22_8.png':ImageFile('GeoMapTool/images/pin_22_8.png', globals()),
    'pin_22_9.png':ImageFile('GeoMapTool/images/pin_22_9.png', globals()),
    'pin_22_10.png':ImageFile('GeoMapTool/images/pin_22_10.png', globals()),
    'pin_22_11.png':ImageFile('GeoMapTool/images/pin_22_11.png', globals()),
    'pin_22_12.png':ImageFile('GeoMapTool/images/pin_22_12.png', globals()),
    'pin_22_13.png':ImageFile('GeoMapTool/images/pin_22_13.png', globals()),
    'pin_22_14.png':ImageFile('GeoMapTool/images/pin_22_14.png', globals()),
    }
    misc_.update(gmisc_)
