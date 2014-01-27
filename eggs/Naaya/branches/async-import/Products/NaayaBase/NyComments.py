"""
This module contains the class that handles comments (discussion) for the
current object.

Only the types of objects for which their class extends the I{NyCommentable}
can be commented.
"""

from StringIO import StringIO
from warnings import warn

from zope.interface import implements
from zope.component import adapter
from zope.event import notify
from zope.lifecycleevent.interfaces import (IObjectAddedEvent,
                                            IObjectMovedEvent)
from App.config import getConfiguration
from zope.component.interfaces import IObjectEvent
from OFS.interfaces import IObjectWillBeMovedEvent
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

from Products.NaayaBase.events import NyCommentAddEvent
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from constants import *
from Products.NaayaCore.managers.utils import utils
import interfaces
import akismet
from akismet import AkismetError
from unidecode import unidecode
from naaya.core.utils import cleanup_message, is_ajax, str2bool
from naaya.core.backport import json
from naaya.core.zope2util import json_response, ofs_path

akismet.USERAGENT = "MyApplication/MyVersion"

configuration = getConfiguration()
environment = getattr(configuration, 'environment', {})
has_api_key = environment.has_key('AKISMET_API_KEY')

if has_api_key:
    akismet_api_key = environment.get('AKISMET_API_KEY', '')

@adapter(interfaces.INyCommentable, IObjectEvent)
def handleComentedObject(ob, event):
    if IObjectAddedEvent.providedBy(event):
        catalog_comments(ob)
    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            catalog_comments(ob)
    elif IObjectWillBeMovedEvent.providedBy(event):
        if event.oldParent is not None:
            uncatalog_comments(ob)

def catalog_comments(obj):
    catalog = obj.getSite().getCatalogTool()
    container = obj._get_comments_container()
    if container is not None:
        for comment in container.objectValues(NyComment.meta_type):
            try:
                catalog.catalog_object(comment, ofs_path(comment))
            except:
                obj.getSite().log_current_error()

def uncatalog_comments(obj):
    catalog = obj.getSite().getCatalogTool()
    container = obj._get_comments_container()
    if container is not None:
        for comment in container.objectValues(NyComment.meta_type):
            try:
                catalog.uncatalog_object(ofs_path(comment))
            except:
                obj.getSite().log_current_error()

class NyComment(SimpleItem):

    implements(interfaces.INyComment)
    meta_type = 'Naaya Comment'
    security = ClassSecurityInfo()

    icon = 'misc_/Naaya/comment.gif'

    def __init__(self, id, title, body, author, releasedate, spamstatus):
        self.id = id
        self.title = title
        self.body = body
        self.author = author
        self.releasedate = releasedate
        self.spamstatus = spamstatus

    def export(self):
        """ Export object in Naaya XML format. """

        encode = self.getSite().utXmlEncode
        return '<comment id="%s" title="%s" body="%s" author="%s" date="%s" />' % \
            (encode(self.id),
                encode(self.title),
                encode(self.body),
                encode(self.author),
                encode(self.releasedate))

    def absolute_url(self):
        """ override `absolute_url` to link to our parent object """

        obj = self.aq_parent.aq_parent
        return '%s#comment-%s' % (obj.absolute_url(), self.id)

    def syndicateThis(self, lang=None):
        """ Render this comment as a fragment of an RSS 1.0 feed """
        out = StringIO()
        if lang is None: 
            lang = self.gl_get_selected_language()

        title = "Comment by %s: %s" % (self.author, self.title)
        out.write('<item rdf:about="%s">' % self.absolute_url())
        out.write('<link>%s</link>' % self.absolute_url())
        out.write('<title>%s</title>' % self.utXmlEncode(title))
        out.write('<description><![CDATA[%s]]></description>' %
                     self.utToUtf8(self.body))
        out.write('<dc:title>%s</dc:title>' % self.utXmlEncode(title))
        out.write('<dc:date>%s</dc:date>'
                     % self.utShowFullDateTimeHTML(self.releasedate))
        out.write('<dc:description><![CDATA[%s]]></dc:description>' %
                     self.utToUtf8(self.body))
        out.write('<dc:contributor>%s</dc:contributor>' %
                     self.utXmlEncode(self.author))
        out.write('<dc:language>%s</dc:language>' %
                     self.utXmlEncode(lang))
        out.write('</item>')
        return out.getvalue()

InitializeClass(NyComment)


