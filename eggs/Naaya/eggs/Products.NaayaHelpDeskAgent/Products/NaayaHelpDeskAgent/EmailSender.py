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
# The Original Code is HelpDeskAgent version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Dragos Chirila, Finsiel Romania

import smtplib
import time
import MimeWriter
import mimetools
import cStringIO

class EmailSender:
    """ Email Engine
        - sends emails using smtplib
        - doesn't use any MailHost object from Zope
        - HelpDesk class extends this one
        - variables 'mail_server_name' and 'mail_server_port' are properties of HelpDesk object
    """

    def __init__(self):
        """constructor"""

    def SendEmail(self, eContent, eTo, eFrom, eSubject):
        """Sends an email"""
        #Uncomment following lines for debug
        #print '\n--------------------\n'
        #print 'from: ' + str(eFrom)
        #print 'to: ' + str(eTo)
        #print 'subject: ' + str(eSubject)
        #print 'content: ' + str(eContent)
        #print '\n--------------------\n'
        try:
            eTo = self.CreateToList(eTo)
            message = self.CreateEmail(eContent, eFrom, eTo, eSubject)
            server = smtplib.SMTP(self.mail_server_name, self.mail_server_port)
            server.sendmail(eFrom, eTo, message)
            server.quit()
            return 1
        except:
            return 0

    def CreateEmail(self, eContent, eFrom, eTo, eSubject):
        """Create a mime-message that will render as text"""
        out = cStringIO.StringIO() # output buffer for our message
        writer = MimeWriter.MimeWriter(out)
        # set up some basic headers
        writer.addheader("From", eFrom)
        writer.addheader("To", ','.join(eTo))
        writer.addheader("Date", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        writer.addheader("Subject", eSubject)
        writer.addheader("MIME-Version", "1.0")
        # start the multipart section of the message
        writer.startmultipartbody("alternative")
        writer.flushheaders()
        # the plain text section
        subpart = writer.nextpart()
        pout = subpart.startbody("text/plain", [("charset", 'iso-8859-1')])
        pout.write(eContent)
        #close your writer and return the message body
        writer.lastpart()
        msg = out.getvalue()
        out.close()
        return msg

    def CreateToList(self, eTo):
        """eTo is a dictionary {'email1':'', ..., 'emailn':''}
            and we'll build something like [<email1>, ..., <emailn>]"""
        listTo = []
        for email in eTo.keys():
            listTo.append('<' + email + '>')
        return listTo