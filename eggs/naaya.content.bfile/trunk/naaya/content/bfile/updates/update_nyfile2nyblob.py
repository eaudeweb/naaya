""" Naaya updater script """
__author__ = """Alin Voinea"""

from Products.Naaya.adapters import FolderMetaTypes
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from StringIO import StringIO
from naaya.content.bfile import bfile_item
from naaya.content.bfile.NyBlobFile import make_blobfile
from persistent.list import PersistentList
from zope.annotation import IAnnotations
from datetime import datetime
import logging


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
        extfile = self.data.pop('_ext_file', None)
        versions = self.data.pop('versions', [])
        if versions:
            versions = versions.objectValues()

        for version in versions:
            if version.is_broken():
                self.logger.warning("\t BROKEN EXTFILE: %s",
                                    self.context.absolute_url())
                continue

            sfile = StringIO(version.data)
            self.logger.debug('\t VERSION FILENAME: %s',
                              '/'.join(version.filename))
            sfile.filename = version.filename[-1]
            sfile.headers = {'content-type': version.content_type}
            yield sfile

        if extfile is not None:
            if not extfile.is_broken():
                sfile = StringIO(extfile.data)
                self.logger.debug('\t FILENAME: %s', '/'.join(extfile.filename))
                sfile.filename = extfile.filename[-1]
                sfile.headers = {'content-type': extfile.content_type}
                yield sfile
            else:
                self.logger.warning("\t BROKEN EXTFILE: %s",
                                    self.context.absolute_url())
        else:
            self.logger.warning("\t Already migrate?: %s",
                                self.context.absolute_url())

    @property
    def local_properties(self):
        """ Localized properties
        """
        return self.data.pop('_local_properties')

    @property
    def local_properties_metadata(self):
        """ Localized properties metadata
        """
        return self.data.pop('_local_properties_metadata')

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
            value = self.data.pop(name, None)
            if not value:
                continue
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
        if getattr(data, 'logger', None):
            self.logger = data.logger
        self.versions = data.versions
        self.properties = data.properties
        self.local_properties = data.local_properties
        self.local_properties_metadata = data.local_properties_metadata
        self.annotations = data.annotations
        self.finish = data.data

    def versions(self, value):
        """ Import versions
        """
        for version in value:
            bf = make_blobfile(version,
                               removed=False,
                               timestamp=datetime.utcnow(),
                               contributor='')

            vstorage = getattr(self.context, '_versions', None)
            if vstorage is None:
                self.context._versions = PersistentList()
            self.context._versions.append(bf)

            fname = bf.get_filename()
            with open(fname) as f:
                version.seek(0)
                if not len(f.read()) == len(version.read()):
                    raise ValueError("Different size of files")

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

    def local_properties_metadata(self, value):
        """ Import localized properties metadata
        """
        setattr(self.context, '_local_properties_metadata', value)
    local_properties_metadata = property(None, local_properties_metadata)

    def annotations(self, value):
        """ Import annotations
        """
        anno = IAnnotations(self.context)
        for key, val in value.items():
            anno[key] = val
    annotations = property(None, annotations)

    def finish(self, value):
        """ Setup non-schema properties
        """
        # XXX These should stay in annotations
        self.context.approved = value.pop('approved', False)
        self.context.approved_by = value.pop('approved_by', u"")
        self.context.submitted = value.pop('submitted', 1)
        self.context.discussion = value.pop('discussion', 0)
        self.context.recatalogNyObject(self.context)

        # XXX Comments
        comments = value.pop('_NyComments__comments_collection', {})
        if comments:
            setattr(self.context, '_NyComments__comments_collection', comments)

        # XXX Local roles
        localroles = value.pop('__ac_local_roles__', {})
        if localroles:
            setattr(self.context, '__ac_local_roles__', localroles)

        # XXX Dynamic properties
        properties = value.pop('_NyProperties__dynamic_properties', {})
        if properties:
            self.logger.warn('\t DEPRECATED: '
                             'Dynamic properties are deprecated. '
                             'Please update portal_schemas for NyBFile '
                             'with the following widgets: %s',
                             properties.keys())

        # XXX Validation
        validation_by = value.pop('validation_by', '')
        if validation_by:
            self.context.validation_by = validation_by
        validation_date = value.pop('validation_date', None)
        if validation_date:
            self.context.validation_date = validation_date
        validation_comment = value.pop('validation_comment', '')
        if validation_comment:
            self.context.validation_comment = validation_comment
        validation_status = value.pop('validation_status', 0)
        if validation_status:
            self.context.validation_status = validation_status

        # XXX Permissions
        permissions = value.pop('_Naaya___Edit_content_Permission', [])
        context_permissions = getattr(self.context,
                                      '_Naaya___Edit_content_Permission', [])
        if permissions != context_permissions:
            setattr(self.context, '_Naaya___Edit_content_Permission',
                    permissions)

        # Languages
        languages = value.pop('_languages', ())
        context_languages = getattr(self.context, '_languages', ())
        if languages != context_languages:
            setattr(self.context, '_languages', languages)

        # XXX Deprecated attributes
        checkout = value.pop('checkout', 0)
        if checkout:
            self.logger.debug('\t DEPRECATED %30s: \t %r', 'checkout',
                              checkout)
        checkout_user = value.pop('checkout_user', '')
        if checkout_user:
            self.logger.debug('\t DEPRECATED %30s \t %r', 'checkout_user',
                              checkout_user)
        version = value.pop('version', None)
        if version:
            get_data = getattr(version, 'get_data', None)
            get_data = get_data and get_data(as_string=False)
            filename = getattr(get_data, 'filename', [])
            self.logger.debug('\t DEPRECATED %30s \t %r', 'version', filename)

    finish = property(None, finish)

