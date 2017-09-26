# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Valentin Dumitru, Eau de Web

# Python imports
from copy import deepcopy
import os
import sys
from urllib import unquote

# Zope imports
from Persistence import Persistent
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Acquisition import Implicit
from OFS.SimpleItem import Item
from zope.interface import implements
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

# Product imports
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from naaya.content.bfile.NyBlobFile import NyBlobFile
from Products.NaayaCore.managers.utils import utils, make_id
from Products.NaayaCore.EmailTool.EmailPageTemplate import \
    EmailPageTemplateFile
from Products.NaayaCore.LayoutTool.LayoutTool import AdditionalStyle


from interfaces import INyMunicipality
from permissions import PERMISSION_ADD_MUNICIPALITY

# module constants
METATYPE_OBJECT = 'Naaya Municipality'
LABEL_OBJECT = 'Municipality'
OBJECT_FORMS = ['municipality_add', 'municipality_edit', 'municipality_index']
OBJECT_CONSTRUCTORS = ['municipality_add_html', 'addNyMunicipality']
OBJECT_ADD_FORM = 'municipality_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Municipality type.'
PREFIX_OBJECT = 'municipality'

DEFAULT_SCHEMA = {
    'province': dict(sortorder=100, widget_type='Select', label='Province',
                     required=True, list_id='provinces'),
    'municipality': dict(sortorder=110, widget_type='String',
                         label='Municipality', required=True, localized=True),
    'contact_person': dict(sortorder=120, widget_type='String',
                           label='Contact person', required=True),
    'email': dict(sortorder=130, widget_type='String', label='Email address',
                  required=True),
    'phone': dict(sortorder=140, widget_type='String',
                  label='Telephone number'),
    'choice': dict(sortorder=150, widget_type='Select',
                   label='Our municipality:', required=True,
                   list_id='ambassador_choices'),
    'explain_why': dict(
        sortorder=200, widget_type='TextArea',
        label='Please explain why you chose this / these species:',
        localized=True, tinymce=True),
    'explain_how': dict(
        sortorder=210, widget_type='TextArea',
        label='Please explain how you chose this / these species:',
        localized=True, tinymce=True),
    'importance1': dict(sortorder=220, widget_type='TextArea',
                        label=('The selected ambassador species is / '
                               'are important to our municipality because:'),
                        localized=True, tinymce=True),
    'importance2': dict(sortorder=230, widget_type='TextArea',
                        label=('Our municipality is important for the '
                               'ambassador species because:'), localized=True,
                        tinymce=True),
    'usage': dict(sortorder=240, widget_type='TextArea',
                  label=('Please explain how you use the ambassador species '
                         'in your municipality:'), localized=True,
                  tinymce=True),
    'link1': dict(sortorder=250, widget_type='String',
                  label='Interesting links:'),
    'link2': dict(sortorder=260, widget_type='String',
                  label='Interesting links:'),
}

DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(visible=False, required=False)
DEFAULT_SCHEMA['description'].update(visible=False)
DEFAULT_SCHEMA['geo_location'].update(visible=False)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)


def setupContentType(site):
    from skel import PROVINCES, AMBASSADOR_CHOICES
    ptool = site.getPortletsTool()
    iprovinces = getattr(ptool, 'provinces', None)
    if not iprovinces:
        ptool.manage_addRefTree('provinces')
        for k, v in PROVINCES.items():
            ptool.provinces.manage_addRefTreeNode(k, v)
    ichoices = getattr(ptool, 'ambassador_choices', None)
    if not ichoices:
        ptool.manage_addRefTree('ambassador_choices')
        for k, v in AMBASSADOR_CHOICES.items():
            ptool.ambassador_choices.manage_addRefTreeNode(k, v)

# this dictionary is updated at the end of the module
config = {'product': 'NaayaContent',
          'module': 'municipality_item',
          'package_path': os.path.abspath(os.path.dirname(__file__)),
          'meta_type': METATYPE_OBJECT,
          'label': LABEL_OBJECT,
          'permission': PERMISSION_ADD_MUNICIPALITY,
          'forms': OBJECT_FORMS,
          'add_form': OBJECT_ADD_FORM,
          'description': DESCRIPTION_OBJECT,
          'default_schema': DEFAULT_SCHEMA,
          'schema_name': 'NyMunicipality',
          '_module': sys.modules[__name__],
          'icon': os.path.join(os.path.dirname(__file__), 'www',
                               'NyMunicipality.gif'),
          'on_install': setupContentType,
          'additional_style': AdditionalStyle('www/municipality.css',
                                              globals()),
          '_misc': {
              'NyMunicipality.gif': ImageFile('www/NyMunicipality.gif',
                                              globals()),
              'NyMunicipality_marked.gif': ImageFile(
                  'www/NyMunicipality_marked.gif', globals()),
              },
          }

