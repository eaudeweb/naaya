import os
import tempfile
from zipfile import *
from os.path import join 
import time

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.Sidimar.constants import *
from Products.Sidimar.Core.Mappings import Mappings

class ZipSQL(Mappings):

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        pass


    security.declarePrivate('zip_sql')
    def zip_sql(self, campaign, region, monit, year, instruments, stations, monit_exp, monit_pb, info=0, REQUEST=None, RESPONSE=None):
        """ zip all the comma separated files """
        path = join(CLIENT_HOME, self.getSite().id)
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except:
                raise OSError, 'Can\'t create directory %s' % path
        tempfile.tempdir = path
        tmpfile = tempfile.mktemp(".temp")
        zf = ZipFile(tmpfile,"w")

        #zip the instruments
        instr = self.process_instruments(region, monit, year, instruments)
        self.write_sql(instr, zf)

        #zip the stations
        stations = self.process_stations(region, monit, year, stations)
        self.write_sql(stations, zf)

        monit_p_ = monit_pb_ = None
        if monit_exp is not None:
            #zip the data monitored
            monit_p_ = self.process_monit_except_plancton(campaign, region, monit, year, monit_exp)
            self.write_sql(monit_p_, zf)
        if monit_pb is not None:
            #zip the data monitored
            monit_pb_ = self.process_monit_benthos_plancton(campaign, region, monit, year, monit_pb)
            self.write_sql(monit_pb_, zf)

        zf.close()
        stat = os.stat(tmpfile)

        if info:
            os.unlink(tmpfile)
            return (instr, stations, monit_p_, monit_pb_, self.getSize(stat[6]))

        f = open(tmpfile, 'rb')
        cont = f.read()
        f.close()
        os.unlink(tmpfile)

        #write in the user log
        users_tool = self.getUsersTool()
        auth_user = users_tool.getUser(REQUEST.AUTHENTICATED_USER.getUserName())
        if auth_user is not None:
            users_tool.change_downloads(auth_user, region, campaign, year, monit)

        download_id = "%s_%s_%s_%s.zip" % (region, monit, campaign, year)
        RESPONSE.setHeader('Content-Type', 'application/x-zip')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % download_id)
        RESPONSE.setHeader('Content-Length', stat[6])
        return cont


    security.declarePrivate('getSize')
    def getSize(self, size):
        """ transforms a file size in Kb, Mb .. """
        bytes = float(size)
        unit = ''
        if bytes >= 1000:
            bytes = bytes/1024
            unit = 'Kb'
            if bytes >= 1000:
                bytes = bytes/1024
                unit = 'Mb'
            res = '%s %s' % ('%4.2f' % bytes, unit)
        else:
            unit = 'Bytes'
            res = '%s %s' % ('%4.0f' % bytes, unit)
        return res


    security.declarePrivate('write_sql')
    def write_sql(self, objs, zf):
        """ write the sql files into zip """
        timetuple = time.localtime()[:6]
        objs = self.utConvertToList(objs)
        for ob in objs:
            zfi = ZipInfo(ob.getId())
            zfi.date_time = timetuple
            zfi.compress_type = ZIP_DEFLATED
            zf.writestr(zfi, str(ob.getData()))


    security.declarePrivate('process_instruments')
    def process_instruments(self, region, monit, year, instruments):
        """ process the records returned from the database and generate a comma-separated structure """
        res = []
        res.append('%s; %s; %s; %s; %s; %s' % (FORNIT, COD, DESCR, UNIT, NAME, RIL))

        for instr in instruments:
            res.append('%s; %s; %s; %s; %s; %s' % (self.mp_fornit(instr), self.mp_codparam(instr), \
                self.mp_paramdescr(instr), self.mp_unita(instr), self.mp_nome(instr), self.mp_limite_ril(instr)))

        data = '\r\n'.join(res)
        id = "Strumenti_%s_%s_%s.txt" % (region, monit, year)
        return SQLContainer(id, data)

    security.declarePrivate('process_monit_except_plancton')
    def process_monit_except_plancton(self, campaign, region, monit, year, monit_exp):
        """ process all the data monitored except for plancton """

        from copy import copy
        if monit == 'Acque':
            monit_codes = copy(W_MONIT_CODES)
            monit_codes_values = copy(W_MONIT_CODES_VALUES)
        elif monit == 'Biota':
            monit_codes = copy(Z_MONIT_CODES)
            monit_codes_values = copy(Z_MONIT_CODES_VALUES)
        elif monit == 'Benthos':
            monit_codes = copy(X_MONIT_CODES)
            monit_codes_values = copy(X_MONIT_CODES_VALUES)
        elif monit == 'Plancton':
            monit_codes = copy(P_MONIT_CODES)
            monit_codes_values = copy(P_MONIT_CODES_VALUES)
        elif monit == 'Sedimenti':
            monit_codes = copy(S_MONIT_CODES)
            monit_codes_values = copy(S_MONIT_CODES_VALUES)
        else:
            monit_codes = []
            monit_codes_values = {}

        staz = ''
        progr = 0
        buf = {}
        monit_data = []
        for i in monit_exp:
            if i['staz'] != staz or i['progrprel'] != progr:
                staz = i['staz']
                progr = i['progrprel']
                if len(buf) > 0:   monit_data.append(buf)
                buf = copy(monit_codes_values)
                buf.update(i)
            buf[i['codparam']] = '%.2f' % i['valore']

        res = []
        params = '; '.join(monit_codes)
        res.append('%s; %s; %s; %s; %s; %s; %s; %s' % (STAZIONE, REGIONE, DATA, MONITOR, CAMPAG, DIST_SUP, PROGR_PREL, params))


        for m in monit_data:
            params_data = []
            for i in monit_codes:
                params_data.append(m[i])
            res.append('%s; %s; %s; %s; %s; %s; %s; %s' % (self.mp_staz(m), self.mp_fornit(m), \
                self.mp_data(m), self.mp_monit(m), self.mp_campag(m), self.mp_distsup(m), self.mp_progrprel(m), \
                '; '.join(params_data)))

        data = '\r\n'.join(res)
        id = "%s_%s_%s_%s.txt" % (monit, region, campaign, year)
        return SQLContainer(id, data)


    security.declarePrivate('process_monit_benthos_plancton')
    def process_monit_benthos_plancton(self, campaign, region, monit, year, monit_pb):
        """ process all the data monitored for plancton and benthos """
        res = []
        res.append('%s; %s; %s; %s; %s; %s; %s; %s; %s; %s;' % (STAZIONE, FORNIT, MONITOR, DATA, CAMPAG, DIST_SUP, PROGR_PREL, COD_PARAM, NOME_SPECIE, VALUE))

        for m in monit_pb:
            res.append('%s; %s; %s; %s; %s; %s; %s; %s; %s; %s;' % (self.mp_staz(m), self.mp_fornit(m), \
                self.mp_monit(m), self.mp_data(m), self.mp_campag(m), self.mp_distsup(m), self.mp_progrprel(m), \
                self.mp_codparam(m), self.mp_nomespecie(m), self.mp_valore(m)))
        data = '\r\n'.join(res)
        id = "%s_%s_%s_%s_second.txt" % (monit, region, campaign, year)
        return SQLContainer(id, data)


    security.declarePrivate('process_stations')
    def process_stations(self, region, monit, year, stations):
        """ process the records returned from the database and generate a comma-separated structure """
        res = []
        res.append('%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s;' % (STAZ_DESCR, STAZ, LATG, LATP, LATS, LATPC, LONGG, LONGP, LONGS, LONGPC, DESCR, CODISTAT, PROF_TOT))

        for s in stations:
            res.append('%s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s; %s;' % (self.mp_supplier(s), \
                self.mp_staz(s), self.mp_latg(s), self.mp_latp(s), self.mp_lats(s), self.mp_latpc(s), \
                self.mp_longg(s), self.mp_longp(s), self.mp_longs(s), self.mp_longpc(s), self.mp_description(s), \
                self.mp_codistat(s), self.mp_prof_tot(s)))
        data = '\r\n'.join(res)
        id = "Stazioni_%s_%s_%s.txt" % (region, monit, year)
        return SQLContainer(id, data)

InitializeClass(ZipSQL)


class SQLContainer:

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, id, data):
        """ constructor """
        self.id = id
        self.data = data

    def getId(self):
        return self.id

    def getData(self):
        return self.data

InitializeClass(SQLContainer)