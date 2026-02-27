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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join, isdir
from os import mkdir, unlink
import time
import smtplib
import MimeWriter
import cStringIO
import mimetools

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.NaayaCore.managers.utils import utils

MAILDROP_HOME = join(CLIENT_HOME, 'maildrop')
if not isdir(MAILDROP_HOME):
    try:
        mkdir(MAILDROP_HOME)
    except:
        raise OSError, 'Can\'t create directory %s' % MAILDROP_HOME

MAILDROP_SPOOL = join(MAILDROP_HOME, 'spool')
if not isdir(MAILDROP_SPOOL):
    try:
        mkdir(MAILDROP_SPOOL)
    except:
        raise OSError, 'Can\'t create directory %s' % MAILDROP_SPOOL

FLASH_MAIL_TEMPLATE = """
##To:%s
##From:%s
%s
"""

class MDH(utils):
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass

    #core
    def __create_flash_email(self, p_html_content, p_text_content, p_to, p_from, p_subject):
        #creates a mime-message that will render as text
        if isinstance(p_html_content, unicode): p_html_content = p_html_content.encode('utf-8')
        if isinstance(p_text_content, unicode): p_text_content = p_text_content.encode('utf-8')
        if isinstance(p_subject, unicode): p_subject = p_subject.encode('utf-8')
        htmlin = cStringIO.StringIO(p_html_content)
        textin = cStringIO.StringIO(p_text_content)
        out = cStringIO.StringIO()
        writer = MimeWriter.MimeWriter(out)
        # set up some basic headers... we put subject here
        writer.addheader("From", p_from)
        writer.addheader("To", p_to)
        writer.addheader("Subject", p_subject)
        writer.addheader("Date", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        writer.addheader("MIME-Version", "1.0")
        # start the multipart section of the message
        writer.startmultipartbody("alternative")
        writer.flushheaders()
        # the plain text section
        subpart = writer.nextpart()
        subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
        pout = subpart.startbody("text/plain", [("charset", 'utf-8')])
        mimetools.encode(textin, pout, 'quoted-printable')
        textin.close()
        # the html subpart of the message
        subpart = writer.nextpart()
        subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
        pout = subpart.startbody("text/html", [("charset", 'utf-8')])
        mimetools.encode(htmlin, pout, 'quoted-printable')
        htmlin.close()
        #close your writer and return the message body
        writer.lastpart()
        msg = out.getvalue()
        out.close()
        return msg

    def __build_addresses(self, p_emails):
        #given a list of emails returns a valid string for an email address
        if type(p_emails) == type(''):
            return p_emails
        elif type(p_emails) == type([]):
            return '<%s>' % '>, <'.join(p_emails)

    #api
    security.declarePublic('sendFlashEmail')
    def sendFlashEmail(self, p_html_content, p_text_content, p_to, p_from, p_subject):
        """
        Sends flash email.
        """
        #process email parameters
        p_to = self.__build_addresses(p_to)
        l_body = self.__create_flash_email(p_html_content, p_text_content, p_to, p_from, p_subject)
        temp_path = join(MAILDROP_SPOOL, self.utGenerateUID())

        #generate email
        lock = open('%s.lck' % temp_path, 'w')
        lock.write('locked')
        lock.close()
        temp = open(temp_path, 'w')
        temp.write(FLASH_MAIL_TEMPLATE % (p_to, p_from, l_body))
        temp.close()
        unlink('%s.lck' % temp_path)

InitializeClass(MDH)