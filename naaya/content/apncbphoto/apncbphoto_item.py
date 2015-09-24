from copy import deepcopy
import os
import sys
import xlrd

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.interface import implements
from zope.event import notify

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
# from naaya.content.base.constants import *
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED_MSG
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import make_id

from interfaces import INyAPNCBPhoto
from permissions import PERMISSION_ADD_APNCBPHOTO

from alchemy import Session, SessionTest
from alchemy import Document, Author, Image, Park, Biome, Vegetation
from upload import save_uploaded_file

DEFAULT_SCHEMA = {
    'db_test': dict(sortorder=30, widget_type='Checkbox',
                    label='Test database', data_type='bool'),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)

# this dictionary is updated at the end of the module
config = {
    'product': 'NaayaAPNCBPhoto',
    'module': 'apncbphoto_item',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': 'Naaya APNCB Photo archive',
    'label': 'APNCB Photo archive',
    'permission': PERMISSION_ADD_APNCBPHOTO,
    'forms': ['apncbphoto_add', 'apncbphoto_edit', 'apncbphoto_index'],
    'add_form': 'apncbphoto_add_html',
    'description': 'This is Naaya APNCB Photo archive.',
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': 'NyAPNCBPhoto',
    '_module': sys.modules[__name__],
    'additional_style': None,
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'apncbphoto.png'),
    '_misc': {
        'NyAPNCBPhoto.png': ImageFile('www/apncbphoto.png', globals()),
        'NyAPNCBPhoto_marked.png': ImageFile('www/apncbphoto_marked.png',
                                             globals()),
        },
    }


def apncbphoto_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent(
        {'here': self, 'kind': config['meta_type'],
         'action': 'addNyAPNCBPhoto', 'form_helper': form_helper},
        'apncbphoto_add')


def _create_NyAPNCBPhoto_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='apncbphoto')
    ob = NyAPNCBPhoto(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyAPNCBPhoto(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create APNCB Photo archive.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate',
                                                                ''))
    recaptcha_response = schema_raw_data.get('g-recaptcha-response', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''),
                 prefix='ep')
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyAPNCBPhoto_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                                            _override_releasedate=_releasedate)

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
            transaction.abort()
            # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/apncbphoto_add_html' %
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
        if (l_referer == 'apncbphoto_manage_add' or
                l_referer.find('apncbphoto_manage_add') != -1):
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'apncbphoto_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()