#@obsolete class
class comment_item(utils):
    """
    Class that implements a comment.
    """

    def __init__(self, id, title, body, author, date):
        """
        Initialize variables:

        B{id} - unique id

        B{title} - the title of the comment (subject)

        B{body} - comment's body

        B{author} - authenticated user's name

        B{date} - posting date

        """
        raise NotImplementedError
        self.id = id
        self.title = title
        self.body = body
        self.author = author
        self.date = date

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    security.declarePublic('export_this')
    def export_this(self):
        """
        Exports object into Naaya XML format.
        """

        return '<comment id="%s" title="%s" body="%s" author="%s" date="%s" />' % \
            (self.utXmlEncode(self.id),
                self.utXmlEncode(self.title),
                self.utXmlEncode(self.body),
                self.utXmlEncode(self.author),
                self.utXmlEncode(self.date))

    def title_or_id(self):
        """
        Returns title or id.
        """

        if not self.title:
            return self.id
        else:
            return self.title

InitializeClass(comment_item)

class NyCommentable:
    """
    Class that handles the validation operation for a single object.
    """

    implements(interfaces.INyCommentable)
    security = ClassSecurityInfo()

    def _get_comments_container(self):
        if not hasattr(self.aq_base, '.comments'):
            return None
        return getattr(self, '.comments', None)

    def _add_comments_container(self):
        folder = Folder(id='.comments')
        setattr(self, '.comments', folder)
        return self._get_comments_container()

    security.declareProtected(view, 'get_comments_list')
    def get_comments_list(self):
        """ Return the list of comments sorted by releasedate. """

        container = self._get_comments_container()
        if container:
            comments = container.objectValues()
            return sorted(comments, key=lambda c: c.releasedate)
        else:
            return []

    security.declareProtected(view, 'count_comments')
    def count_comments(self):
        """ Returns the number of comments. """

        container = self._get_comments_container()
        if container:
            return len(container.objectIds())
        else:
            return 0

    def is_open_for_comments(self):
        return self.discussion
        warn('Function `is_open_for_comments` is deprecated. NyCommentable reads '
             'the `discussion` property directly',
             DeprecationWarning, stacklevel=2)

    security.declarePrivate('open_for_comments')
    def open_for_comments(self):
        """
        Enable(open) comments.
        """

        warn('Function `open_for_comments` is deprecated. NyCommentable reads '
             'the `discussion` property directly',
             DeprecationWarning, stacklevel=2)

    security.declarePrivate('close_for_comments')
    def close_for_comments(self):
        """
        Disable(close) comments.
        """

        warn('Function `close_for_comments` is deprecated. NyCommentable reads '
             'the `discussion` property directly',
             DeprecationWarning, stacklevel=2)

    security.declarePrivate('export_comments')
    def export_comments(self):
        """
        Export all the comments in XML format.
        """

        r = []
        ra = r.append
        ra('<discussion>')
        for c in self.get_comments_list():
            ra(c.export())
        ra('</discussion>')
        return ''.join(r)

    security.declarePrivate('import_comments')
    def import_comments(self, discussion):
        """
        Import comments.
        """

        if discussion is not None:
            for c in discussion.comments:
                self._comment_add(c.id,
                            c.title.encode('utf-8'),
                            c.body.encode('utf-8'),
                            c.author.encode('utf-8'),
                            c.releasedate.encode('utf-8'))

    def _is_spam(self, text):
        """
        Check if user submitted a spam comment.
        """
        site = self.getSitePath()
        user_agent = self.REQUEST.get('HTTP_USER_AGENT', '')
        user_ip = self.REQUEST.get('REMOTE_ADDR', '127.0.0.1')
        text = unidecode(text)

        is_spam = False
        if has_api_key:
            try:
                akismet_key = akismet.verify_key(akismet_api_key, site)
                if akismet_key:
                    is_spam = akismet.comment_check(akismet_api_key, site, user_ip,
                                                    user_agent,
                                                    comment_content=text)
            except akismet.AkismetError:
                pass

        return is_spam

    def _submit_comment_to_akismet(self, text, status):
        """
        Submit spam comment to akismet
        """
        site = self.getSitePath()
        user_agent = self.REQUEST.get('HTTP_USER_AGENT', '')
        user_ip = self.REQUEST.get('REMOTE_ADDR', '127.0.0.1')
        text = unidecode(text)

        if has_api_key and akismet_api_key:
            if akismet.verify_key(akismet_api_key, site):
                if status:
                    akismet.submit_spam(akismet_api_key, site, user_ip, user_agent,
                                        comment_content=text)
                else:
                    akismet.submit_ham(akismet_api_key, site, user_ip, user_agent,
                                        comment_content=text)

    #permissions
    def checkPermissionAddComments(self):
        """ Check for adding comments. """

        return self.checkPermission(PERMISSION_COMMENTS_ADD)

    def checkPermissionManageComments(self):
        """ Check for managing comments. """

        return self.checkPermission(PERMISSION_COMMENTS_MANAGE)

    def _comment_add(self, title='', body='', author='', releasedate=None,
                     spamstatus=False):
        container = self._get_comments_container()
        if container is None:
            container = self._add_comments_container()

        id = self.utGenRandomId()
        ob = NyComment(id, title, body, author, releasedate, spamstatus)
        container._setObject(id, ob)

        notify(NyCommentAddEvent(ob, author, self))

        return ob

    def _comment_del(self, id):
        container = self._get_comments_container()
        if container:
            container.manage_delObjects([id])

    security.declareProtected(PERMISSION_COMMENTS_ADD, 'comment_add')
    def comment_add(self, REQUEST):
        """
        Add a comment for this object.
        """
        err = []
        if not self.checkPermissionSkipCaptcha():
            contact_word = REQUEST.get('contact_word')
            captcha_errors = self.validateCaptcha(contact_word, REQUEST)
            if captcha_errors:
                err.extend(captcha_errors)
        if err:
            self.setSessionErrorsTrans(err)
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        form_data = dict(REQUEST.form)
        author = REQUEST.AUTHENTICATED_USER.getUserName()
        comment_title = form_data.get('title')
        comment_body = cleanup_message(form_data.get('body'))

        spamstatus = self._is_spam(comment_title)
        if not spamstatus:
            spamstatus = self._is_spam(comment_body)

        ob = self._comment_add(title = comment_title,
                               body = comment_body,
                               author = author,
                               releasedate = self.utGetTodayDate())

        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(author)

        self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        return REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_COMMENTS_MANAGE, 'comment_del')
    def comment_del(self, REQUEST):
        """
        Delete a comment.
        """

        id_comment = REQUEST.form.get('id', '')
        user = REQUEST.AUTHENTICATED_USER.getUserName()

        self._comment_del(id_comment)

        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(user)

        if is_ajax(REQUEST):
            return json_response({'status': 'success'}, REQUEST.RESPONSE)
        else:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    def _set_comment_spam_status(self, id, status):
        """
        """
        container = self._get_comments_container()
        if container:
            comment = container._getOb(id, None)
            if comment:
                comment.spamstatus = status
                comment.recatalogNyObject(comment)
                try:
                    self._submit_comment_to_akismet(comment.title, status)
                    self._submit_comment_to_akismet(comment.body, status)
                except AkismetError:
                    pass

                return True
            else:
                return False

        return False

    security.declareProtected(PERMISSION_COMMENTS_MANAGE, 'comment_spam_status')
    def comment_spam_status(self, REQUEST):
        """
        Set comment spam status
        Status: True/False
        If it's an AJAX request return a message,
        else redirect user to the admin page
        """

        id_comment = REQUEST.form.get('id', '')
        status = str2bool(REQUEST.form.get('status', False))
        user = REQUEST.AUTHENTICATED_USER.getUserName()
        status_set = False
        translate = self.getPortalI18n().get_translation

        if self._set_comment_spam_status(id_comment, status):
            status_set = True

        if is_ajax(REQUEST):
            if status_set:
                return json_response({'status': 'success'}, REQUEST.RESPONSE)
            else:
                return json_response({'status': 'error',
                                      'message': translate(MESSAGE_ERROROCCURRED)},
                                    REQUEST.RESPONSE)
        else:
            if status_set:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            else:
                self.setSessionErrorsTrans(MESSAGE_ERROROCCURRED)
            return REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

        return False

    comments_box = NaayaPageTemplateFile('zpt/comments_box', globals(), 'naaya.base.comments.box')

    security.declareProtected(PERMISSION_COMMENTS_ADD, 'comment_add_html')
    comment_add_html = NaayaPageTemplateFile('zpt/comment_add', globals(), 'naaya.base.comments.add')

InitializeClass(NyCommentable)
