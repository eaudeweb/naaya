#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path

class UpdateCountContentType(UpdateScript):
    """ Update example script  """
    title = 'Count content type objects'
    creation_date = 'Oct 6, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'This just counts the number of objects of a particular class (default is NySite)'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        count_map = {}
        object_map = {}
        def log_subobjects(parent):
            for ob_id, ob in parent.objectItems():
                class_name = ob.__class__.__name__
                count_map.setdefault(class_name, 0)
                count_map[class_name] += 1
                object_map.setdefault(class_name, [])
                if count_map[class_name] < 5 and hasattr(ob, 'absolute_url'):
                    object_map[class_name].append(ob.absolute_url())

                if hasattr(ob, 'objectItems'):
                    log_subobjects(ob)
        log_subobjects(portal)

        self.log.debug(physical_path(portal))

        for class_name, count in sorted(count_map.items()):
            self.log.debug("%s %d objects: %r" % (class_name, count, object_map[class_name]))

        return True

    update_template = PageTemplateFile('zpt/count_contenttype', globals())
    standard_update_template = PageTemplateFile('zpt/update_template', globals())