email_templates = {
    'email_when_unapproved_to_maintainer': EmailPageTemplateFile(
        'templates/email_when_unapproved_to_maintainer.zpt', globals()),
}


def municipality_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent(
        {'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyMunicipality',
         'form_helper': form_helper}, 'municipality_add')


def _create_NyMunicipality_object(parent, id, title, contributor):
    id = make_id(parent, id=id, title=title, prefix='municipality')
    ob = NyMunicipality(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.species = []
    ob.after_setObject()
    return ob


def addNyMunicipality(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Municipality type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate',
                                                                ''))

    _title = '%s, %s' % (
        schema_raw_data.get('municipality', ''),
        self.get_node_title('provinces',
                            schema_raw_data.get('province', '')))
    schema_raw_data['title'] = _title
    recaptcha_response = schema_raw_data.get('g-recaptcha-response', '')

    # process parameters
    id = make_id(self, id=id, title=_title, prefix='municipality')
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyMunicipality_object(self, id, _title, contributor)

    ambassador_species = schema_raw_data.pop('ambassador_species', '')
    ambassador_species_description = schema_raw_data.pop(
        'ambassador_species_description', '')

    # picture processing
    upload_picture_url = schema_raw_data.pop('upload_picture_url', None)
    if upload_picture_url:
        temp_folder = self.getSite().temp_folder
        picture_id = upload_picture_url.split('/')[-1]
        ambassador_species_picture = getattr(temp_folder, picture_id)
    else:
        ambassador_species_picture = None
    x1 = schema_raw_data.pop('x1')
    y1 = schema_raw_data.pop('y1')
    x2 = schema_raw_data.pop('x2')
    y2 = schema_raw_data.pop('y2')
    crop_coordinates = (x1, y1, x2, y2)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                                            _override_releasedate=_releasedate)

    ob.process_species(
        None, None, ambassador_species, ambassador_species_description,
        ambassador_species_picture, crop_coordinates, form_errors)

    # check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(recaptcha_response, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            import transaction
            # because we already called _crete_NyZzz_object
            transaction.abort()
            schema_raw_data['ambassador_species'] = ambassador_species
            schema_raw_data['ambassador_species_description'] = \
                ambassador_species_description
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/municipality_add_html' %
                                      self.absolute_url())
            return

    # process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = (1,
                                 self.REQUEST.AUTHENTICATED_USER.getUserName())
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    # Overwrite any inconsistent values in the choice property
    if not ob.species and ob.choice == u'3':
        ob.choice = u'1'
        ob._p_changed = True
    if ob.species:
        ob.choice = u'3'
        ob._p_changed = True

    if ob.discussion:
        ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    # log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    # redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if (l_referer == 'municipality_manage_add' or
                l_referer.find('municipality_manage_add') != -1):
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'municipality_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)

    return ob.getId()


class AmbassadorSpecies(Persistent):
    def __init__(self, title, description='', picture=None):
        self.title = title
        self.description = description
        self.picture = picture

    def edit(self, title, description='', picture=None):
        self.title = title
        self.description = description
        self.picture = picture


