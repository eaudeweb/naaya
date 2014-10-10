""" Naaya updater script """

# Python imports
import logging
from StringIO import StringIO

# Zope imports
from zope.annotation import IAnnotations

# Naaya imports
from naaya.content.bfile import bfile_item
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.Naaya.adapters import FolderMetaTypes
#
# Export / Import


class Export(object):
    """
    Naaya Extended File data extractor

    Required arguments:
      context -- parent of NyExFile instance
      data -- NyExFile.__dict__

    """

    logger = logging.getLogger('nyexfile2nyblob.update')

    def __init__(self, context, data):
        self.context = context
        self.data = data

    @property
    def versions(self):
        """ Exports NyExFile versions
        """
        languages = self.data.get('_languages', ())
        if len(languages) > 1:
            self.logger.debug("\t Object %s has %r languages: %r",
                              self.data.get('id', 'ERROR'), len(languages),
                              languages)
        if not languages:
            languages = [x['id'] for x in self.data['_objects']]

        for language in languages:
            nyfile = self.data.pop(language, None)
            if not nyfile:
                continue

            extfile = getattr(nyfile, '_ext_file', None)
            if not extfile:
                continue

            versions = getattr(nyfile, 'versions', [])
            if versions:
                versions = versions.objectValues()

            for version in versions:
                filename = '/'.join(version.filename)
                if not filename:
                    continue

                if version.is_broken():
                    self.logger.warn('\t BROKEN VERSION: %s (%s)',
                                     version.getId(), filename)
                    continue

                sfile = StringIO(version.data)
                self.logger.debug('\t VERSION FILENAME: %s', filename)
                sfile.filename = version.filename[-1]
                sfile.headers = {'content-type': version.content_type}
                sfile.releasedate = self.data['releasedate']
                yield sfile

            filename = '/'.join(extfile.filename)
            if not filename:
                continue

            if extfile.is_broken():
                self.logger.warn('\t BROKEN EXTFILE: %s (%s)', language,
                                 filename)
                continue

            sfile = StringIO(extfile.data)
            self.logger.debug('\t FILENAME: %s', filename)
            sfile.filename = extfile.filename[-1]
            sfile.headers = {'content-type': extfile.content_type}
            sfile.releasedate = self.data['releasedate']
            yield sfile

    @property
    def local_properties(self):
        """ Exports localized properties
        """
        return self.data.pop('_local_properties')

    @property
    def local_properties_metadata(self):
        """ Exports localized properties
        """
        return self.data.pop('_local_properties_metadata')

    @property
    def properties(self):
        """ Exports not localized properties
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
        """ Exports annotations
        """
        return self.data.pop('__annotations__', {})


class Import(object):
    """
    Imports Naaya Extended File as a Naaya Blob File

    Required arguments:
    context -- Naaya Blob File instance
    data -- Export instance

    """

    logger = logging.getLogger('nyexfile2nyblob.update')

    def __init__(self, context, data):
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

        Required arguments:
        value -- Iterator over NyExFile versions

        """
        for version in value:
            self.context._save_file(version,
                                    contributor='')
            self.context._versions[-1].timestamp = \
                version.releasedate.asdatetime()
    versions = property(None, versions)

    def properties(self, value):
        """ Import properties

        Required arguments:
        value -- (key, value) iterator over NyExFile not localized properties

        """
        for name, val in value:
            setattr(self.context, name, val)
    properties = property(None, properties)

    def local_properties(self, value):
        """ Import localized properties

        Required arguments:
        value -- _local_properties dict from NyExFile instance

        """
        setattr(self.context, '_local_properties', value)
    local_properties = property(None, local_properties)

    def local_properties_metadata(self, value):
        """ Import localized properties metadata

        Required arguments:
        value -- _local_properties_metadata dict from NyExFile instance

        """
        setattr(self.context, '_local_properties_metadata', value)
    local_properties_metadata = property(None, local_properties_metadata)

    def annotations(self, value):
        """ Import annotations

        Required arguments:
        value --Annotations dict from NyExFile instance

        """
        anno = IAnnotations(self.context)
        for key, val in value.items():
            anno[key] = val
    annotations = property(None, annotations)

    def finish(self, value):
        """ Setup non-schema properties

        Required arguments:
        value -- NyExFile.__dict__

        """
        # XXX These should stay in annotations
        self.context.approved = value.pop('approved', 1)
        self.context.approved_by = value.pop('approved_by', None)
        self.context.submitted = value.pop('submitted', 0)
        self.context.discussion = value.pop('discussion', 0)

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

        # Default language
        default_language = value.pop('_default_language', '')
        if default_language:
            setattr(self.context, '_default_language', default_language)

        # Owner
        owner = value.pop('_owner', '')
        if owner:
            setattr(self.context, '_owner', owner)

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

        self.context.recatalogNyObject(self.context)

        # update modified properties
        last_modification = value.pop('last_modification', None)
        if last_modification:
            self.context.last_modification = last_modification
        for k in ['keywords', 'coverage']:
            if k in value:
                setattr(self.context, k, value.pop(k))

    finish = property(None, finish)
