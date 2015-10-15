from AccessControl.Permission import Permission
from AccessControl.Permissions import view

from naaya.core.zope2util import permission_add_role, sha_hexdigest
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import get_standard_template
from naaya.i18n.LocalPropertyManager import LocalAttribute
from naaya.content.mediafile.converters.MediaConverter import get_resolution

class SkipApprovalPermission(UpdateScript):
    title = ('Set the "Naaya - Skip approval" permission '
             'based on the `submit_unapproved` setting')
    authors = ['Alex Morega']
    creation_date = 'Feb 21, 2011'

    def _update(self, portal):
        if not hasattr(portal.aq_base, 'submit_unapproved'):
            self.log.info("submit_unapproved flag already updated.")
            return True

        value = portal.submit_unapproved
        portal._set_submit_unapproved(value)
        self.log.info("submit_unapproved flag set to %r" % value)
        del portal.submit_unapproved
        return True

class HideSortOrderFromSchemas(UpdateScript):
    title = ('Hide the sortorder property from all schemas')
    authors = ['Valentin Dumitru']
    creation_date = 'Jul 19, 2011'

    def _update(self, portal):
        for schema in portal.portal_schemas.objectValues('Naaya Schema'):
            sortorder_property = getattr(schema, 'sortorder-property')
            sortorder_property.visible = False
            self.log.info("property hidden in schema %r" % schema.id)
        return True

class AddHelpTextOnNewsDescription(UpdateScript):
    title = ('Add a help text to the description property '
             'of News Items')
    authors = ['Valentin Dumitru']
    creation_date = 'Jul 19, 2011'

    def _update(self, portal):
        ny_news = getattr(portal.portal_schemas, 'NyNews', None)
        if ny_news:
            description = getattr(ny_news, 'description-property', None)
            if description and hasattr(description, 'help_text')\
                and not description.help_text:
                description.help_text = u'Keep this description short, about 50 words. Use the <strong>Details</strong> field below to add more information.'
                self.log.info("Help text updated")
        return True

class RestrictUnapproved(UpdateScript):
    """ """
    title = 'Restrict view for unapproved objects'
    creation_date = 'Oct 28, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['HIGH']
    description = "Don't inherit view permission for unapproved objects"

    def _update(self, portal):
        catalog = portal.getCatalogTool()
        for brain in catalog(approved=0):
            obj = brain.getObject()
            permission = Permission(view, (), obj)
            roles = permission.getRoles()
            if isinstance(roles, list):
                obj.dont_inherit_view_permission()
                self.log.debug('restricted view permission for %s',
                                obj.absolute_url())
        return True

class SetPhotoFolderGalleryPermission(UpdateScript):
    title = ('Set Naaya Photo related permissions to administrators')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 18, 2012'

    def _update(self, portal):
        permissions = ["Naaya - Add Naaya Photo Folder",
                        "Naaya - Add Naaya Photo Gallery"]
        for permission in permissions:
            p = Permission(permission, (), portal)
            if 'Administrator' not in p.getRoles():
                permission_add_role(portal, permission, 'Administrator')
                self.log.debug('Added %s permission', permission)

        return True

class RemoveNyContentProps(UpdateScript):
    title = ('Delete old properties of NyContent objects '
                'for already localized properties')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 18, 2012'

    def _update(self, portal):
        schema_tool = portal.getSchemaTool()
        objects_local_props = {}
        deleted_props = {}
        affected_meta_types = {}
        affected_objects = 0
        for meta_type, schema_ob in schema_tool.listSchemas().items():
            localized_props = []
            for widget in schema_ob.objectValues():
                if widget.localized:
                    localized_props.append(widget.id.rsplit('-property', 1)[0])
            objects_local_props[meta_type] = localized_props

        for ob in portal.getCatalogedObjectsA(
                meta_type=objects_local_props.keys()):
            for prop in objects_local_props[ob.meta_type]:
                if prop in ob.__dict__.keys():
                    value = getattr(ob, prop)
                    if isinstance(value, LocalAttribute):
                        continue
                    if (not ob._local_properties.has_key(prop) or
                            ob._local_properties[prop] == {}):
                        for lang in portal.gl_get_languages():
                            ob.set_localpropvalue(prop, lang, value)
                    delattr(ob, prop)
                    affected_objects += 1
                    deleted_props[prop] = True
                    affected_meta_types[ob.meta_type] = True
                    self.log.debug('Deleted property "%s" for %s' %
                            (prop, ob.absolute_url()))
        self.log.debug('Affected objects: %s' % affected_objects)
        if deleted_props.keys():
            self.log.debug('Deleted properties: %s' % deleted_props.keys())
        if affected_meta_types.keys():
            self.log.debug('Affected meta_types: %s' % affected_meta_types.keys())
        return True

class AddLastModificationProperty(UpdateScript):
    title = ('Add last_modification date-time to NyContent objects')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 20, 2012'

    def _update(self, portal):
        schema_tool = portal.getSchemaTool()
        meta_types = schema_tool.listSchemas().keys()
        for ob in portal.getCatalogedObjectsA(meta_type=meta_types):
            if not hasattr(ob, 'last_modification'):
                ob.last_modification = ob.bobobase_modification_time()
                self.log.debug('Added last modification "%s" for %s' %
                    (portal.utShowFullDateTime(ob.bobobase_modification_time()),
                        ob.absolute_url()))
        return True

