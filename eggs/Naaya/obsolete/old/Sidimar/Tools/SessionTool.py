from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

class SessionTool:

    security = ClassSecurityInfo()


    #SESSION related functions
    security.declareProtected(view, 'setUserSession')
    def setUserSession(self, name, password, roles, firstname, lastname, job, organisation, country, street, 
            street_number, zip, city, region, phone, mail, note):
        """ put the user information on session """
        self.setSession('name', name)
        self.setSession('password1' , password)
        self.setSession('roles', roles)
        self.setSession('firstname', firstname)
        self.setSession('lastname', lastname)
        self.setSession('job', job)
        self.setSession('organisation', organisation)
        self.setSession('country', country)
        self.setSession('street', street)
        self.setSession('street_number', street_number)
        self.setSession('zip', zip)
        self.setSession('city', city)
        self.setSession('region', region)
        self.setSession('phone', phone)
        self.setSession('mail', mail)
        self.setSession('note', note)

    security.declareProtected(view, 'delUserSession')
    def delUserSession(self):
        """ delete user information from session """
        self.delSession('name')
        self.delSession('password1')
        self.delSession('roles')
        self.delSession('firstname')
        self.delSession('lastname')
        self.delSession('job')
        self.delSession('organisation')
        self.delSession('country')
        self.delSession('street')
        self.delSession('street_number')
        self.delSession('zip')
        self.delSession('city')
        self.delSession('region')
        self.delSession('phone')
        self.delSession('mail')
        self.delSession('note')

    def setRecords(self, records):
        """ put the records data on session """
        self.setSession('records', records)

    def delRecords(self):
        """ delete the records data drom sesssion """
        self.delSession('records')

    def hasRecords(self):
        """ check if there are records on session """
        return self.isSession('records')

    def hasScale(self):
        """ check if there are records on session """
        return self.isSession('scale')

    def setScale(self, scale):
        """ put the scale data on session """
        self.setSession('scale', scale)

    def delScale(self):
        """ delete the scale data drom sesssion """
        self.delSession('scale')

    def setDownloadInfo(self, region, monit, year):
        """ put the download data on session """
        self.setSession('region', region)
        self.setSession('monit', monit)
        self.setSession('year', year)

    def delDownloadInfo(self):
        """ put the download data on session """
        self.delSession('region')
        self.delSession('monit')
        self.delSession('year')

    def getSessionScale(self, default=''):
        return self.getSession('scale', default)

    def getSessionRecords(self, default=''):
        return self.getSession('records', default)

    def getSessionRegion(self, default=''):
        return self.getSession('region', default)

    def getSessionDataMonit(self, default=''):
        return self.getSession('monit', default)

    def getSessionYear(self, default=''):
        return self.getSession('year', default)

    security.declareProtected(view, 'getSessionUserAccount')
    def getSessionUserAccount(self, default=''):
        return self.getSession('name', default)

    security.declareProtected(view, 'getSessionUserPassword')
    def getSessionUserPassword(self, default=''):
        return self.getSession('password1', default)

    security.declareProtected(view, 'getSessionUserRoles')
    def getSessionUserRoles(self, default=''):
        return self.getSession('roles', default)

    security.declareProtected(view, 'getSessionUserFirstName')
    def getSessionUserFirstName(self, default=''):
        return self.getSession('firstname', default)

    security.declareProtected(view, 'getSessionUserLastName')
    def getSessionUserLastName(self, default=''):
        return self.getSession('lastname', default)

    security.declareProtected(view, 'getSessionJob')
    def getSessionJob(self, default=''):
        return self.getSession('job', default)

    security.declareProtected(view, 'getSessionOrganisation')
    def getSessionOrganisation(self, default=''):
        return self.getSession('organisation', default)

    security.declareProtected(view, 'getSessionCountry')
    def getSessionCountry(self, default=''):
        return self.getSession('country', default)

    security.declareProtected(view, 'getSessionStreet')
    def getSessionStreet(self, default=''):
        return self.getSession('street', default)

    security.declareProtected(view, 'getSessionStreetNumber')
    def getSessionStreetNumber(self, default=''):
        return self.getSession('street_number', default)

    security.declareProtected(view, 'getSessionZIP')
    def getSessionZIP(self, default=''):
        return self.getSession('zip', default)

    security.declareProtected(view, 'getSessionCity')
    def getSessionCity(self, default=''):
        return self.getSession('city', default)

    security.declareProtected(view, 'getSessionRegion')
    def getSessionRegion(self, default=''):
        return self.getSession('region', default)

    security.declareProtected(view, 'getSessionPhone')
    def getSessionPhone(self, default=''):
        return self.getSession('phone', default)

    security.declareProtected(view, 'getSessionEmail')
    def getSessionEmail(self, default=''):
        return self.getSession('mail', default)

    security.declareProtected(view, 'getSessionNote')
    def getSessionNote(self, default=''):
        return self.getSession('note', default)

InitializeClass(SessionTool)