class NyAPNCBPhoto(Implicit, NyContentData, NyAttributes, NyItem,
                   NyNonCheckControl, NyValidation, NyContentType):
    """ """

    implements(INyAPNCBPhoto)

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyAPNCBPhoto.png'
    icon_marked = 'misc_/NaayaContent/NyAPNCBPhoto_marked.png'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyValidation.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    # zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')

    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            raise ValueError(form_errors.popitem()[1])  # pick a random error

        if _approved != self.approved:
            if _approved == 0:
                _approved_by = None
            else:
                _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        if self.discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')

    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            if self.discussion:
                self.open_for_comments()
            else:
                self.close_for_comments()
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
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors,
                                             schema_raw_data)
                REQUEST.RESPONSE.redirect(
                    '%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1])  # pick an error

    # zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/apncbphoto_manage_edit',
                                        globals())

    # site pages
    security.declareProtected(view, 'index_html')

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        results = []
        if 'submit' in REQUEST:
            subject = REQUEST.form.get('subject', '').encode('utf-8')
            date = REQUEST.form.get('date', '').encode('utf-8')
            esp_nom_com = REQUEST.form.get('esp_nom_com', '').encode('utf-8')
            esp_nom_lat = REQUEST.form.get('esp_nom_lat', '').encode('utf-8')
            park = REQUEST.form.get('park', '').encode('utf-8')
            author = REQUEST.form.get('author', '').encode('utf-8')

            if self.db_test:
                session = SessionTest()
            else:
                session = Session()
            try:
                documents = session.query(
                    Document, Author, Image, Park, Biome, Vegetation)\
                    .filter(Document.subject.like('%' + subject + '%'))\
                    .filter(Document.date.like('%' + date + '%'))\
                    .filter(Document.esp_nom_com.like('%' + esp_nom_com + '%'))\
                    .filter(Document.esp_nom_lat.like('%' + esp_nom_lat + '%'))\
                    .filter(Author.authorid == Document.authorid)\
                    .filter(Image.imageid == Document.imageid)\
                    .filter(Park.parkid == Document.parkid)\
                    .filter(Biome.biomeid == Document.biomeid)\
                    .filter(Vegetation.vegetationid == Document.vegetationid)
                if park:
                    documents = documents.filter(Park.code == park)
                if author:
                    documents = documents.filter(Author.code == author)
                documents = documents.all()
                for document in documents:
                    results.append({
                        'subject': document.Document.subject,
                        'author': document.Author.name,
                        'image': document.Image.code,
                        'imageid': document.Image.imageid,
                        'ref_geo': document.Document.ref_geo,
                        'park': document.Park.name,
                        'date': document.Document.date,
                        'altitude': document.Document.altitude,
                        'esp_nom_lat': document.Document.esp_nom_lat,
                        'docid': document.Document.docid,
                        })
            except:
                raise
            finally:
                if session is not None:
                    session.close()

        return self.getFormsTool().getContent(
            {'here': self, 'results': results},
            'apncbphoto_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')

    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'apncbphoto_edit')

    _admin = PageTemplateFile('zpt/apncbphoto_admin', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'admin')

    def admin(self, REQUEST=None):
        """ Edit lists (parks, authors) """
        return self._admin(REQUEST)

    _upload = PageTemplateFile('zpt/apncbphoto_upload', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'upload')

    def upload(self, REQUEST=None):
        """ upload metatada into the database """
        rows = None
        if 'submit_metadata' in REQUEST.form:
            file = REQUEST.get('metadata_file')
            update_existing = REQUEST.get('update_existing')
            workbook = xlrd.open_workbook(file_contents=file.read())
            if self.db_test:
                session = SessionTest()
            else:
                session = Session()
            rows, imported, skipped = save_uploaded_file(workbook, session,
                                                         update_existing)
            have_errors = False
            for sheet in skipped:
                if sheet:
                    have_errors = True
            if have_errors:
                errors = []
                for sheet in range(len(skipped)):
                    if skipped[sheet]:
                        errors.append(
                            'Sheet %s: %s row(s) already in the database and '
                            'skipped: %s' % (
                                sheet+1, len(skipped[sheet]),
                                ', '.join(str(x+2) for x in skipped[sheet])))
                    if imported[sheet]:
                        self.setSessionInfoTrans(
                            'Sheet %s: %s row(s) imported: %s' % (
                                sheet+1, len(imported[sheet]),
                                ', '.join(str(x+2) for x in imported[sheet])))
                if not imported:
                    errors.append('No rows imported')
                self.setSessionErrorsTrans(errors)
            else:
                total_imported = 0
                for sheet in imported:
                    total_imported += len(sheet)
                self.setSessionInfoTrans('File imported successfully (%s rows)'
                                         % total_imported)
        return self._upload(REQUEST, workbook=rows)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_park')

    def update_park(self, REQUEST):
        """ Update park name """
        name = REQUEST.get('name')
        park_id = REQUEST.get('park_id')
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            park = session.query(Park).filter(Park.parkid == park_id).first()
            park.name = name
            session.commit()
        except:
            raise
        finally:
            if session is not None:
                session.close()
        self.setSessionInfoTrans(
            'Park name changed successfully (Park ID: %s)' % park_id)

        return self._admin(REQUEST)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'delete_park')

    def delete_park(self, REQUEST):
        """ Delete park """
        park_id = REQUEST.get('park_id')
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            session.query(Park).filter(Park.parkid == park_id).delete()
            session.commit()
        except:
            raise
        finally:
            if session is not None:
                session.close()
        self.setSessionInfoTrans('Park deleted')

        return self._admin(REQUEST)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_author')

    def update_author(self, REQUEST):
        """ Update author name """
        name = REQUEST.get('name')
        author_id = REQUEST.get('author_id')
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            author = session.query(Author).filter(
                Author.authorid == author_id).first()
            author.name = name
            session.commit()
        except:
            raise
        finally:
            if session is not None:
                session.close()
        self.setSessionInfoTrans(
            "Author's name changed successfully (Author ID: %s)" % author_id)

        return self._admin(REQUEST)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'delete_author')

    def delete_author(self, REQUEST):
        """ Delete author """
        author_id = REQUEST.get('author_id')
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            session.query(Author).filter(Author.authorid == author_id).delete()
            session.commit()
        except:
            raise
        finally:
            session.close()
        self.setSessionInfoTrans(
            "Author deleted")

        return self._admin(REQUEST)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'delete_photo')

    def delete_photo(self, REQUEST):
        """ Delete record of a photo """
        docid = REQUEST.get('docid')
        if not docid:
            return
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            docs = session.query(Document).filter(
                Document.docid == docid).all()
            count = len(docs)
            session.query(Document).filter(
                Document.docid == docid).delete()
            session.query(Image).filter(
                Image.imageid == docs[0].imageid).delete()
            session.commit()
            self.setSessionInfoTrans("%s record(s) deleted" % count)
        except:
            raise
        finally:
            session.close()

        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view_management_screens, 'delete_all')

    def delete_all(self, REQUEST):
        """ Delete all records """
        if self.db_test:
            session = SessionTest()
        elif REQUEST.get('force'):
            session = Session()
        else:
            self.setSessionErrorsTrans("Production database cannot be deleted")
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        try:
            session.query(Document).delete()
            session.query(Park).delete()
            session.query(Author).delete()
            session.query(Image).delete()
            session.query(Author).delete()
            session.query(Biome).delete()
            session.query(Vegetation).delete()
            session.commit()
        except:
            raise
        finally:
            session.close()
        self.setSessionInfoTrans("All records deleted")

        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view, 'get_parks')

    def get_parks(self):
        """ return all parks """
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            parks = session.query(Park).all()
        except:
            raise
        finally:
            if session is not None:
                session.close()
        return [{'code': park.code, 'name': park.name, 'id': park.parkid}
                for park in parks]

    security.declareProtected(view, 'get_authors')

    def get_authors(self):
        """ return all authors """
        if self.db_test:
            session = SessionTest()
        else:
            session = Session()
        try:
            authors = session.query(Author).all()
        except:
            raise
        finally:
            if session is not None:
                session.close()
        return [{'code': author.code, 'name': author.name,
                 'id': author.authorid}
                for author in authors]

    def checkPermissionViewManagementScreens(self):
        return self.checkPermission(view_management_screens)


InitializeClass(NyAPNCBPhoto)

manage_addNyAPNCBPhoto_html = PageTemplateFile('zpt/apncbphoto_manage_add',
                                               globals())
manage_addNyAPNCBPhoto_html.kind = config['meta_type']
manage_addNyAPNCBPhoto_html.action = 'addNyAPNCBPhoto'
config.update({
    'constructors': (manage_addNyAPNCBPhoto_html, addNyAPNCBPhoto),
    'folder_constructors': [
        ('manage_addNyAPNCBPhoto_html', manage_addNyAPNCBPhoto_html),
        ('apncbphoto_add_html', apncbphoto_add_html),
        ('addNyAPNCBPhoto', addNyAPNCBPhoto),
        ],
    'add_method': addNyAPNCBPhoto,
    'validation': issubclass(NyAPNCBPhoto, NyValidation),
    '_class': NyAPNCBPhoto,
})


def get_config():
    return config
