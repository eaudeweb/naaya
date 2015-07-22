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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
from CatalogTool import CatalogTool
from EmailTool import EmailTool
from TranslationsTool import TranslationsTool
from SyndicationTool import SyndicationTool
from AuthenticationTool import AuthenticationTool
from PropertiesTool import PropertiesTool
from DynamicPropertiesTool import DynamicPropertiesTool
from PortletsTool import PortletsTool
from FormsTool import FormsTool
from LayoutTool import LayoutTool
from NotificationTool import NotificationTool
from ProfilesTool import ProfilesTool
from EditorTool import EditorTool
from ControlsTool import NyControlSettings

try:
    from GeoMapTool import GeoMapTool
    geo_installed = True
except ImportError:
    geo_installed = False

def initialize(context):
    """ """
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
        TranslationsTool.TranslationsTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                TranslationsTool.manage_addTranslationsTool,
                ),
        icon = 'TranslationsTool/www/TranslationsTool.gif'
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
        ProfilesTool.ProfilesTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                ProfilesTool.manage_addProfilesTool,
                ),
        icon = 'ProfilesTool/www/ProfilesTool.gif'
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
        NyControlSettings.NyControlSettings,
        permission = 'Add NyControl',
        constructors = (
                NyControlSettings.manage_addNyControlSettings,
                ),
        icon = 'ControlsTool/www/ControlsTool.gif'
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
    'ControlsTool.gif':ImageFile('ControlsTool/www/ControlsTool.gif', globals()),
    'EmailTemplate.gif':ImageFile('EmailTool/www/EmailTemplate.gif', globals()),
    'TranslationsTool.gif':ImageFile('TranslationsTool/www/TranslationsTool.gif', globals()),
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
    'TemplateCustomized.gif':ImageFile('LayoutTool/www/TemplateCustomized.gif', globals()),
    'Scheme.gif':ImageFile('LayoutTool/www/Scheme.gif', globals()),
    'Style.gif':ImageFile('LayoutTool/www/Style.gif', globals()),
    'NotificationTool.gif':ImageFile('NotificationTool/www/NotificationTool.gif', globals()),
    'ProfilesTool.gif':ImageFile('ProfilesTool/www/ProfilesTool.gif', globals()),
    'Profile.gif':ImageFile('ProfilesTool/www/Profile.gif', globals()),
    'ProfileSheet.gif':ImageFile('ProfilesTool/www/ProfileSheet.gif', globals()),
    'xml.png':ImageFile('SyndicationTool/www/xml.png', globals()),
}
if geo_installed:
    gmisc_ = {
    'GeoMapTool.gif':ImageFile('GeoMapTool/www/GeoMapTool.gif', globals()),
    'shadow.png':ImageFile('GeoMapTool/www/shadow.png', globals()),
    'yahoomaps.js':ImageFile('GeoMapTool/www/yahoomaps.js', globals()),
    'geomaptool.js':ImageFile('GeoMapTool/www/geomaptool.js', globals()),
    'remote.js':ImageFile('GeoMapTool/www/remote.js', globals()),
    'template.csv':ImageFile('GeoMapTool/www/template.csv', globals()),
    'googlemaps.js':ImageFile('GeoMapTool/www/googlemaps.js', globals()),
    'xmlhttp.js':ImageFile('GeoMapTool/www/xmlhttp.js', globals()),
    }
    misc_.update(gmisc_)