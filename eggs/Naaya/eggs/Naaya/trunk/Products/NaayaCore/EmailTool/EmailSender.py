import os
import os.path
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import email
import smtplib
import time
from threading import Thread, Lock
from sha import sha
from optparse import OptionParser

class EmailSenderThread(Thread):
    """
    This thread should be used if the current process
    should not be burdened with sending the emails.
    """
    active_ids = set()
    lock = Lock()

    def __init__(self, group_id, sender):
        Thread.__init__(self)

        self.group_id = group_id
        self.sender = sender

    def run(self):
        """ the thread main function """
        #don't run if a thread from the same group alredy running
        EmailSenderThread.lock.acquire()
        if self.group_id in EmailSenderThread.active_ids:
            EmailSenderThread.lock.release()
            return

        EmailSenderThread.active_ids.add(self.group_id)
        EmailSenderThread.lock.release()

        self.sender.send_emails()

        EmailSenderThread.lock.acquire()
        EmailSenderThread.active_ids.remove(self.group_id)
        EmailSenderThread.lock.release()


class EmailSender(object):
    """
    This is a command class to send the emails in a folder
    """
    def __init__(self, error_folder, folder, tmp_folder, smtp_host):
        self.error_folder = error_folder
        self.folder = folder
        self.tmp_folder = tmp_folder
        self.smtp_host = smtp_host
        self.mail_server = None

    def _open_smtp(self):
        self.mail_server = smtplib.SMTP(self.smtp_host)

    def _close_smtp(self):
        self.mail_server.quit()

    def send_emails(self):
        """ send all the emails in the folder """
        self._open_smtp()
        while True:
            file_name = self._get_email_file()
            if file_name is None:
                break

            tmp_path = os.path.join(self.tmp_folder, file_name)
            fd = open(tmp_path, 'r')
            email_content = fd.read()
            fd.close()

            try:
                self._send_email(email_content)
            except:
                self._error_onsend(file_name, email_content)

            self._finished_email(file_name)
        self._close_smtp()

    def _get_email_file(self):
        """ gets the email from the first file in the folder """
        file_names = os.listdir(self.folder)
        for file_name in file_names:
            file_path = os.path.join(self.folder, file_name)
            tmp_path = os.path.join(self.tmp_folder, file_name)

            try:
                os.rename(file_path, tmp_path)
            except:
                continue

            return file_name

        return None

    def _error_onsend(self, file_name, email_content):
        """ on error saves the file in the error_folder """
        error_path = os.path.join(self.error_folder, file_name)

        fd = open(error_path, 'w')
        fd.write(email_content)
        fd.close()

    def _finished_email(self, file_name):
        """ when finished removes the file """
        os.remove(os.path.join(self.tmp_folder, file_name))

    def _send_email(self, content):
        """ send the content as an email """
        from_addr, to_addrs = self._get_from_and_to_addrs(content)

        self.mail_server.sendmail(from_addr, to_addrs, content)

    def _get_from_and_to_addrs(self, content):
        """ get the from and to addresses from the content """
        msg = email.message_from_string(content)
        return msg['From'], msg['To']


def save_email(tmp_folder, sender_folder, email_content):
    """ saves the content to a file in the send folder """
    # generate file name as a checksum
    fname = sha(email_content).hexdigest()

    # save it in the tmp and then move it to send folder
    tmp_path = os.path.join(tmp_folder, fname)
    fd = open(tmp_path, 'w')
    fd.write(email_content)
    fd.close()

    send_path = os.path.join(sender_folder, fname)
    os.rename(tmp_path, send_path)

def build_email(from_addr, to_addrs, subject,
        text_content, html_content=None):
    """ creates a mime-message and returns it as a string """

    if isinstance(to_addrs, list):
        to_addrs = ', '.join(to_addrs)
    if isinstance(subject, unicode):
        subject = subject.encode('utf-8')
    if isinstance(html_content, unicode):
        html_content = html_content.encode('utf-8')
    if isinstance(text_content, unicode):
        text_content = text_content.encode('utf-8')

    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['To'] = to_addrs
    msg['Subject'] = subject
    msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
            time.gmtime())

    # the plain text section
    part1 = MIMEText(text_content, 'plain')
    msg.attach(part1)

    if html_content is not None:
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)

    #return the message content
    return msg.as_string()



def main():
    """ method called when running from command line """
    usage = "usage: %prog error_folder folder smtp_host"
    parser = OptionParser(usage=usage)
    options, args = parser.parse_args()
    if len(args) != 3:
        parser.error("incorrect number of arguments")
    esender = EmailSender(*args)
    esender.send_emails()


if __name__ == "__main__":
    main()
