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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Cornel Nitu - Finsiel Romania

#python imports
import os
import errno

#zope imports
from Globals import package_home
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

#product imports
from SafeDict import SafeDict
from MaildropHost import MaildropHost

class Notification:
    """ using a template, sends a notification """

    security = ClassSecurityInfo()

    security.declarePrivate('findtext')
    def findtext(self, template, dict=None):
        """Make some text from a template file. Once the templatefile is found,
            string substitution is performed by interpolation in `dict'."""
        if dict is not None:
            try:
                sdict = SafeDict(dict)
                try:
                    text = sdict.interpolate(template)
                except UnicodeError:
                    # Try again after coercing the template to unicode
                    utemplate = unicode(template, 'utf-8', 'replace')
                    text = sdict.interpolate(utemplate)
            except (TypeError, ValueError), e:
                # The template is really screwed up
                raise Exception, "This template is really screwed up"
        return text


    security.declarePrivate('maketext')
    def maketext(self, template, dict=None):
        return self.findtext(template, dict)


    security.declarePrivate('send_registration')
    def send_registration(self, account, email, fname, lname, password, webmaster, subject, template_text, template_html):
        msg_text = self.maketext(
            template_text,
            {'firstname': fname,
             'lastname' : lname,
             'sender'   : webmaster,
             'username' : account,
             'password' : password,
             'email'    : email,
             })
        msg_html = self.maketext(
            template_html,
            {'firstname': fname,
             'lastname' : lname,
             'sender'   : webmaster,
             'username' : account,
             'password' : password,
             'email'    : email,
             })
        self.send_email(webmaster, webmaster, subject, msg_text, msg_html)


    security.declarePrivate('send_feedback')
    def send_feedback(self, title, comments, fname, lname, email, url, webmaster, template_text, template_html):
        msg_text = self.maketext(
            template_text,
            {'fullname': "%s %s" % (fname, lname),
             'from_address'   : email,
             'url' :    url,
             'message' : comments,
             })
        msg_html = self.maketext(
            template_html,
            {'fullname': "%s %s" % (fname, lname),
             'from_address'   : email,
             'url' :    url,
             'message' : comments,
             })
        self.send_email(webmaster, webmaster, title, msg_text, msg_html)

    security.declarePrivate('send_passwords')
    def send_passwords(self, account, email, fname, lname, pwd, webmaster, subject, template_text, template_html):
        msg_text = self.maketext(
            template_text,
            {'firstname'      : fname,
             'lastname'   : lname,
             'sender'   : webmaster,
             'username' : account,
             'password' : pwd,
             })
        msg_html = self.maketext(
            template_html,
            {'firstname'      : fname,
             'lastname'   : lname,
             'sender'   : webmaster,
             'username' : account,
             'password' : pwd,
             })
        self.send_email(email, webmaster, subject, msg_text, msg_html)


    security.declarePrivate('send_notifications')
    def send_notifications(self, to, fr, template):
        mssg = self.maketext(
            template,
            {'firstname'      : 'Cornel',
             'lastname'   : 'Nitu',
             'sender'   : 'Marius',
             })
        self.send_email(to, fr, mssg)


    security.declarePrivate('send_email')
    def send_email(self, to, fr, subject, text, html):
        headers = {}
        headers['from'] = fr
        headers['to'] = to

        maildrop = MaildropHost()
        message = self.createHtmlMail(html, text, subject, fr, to)
        maildrop._send(headers, message)
        return 1


    security.declarePrivate('createHtmlMail')
    def createHtmlMail(self, html, text, subject, fromA, to):
        """ create a mime-message that will render HTML in popular MUAs, text in better ones """
        import MimeWriter
        import mimetools
        import cStringIO

        out = cStringIO.StringIO() # output buffer for our message 
        htmlin = cStringIO.StringIO(html)
        txtin = cStringIO.StringIO(text)

        writer = MimeWriter.MimeWriter(out)
        #
        # set up some basic headers... we put subject here
        # because smtplib.sendmail expects it to be in the
        # message body
        #
        writer.addheader("From", fromA)
        writer.addheader("To", to)
        writer.addheader("Subject", subject)
        #writer.addheader("Date", DateTime())   #do be done!!!!
        writer.addheader("MIME-Version", "1.0")
        #
        # start the multipart section of the message
        # multipart/alternative seems to work better
        # on some MUAs than multipart/mixed
        #
        writer.startmultipartbody("alternative")
        writer.flushheaders()
        #
        # the plain text section
        #
        subpart = writer.nextpart()
        subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
        pout = subpart.startbody("text/plain", [("charset", 'utf-8')])
        mimetools.encode(txtin, pout, 'quoted-printable')
        txtin.close()
        #
        # start the html subpart of the message
        #
        subpart = writer.nextpart()
        subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
        #
        # returns us a file-ish object we can write to
        #
        pout = subpart.startbody("text/html", [("charset", 'utf-8')])
        mimetools.encode(htmlin, pout, 'quoted-printable')
        htmlin.close()
        #
        # Now that we're done, close our writer and
        # return the message body
        #
        writer.lastpart()
        msg = out.getvalue()
        out.close()
        return msg

InitializeClass(Notification)