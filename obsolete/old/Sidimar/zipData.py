from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from AccessControl.Permissions import view

class zipData:
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass

    security.declareProtected(view, 'make_zip')
    def make_zip(self, region='', monit='', campaign='', year='', info=0, REQUEST=None, RESPONSE=None):
        """ make a zip file """

        year = self.getSessionYear()
        reg = self.getSessionRegion()
        reg = reg.replace('Regione ', '')
        data = self.getSessionDataMonit()

        mysql_tool = self.getMySQLTool()

        #open connection
        conn = mysql_tool.createDbManager()


        if monit.strip() != 'P':
            #get instruments
            instruments, err = mysql_tool.get_instruments(monit, region, conn)
            if err: 
                return 0
            #get stations
            stations, err = mysql_tool.get_stations(year, region, monit, conn)
            if err: 
                return 0
        else:
            #get instruments
            instruments, err = mysql_tool.get_instruments_plancton(monit, region, conn)
            if err: 
                return 0
            #get stations
            stations, err = mysql_tool.get_plancton_stations(year, region, conn)
            if err: 
                return 0

        monit_exp = monit_pb = None
        #get the data monitored
        if monit.strip() != 'P':
            monit_exp, err = mysql_tool.get_monit_except_plancton(region, year, monit, campaign, conn)
        if monit.strip() == 'P' or monit.strip() == 'X':
            monit_pb, err = mysql_tool.get_monit_benthos_plancton(region, year, monit, campaign, conn)

        #close connection
        mysql_tool.destroyDbManager(conn)

        return self.zip_sql(campaign, reg, data, year, instruments, stations, monit_exp, monit_pb, info, REQUEST, RESPONSE)


    security.declareProtected(view, 'processIndex')
    def processIndex(self):
        """ get region, data monitored and year """

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get regions
        regions, err = mysql_tool.get_regions(dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored
        data,err = mysql_tool.get_data_monitored(dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #get years
        years, err = mysql_tool.get_years(dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)
        return (regions, data, years)


    security.declareProtected(view, 'processCampaign')
    def processCampaign(self, region='', monit='', year=''):
        """ get the campaign """

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get the region description
        reg_descr, err = mysql_tool.get_region_descr(region)
        if err:
            self.setSessionErrors(['Database error'])

        #get the data monitored description
        monit_descr, err = mysql_tool.get_data_monitored_descr(monit)
        if err:
            self.setSessionErrors(['Database error'])

        #set the session
        self.setDownloadInfo(mysql_tool.mp_region(reg_descr[0]), mysql_tool.mp_descrmonit(monit_descr[0]), year)

        #get the campaigns
        if monit.strip() != 'P':
            campaigns, err = mysql_tool.get_campaign(region, monit, year)
            if err:
                self.setSessionErrors(['Database error'])
        else:
            campaigns, err = mysql_tool.get_campaign_plancton(region, monit, year)
            if err:
                self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)
        return (region, campaigns)

InitializeClass(zipData)