class NyMunicipality(NyContentData, NyAttributes, NyItem, NyNonCheckControl,
                     NyValidation, NyContentType, utils):
    """ """
    implements(INyMunicipality)
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyMunicipality.gif'
    icon_marked = 'misc_/NaayaContent/NyMunicipality_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += ({'label': 'View',
                       'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        NyContentData.__dict__['__init__'](self)
        NyValidation.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'obfuscated_email')

    def obfuscated_email(self):
        ret = self.email
        if self.email:
            if isinstance(self.email, unicode):
                self.email = self.email.encode('UTF-8')
            ret = self.email.replace('@', ' at ')
        return ret

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')

    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if self.hasVersion():
            obj = self.version
            if self.checkout_user != \
                    self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop(
            'releasedate', ''), obj.releasedate)

        edit_species = schema_raw_data.pop('edit_species', None)
        delete_picture = schema_raw_data.pop('delete_picture', None)
        schema_raw_data['title'] = obj.title

        ambassador_species = schema_raw_data.get('ambassador_species', '')
        ambassador_species_description = schema_raw_data.get(
            'ambassador_species_description', '')

        delete_species = sorted(
            list(schema_raw_data.pop('delete_species', '')), reverse=True)
        if edit_species is None:
            for list_index in delete_species:
                self.species.pop(int(list_index))

        # picture processing
        upload_picture_url = schema_raw_data.pop('upload_picture_url', None)
        if upload_picture_url:
            temp_folder = self.getSite().temp_folder
            picture_id = unquote(upload_picture_url.split('/')[-1])
            ambassador_species_picture = getattr(temp_folder, picture_id)
        else:
            ambassador_species_picture = None
        x1 = schema_raw_data.pop('x1')
        y1 = schema_raw_data.pop('y1')
        x2 = schema_raw_data.pop('x2')
        y2 = schema_raw_data.pop('y2')
        crop_coordinates = (x1, y1, x2, y2)

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        species_success = self.process_species(
            edit_species, delete_picture, ambassador_species,
            ambassador_species_description, ambassador_species_picture,
            crop_coordinates, form_errors)

        if form_errors:
            if REQUEST is not None:
                if not species_success:
                    schema_raw_data['ambassador_species'] = ambassador_species
                    schema_raw_data['ambassador_species_description'] = \
                        ambassador_species_description
                self._prepare_error_response(REQUEST, form_errors,
                                             schema_raw_data)
                if edit_species is not None and not species_success:
                    REQUEST.RESPONSE.redirect(
                        '%s/edit_html?lang=%s&edit_species=%s' % (
                            self.absolute_url(), _lang, edit_species))
                else:
                    REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                              (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1])  # pick an error

        if self.discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()

        # if the user doesn't have permission to publish objects,
        # the object must be unapproved
        if not self.glCheckPermissionPublishObjects():
            self.approveThis(0, None)
            self.sendEmailNotificationWhenUnapproved()

        # Overwrite any inconsistent values in the choice property
        if not self.species and self.choice == u'3':
            self.choice = u'1'
        if self.species:
            self.choice = u'3'

        self._p_changed = 1
        self.recatalogNyObject(self)
        # log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        notify(NyContentObjectEditEvent(self, contributor))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                      (self.absolute_url(), _lang))

    security.declarePrivate('sendEmailNotificationWhenUnapproved')

    def sendEmailNotificationWhenUnapproved(self):
        """ """
        site = self.getSite()
        auth_tool = site.getAuthenticationTool()
        email_tool = site.getEmailTool()
        translate_tool = site.getPortalTranslations()
        notification_tool = site.getNotificationTool()

        template = email_templates['email_when_unapproved_to_maintainer']
        contributor = self.REQUEST.AUTHENTICATED_USER
        d = {'NAME': '',
             'CONTRIBUTOR': auth_tool.getUserFullName(contributor),
             'MUNICIPALITY_TITLE': self.title_or_id(),
             'MUNICIPALITY_URL': self.absolute_url(),
             '_translate': translate_tool,
             'portal': site,
             }
        try:
            mail_from = notification_tool.from_email
        except AttributeError:
            mail_from = email_tool.get_addr_from()

        mails_to = site.getMaintainersEmails(self)

        for mail_to in mails_to:
            users = list(auth_tool.lookup_user_by_email(mail_to))
            if users:
                name = auth_tool.getUserFirstName(users[0])
            else:
                name = mail_to[:mail_to.find('@')]
            d['NAME'] = name
            mail_data = template.render_email(**d)

            email_tool.sendEmail(mail_data['body_text'],
                                 mail_to,
                                 mail_from,
                                 mail_data['subject'])
            d['NAME'] = ''

    # site actions
    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'municipality_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')

    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'municipality_edit')

    security.declareProtected(PERMISSION_ADD_MUNICIPALITY, 'process_species')

    def process_species(
            self, edit_species, delete_picture, ambassador_species,
            ambassador_species_description, ambassador_species_picture,
            crop_coordinates, form_errors):
        picture_test = ambassador_species_picture is not None
        if picture_test:
            ambassador_species_picture = process_picture(
                ambassador_species_picture, crop_coordinates)
        if edit_species is not None:
            if not ambassador_species:
                form_errors['ambassador_species'] = [
                    'The species name is mandatory!']
            else:
                if not ambassador_species_picture and not delete_picture:
                    ambassador_species_picture = self.species[
                        edit_species].picture
                self.species[edit_species].edit(
                    ambassador_species, ambassador_species_description,
                    ambassador_species_picture)
                self._p_changed = True
                return True
        else:
            if ((ambassador_species_description or picture_test) and
                    not ambassador_species):
                form_errors['ambassador_species'] = [
                    'The species name is mandatory!']
            elif ambassador_species:
                new_species = AmbassadorSpecies(ambassador_species,
                                                ambassador_species_description,
                                                ambassador_species_picture)
                self.species.append(new_species)
                return True

    security.declareProtected(view, 'render_picture')

    def render_picture(self, RESPONSE, list_index=0):
        """ Render municipality picture """
        list_index = int(list_index)
        if len(self.species) > list_index and self.species[
                list_index].picture is not None:
            return self.species[list_index].picture.send_data(
                RESPONSE, as_attachment=False)
        else:
            return None

    security.declarePrivate('objectkeywords')

    def objectkeywords(self, lang):
        return u' '.join([
            self._objectkeywords(lang),
            self.municipality,
            self.specieskeywords(),
            self.html2text(self.getLocalProperty('explain_why', lang)),
            self.html2text(self.getLocalProperty('explain_how', lang)),
            self.html2text(self.getLocalProperty('importance1', lang)),
            self.html2text(self.getLocalProperty('importance2', lang)),
            self.html2text(self.getLocalProperty('usage', lang))]
            )

    security.declarePrivate('specieskeywords')

    def specieskeywords(self):
        if len(self.species) > 0:
            species = ['%s %s' % (ob.title, self.html2text(ob.description))
                       for ob in self.species]
            return u' '.join(species)
        return ''

