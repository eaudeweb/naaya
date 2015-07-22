###
# Epoz-Installer-Script for CMF/Plone
# Taken and adapted from CMFVisualEditor
###

from Products.Epoz import cmfepoz_globals
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

_globals = globals()

def install_plone(self, out):
    """ add Epoz to 'my preferences' """
    portal_props=getToolByName(self,'portal_properties')
    site_props=getattr(portal_props,'site_properties', None)
    attrname='available_editors'
    if site_props is not None:
        editors=list(site_props.getProperty(attrname))
        if 'Epoz' not in editors:
            editors.append('Epoz')
            site_props._updateProperty(attrname, editors)
            print >>out, "Added 'Epoz' to available editors in Plone."

def install_subskin(self, out, skin_name, globals=cmfepoz_globals):
    skinstool=getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'epoz', globals)

    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        try:
            if skin_name not in path:
                path.insert(path.index('custom') +1, skin_name)
        except ValueError:
            if skin_name not in path:
                path.append(skin_name)

        path = ','.join(path)
        skinstool.addSkinSelection(skinName, path)

def install(self):
    out = StringIO()
    print >>out, "Installing Epoz"
    install_subskin(self, out, 'epoz_core')
    install_subskin(self, out, 'epoz_i18n')
    install_subskin(self, out, 'epoz_images')
    install_subskin(self, out, 'epoz_plone')
    install_plone(self, out)

    print >>out, "Done."

    return out.getvalue()
