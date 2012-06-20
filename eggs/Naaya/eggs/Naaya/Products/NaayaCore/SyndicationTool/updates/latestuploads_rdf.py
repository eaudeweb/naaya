"""
Update scripts related to latestuploads_rdf portal syndication script.

"""
import os

from Products.Naaya.managers.skel_parser import skel_parser
from Products.Naaya import NySite

from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater import utils

class RebuildLatestUploadsRdf(UpdateScript):
    title = 'Rebuild latestuploads_rdf from skel'
    authors = ['Mihnea Simian']
    creation_date = 'Jun 20, 2012'

    def _update(self, portal):
        portal_path = utils.get_portal_path(self, NySite)
        py_path = os.path.join(portal_path, 'skel', 'syndication',
                               'latestuploads_rdf.py')
        f = open(py_path, 'r')
        py_contents = f.read()
        f.close()
        syndication = portal.getSyndicationTool()
        zodb_script = syndication.latestuploads_rdf
        if py_contents.strip() == zodb_script._body.strip():
            self.log.info('latestuploads_rdf Python Script same as in skel.')
        else:
            zodb_script.ZPythonScript_edit('', py_contents)
            self.log.info('latestuploads_rdf Python Script updated.')

        return True
