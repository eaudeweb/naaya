# Zope imports
from zLOG import LOG, INFO
from OFS.Folder import manage_addFolder

# Product imports
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.Naaya.NySite import NySite

from CronTool import CronTool, manage_addCronTool, PERMISSION_ADD_CRON_TOOL, CRON_TOOL_ID
from constants import CATALOG_ID


def findNySites(container):
    if isinstance(container, NySite): # TODO replace isinstance with meta_type
        yield container
    if not hasattr(container, 'objectValues'):
        return
    for ob in container.objectValues():
        for x in findNySites(ob):
            yield x


def configure_catalog(container):
    if container._getOb(CATALOG_ID, None) is None:
        manage_addZCatalog(container, CATALOG_ID, title='Naaya Admin Catalog')
        LOG('NaayaAdminTool', INFO, '%s created' % (CATALOG_ID,))
    catalog = container._getOb(CATALOG_ID)

    if 'meta_type' not in catalog.indexes():
        catalog.addIndex(name='meta_type', type='FieldIndex')
        LOG('NaayaAdminTool', INFO, 'cataloging all Naaya sites')
        for site in findNySites(container):
            catalog.catalog_object(site)
        LOG('NaayaAdminTool', INFO, 'finished cataloging all Naaya sites')


def configure_cron(container):
    if container._getOb(CRON_TOOL_ID, None) is None:
        manage_addCronTool(container)
        LOG('NaayaAdminTool', INFO, '%s created' % (CRON_TOOL_ID, ))


def initialize(context):
    """ """
    app = context._ProductContext__app

    context.registerClass(
            CronTool,
            permission=PERMISSION_ADD_CRON_TOOL,
            constructors=CronTool._constructors
    )

    if app._getOb('naaya_admin_tool', None) is None:
        manage_addFolder(app, 'naaya_admin_tool', title='Naaya Admin Tool')
        LOG('NaayaAdminTool', INFO, 'naaya_admin_tool folder created')
    naaya_admin_tool = app._getOb('naaya_admin_tool')

    configure_catalog(app)
    configure_cron(naaya_admin_tool)
