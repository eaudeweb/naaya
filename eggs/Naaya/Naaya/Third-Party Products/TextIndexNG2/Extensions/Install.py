###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################


from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.TextIndexNG2 import textindexng_globals


configlets = \
( { 'id'         : 'TextIndexNG2'
  , 'name'       : 'TextIndexNG2 maintenance'
  , 'action'     : 'string:txng_maintenance'
  , 'category'   : 'Plone'
  , 'appId'      : 'TextIndexNG2'
  , 'permission' : ManagePortal
  , 'imageUrl'   : 'index.gif'
  }
,
)

def install(self):                                       
    out = StringIO()

    skins_tool = getToolByName(self, 'portal_skins')

    # Setup the skins
    if 'textindexng' not in skins_tool.objectIds():
        addDirectoryViews(skins_tool, 'skins',  textindexng_globals)
        out.write("Added textindexng skin directory view to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # 'textindexng' into the configurations.  Preferably, this should be
    # right before where 'content' is placed.  Otherwise, we append
    # it to the end.
    skins = skins_tool.getSkinSelections()

    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = [p.strip() for p in  path.split(',')]

        if 'textindexng' not in path:
            try: path.insert(0, 'textindexng')
            except ValueError:
                path.append('textindexng')
                
            path = ', '.join(path)
            # addSkinSelection will replace exissting skins as well.
            skins_tool.addSkinSelection(skin, path)
            out.write("Added 'textindexng' to %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'textindexng' is already set up\n" % (
                skin))


    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            print >>out, 'Adding configlet %s\n' % conf['id']
            configTool.registerConfiglet(**conf)

    print >> out, "Successfully installed"  
    return out.getvalue()


def uninstall(self):                                       
    out = StringIO()

    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            print >>out, 'Removing configlet %s\n' % conf['id']
            configTool.unregisterConfiglet(conf['id'])

    skins_tool = getToolByName(self, 'portal_skins')

    # Now we need to go through the skin configurations and insert
    # 'textindexng' into the configurations.  Preferably, this should be
    # right before where 'content' is placed.  Otherwise, we append
    # it to the end.
    skins = skins_tool.getSkinSelections()

    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = [p.strip() for p in  path.split(',')]

        if 'textindexng' in path:
            path.remove('textindexng')
                
            path = ', '.join(path)
            # addSkinSelection will replace exissting skins as well.
            skins_tool.addSkinSelection(skin, path)
            out.write("Removed 'textindexng' from %s skin\n" % skin)
        else:
            out.write("Skipping %s skin, 'textindexng' is removed set up\n" % (
                skin))

    print >> out, "Successfully uninstalled" 
    return out.getvalue()
