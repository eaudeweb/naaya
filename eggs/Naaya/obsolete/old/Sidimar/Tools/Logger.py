import time
from Products.Sidimar.constants import *

class Logger:
    """ Logger class """

    def __init__(self):
        self.log = ""
        self.date = ""
        self.type = ""

    def get_curr_date(self):
        return time.ctime(time.time())

    def log_credentials(self, user):
        self.log = LOG_UPDATE_USER % user
        self.date = self.get_curr_date()

    def log_activate(self, user):
        self.log = LOG_ACTIVATE_USER % user
        self.date = self.get_curr_date()

    def log_deactivate(self, user):
        self.log = LOG_DEACTIVATE_USER % user
        self.date = self.get_curr_date()

    def log_create(self, user):
        self.log = LOG_CREATE_USER % user
        self.date = self.get_curr_date()

    def log_delete(self, user):
        self.log = LOG_DELETE_USER % user
        self.date = self.get_curr_date()

    def log_delete_pending(self, email):
        self.log = LOG_DELETE_PENDING % email
        self.date = self.get_curr_date()

    def log_user_credentials(self):
        self.log = LOG_CHG_CRED
        self.date = self.get_curr_date()

    def log_user_password(self):
        self.log = LOG_CHG_PASS
        self.date = self.get_curr_date()


class LogInfo:
    """ """

    def __init__(self, region, campaign, year, downloads, monitor):
        self.region = region
        self.campaign = campaign
        self.year = year
        self.downloads = downloads
        self.monitor = monitor
        self.date = self.get_curr_date()

    def get_curr_date(self):
        return time.ctime(time.time())