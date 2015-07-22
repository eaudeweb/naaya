from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class gisRPC:
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass


    security.declarePublic('getStations')
    def getStations(self, year, campag, monit, minx, maxx, miny, maxy, REQUEST=None, RESPONSE=None):
        """ """
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get stations
        stations, err = mysql_tool.gis_stations(minx, maxx, miny, maxy, year, campag, monit, dbconn)

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        if not err:
            return stations


    security.declarePublic('getStationsMonit')
    def getStationsMonit(self, year, campag, monit, minx, maxx, miny, maxy, REQUEST=None, RESPONSE=None):
        """ """
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get stations
        stations, err = mysql_tool.gis_stations_monit(minx, maxx, miny, maxy, year, monit, campag, dbconn)

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        if not err:
            return stations


    security.declarePublic('getLastCampaignWater')
    def getLastCampaignWater(self, REQUEST=None, RESPONSE=None):
        """ """
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get stations
        water_data, err = mysql_tool.get_last_campaign_water(dbconn)

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        if not err:
            return water_data


    security.declarePublic('getStationsPlancton')
    def getStationsPlancton(self, minx, maxx, miny, maxy, year, campag, REQUEST=None, RESPONSE=None):
        """ """
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get stations
        water_data, err = mysql_tool.get_stations_plancton(minx, maxx, miny, maxy, year, campag, dbconn)

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        if not err:
            return water_data

    def test_plancton(self):
        """ """
        return self.getStationsPlancton('308909.631250', '4127902.550000', '1318880.131250', '5137873.050000', '2005', '04A')
InitializeClass(gisRPC)