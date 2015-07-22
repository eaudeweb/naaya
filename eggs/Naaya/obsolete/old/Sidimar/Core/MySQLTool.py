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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania


from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.managers.utils import utils

#product imports
from Products.Sidimar.constants import *
from Products.Sidimar.Core.DatabaseManager import DatabaseManager
from Products.Sidimar.Core.SQLStatements import *
from Products.Sidimar.Core.Mappings import Mappings

def manage_addMySQLTool(self, REQUEST=None):
    """ """
    ob = MySQLTool(MYSQLTOOL_ID, MYSQLTOOL_TITLE)
    self._setObject(MYSQLTOOL_ID, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class MySQLTool(SimpleItem, Mappings):
    """ """

    meta_type = MYSQLTOOL_METATYPE
    icon = 'misc_/Sidimar/MySQL.gif'


    security = ClassSecurityInfo()

    manage_options = (
        (
            {'label':'Properties', 'action':'manage_properties'},
        )
        +
        SimpleItem.manage_options
    )

    def __init__(self, id, title):
        self.id = id
        self.title = title
        #database stuff
        self.db_host = None
        self.db_name = None
        self.db_user = None
        self.db_password = None
        self.db_port = None
        Mappings.__dict__['__init__'](self)

    security.declarePrivate('save_dbconnection')
    def save_dbconnection(self, db_host, db_name, db_user, db_password, db_port):
        """Update database connection configuration"""
        try:    
            db_port = int(db_port)
        except: 
            pass
        #test connection
        err = DatabaseManager().testConnection(db_host, db_user, db_password, db_name, db_port)
        if err:
            raise Exception, err
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self._p_changed = 1

    security.declareProtected(view_management_screens, 'saveDbConnection')
    def saveDbConnection(self, db_host='', db_name='', db_user='', 
                db_password='', db_port=3306, REQUEST=None, RESPONSE=None):
        """ save the database connection parameters """
        self.save_dbconnection(db_host, db_name, db_user, db_password, db_port)
        return RESPONSE.redirect(REQUEST.HTTP_REFERER)


    #xxx
    def createDbManager(self):
        """ create a new connection to MySQL"""
        try:
            db = DatabaseManager()
            db.openConnection(self)
            return db
        except:
            return None

    #xxx
    def destroyDbManager(self, db):
        """ destroy the MySQL connection """
        try:
            db.closeConnection()
            db = None
        except:
            pass

    security.declarePrivate('get_regions')
    def get_regions(self, conn=None):
        """ get regions """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_regions())

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_campaigns')
    def get_campaigns(self, conn=None):
        """ get campaigns """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_campaigns())

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_region_descr')
    def get_region_descr(self, id, conn=None):
        """ get regions """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_region_by_id(id))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_station_descr')
    def get_station_descr(self, id, region, conn=None):
        """ get station description """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_station_by_id(id, region))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_data_monitored')
    def get_data_monitored(self, conn=None):
        """ get data monitored """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_data_monitored())

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_data_monitored_descr')
    def get_data_monitored_descr(self, monit, conn=None):
        """ get data monitored """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_data_monitored_by_id(monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_years')
    def get_years(self, conn=None):
        """ get years """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_years())

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_campaign')
    def get_campaign(self, region, monit, year, conn=None):
        """ get campaign """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_campaign(region, monit, year))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_campaign_plancton')
    def get_campaign_plancton(self, region, monit, year, conn=None):
        """ get campaign """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_campaign_plancton(region, monit, year))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_instruments')
    def get_instruments(self, monit, region, conn=None):
        """ get instruments """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_instruments(monit, region))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_instruments_plancton')
    def get_instruments_plancton(self, monit, region, conn=None):
        """ get instruments """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_instruments_plancton(monit, region))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_stations')
    def get_stations(self, year, cod, monit, conn=None):
        """ get stations """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_stations(year, cod, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_plancton_stations')
    def get_plancton_stations(self, year, cod, conn=None):
        """ get stations """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_stations_plancton(year, cod))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_monit_except_plancton')
    def get_monit_except_plancton(self, region, year, monit, campaign, conn=None):
        """ get the data monitored except for plancton """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_monit_except_plancton(region, year, monit, campaign))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_monit_benthos_plancton')
    def get_monit_benthos_plancton(self, region, year, monit, campaign, conn=None):
        """ get the data monitored except for plancton """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_get_monit_benthos_plancton(region, year, monit, campaign))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('gis_stations')
    def gis_stations(self, minx, maxx, miny, maxy, year, campag, monit, conn=None):
        """ get stations """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.rpc_query(sql_gis_stations_interval(minx, miny, maxx, maxy, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('gis_stations_monit')
    def gis_stations_monit(self, minx, maxx, miny, maxy, year, monit, campag, conn=None):
        """ get stations """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.rpc_query(sql_gis_stations_monit(minx, maxx, miny, maxy, year, monit, campag))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_water_info')
    def get_water_info(self, station, region, year, campag, monit, conn=None):
        """ get water information """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_water_info(station, region, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_water_scale_info')
    def get_water_scale_info(self, region, year, campag, monit, conn=None):
        """ get water scale information """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_water_scale_info(region, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_water_data')
    def get_water_data(self, year, campaign, region, conn=None):
        """ get all the water data monitored by year and campaign """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        if region:
            err, res, msg = conn.query(sql_get_region_waterdata_monitored(year, campaign, region))
        else:
            err, res, msg = conn.query(sql_get_waterdata_monitored(year, campaign))
        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_last_campaign_water')
    def get_last_campaign_water(self, conn=None):
        """ get the last campaign for water data"""
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.rpc_query(sql_last_campaign_water())

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_stations_plancton')
    def get_stations_plancton(self, minx, maxx, miny, maxy, year, campag, conn=None):
        """ get the stations for plancton """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.rpc_query(sql_gis_stations_plancton(minx, maxx, miny, maxy, year, campag))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    security.declarePrivate('get_station_info')
    def get_station_info(self, station, region, year, campag, monit, conn=None):
        """ get stations related information """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_station_info(station, region, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declareProtected(view_management_screens, 'manage_properties')
    manage_properties = PageTemplateFile('zpt/mysql_properties', globals())


    #------------SEDIMENTS --------------------#
    security.declarePrivate('get_sediments_data')
    def get_sediments_data(self, region, year, campag, monit, conn=None):
        """ get the sediments data """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_sediments_data(region, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    #------------MOLLUSCHI --------------------#
    security.declarePrivate('get_molluschi_data')
    def get_molluschi_data(self, region, year, campag, monit, conn=None):
        """ get the molluschi data """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_molluschi_data(region, year, campag, monit))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    #------------PLANCTON --------------------#
    security.declarePrivate('get_plancton_data')
    def get_plancton_data(self, region, year, campag, monit, station, conn=None):
        """ get the plancton data """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_plancton_data(region, year, campag, monit, station))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


    #------------BENTHOS --------------------#
    security.declarePrivate('get_benthos_data')
    def get_benthos_data(self, region, year, campag, monit, station, conn=None):
        """ get the benthos data """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_benthos_data(region, year, campag, monit, station))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)

    security.declarePrivate('get_anual_indices')
    def get_anual_indices(self, region, year, conn=None):
        """ get the sediments data """
        destroy = 0
        if conn is None:
            conn = self.createDbManager()
            destroy = 1

        err, res, msg = conn.query(sql_anual_indices(region, year))

        if destroy: self.destroyDbManager(conn)
        if err:
            return ({}, 1)
        return (res, 0)


InitializeClass(MySQLTool)