#
# Update script


class UpdateNyFile2NyBlobFile(UpdateScript):
    """ Update example script  """
    title = 'Update NyFiles to NyBlobFiles'
    creation_date = 'Jul 16, 2010'
    authors = ['Alin Voinea']
    priority = PRIORITY['HIGH']
    description = ('Upgrade diskstorage from ExtFile to Blob. '
                   'See WARNINGs in update log for required manual steps')

    def exchange(self, value):
        """ Exchange an old Naaya File for a new and fresh Naaya Blob File
        """
        parent = value.getParentNode()

        name = value.__name__
        contributor = value.contributor

        before = value.__dict__.copy()

        bname = before.get('id', '')
        if bname != name:
            before['id'] = name

        before['meta_type'] = value.meta_type
        export = Export(parent, before)
        export.logger = self.log
        doc = bfile_item.NyBFile(name, contributor)
        parent.gl_add_languages(doc)

        parent._delObject(name, suppress_events=True)
        name = parent._setObject(name, doc,
                                 set_owner=False, suppress_events=True)
        doc = parent._getOb(name)
        doc.after_setObject()
        Import(doc, export)
        try:
            value._ext_file._delete('/'.join(value._ext_file.filename))
            for ob in value.versions.objectValues():
                ob._delete('/'.join(ob.filename))
        except AttributeError:
            # The script should not fail in case some old file objects
            # dont have the versions folder
            pass

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

    def update_control_panel(self, portal):
        # Uninstall Naaya File
        if portal.is_pluggable_item_installed('Naaya File'):
            try:
                portal.manage_uninstall_pluggableitem('Naaya File')
            except Exception, err:
                self.log.warn('You need to manually uninstall Naaya File '
                              'in Control Panel')
                self.log.error(err)
            else:
                self.log.debug('Uninstalled Naaya File in Control Panel')

        # Install Naaya Blob File
        if not portal.is_pluggable_item_installed('Naaya Blob File'):
            try:
                portal.manage_install_pluggableitem('Naaya Blob File')
            except Exception, err:
                self.log.warn('You need to manually install Naaya Blob File '
                              'in Control Panel')
                self.log.error(err)
            else:
                self.log.debug('Installed Naaya Blob File in Control Panel')

    def update_subobjects(self, portal):
        # Subobjects
        meta_types = portal.adt_meta_types[:]
        if 'Naaya File' in meta_types:
            meta_types.remove('Naaya File')
            meta_types.append('Naaya Blob File')
            self.log.debug('Updating portal %s subobjects = %s',
                           portal.absolute_url(1), meta_types)
            portal.portal_properties.manageSubobjects(subobjects=meta_types)

        brains = portal.portal_catalog(meta_type='Naaya Folder')
        for brain in brains:
            doc = brain.getObject()
            if not doc:
                continue

            folder_meta_types = FolderMetaTypes(doc)
            meta_types = folder_meta_types.get_values()
            if 'Naaya File' in meta_types:
                meta_types.remove('Naaya File')
                meta_types.append('Naaya Blob File')
                self.log.debug('Updating folder %s subobjects = %s',
                               doc.absolute_url(1), meta_types)
                doc.manageSubobjects(subobjects=meta_types)

    def _update(self, portal):
        """ Run updater
        """
        ftool = portal.portal_forms
        templates = set(['file_add', 'file_edit', 'file_index'])
        customized = templates.intersection(ftool.objectIds())
        if customized:
            self.log.warn('Check customized templates in %s/portal_forms: %s',
                          portal.absolute_url(1), ', '.join(customized))

        ctool = portal.portal_catalog
        brains = ctool(meta_type='Naaya File')
        brains = set(brains)

        self.log.debug('Updating %s files in %s',
                       len(brains), portal.absolute_url(1))

        for brain in brains:
            doc = brain.getObject()
            self.log.debug('Updating file: %s' % doc.absolute_url(1))
            self.exchange(doc)

        self.update_control_panel(portal)
        self.update_subobjects(portal)
        return True