InitializeClass(NyMunicipality)

config.update({
    'constructors': (municipality_add_html, addNyMunicipality),
    'folder_constructors': [
        ('municipality_add_html', municipality_add_html),
        ('addNyMunicipality', addNyMunicipality),
        ],
    'add_method': addNyMunicipality,
    'validation': issubclass(NyMunicipality, NyValidation),
    '_class': NyMunicipality,
})


def get_config():
    return config

from PIL import Image
from OFS.Image import manage_addFile as manage_addImage
from cStringIO import StringIO


class FileUpload(Implicit, Item):
    """
    Manage file uploads
    """

    def __init__(self, id):
        self.id = id

    security = ClassSecurityInfo()

    security.declareProtected(PERMISSION_ADD_MUNICIPALITY, 'upload_file')

    def upload_file(self, REQUEST):
        """ """
        temp_folder = self.getSite().temp_folder
        file = REQUEST.form.get('upload_file', None)
        if file is None:
            return None

        try:
            image = Image.open(file)
        except:  # Python Imaging Library doesn't recognize it as an image
            return None

        x, y = image.size
        filename = file.filename

        image_format = image.format
        if not image_format:
            _, ext = os.path.splitext(filename)
            image_format = ext
        # can't leave empty because image.save will crash
        if not image_format:
            image_format = 'JPEG'

        MAX_SIZE = 400
        if x >= MAX_SIZE and x >= y:
            x, y = MAX_SIZE, y * MAX_SIZE / x
            resize = True
        elif y >= MAX_SIZE and y >= x:
            x, y = x * MAX_SIZE / y, MAX_SIZE
            resize = True
        else:
            resize = False
        if resize:
            try:
                image = image.resize((x, y), Image.ANTIALIAS)
            except AttributeError:
                image = image.resize((x, y))

        image_io = StringIO()
        image.save(image_io, image_format, quality=85)

        id = make_id(temp_folder, id=filename)
        manage_addImage(temp_folder, id, file=image_io.getvalue())
        ob = getattr(temp_folder, id)
        ob.filename = filename
        ob.p_changed = 1

        if x > y:
            return (ob.absolute_url(), (x-y)/2, 0, y + (x-y)/2, y, resize)
        else:
            return (ob.absolute_url(), 0, (y-x)/2, x, x + (y-x)/2, resize)

InitializeClass(FileUpload)

from Products.Naaya.NyFolder import NyFolder
NyFolder.file_upload = FileUpload('file_upload')


def get_image_size(file):
    """
    Test if the specified uploaded B{file} is a valid image.
    """
    try:
        image = Image.open(file)
    except:  # Python Imaging Library doesn't recognize it as an image
        return False
    else:
        file.seek(0)
        return image.size


def image2blob(image, filename, content_type):
    blobfile = NyBlobFile(filename=filename, content_type=content_type)
    bf_stream = blobfile.open_write()
    # data = image.data
    # bf_stream.write(data)
    bf_stream.write(image)
    bf_stream.close()
    blobfile.size = len(image)
    return blobfile


def process_picture(ambassador_species_picture, crop_coordinates):
    filename = ambassador_species_picture.filename
    content_type = ambassador_species_picture.content_type
    image_string = data2stringIO(ambassador_species_picture.data)
    img = Image.open(image_string)
    fmt = img.format
    crop_size = crop_coordinates[2] - crop_coordinates[0]
    if crop_size == 0:
        x = img.size[0]
        y = img.size[1]
        crop_size = min(x, y)
        if x > y:
            crop_coordinates = ((x-y)/2, 0, y + (x-y)/2, y)
        else:
            crop_coordinates = (0, (y-x)/2, x, x + (y-x)/2)
    img = img.crop(crop_coordinates)
    if crop_size > 640:
        crop_size = 190
    try:
        img = img.resize((crop_size, crop_size), Image.ANTIALIAS)
    except AttributeError:
        img = img.resize((width, height))
    newimg = StringIO()
    img.save(newimg, fmt, quality=85)
    blobfile = image2blob(newimg.getvalue(), filename=filename,
                          content_type=content_type)
    return blobfile


def data2stringIO(data):
    str_data = StringIO()
    if isinstance(data, str):
        str_data.write(data)
    else:
        while data is not None:
            str_data.write(data.data)
            data = data.next
    str_data.seek(0)
    return str_data
