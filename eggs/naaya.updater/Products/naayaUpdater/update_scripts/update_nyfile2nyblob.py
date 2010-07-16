""" Naaya updater script """
__author__ = """Alin Voinea"""

#Python imports
import logging
from StringIO import StringIO

#Zope imports
from DateTime import DateTime
from zope.annotation import IAnnotations

#Naaya imports
from naaya.content.bfile import bfile_item
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
#
# Export / Import
#
class Export(object):
    """ Export
    """

    logger = logging.getLogger('naaya.updater.update_nyfile2nyblob.export')

    def __init__(self, context, data):
        """ @param context: NyFile parent
            @param data: NyFile.__dict__
        """
        self.context = context
        self.data = data

    @property
    def versions(self):
        """ NyFile versions
        """
        extfile = self.data.pop('_ext_file')
        versions = self.data.pop('versions', [])
        if versions:
            versions = versions.objectValues()

        for version in versions:
            if version.is_broken():
                continue

            sfile = StringIO(version.data)
            sfile.filename = version.filename[-1]
            sfile.headers = {'content-type': version.content_type}
            yield sfile

        if not extfile.is_broken():
            sfile = StringIO(extfile.data)
            sfile.filename = extfile.filename[-1]
            sfile.headers = {'content-type': extfile.content_type}
            yield sfile

    @property
    def local_properties(self):
        """ Localized properties
        """
        return self.data.pop('_local_properties')

    @property
    def properties(self):
        """ Not localized properties
        """
        schema = self.context.portal_schemas.getSchemaForMetatype(
            self.data.pop('meta_type')
        )
        widgets = schema.listWidgets()
        for widget in widgets:
            if widget.localized:
                continue
            name = widget.prop_name()
            value = self.data.pop(name)
            yield name, value

    @property
    def annotations(self):
        """ Annotations
        """
        return self.data.pop('__annotations__', {})

class Import(object):
    """ Importer
    """

    logger = logging.getLogger('naaya.updater.update_nyfile2nyblob.import')

    def __init__(self, context, data):
        """
        @param context: NyBFile instance
        @param data: Export instance
        """
        self.context = context
        self.versions = data.versions
        self.properties = data.properties
        self.local_properties = data.local_properties
        self.annotations = data.annotations
        self.finish = data.data

    def versions(self, value):
        """ Import versions
        """
        for version in value:
            self.context._save_file(version)
    versions = property(None, versions)

    def properties(self, value):
        """ Import properties
        """
        for name, val in value:
            setattr(self.context, name, val)
    properties = property(None, properties)

    def local_properties(self, value):
        """ Import localized properties
        """
        setattr(self.context, '_local_properties', value)
    local_properties = property(None, local_properties)

    def annotations(self, value):
        """ Import annotations
        """
        anno = IAnnotations(self.context)
        for key, val in value.items():
            anno[key] = val
    annotations = property(None, annotations)

    def finish(self, value):
        """ Setup other properties
        """
        # XXX These should stay in annotations
        self.context.approved = value.pop('approved')
        self.context.approved_by = value.pop('approved_by')
        self.context.submitted = value.pop('submitted')
        self.context.discussion = value.pop('discussion', 0)
        self.context.recatalogNyObject(self.context)
    finish = property(None, finish)

#
# Update script
#
class UpdateNyFile2NyBlobFile(UpdateScript):
    """ Update example script  """
    id = 'update_nyfile_2_nyblobfile'
    title = 'Update NyFiles to NyBlobFiles'
    creation_date = DateTime('Jul 16, 2010')
    authors = ['Alin Voinea']
    priority = PRIORITY['HIGH']
    description = 'Upgrade diskstorage from ExtFile to Blob.'

    def exchange(self, value):
        """ Exchange an old Naaya File for a new and fresh Naaya Blob File
        """
        parent = value.getParentNode()

        name = value.__name__
        contributor = value.contributor

        before = value.__dict__
        before['meta_type'] = value.meta_type
        export = Export(parent, before)
        doc = bfile_item.NyBFile(name, contributor)
        parent.gl_add_languages(doc)

        parent._delObject(name, suppress_events=True)
        name = parent._setObject(name, doc,
                                 set_owner=False, suppress_events=True)
        doc = parent._getOb(name)
        doc.after_setObject()
        Import(doc, export)

        self.check_integrity(export.data, doc.__dict__)

    def check_integrity(self, before, after):
        """ Check for missing or invalid properties
        """
        for key, value in before.items():
            if key == '_v__object_deleted__':
                continue

            if not value:
                continue

            if key not in after.keys():
                self.log.debug('\t DEPRECATED %30s: \t %r', key, value)
                continue

            if before[key] != after[key]:
                self.log.debug('\t BROKEN %30s: \t %r => %r',
                               key, before[key], after[key])
                raise ValueError('%s: %r' % (key, value))

    def _update(self, portal):
        """ Run updater
        """
        ctool = portal.portal_catalog
        brains = ctool(meta_type='Naaya File')
        brains = set(brains)

        self.log.debug('Updating %s files in %s',
                       len(brains), portal.absolute_url(1))

        for brain in brains:
            doc = brain.getObject()
            self.log.debug('Updating file: %s' % doc.absolute_url(1))
            self.exchange(doc)