#
# Update script


class UpdateNyExFile2NyBlobFile(UpdateScript):
    """ Update example script  """
    title = 'Update Naaya Extended Files to Naaya Blob Files'
    creation_date = 'Aug 02, 2010'
    authors = ['Alin Voinea']
    priority = PRIORITY['HIGH']
    description = ('Upgrade diskstorage from ExtFile to Blob. '
                   'See WARNINGs in update log for required manual steps')

    def exchange(self, value):
        """ Exchange an old Naaya Extended File for a new and
        fresh Naaya Blob File

        Required arguments:
        value --Naaya Extended File instance

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
        for lang in value.getSite().gl_get_languages():
            extfile = value.get(lang)
            if extfile:
                extfile._ext_file._delete('/'.join(extfile._ext_file.filename))
                for ob in extfile._ext_file.versions.objectValues():
                    ob._delete('/'.join(ob.filename))

        self.check_integrity(export.data, doc.__dict__)

    def check_integrity(self, before, after):
        """ Check for missing or invalid properties

        Required arguments:
        before -- NyExFile.__dict__
        after -- NyBFile.__dict__
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
        """ Uninstall Naaya Extended File in Control Panel and install
        Naaya Blob File if not installed
        """
        # Uninstall Naaya Extended File
        if portal.is_pluggable_item_installed('Naaya Extended File'):
            try:
                portal.manage_uninstall_pluggableitem('Naaya Extended File')
            except Exception, err:
                self.log.warn('You need to manually uninstall '
                              'Naaya Extended File in Control Panel')
                self.log.error(err)
            else:
                self.log.debug(
                    'Uninstalled Naaya Extended File in Control Panel')

        # Install Naaya Blob File
        if not portal.is_pluggable_item_installed('Naaya Blob File'):
            try:
                portal.manage_install_pluggableitem('Naaya Blob File')
            except Exception, err:
                self.log.warn('You need to manually install '
                              'Naaya Blob File in Control Panel')
                self.log.error(err)
            else:
                self.log.debug('Installed Naaya Blob File in Control Panel')

    def update_subobjects(self, portal):
        """ Update allowed subobject in Naaya Folders if Naaya Extended File
        is present in this list

        Required arguments:
        portal -- Naaya Site instance

        """
        # Subobjects
        meta_types = portal.adt_meta_types[:]
        changed = False
        if 'Naaya Extended File' in meta_types:
            meta_types.remove('Naaya Extended File')
            changed = True
        if 'Naaya Blob File' not in meta_types:
            meta_types.append('Naaya Blob File')
            changed = True
        if changed:
            self.log.debug('Updating portal %s subobjects = %s',
                           portal.absolute_url(1), meta_types)
            portal.portal_properties.manageSubobjects(subobjects=meta_types)

        brains = portal.portal_catalog(meta_type='Naaya Folder')
        for brain in brains:
            doc = brain.getObject()
            if not doc:
                continue

            self.log.debug("Replacing object %s", doc.absolute_url())
            folder_meta_types = FolderMetaTypes(doc)
            meta_types = folder_meta_types.get_values()
            changed = False
            if 'Naaya Extended File' in meta_types:
                meta_types.remove('Naaya Extended File')
                changed = True
            if 'Naaya Blob File' not in meta_types:
                meta_types.append('Naaya Blob File')
                changed = True
            if changed:
                self.log.debug('Updating folder %s subobjects = %s',
                               doc.absolute_url(1), meta_types)
                folder_meta_types.set_values(meta_types)

    def _update(self, portal):
        """ Run updater

        Required arguments:
        portal -- Naaya Site instance

        """
        ftool = portal.portal_forms
        templates = set(['exfile_add', 'exfile_edit', 'exfile_index'])
        customized = templates.intersection(ftool.objectIds())
        if customized:
            self.log.warn('Check customized templates in %s/portal_forms: %s',
                          portal.absolute_url(1), ', '.join(customized))

        ctool = portal.portal_catalog
        brains = ctool(meta_type='Naaya Extended File')
        brains = set(brains)

        self.log.debug('Updating %s extended files in %s',
                       len(brains), portal.absolute_url(1))

        for brain in brains:
            doc = brain.getObject()
            self.log.info('Updating extended file: %s' % doc.absolute_url(1))
            self.exchange(doc)

        self.update_control_panel(portal)
        self.update_subobjects(portal)
        return True
