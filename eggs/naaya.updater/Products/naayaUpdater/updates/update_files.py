import os
from Globals import INSTANCE_HOME
from Products.naayaUpdater.updates import UpdateScript

class UpdateFiles(UpdateScript):
    """  """
    id = 'update_files'
    title='Check the existence of Naaya Files and Exfiles on disk'
    description="If the file exists ignore it else print the path<br /> CHECK \
    THE OUTPUT IN CONSOLE"

    def _update(self, portal):
        """ """
        naaya_files = portal.portal_catalog(meta_type="Naaya File")
        naaya_exfiles = portal.portal_catalog(meta_type="Naaya Extended File")

        for brain in naaya_files:
            file = brain.getObject()
            path = file._ext_file.get_filename()
            if not os.path.exists(path):
                print path

        for brain in naaya_exfiles:
            exfile = brain.getObject()
            for language, file in exfile.getFileItems():
                path = file._ext_file.get_filename()
                if not os.path.exists(path):
                    print path
        return True