class RemoveDuplicateImages(UpdateScript):
    title = ('Remove duplicate files from /images folder')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 20, 2012'

    def _update(self, portal):
        images = portal.images.objectValues('Image')
        dup_images = {}
        for image in images:
            if not hasattr(image, 'sha1_hash'):
                image.sha1_hash = sha_hexdigest(image)
                self.log.debug('Image hash added, %s: %s' % (
                    image.getId(), image.sha1_hash))
            if image.getId() != image.title:
                orig_image = getattr(portal.images, image.title, None)
                if orig_image:
                    if not hasattr(orig_image, 'sha1_hash'):
                        orig_image.sha1_hash = sha_hexdigest(orig_image)
                    if image.sha1_hash == orig_image.sha1_hash:
                        dup_images[image.getId()] = orig_image.getId()

        schema_tool = portal.getSchemaTool()
        obj_textarea_props = {}
        for meta_type, schema_ob in schema_tool.listSchemas().items():
            textarea_widgets = schema_ob.objectValues('Naaya Schema Text Area Widget')
            textarea_props = [widget.id.rsplit('-property', 1)[0]
                    for widget in textarea_widgets]
            obj_textarea_props[meta_type] = textarea_props
        for ob in portal.getCatalogedObjectsA(
                meta_type=obj_textarea_props.keys()):
            for dup_id in dup_images.keys():
                for prop_id in obj_textarea_props[ob.meta_type]:
                    for lang in portal.gl_get_languages():
                        curr_prop = ob.getLocalAttribute(
                                prop_id, lang)
                        if dup_id in curr_prop:
                            ob.set_localpropvalue(prop_id, lang,
                                    curr_prop.replace(
                                        dup_id, dup_images[dup_id]))
                            self.log.debug('Object %s, image id changed from %s to %s'
                                    % (ob.absolute_url(), dup_id, dup_images[dup_id]))
        portal.images.manage_delObjects(dup_images.keys())
        for image_id in dup_images.keys():
            self.log.debug('Deleted duplicated image: %s' % image_id)
        return True

class AddMissingCSSToStandardTemplate(UpdateScript):
    title = ('Add missing css files to standard template')
    authors = ['Valentin Dumitru']
    creation_date = 'Feb 13, 2012'

    def _update(self, portal):
        self.log.debug('Updating standard_template')
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        todo = {
            'jquery-ui.css': '<metal:block define-macro="standard-head-links">\n            <link rel="stylesheet" type="text/css" media="screen" tal:attributes="href string:${site_url}/www/js/css/jquery-ui.css" />',
            'additional_style_css': '<metal:block define-macro="standard-head-links">\n            <link rel="stylesheet" type="text/css" media="screen" tal:attributes="href string:${here/absolute_url}/additional_style_css" />',
        }

        entry_point = '<metal:block define-macro="standard-head-links">'

        changed = False
        for k, v in todo.items():
            if k in tal:
                self.log.debug('%s in standard_template' % k)
            else:
                self.log.debug('%s not in standard_template' % k)
                tal = tal.replace(entry_point, v)
                self.log.debug('added %s link', k)
                changed = True
        if changed:
            self.log.debug('standard_template changed')
            standard_template.write(tal)
        else:
            self.log.debug('standard_template not changed')
        return True

class AddAspectRatioToMediaFiles(UpdateScript):
    title = ('Add aspect_ratio property to the ExtFile movies in Media File')
    authors = ['Valentin Dumitru']
    creation_date = 'Feb 28, 2012'

    def _update(self, portal):
        for ob in portal.getCatalogedObjects(meta_type="Naaya Media File"):
            media = ob.getSingleMediaObject()
            if not media or hasattr(media.aq_base, 'aspect_ratio') or ob.is_audio():
                continue
            file_path = media.get_filename()
            try:
                if file_path:
                    resolution = get_resolution(file_path)
                    aspect_ratio = resolution[0]/resolution[1]
                    media.aspect_ratio = aspect_ratio
                    self.log.debug('Aspect ratio %s saved for %s' %
                        (aspect_ratio, ob.absolute_url()))
                else:
                    self.log.debug('Media file %s missing' % ob.absolute_url())
            except ValueError:
                self.log.error('Media file not found for %s' % ob.absolute_url())
        return True

class DeleteInvalidPointers(UpdateScript):
    title = ('Delete pointer objects pointing to inexisting objects')
    authors = ['Valentin Dumitru']
    creation_date = 'Mar 8, 2012'

    def _update(self, portal):
        catalog = portal.portal_catalog
        counter = 0
        for brain in list(catalog(meta_type="Naaya Pointer")):
            pointer_item = brain.getObject()
            pointer = pointer_item.pointer
            if pointer.startswith('/'):
                pointer = pointer[1:]
            obj = portal.unrestrictedTraverse(pointer.encode('utf-8'), None)
            if obj is None:
                self.log.debug('Pointer %s deleted' %
                    pointer_item.absolute_url())
                pointer_item.aq_parent.manage_delObjects(pointer_item.getId())
                counter += 1
        self.log.debug('A total of %s pointer items were deleted' % counter)
        return True

class CreateUserPermission(UpdateScript):
    title = ('Set the "Naaya - Create user" permission '
             'for Administrator, Anonymous')
    authors = ['Alex Morega']
    creation_date = 'Mar 27, 2012'

    def _update(self, portal):
        permission = "Naaya - Create user"
        p = Permission(permission, (), portal)
        if 'Administrator' not in p.getRoles():
            permission_add_role(portal, permission, 'Administrator')
            permission_add_role(portal, permission, 'Anonymous')
            self.log.debug('Added %s permission', permission)

        return True
