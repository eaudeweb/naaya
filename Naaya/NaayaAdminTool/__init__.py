# Zope imports
from zLOG import LOG, INFO
from OFS.Folder import manage_addFolder

# Product imports
from CronTool import CronTool, manage_addCronTool, PERMISSION_ADD_CRON_TOOL, CRON_TOOL_ID

def initialize(context):
    """ """
    context.registerClass(
            CronTool,
            permission=PERMISSION_ADD_CRON_TOOL,
            constructors=CronTool._constructors
    )

    app = context._ProductContext__app
    if not app._getOb('naaya_admin_tool', None):
        manage_addFolder(app, 'naaya_admin_tool')
        LOG('NaayaAdmin', INFO, 'naaya_admin folder created')

    folder = app._getOb('naaya_admin_tool')
    if not folder._getOb(CRON_TOOL_ID, None):
        manage_addCronTool(folder)
        LOG('NaayaAdmin', INFO, 'CronTool created')
