import os
from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.PortletsTool.Portlet import addPortlet
from naaya.core.utils import path_in_site

class UpdateMainSections(UpdateScript):
    """ Update portlet_maincategories  """
    title = 'Update main sections portlet'
    creation_date = 'Sep 6, 2010'
    authors = ['Alexandru Plugaru']
    description = 'Adds mainsections_settings dict to NySite for configuration\
                  of the navigation. Also a little cleanup of the current\
                    maintopics values '

    def _update(self, portal):
        portal.maintopics_settings = {
            'expanded': True,
            'persistent': True,
            'expand_levels': 1,
            'max_levels': 1
        }
        maintopics = []
        old_maintopics = portal.utSortObjsListByAttr(filter(lambda x: x is not None, map(lambda f, x: f(x, None), (portal.utGetObject,)*len(portal.maintopics), portal.maintopics)), 'sortorder', 0)
        for path_ob in old_maintopics:
            maintopics.append(path_in_site(path_ob))
        portal.maintopics = maintopics
        portal._p_changed = True
        return True
