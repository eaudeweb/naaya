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
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view, manage_users

#Naaya imports
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.Naaya.managers.skel_parser import skel_parser

#Product imports
from Products.Sidimar.constants import *
from Products.Sidimar.Tools.UsersTool import manage_addUsersTool
from Products.Sidimar.Core.MySQLTool import manage_addMySQLTool
from Products.Sidimar.Core.ZipSQL import ZipSQL
from Products.Sidimar.Tools.NotifTool import NotifTool
from Products.Sidimar.Tools.SessionTool import SessionTool
from Products.Sidimar.Tools.Logger import Logger
from Products.Sidimar.gisRPC import gisRPC
from Products.Sidimar.zipData import zipData
from Products.Sidimar.gisResults import gisResults

manage_addSidimarSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addSidimarSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, SidimarSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class SidimarSite(SessionTool, NySite, NotifTool, ZipSQL, gisRPC, zipData, gisResults):
    """ """

    meta_type = METATYPE_SIDIMARSITE
    icon = 'misc_/Sidimar/Site.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        self.predefined_latest_uploads = []
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)
        ZipSQL.__dict__['__init__'](self)
        gisRPC.__dict__['__init__'](self)
        zipData.__dict__['__init__'](self)
        gisResults.__dict__['__init__'](self)

    def update(self, REQUEST=None):
        """ """
        #update the registration form
        register = self.futRead(join(SIDIMAR_PRODUCT_PATH, 'skel', 'forms', 'site_register.zpt'), 'r')
        formstool_ob = self.getFormsTool()
        register_ob = formstool_ob._getOb('site_register', None)
        if register_ob is not None:
            register_ob.pt_edit(text=register, content_type='')

        #update the reflists
        portletstool_ob = self.getPortletsTool()
        skel_handler, error = skel_parser().parse(self.futRead(join(SIDIMAR_PRODUCT_PATH, 'skel', 'skel.xml'), 'r'))
        if skel_handler is not None:
            for reflist in skel_handler.root.portlets.reflists:
                reflist_ob = portletstool_ob._getOb(reflist.id, None)
                if reflist_ob is None:
                    portletstool_ob.manage_addRefList(reflist.id, reflist.title, reflist.description)
                    reflist_ob = portletstool_ob._getOb(reflist.id)
                else:
                    reflist_ob.manage_delete_items(reflist_ob.get_collection().keys())
                for item in reflist.items:
                    reflist_ob.add_item(item.id, item.title)


    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)
        self.manage_delObjects('acl_users')
        manage_addUsersTool(self)
        manage_addMySQLTool(self)
        self.loadSkeleton(join(SIDIMAR_PRODUCT_PATH, 'skel'))
        download_private = self._getOb('download')
        download_private.setRestrictions('', 'Contributor')
        gen_graphs_private = self._getOb('gen_graphs')
        gen_graphs_private.setRestrictions('', 'Authenticated')


    def get_data_path(self):
        """ """
        return SIDIMAR_PRODUCT_PATH

    def getUsersTool(self): return self._getOb(USERSTOOL_ID)
    def getMySQLTool(self): return self._getOb(MYSQLTOOL_ID)

    security.declarePublic('getCountries')
    def getCountries(self):
        return self.getPortletsTool().getRefListById('countries').get_list()

    security.declarePublic('getCountryById')
    def getCountryById(self, id):
        countries = self.getPortletsTool().getRefListById('countries').get_list()
        for country in countries:
            if id == country.id:
                return country.title

    security.declarePublic('getRegions')
    def getRegions(self):
        return self.getPortletsTool().getRefListById('regions').get_list()

    security.declarePublic('getRegionsById')
    def getRegionsById(self, id):
        regions = self.getPortletsTool().getRefListById('regions').get_list()
        for region in regions:
            if id == region.id:
                return region.title

    security.declarePublic('checkParam')
    def checkParam(self, param):
        station, region, year, campag, monit = param.split(',')
        if station=='null' or region=='null' or year=='null' or campag=='null' or monit=='null':
            return 0
        else:
            return 1

    ##############
    #user related#
    ##############

    security.declarePublic('change_password')
    def change_password(self, user='', opass='', npass='', cpass='', REQUEST=None, RESPONSE=None):
        """ change user password """
        msg = err = ''
        users_tool = self.getUsersTool()
        try:
            users_tool.change_user_password(user, opass, npass, cpass)
        except Exception, error:
            err = error
        else:
            auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
            if auth_user is not None:
                log = Logger()
                log.log_user_password()
                users_tool.change_log(auth_user, log)
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                #save form data to session
                self.setUserSession(user, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
                #save error to session
                self.setSessionErrors([err])
                RESPONSE.redirect('%s/user_pwd_html' % self.absolute_url())
            if msg != '':
                self.setSessionInfo([msg])
                RESPONSE.redirect('%s/user_pwd_html' % self.absolute_url())

    security.declarePublic('change_user_prefs')
    def change_user_prefs(self, user='', roles='', firstname='', lastname='', job='', 
        organisation='', country='', street='', street_number='', zip='', city='', 
        region='', phone='', mail='', REQUEST=None, RESPONSE=None):
        """ change user preferences """
        msg = err = ''
        users_tool = self.getUsersTool()
        try:
            users_tool.change_user_preferences(user, roles, firstname, lastname, job, 
                organisation, country, street, street_number, zip, city, region, phone, mail)
        except Exception, error:
            err = error
        else:
            auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
            if auth_user is not None:
                log = Logger()
                log.log_user_credentials()
                users_tool.change_log(auth_user, log)
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                #save form data to session
                self.setUserSession(user, '', roles, firstname, lastname, job, organisation, 
                    country, street, street_number, zip, city, region, phone, mail, '')
                #save error to session
                self.setSessionErrors([err])
                RESPONSE.redirect('%s/user_prefs_html' % self.absolute_url())
            if msg != '':
                self.setSessionInfo([msg])
                RESPONSE.redirect('%s/user_prefs_html' % self.absolute_url())

    security.declarePublic('send_password')
    def send_password(self, email='', REQUEST=None, RESPONSE=None):
        """ send the forgotten passsword """
        msg = err = ''
        try:
            account, pwd, fname, lname = self.getUsersTool().retrieve_password(email)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                RESPONSE.redirect('%s/forgot_password_html' % self.absolute_url())
            if msg != '':
                self.sendPassword(email, account, pwd, fname, lname)
                RESPONSE.redirect('%s/forgot_password_html?save=ok' % self.absolute_url())

    ###############
    #admin related#
    ###############

    security.declarePublic('register_user')
    def register_user(self, firstname='', lastname='', job='', organisation='', 
        country='', street='', street_number='', zip='', city='', region='', phone='', 
        mail='', note='', download=0, privacy=0, REQUEST=None, RESPONSE=None):
        """ register a new user in the portal """
        msg = err = ''
        id = self.utGenRandomId(6)
        try:
            self.getUsersTool().addFakeUser(id, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()  #xxx
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                self.setUserSession('', '', '', firstname, lastname, job, organisation, 
                    country, street, street_number, zip, city, region, phone, mail, note)
                RESPONSE.redirect('%s/register_html' % self.absolute_url())
            if msg != '':
                #send the email xxx
                countries = self.getCountries()
                country = self.getCountryById(country)
                regions = self.getRegions()
                region = self.getRegionsById(region)
                if self.administrator_email:
                    self.sendRegistrationEmail(self.administrator_email, id, firstname, lastname, country, 
                        street, street_number, zip, city, region, mail, job, organisation, phone)
                self.setSessionInfo([msg])  #xxx
                RESPONSE.redirect('%s/info_html' % self.absolute_url())

    security.declareProtected(manage_users, 'activate_user')
    def activate_user(self, username='', passwd='', roles=[], email='', id='', REQUEST=None, RESPONSE=None):
        """ """
        msg = err = ''
        users_tool = self.getUsersTool()
        if REQUEST.has_key('ActivButton'):
            try:
                users_tool.user_activate(username, passwd, roles, id)
            except Exception, error:
                err = error
            else:
                auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
                if auth_user is not None:
                    log = Logger()
                    log.log_activate(username)
                    users_tool.change_log(auth_user, log)
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
            if REQUEST:
                if err != '':
                    self.setSessionErrors([err])
                    self.setUserSession(username, passwd, roles, '', '', '', '', '', '', '', '', '', '', '', '', '')
                    RESPONSE.redirect(REQUEST.HTTP_REFERER)
                if msg != '':
                    #send email
                    self.sendConfirmationEmail(email, username, passwd, roles)
                    self.setSessionInfo([msg])  #xxx
                    self.delUserSession()
                    RESPONSE.redirect('%s/admin_pending_html' % self.absolute_url())
        if REQUEST.has_key('GenButton'):
            ut = utils()
            pswd = ut.utGenRandomId(4)
            self.setUserSession(username, pswd, roles, '', '', '', '', '', '', '', '', '', '', '', '', '')
            RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(manage_users, 'admin_deletepending')
    def admin_deletepending(self, ids=[], REQUEST=None, RESPONSE=None):
        """ """
        msg = err = ''
        try:
            self.getUsersTool().del_pending_users(ids)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                RESPONSE.redirect('%s/admin_pending_html' % self.absolute_url())
            if msg != '':
                self.setSessionInfo([msg])
                RESPONSE.redirect('%s/admin_pending_html' % self.absolute_url())

    security.declareProtected(manage_users, 'admin_edituser')
    def admin_edituser(self, name='', firstname='', lastname='', mail='', job='', organisation='', country='', 
        street='', street_number='', zip='', city='', region='', phone='', roles=[], REQUEST=None, RESPONSE=None):
        """ change user information """
        msg = err = ''
        users_tool = self.getUsersTool()
        try:
            users_tool.change_user_preferences(name, roles, firstname, lastname, job, organisation, 
                country, street, street_number, zip, city, region, phone, mail)
        except Exception, error:
            err = error
        else:
            auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
            if auth_user is not None:
                log = Logger()
                log.log_credentials(name)
                users_tool.change_log(auth_user, log)
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                self.setUserSession(name, '', roles, firstname, lastname, job, organisation, 
                    country, street, street_number, zip, city, region, phone, mail, '')
            if msg != '':
                self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/admin_edituser_html?name=%s' % (self.absolute_url(), name))

    security.declareProtected(manage_users, 'admin_adduser')
    def admin_adduser(self, username='', passwd='', firstname='', lastname='', mail='', job='', organisation='', country='', 
        street='', street_number='', zip='', city='', region='', phone='', roles=[], REQUEST=None, RESPONSE=None):
        """ """
        msg = err = ''
        users_tool = self.getUsersTool()
        if REQUEST.has_key('SaveButton'):
            try:
                users_tool.add_user(username, passwd, roles, firstname, lastname, job, organisation,
                    country, street, street_number, zip, city, region, phone, mail)
            except Exception, error:
                err = error
            else:
                auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
                if auth_user is not None:
                    log = Logger()
                    log.log_create(username)
                    users_tool.change_log(auth_user, log)
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
            if REQUEST:
                if err != '':
                    self.setSessionErrors([err])
                    self.setUserSession(username, '', roles, firstname, lastname, job, organisation, 
                        country, street, street_number, zip, city, region, phone, mail, '')
                    RESPONSE.redirect('%s/admin_adduser_html' % self.absolute_url())
                if msg != '':
                    self.setSessionInfo([msg])
                    RESPONSE.redirect('%s/admin_users_html' % self.absolute_url())
        if REQUEST.has_key('GenButton'):
            ut = utils()
            pswd = ut.utGenRandomId(4)
            self.setUserSession(username, pswd, roles, firstname, lastname, job, organisation, 
                        country, street, street_number, zip, city, region, phone, mail, '')
            RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(manage_users, 'admin_deleteusers')
    def admin_deleteusers(self, names=[], REQUEST=None, RESPONSE=None):
        """ delete or invalidate a list of users """
        names = self.utConvertToList(names)
        if REQUEST.has_key('DeleteButton'):
            users_tool = self.getUsersTool()
            try:
                users_tool.manage_delUsers(names)
            except Exception, error:
                return error
            else:
                auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
                if auth_user is not None:
                    log = Logger()
                    for name in names:
                        log.log_delete(name)
                        users_tool.change_log(auth_user, log)
        if REQUEST.has_key('DeactivateButton'):
            users_tool = self.getUsersTool()
            try:
                for u in [ users_tool.getUser(n) for n in names ]:
                    mail = users_tool.getUserEmail(u)
                    firstname = users_tool.getUserFirstName(u)
                    lastname = users_tool.getUserLastName(u)
                    self.sendDeactivateEmail(mail, firstname, lastname, n)
                users_tool.user_deactivate(names)
            except Exception, error:
                return error
            else:
                auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
                if auth_user is not None:
                    log = Logger()
                    for name in names:
                        log.log_deactivate(name)
                        users_tool.change_log(auth_user, log)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_users_html' % self.absolute_url())


    def update_users(self, REQUEST=None, RESPONSE=None):
        """ """
        site = self.getSite()
        skel_path = join(site.get_data_path(), 'skel')
        formstool_ob = site.getFormsTool()
        #site_admin_adduser.zpt
        content = self.futRead(join(skel_path, 'forms', 'site_admin_adduser.zpt'), 'r')
        formstool_ob._getOb('site_admin_adduser').pt_edit(text=content, content_type='')

        #site_admin_edituser.zpt
        content = self.futRead(join(skel_path, 'forms', 'site_admin_edituser.zpt'), 'r')
        formstool_ob._getOb('site_admin_edituser').pt_edit(text=content, content_type='')

        #site_admin_pendinguser.zpt
        content = self.futRead(join(skel_path, 'forms', 'site_admin_pendinguser.zpt'), 'r')
        formstool_ob._getOb('site_admin_pendinguser').pt_edit(text=content, content_type='')

        #site_admin_user.zpt
        content = self.futRead(join(skel_path, 'forms', 'site_admin_user.zpt'), 'r')
        formstool_ob._getOb('site_admin_user').pt_edit(text=content, content_type='')

        #site_user_preferences.zpt
        content = self.futRead(join(skel_path, 'forms', 'site_user_preferences.zpt'), 'r')
        formstool_ob._getOb('site_user_preferences').pt_edit(text=content, content_type='')
        return "Update users was successfully"

    def update_02022006(self, REQUEST=None, RESPONSE=None):
        """ """
        site = self.getSite()
        graphs_ob = getattr(site, 'gen_graphs')
        #show graphs
        content = """<span tal:replace="structure here/standard_html_header" />

<tal:block define="mysql_tool here/getMySQLTool;
					region python:request.get('region', '');
					campaign python:request.get('campaign', '');
					year python:request.get('year', '');
					s python:here.createGraphs(region, year, campaign);
					graphs python:here.showGraphs(region, year, campaign)">


<p>Selected parameters:</p>
<table class="horizontal_table" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:1em">
	<tr>
		<th i18n:translate="">Region:</th> <td tal:content="region" />
	</tr>
	<tr>
		<th i18n:translate="">Monitored data:</th> <td>Water</td>
	</tr>
	<tr>
		<th i18n:translate="">Campaign:</th> <td tal:content="campaign" />
	</tr>
	<tr>
		<th i18n:translate="">Year:</th> <td tal:content="year" />
	</tr>
</table>

<table cellpadding="5" cellspacing="7" tal:condition="python:len(graphs)>0">
	<tr tal:repeat="graph_url graphs">
		<td tal:condition="python:len(graph_url)>0">
			<strong i18n:translate="">Station: <span tal:replace="python:graph_url[0].station" /></strong><br />
			<strong i18n:translate="">Data monitored: <span tal:replace="python:graph_url[0].monitor" /></strong><br />
			<img tal:attributes="src python:graph_url[0].absolute_url()" />
		</td>
		<td tal:condition="python:len(graph_url)>1">
			<strong i18n:translate="">Station: <span tal:replace="python:graph_url[1].station" /></strong><br />
			<strong i18n:translate="">Data monitored: <span tal:replace="python:graph_url[1].monitor" /></strong><br />
			<img tal:attributes="src python:graph_url[1].absolute_url()" />
		</td>
	</tr>
</table>

<span tal:condition="python:len(graphs)==0" i18n:translate="">No data available</span>

</tal:block>
<span tal:content="here/delSessionErrors" tal:omit-tag=""></span>
<span tal:replace="structure here/standard_html_footer"/>"""
        graphs_ob._getOb('show_graphs').pt_edit(text=content, content_type='')

        #results_html
        map_ob = getattr(site, 'map')
        content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	tal:attributes="xml:lang here/gl_get_selected_language; lang here/gl_get_selected_language">
<head tal:define="layout_tool here/getLayoutTool">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Scheda Stazione</title>
	<link tal:attributes="href string:${layout_tool/getSkinFilesPath}/style" rel="stylesheet" type="text/css" />
	<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_common" />
	<link rel="stylesheet" type="text/css" media="print" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_print" />
	<link rel="stylesheet" type="text/css" media="handheld" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_handheld" />
</head>

<body style="background-image: none; background-color: white;">

<tal:block define="param python:request.get('param', '')">
<tal:block condition="python:param !=''">
<div id="includes_tables"
	tal:define="results python:here.getWaterInfo(param);
	info python:results[0];
	stat_descr python:results[1];
	reg_descr python:results[2];
	data_descr python:results[3];
	year python:results[4];
	campag python:results[5];
	monit python:results[6];
	station python:results[7];
	region python:results[8];
	station_data python:results[9]">

<!-- Water -->

<tal:block condition="python:monit=='W'">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table" i18n:translate="">Tipologia Punto di prelievo</td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])" />
</tr>
<tr>
	<th i18n:translate="">Stazione</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Fornitore</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Anno</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campagna</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Localit&agrave;</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
<tal:block condition="python:len(station_data) > 0">
<tr>
	<th i18n:translate="">Tipo stazione</th>
	<td tal:content="python:here.mp_tipo_staz(station_data[0])" />
</tr>
<tr>
	<th i18n:translate="">Prof. tot</th>
	<td tal:content="python:here.mp_prof_tot(station_data[0])" />
</tr>
<tr>
	<th i18n:translate="">Indice qual.amb.marino</th>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 1.0">alta qualit&agrave;</td>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 2.0">media qualit&agrave;</td>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 3.0">bassa qualit&agrave;</td>
</tr>
<tr>
	<th i18n:translate="">Indice annuale</th>
	<td><a tal:attributes="href string:indices_html?param=${param}" target="_blank"> Andamento annuale
	qualit&agrave; <span tal:content="python:here.mp_region(reg_descr[0])"/></a></td>
</tr>
<tr>
	<th i18n:translate="">Grafici altre stazioni</th>
	<td><a tal:attributes="href string:stations_html?param=${param}" target="_blank">Grafici
	altre stazioni della <span tal:content="python:here.mp_region(reg_descr[0])"/></a></td>
</tr>
<tr>
	<td id="left_values"><div id="chart_legend"><span i18n:translate="">Legend</span><br />
	<img src="misc_/Sidimar/legenda.gif" alt="Legend" /><br />
	Le scale del grafico sono state scelte sulla base dei valori minimi e massimi
	riscontrati per la regione nella campagna monitorata</div>
	</td>
	<tal:block define="graph python:here.getGraph(region, year, campag, station)">
	<td id="chart" tal:condition="python:graph != 0">
	<img tal:attributes="src python:graph.absolute_url()" alt="graphic_results" border="1" />
	</td>
	<td id="chart" tal:condition="python:graph == 0" i18n:translate="">No graph available</td>
	</tal:block>
</tr>
</tal:block>
</table>
<hr />

<tal:block condition="python:len(station_data) > 0">
<p class="text_title" i18n:translate="">Parametri per la Classificazione delle Acque Marine</p>

<table cellspacing="3" class="table_indicators">
<tr tal:repeat="i info">
	<th tal:content="python:here.mp_descrmonit(i)" />
	<td class="numeric_values" tal:content="python:here.mp_valore(i)"/>
</tr>
</table>

<p class="italic_notes" i18n:translate="">(*) Se la trasparenza ha valore di 55 il disco secchi ha toccato il fondo</p>
<br />
<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp" target="_blank">Indicazioni
sui parametri indagati nel Programma di monitoraggio</a></p>
<br />
</tal:block>

<p tal:condition="python:len(station_data) == 0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

</tal:block>

<!-- Sedimenti -->

<tal:block condition="python:monit=='S'">
	<tal:block define="result python:here.createSedimentiCharts(param);
				stat_descr python:result[0];
				reg_descr python:result[1];
				data_descr python:result[2];
				station python:result[3];
				tuples python:result[4];
				granulometria python:result[5];
				granulometria_legend python:result[6];
				compostiorganoclorurati python:result[7];
				compostiorganoclorurati_legend python:result[8];
				policlorobifenili python:result[9];
				policlorobifenili_legend python:result[10];
				idrocarburi python:result[11];
				idrocarburi_legend python:result[12];
				others python:result[13]">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table">Tipologia Punto di prelievo</td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Year</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp">Indicazioni sui parametri indagati nel Programma di monitoraggio</a>
</p>

<table border="1" cellspacing="2" class="table_indicators_images">
<tr tal:repeat="tuple tuples">
	<td>
		<div>
			<img tal:attributes="src python:tuple[0].absolute_url(); alt python:tuple[0].title_or_id()" /><img tal:condition="python:len(tuple)>1" tal:attributes="src python:tuple[1].absolute_url(); alt python:tuple[1].title_or_id()" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src granulometria/absolute_url; alt granulometria/title_or_id" /><img tal:attributes="src granulometria_legend/absolute_url; alt granulometria_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src compostiorganoclorurati/absolute_url; alt compostiorganoclorurati/title_or_id" /><img tal:attributes="src compostiorganoclorurati_legend/absolute_url; alt compostiorganoclorurati_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src policlorobifenili/absolute_url; alt policlorobifenili/title_or_id" /><img tal:attributes="src policlorobifenili_legend/absolute_url; alt policlorobifenili_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src idrocarburi/absolute_url; alt idrocarburi/title_or_id" /><img tal:attributes="src idrocarburi_legend/absolute_url; alt idrocarburi_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img tal:repeat="item others" tal:attributes="src item/absolute_url; alt item/title_or_id" />
		</div>
	</td>
</tr>
</table>

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Moluschi -->

<tal:block condition="python:monit=='Z'">
	<tal:block define="result python:here.createMolluschiCharts(param);
				stat_descr python:result[0];
				reg_descr python:result[1];
				data_descr python:result[2];
				station python:result[3];
				tuples python:result[4];
				compostiorganoclorurati python:result[5];
				compostiorganoclorurati_legend python:result[6];
				policlorobifenili python:result[7];
				policlorobifenili_legend python:result[8];
				idrocarburi python:result[9];
				idrocarburi_legend python:result[10];
				others python:result[11]">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table"> Tipologia Punto di prelievo </td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
<th i18n:translate="">Year</th>
<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp">Indicazioni sui parametri indagati nel Programma di monitoraggio</a>
</p>
<table border="1" cellspacing="2" class="table_indicators_images">
<tr tal:repeat="tuple tuples">
	<td>
		<div>
			<img tal:attributes="src python:tuple[0].absolute_url(); alt python:tuple[0].title_or_id()" /><img tal:condition="python:len(tuple)>1" tal:attributes="src python:tuple[1].absolute_url(); alt python:tuple[1].title_or_id()" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src compostiorganoclorurati/absolute_url; alt compostiorganoclorurati/title_or_id" /><img tal:attributes="src compostiorganoclorurati_legend/absolute_url; alt compostiorganoclorurati_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src policlorobifenili/absolute_url; alt policlorobifenili/title_or_id" /><img tal:attributes="src policlorobifenili_legend/absolute_url; alt policlorobifenili_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src idrocarburi/absolute_url; alt idrocarburi/title_or_id" /><img tal:attributes="src idrocarburi_legend/absolute_url; alt idrocarburi_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img tal:repeat="item others" tal:attributes="src item/absolute_url; alt item/title_or_id" />
		</div>
	</td>
</tr>
</table>

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Plancton -->

<tal:block condition="python:monit=='P'">
	<tal:block define="result python:here.getPlanctonData(param);
						fitoplancton python:result[0];
						zooplancton python:result[1];
						stat_descr python:result[2];
						reg_descr python:result[3];
						data_descr python:result[4];
						station python:result[5];
						year python:result[6];
						fitoplancton_ob python:result[7];
						fitoplancton_legend python:result[8];
						zooplancton_ob python:result[9];
						zooplancton_legend python:result[10]">


<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table">Tipologia Punto di prelievo </td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Year</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<table border="0" cellspacing="0" class="table_indicators_images">
<tr>
	<td>
		<div>
			<img tal:attributes="src fitoplancton_ob/absolute_url; alt fitoplancton_ob/title_or_id" /><img tal:attributes="src zooplancton_ob/absolute_url; alt zooplancton_ob/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src fitoplancton_legend/absolute_url; alt fitoplancton_legend/title_or_id" /><img tal:attributes="src zooplancton_legend/absolute_url; alt zooplancton_legend/title_or_id" />
		</div>
	</td>
</tr>
</table>

<table cellspacing="3" class="table_indicators">
<tr>
	<td colspan="2">Fitoplancton: taxa rilevati</td>
</tr>
<tr>
	<th i18n:translate="">Group</th>
	<th i18n:translate="">Taxa(*)</th>
	<th i18n:translate="">Cell/liter</th>
<tr>
<tr tal:repeat="val python:fitoplancton.keys()">
	<td tal:content="python:here.mp_descrmonit(fitoplancton[val][0])" />
	<td><tal:block repeat="item python:fitoplancton[val]">
		<span tal:replace="python:here.mp_nomespecie(item)" /><br />
		</tal:block>
	</td>
	<td><tal:block repeat="item python:fitoplancton[val]">
		<span tal:replace="python:here.mp_valore(item)" /><br />
		</tal:block>
	</td>
</tr>
</table>

<table cellspacing="3" class="table_indicators">
<tr>
	<td colspan="2"> Zooplancton: taxa rilevati</td>
</tr>
<tr>
	<th i18n:translate="">Group</th>
	<th i18n:translate="">Taxa(*)</th>
	<th i18n:translate="">Individui/mc</th>
<tr>
<tr tal:repeat="val python:zooplancton.keys()">
	<td tal:content="python:here.mp_descrmonit(zooplancton[val][0])" />
	<td><tal:block repeat="item python:zooplancton[val]">
		<span tal:replace="python:here.mp_nomespecie(item)" /><br />
		</tal:block>
	</td>
	<td><tal:block repeat="item python:zooplancton[val]">
		<span tal:replace="python:here.mp_valore(item)" /><br />
		</tal:block>
	</td>
</tr>
</table>

<p class="italic_notes">(*) I dati sulle specie sono stati rilevati solo a partire da Luglio 2002</p>

<form name="frmControl" action="" style="text-align: center; margin-top: 2em;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Benthos -->

<tal:block condition="python:monit=='X'">
	<tal:block define="result python:here.getBenthosData(param);
						data python:result[0];
						stat_descr python:result[1];
						reg_descr python:result[2];
						data_descr python:result[3];
						station python:result[4];
						year python:result[5]">

<table cellspacing="3" class="table_indicators">
	<tr>
		<td class="header_table"> Tipologia Punto di prelievo </td>
		<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
	</tr>
	<tr>
		<th i18n:translate="">Station</th>
		<td tal:content="station"/>
	</tr>
	<tr>
		<th i18n:translate="">Region</th>
		<td tal:content="python:here.mp_region(reg_descr[0])"/>
	</tr>
	<tr>
		<th i18n:translate="">Year</th>
		<td tal:content="year"/>
	</tr>
	<tr>
		<th i18n:translate="">Campaign</th>
		<td tal:content="campag"/>
	</tr>
	<tr>
		<th i18n:translate="">Locality</th>
		<td tal:content="python:here.mp_staz(stat_descr[0])"/>
	</tr>
</table>

<table cellspacing="3" class="table_indicators">
	<tr tal:repeat="res data">
		<th tal:content="python:here.mp_descrmonit(res)"></th>
		<td tal:content="python:here.mp_valore(res)"/>
	</tr>
</table>

<br />

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" class="button-normal" onclick="window.print()" i18n:attributes="value" value="Print" />
	<input type="button" class="button-normal" onclick="window.close()" i18n:attributes="value" value="Close window" />
</form>
<p>&nbsp;</p>

	</tal:block>
</tal:block>
</div>
</tal:block>

<!-- Invalid parameter -->

<tal:block condition="python:param==''">
<div style="background-color:white;height:600px">Invalid parameter
<form name="frmControl" action="" style="text-align: center;">
	<input type="button" class="button-normal" onclick="window.close()" i18n:attributes="value" value="Close window" />
</form>
</div>

</tal:block>
</tal:block>

</body>
</html>"""
        map_ob._getOb('results_html').pt_edit(text=content, content_type='')
        return "Update 02/02/2006 was successfully"

    def update_09022006(self, REQUEST=None, RESPONSE=None):
        """ """
        site = self.getSite()
        map_ob = getattr(site, 'map')
        #results_html
        content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	tal:attributes="xml:lang here/gl_get_selected_language; lang here/gl_get_selected_language">
<head tal:define="layout_tool here/getLayoutTool">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Scheda Stazione</title>
	<link tal:attributes="href string:${layout_tool/getSkinFilesPath}/style" rel="stylesheet" type="text/css" />
	<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_common" />
	<link rel="stylesheet" type="text/css" media="print" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_print" />
	<link rel="stylesheet" type="text/css" media="handheld" tal:attributes="href string:${layout_tool/getSkinFilesPath}/style_handheld" />
<style type="text/css">
  .table_indicators_2 {
    width:100%;
  }

  .table_indicators_2 td {
  	font-size: 100%;
    width:50%;
  }
</style>
</head>

<body style="background-image: none; background-color: white;">

<tal:block define="param python:request.get('param', '')">
<tal:block condition="python:param !=''">
<div id="includes_tables"
	tal:define="results python:here.getWaterInfo(param);
	info python:results[0];
	stat_descr python:results[1];
	reg_descr python:results[2];
	data_descr python:results[3];
	year python:results[4];
	campag python:results[5];
	monit python:results[6];
	station python:results[7];
	region python:results[8];
	station_data python:results[9]">

<!-- Water -->

<tal:block condition="python:monit=='W'">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table" i18n:translate="">Tipologia Punto di prelievo</td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])" />
</tr>
<tr>
	<th i18n:translate="">Stazione</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Fornitore</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Anno</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campagna</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Localit&agrave;</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
<tal:block condition="python:len(station_data) > 0">
<tr>
	<th i18n:translate="">Tipo stazione</th>
	<td tal:content="python:here.mp_tipo_staz(station_data[0])" />
</tr>
<tr>
	<th i18n:translate="">Prof. tot</th>
	<td tal:content="python:here.mp_prof_tot(station_data[0])" />
</tr>
<tr>
	<th i18n:translate="">Indice qual.amb.marino</th>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 1.0">alta qualit&agrave;</td>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 2.0">media qualit&agrave;</td>
	<td tal:condition="python:here.mp_indice(station_data[0]) == 3.0">bassa qualit&agrave;</td>
</tr>
<tr>
	<th i18n:translate="">Indice annuale</th>
	<td><a tal:attributes="href string:indices_html?param=${param}" target="_blank"> Andamento annuale
	qualit&agrave; <span tal:content="python:here.mp_region(reg_descr[0])"/></a></td>
</tr>
<tr>
	<th i18n:translate="">Grafici altre stazioni</th>
	<td><a tal:attributes="href string:stations_html?param=${param}" target="_blank">Grafici
	altre stazioni della <span tal:content="python:here.mp_region(reg_descr[0])"/></a></td>
</tr>
<tr>
	<td id="left_values"><div id="chart_legend"><span i18n:translate="">Legend</span><br />
	<img src="misc_/Sidimar/legenda.gif" alt="Legend" /><br />
	Le scale del grafico sono state scelte sulla base dei valori minimi e massimi
	riscontrati per la regione nella campagna monitorata</div>
	</td>
	<tal:block define="graph python:here.getGraph(region, year, campag, station)">
	<td id="chart" tal:condition="python:graph != 0">
	<img tal:attributes="src python:graph.absolute_url()" alt="graphic_results" border="1" />
	</td>
	<td id="chart" tal:condition="python:graph == 0" i18n:translate="">No graph available</td>
	</tal:block>
</tr>
</tal:block>
</table>
<hr />

<tal:block condition="python:len(station_data) > 0">
<p class="text_title" i18n:translate="">Parametri per la Classificazione delle Acque Marine</p>

<table cellspacing="3" class="table_indicators">
<tr tal:repeat="i info">
	<th tal:content="python:here.mp_descrmonit(i)" />
	<td class="numeric_values" tal:content="python:here.mp_valore(i)"/>
</tr>
</table>

<p class="italic_notes" i18n:translate="">(*) Se la trasparenza ha valore di 55 il disco secchi ha toccato il fondo</p>
<br />
<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp" target="_blank">Indicazioni
sui parametri indagati nel Programma di monitoraggio</a></p>
<br />
</tal:block>

<p tal:condition="python:len(station_data) == 0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

</tal:block>

<!-- Sedimenti -->

<tal:block condition="python:monit=='S'">
<tal:block condition="python:here.checkParam(param)">
	<tal:block define="result python:here.createSedimentiCharts(param);
				stat_descr python:result[0];
				reg_descr python:result[1];
				data_descr python:result[2];
				station python:result[3];
				tuples python:result[4];
				granulometria python:result[5];
				granulometria_legend python:result[6];
				compostiorganoclorurati python:result[7];
				compostiorganoclorurati_legend python:result[8];
				policlorobifenili python:result[9];
				policlorobifenili_legend python:result[10];
				idrocarburi python:result[11];
				idrocarburi_legend python:result[12];
				others python:result[13]">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table">Tipologia Punto di prelievo</td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Year</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp">Indicazioni sui parametri indagati nel Programma di monitoraggio</a>
</p>

<table border="1" cellspacing="2" class="table_indicators_images">
<tr tal:repeat="tuple tuples">
	<td>
		<div>
			<img tal:attributes="src python:tuple[0].absolute_url(); alt python:tuple[0].title_or_id()" /><img tal:condition="python:len(tuple)>1" tal:attributes="src python:tuple[1].absolute_url(); alt python:tuple[1].title_or_id()" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src granulometria/absolute_url; alt granulometria/title_or_id" /><img tal:attributes="src granulometria_legend/absolute_url; alt granulometria_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src compostiorganoclorurati/absolute_url; alt compostiorganoclorurati/title_or_id" /><img tal:attributes="src compostiorganoclorurati_legend/absolute_url; alt compostiorganoclorurati_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src policlorobifenili/absolute_url; alt policlorobifenili/title_or_id" /><img tal:attributes="src policlorobifenili_legend/absolute_url; alt policlorobifenili_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src idrocarburi/absolute_url; alt idrocarburi/title_or_id" /><img tal:attributes="src idrocarburi_legend/absolute_url; alt idrocarburi_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img tal:repeat="item others" tal:attributes="src item/absolute_url; alt item/title_or_id" />
		</div>
	</td>
</tr>
</table>
</tal:block>
<p tal:condition="python:here.checkParam(param)==0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>
<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Moluschi -->

<tal:block condition="python:monit=='Z'">
<tal:block condition="python:here.checkParam(param)">
	<tal:block define="result python:here.createMolluschiCharts(param);
				stat_descr python:result[0];
				reg_descr python:result[1];
				data_descr python:result[2];
				station python:result[3];
				tuples python:result[4];
				compostiorganoclorurati python:result[5];
				compostiorganoclorurati_legend python:result[6];
				policlorobifenili python:result[7];
				policlorobifenili_legend python:result[8];
				idrocarburi python:result[9];
				idrocarburi_legend python:result[10];
				others python:result[11]">
<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table"> Tipologia Punto di prelievo </td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
<th i18n:translate="">Year</th>
<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<p><a class="text_link" href="http://www2.minambiente.it/sito/settori_azione/sdm/tutela_ambiente_marino/monitoraggio_ambiente_marino/triennio_01_03_programma_variabili.asp">Indicazioni sui parametri indagati nel Programma di monitoraggio</a>
</p>
<table border="1" cellspacing="2" class="table_indicators_images">
<tr tal:repeat="tuple tuples">
	<td>
		<div>
			<img tal:attributes="src python:tuple[0].absolute_url(); alt python:tuple[0].title_or_id()" /><img tal:condition="python:len(tuple)>1" tal:attributes="src python:tuple[1].absolute_url(); alt python:tuple[1].title_or_id()" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src compostiorganoclorurati/absolute_url; alt compostiorganoclorurati/title_or_id" /><img tal:attributes="src compostiorganoclorurati_legend/absolute_url; alt compostiorganoclorurati_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src policlorobifenili/absolute_url; alt policlorobifenili/title_or_id" /><img tal:attributes="src policlorobifenili_legend/absolute_url; alt policlorobifenili_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src idrocarburi/absolute_url; alt idrocarburi/title_or_id" /><img tal:attributes="src idrocarburi_legend/absolute_url; alt idrocarburi_legend/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img tal:repeat="item others" tal:attributes="src item/absolute_url; alt item/title_or_id" />
		</div>
	</td>
</tr>
</table>
</tal:block>
<p tal:condition="python:here.checkParam(param)==0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Plancton -->

<tal:block condition="python:monit=='P'">
<tal:block condition="python:here.checkParam(param)">
	<tal:block define="result python:here.getPlanctonData(param);
						fitoplancton python:result[0];
						zooplancton python:result[1];
						stat_descr python:result[2];
						reg_descr python:result[3];
						data_descr python:result[4];
						station python:result[5];
						year python:result[6];
						fitoplancton_ob python:result[7];
						fitoplancton_legend python:result[8];
						zooplancton_ob python:result[9];
						zooplancton_legend python:result[10]">


<table cellspacing="3" class="table_indicators">
<tr>
	<td class="header_table">Tipologia Punto di prelievo </td>
	<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Station</th>
	<td tal:content="station"/>
</tr>
<tr>
	<th i18n:translate="">Region</th>
	<td tal:content="python:here.mp_region(reg_descr[0])"/>
</tr>
<tr>
	<th i18n:translate="">Year</th>
	<td tal:content="year"/>
</tr>
<tr>
	<th i18n:translate="">Campaign</th>
	<td tal:content="campag"/>
</tr>
<tr>
	<th i18n:translate="">Locality</th>
	<td tal:content="python:here.mp_staz(stat_descr[0])"/>
</tr>
</table>

<table border="0" cellspacing="0" class="table_indicators_images">
<tr>
	<td>
		<div>
			<img tal:attributes="src fitoplancton_ob/absolute_url; alt fitoplancton_ob/title_or_id" /><img tal:attributes="src zooplancton_ob/absolute_url; alt zooplancton_ob/title_or_id" />
		</div>
	</td>
</tr>
<tr>
	<td>
		<div>
			<img style="vertical-align:top;" tal:attributes="src fitoplancton_legend/absolute_url; alt fitoplancton_legend/title_or_id" /><img tal:attributes="src zooplancton_legend/absolute_url; alt zooplancton_legend/title_or_id" />
		</div>
	</td>
</tr>
</table>

<table cellspacing="3" border="0" class="table_indicators">
<tr>
	<td colspan="2">Fitoplancton: taxa rilevati</td>
</tr>
<tr>
	<th i18n:translate="">Group</th>
	<th i18n:translate="">Taxa(*)</th>
	<th i18n:translate="">Cell/liter</th>
<tr>
<tr tal:repeat="val python:fitoplancton.keys()">
	<td tal:content="val" />
	<td colspan="2">
		<table class="table_indicators_2">
			<tr tal:repeat="item python:fitoplancton[val]">
				<td tal:content="python:item[1]" />
				<td tal:content="python:item[0]" />
			</tr>
		</table>
	</td>
</tr>
</table>

<table cellspacing="3" class="table_indicators">
<tr>
	<td colspan="2"> Zooplancton: taxa rilevati</td>
</tr>
<tr>
	<th i18n:translate="">Group</th>
	<th i18n:translate="">Taxa(*)</th>
	<th i18n:translate="">Individui/mc</th>
<tr>
<tr tal:repeat="val python:zooplancton.keys()">
	<td tal:content="val" />
	<td colspan="2">
		<table class="table_indicators_2">
			<tr tal:repeat="item python:zooplancton[val]">
				<td tal:content="python:item[1]" />
				<td tal:content="python:item[0]" />
			</tr>
		</table>
	</td>
</tr>
</table>

<p class="italic_notes">(*) I dati sulle specie sono stati rilevati solo a partire da Luglio 2002</p>

</tal:block>
<p tal:condition="python:here.checkParam(param)==0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>

<form name="frmControl" action="" style="text-align: center; margin-top: 2em;">
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.print()" value="Print" />
	<input type="button" i18n:attributes="value" class="button-normal" onclick="window.close()" value="Close window" />
</form>

<p>&nbsp;</p>

	</tal:block>
</tal:block>

<!-- Benthos -->

<tal:block condition="python:monit=='X'">
<tal:block condition="python:here.checkParam(param)">
	<tal:block define="result python:here.getBenthosData(param);
						data python:result[0];
						stat_descr python:result[1];
						reg_descr python:result[2];
						data_descr python:result[3];
						station python:result[4];
						year python:result[5]">

<table cellspacing="3" class="table_indicators">
	<tr>
		<td class="header_table"> Tipologia Punto di prelievo </td>
		<td tal:content="python:here.mp_descrmonit(data_descr[0])"/>
	</tr>
	<tr>
		<th i18n:translate="">Station</th>
		<td tal:content="station"/>
	</tr>
	<tr>
		<th i18n:translate="">Region</th>
		<td tal:content="python:here.mp_region(reg_descr[0])"/>
	</tr>
	<tr>
		<th i18n:translate="">Year</th>
		<td tal:content="year"/>
	</tr>
	<tr>
		<th i18n:translate="">Campaign</th>
		<td tal:content="campag"/>
	</tr>
	<tr>
		<th i18n:translate="">Locality</th>
		<td tal:content="python:here.mp_staz(stat_descr[0])"/>
	</tr>
</table>

<table cellspacing="3" class="table_indicators">
	<tr tal:repeat="res data">
		<th tal:content="python:here.mp_descrmonit(res)"></th>
		<td tal:content="python:here.mp_valore(res)"/>
	</tr>
</table>
</tal:block>
<p tal:condition="python:here.checkParam(param)==0" class="text_title" i18n:translate="">
    No data available in order to create graphs for this station.
</p>

<br />

<form name="frmControl" action="" style="text-align: center;">
	<input type="button" class="button-normal" onclick="window.print()" i18n:attributes="value" value="Print" />
	<input type="button" class="button-normal" onclick="window.close()" i18n:attributes="value" value="Close window" />
</form>
<p>&nbsp;</p>

	</tal:block>
</tal:block>
</div>
</tal:block>

<!-- Invalid parameter -->

<tal:block condition="python:param==''">
<div style="background-color:white;height:600px">Invalid parameter
<form name="frmControl" action="" style="text-align: center;">
	<input type="button" class="button-normal" onclick="window.close()" i18n:attributes="value" value="Close window" />
</form>
</div>

</tal:block>
</tal:block>

</body>
</html>"""
        map_ob._getOb('results_html').pt_edit(text=content, content_type='')

        site = self.getSite()
        download_ob = getattr(site, 'download')
        #campagna_html
        content = """<span tal:replace="structure here/standard_html_header" />

<tal:block define="region python:request.get('region', '');
					monit python:request.get('monit', '');
					year python:request.get('year', '');
					mysql_tool here/getMySQLTool;
					results python:here.processCampaign(region, monit, year);
					region python:results[0];
					campaigns python:results[1];">

<h1 i18n:translate="">Choose campaign</h1>

<p>Selected parameters:</p>
<table class="horizontal_table" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:1em">
<tr>
<th i18n:translate="">Region:</th> <td tal:content="here/getSessionRegion" />
</tr>
<tr>
<th i18n:translate="">Monitored data:</th> <td tal:content="here/getSessionDataMonit" />
</tr>
<tr>
<th i18n:translate="">Year:</th> <td tal:content="here/getSessionYear" />
</tr>
</table>


<form action="download_html" method="post" name="frmDownload" id="frmDownload">
	<p tal:condition="not:campaigns">
		No campaign was found matching your criteria.
	</p>
	<p tal:condition="python:len(campaigns)==1">
		One campaign was found matching your criteria.<br />To download it please select it and click <strong>Download</strong>.
	</p>
	<p tal:condition="python:len(campaigns)>1">
		More campaigns were found matching your criteria.<br /> Please select the one you want to download to continue.
	</p>
	<p>
		<tal:block tal:repeat="campaign campaigns">
			<tal:block define="camp python:mysql_tool.mp_campag(campaign); number repeat/campaign/number">
			<input type="radio" name="campaign" tal:attributes="value camp;id string:camp_${number}">
			<label tal:attributes="for string:camp_${number}" tal:content="camp" /><br />
			</tal:block>
		</tal:block>
	</p>


		<input type="button" name="chgReg" value="Change regions" onclick="javascript:history.go(-1)" />
	<tal:block tal:condition="campaigns">
		<input type="hidden" name="monit" tal:attributes="value monit" />
		<input type="hidden" name="region" tal:attributes="value region" />
		<input type="submit" name="download" value="Download" />
		<input name="reset" type="reset" value="Reset" />
	</tal:block>
</form>

</tal:block>

<span tal:content="here/delSessionErrors" tal:omit-tag=""></span>
<span tal:replace="structure here/standard_html_footer" />"""

        download_ob._getOb('campagna_html').pt_edit(text=content, content_type='')
        return "Update 09/02/2006 was successfully"

    security.declareProtected(manage_users, 'admin_edituser_html')
    def admin_edituser_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_edituser')

    security.declarePublic('user_pwd_html')
    def user_pwd_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_user_password')

    security.declarePublic('user_prefs_html')
    def user_prefs_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_user_preferences')

    security.declareProtected(manage_users, 'admin_adduser_html')
    def admin_adduser_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_adduser')

    security.declareProtected(manage_users, 'admin_users_html')
    def admin_users_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users')

    security.declareProtected(manage_users, 'admin_user_history_html')
    def admin_user_history_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_userhistory')

    security.declareProtected(manage_users, 'admin_user_downloads_html')
    def admin_user_downloads_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_userdownloads')

    security.declareProtected(manage_users, 'admin_user_html')
    def admin_user_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_user')

    security.declareProtected(manage_users, 'user_pending_html')
    def user_pending_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_pendinguser')

    security.declareProtected(manage_users, 'admin_pending_html')
    def admin_pending_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_pendingusers')

    security.declareProtected(view, 'register_html')
    def register_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_register')

    security.declareProtected(view, 'forgot_password_html')
    def forgot_password_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_forgotpwd')

    security.declareProtected(view, 'info_html')
    def info_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_info')


#    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_roles_html')
#    def admin_roles_html(self, REQUEST=None, RESPONSE=None):
#        """ """
#        return self.getFormsTool().getContent({'here': self}, 'site_admin_roles')

InitializeClass(SidimarSite)