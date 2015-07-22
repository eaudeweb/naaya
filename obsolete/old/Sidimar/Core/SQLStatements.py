# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights AND limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania
# Cornel Nitu, Finsiel Romania
#
#$Id: SQLStatements.py 3445 2005-04-22 19:16:30Z nituacor $

__version__='$Revision: 1.35 $'[11:-2]

def _replacequote(s):
    return s.replace("'", "''")

def _convertdb(s):
    """ return a string used to build an sql statement """
    return '\'%s\'' % _replacequote(s)
    if s is None or str(s) == '' or str(s).strip() == '': return 'NULL'
    else: return '\'%s\'' % _replacequote(s)


def sql_get_regions():
    return """ SELECT idfornit, descr
               FROM entefornitore 
               WHERE flg_att = 'A' 
               ORDER BY descr
           """

def sql_get_years():
    return """SELECT distinct anno_campag
                FROM analisiprelievo
                ORDER BY anno_campag
            """

def sql_get_campaigns():
    return """SELECT DISTINCT campag 
              FROM indicecam i"""

def sql_get_data_monitored():
    return """ SELECT DISTINCT(descr), a.codmonit AS codmonit
               FROM tipodimonitoraggio a, stazionetipomonitoraggio b
               WHERE a.codmonit = b.codmonit 
                    AND anno = '2001'
               ORDER BY descr
            """

def sql_get_region_waterdata_monitored(year, campaign, region):
    return """SELECT codparam, valore, fornit, monit, data, staz, distsup
                FROM analisiprelievo
                WHERE monit = 'W'
                AND anno_campag = '%s'
                AND campag = '%s'
                AND fornit = '%s'
            """ % (year, campaign, region) #ORDER BY data, staz, codparam, distsup, valore

def sql_get_waterdata_monitored(year, campaign):
    return """SELECT codparam, valore, fornit, monit, data, staz, distsup
                FROM analisiprelievo
                WHERE monit = 'W'
                AND anno_campag = '%s'
                AND campag = '%s'
            """ % (year, campaign) #ORDER BY data, staz, codparam, distsup, valore

def sql_get_instruments(monit, region):
    return """ SELECT analisi.codparam as codparam, b.descr as fornit, c.descr as paramdescr, unita, e.nome as nome, d.limite_ril
                FROM 
                    (SELECT DISTINCT(codparam), fornit 
                    FROM analisiprelievo a 
                    WHERE monit='%s' and fornit='%s') AS analisi
                JOIN entefornitore b ON (idfornit = analisi.fornit)
                JOIN parametromarino c ON (c.codparam = analisi.codparam)
                JOIN strumentoparametrofornitore d ON (d.codparam = analisi.codparam AND codfornit = analisi.fornit)
                JOIN strumento e ON (e.cod_str = d.cod_str)
                ORDER BY analisi.codparam
            """ % (monit, region)

def sql_get_instruments_plancton(monit, region):
    return """SELECT DISTINCT(a.codparam) as codparam, b.descr as fornit, c.descr as paramdescr, unita, e.nome as nome, d.limite_ril
                FROM listaspecie a
                JOIN entefornitore b ON (idfornit = a.fornit)
                JOIN parametromarino c ON (c.codparam = a.codparam)
                JOIN strumentoparametrofornitore d ON (d.codparam = a.codparam AND codfornit = a.fornit)
                JOIN strumento e ON (e.cod_str = d.cod_str)
                WHERE monit='%s'
                    AND idfornit = '%s'
                ORDER BY a.codparam
            """ % (monit, region)

def sql_get_stations(year, region, monit):
    return """SELECT DISTINCT(a.staz), b.descr AS supplier, latg, lats, latp, latpc, longg, longp, longs, longpc, 
                    c.descr AS description, codistat, prof_tot
                FROM analisiprelievo a
                JOIN entefornitore b ON (b.idfornit = a.fornit)
                JOIN stazionedimonitoraggio c ON (c.staz = a.staz and c.fornit=a.fornit)
                WHERE anno_campag = %s
                AND b.idfornit = %s
                AND monit = %s
                ORDER BY a.staz
            """ % (_convertdb(year), _convertdb(region), _convertdb(monit))

def sql_get_stations_plancton(year, region):
    return """SELECT DISTINCT(a.staz), b.descr AS supplier, latg, latp, lats, latpc, longg, longp, longs, longpc, 
                    c.descr AS description, codistat, prof_tot
                FROM listaspecie a
                JOIN entefornitore b ON (idfornit = a.fornit)
                JOIN stazionedimonitoraggio c ON (c.staz = a.staz and c.fornit=a.fornit)
                WHERE monit = 'P'
                AND anno_campag = %s
                AND idfornit = %s
                ORDER BY a.staz
            """ % (_convertdb(year), _convertdb(region))

def sql_get_region_by_id(id):
    return """ SELECT
                    descr
                FROM entefornitore
                WHERE flg_att = 'A'
                    AND idfornit = %s 
                ORDER BY descr
           """ % _convertdb(id)

def sql_get_station_by_id(id, region):
    return """ SELECT descr as staz
               FROM stazionedimonitoraggio
               WHERE staz = '%s'
                AND fornit = '%s' """ % (id, region)

def sql_get_data_monitored_by_id(id):
    return """ SELECT descr
               FROM tipodimonitoraggio 
               WHERE codmonit = %s
               ORDER BY descr """ % _convertdb(id)

def sql_get_campaign_plancton(region, monit, year):
    return """ SELECT distinct
                    campag 
                FROM listaspecie 
                WHERE fornit = %s 
                    AND anno_campag = %s 
                    AND monit = %s ORDER BY campag 
           """ % (_convertdb(region), _convertdb(year), _convertdb(monit))

def sql_get_campaign(region, monit, year):
    return """ SELECT distinct
                    campag 
                FROM analisiprelievo 
                WHERE fornit = %s 
                    AND anno_campag = %s 
                    AND monit = %s ORDER BY campag 
           """ % (_convertdb(region), _convertdb(year), _convertdb(monit))

def sql_get_monitor_type(monit):
    return """ SELECT 
                    codparam 
               FROM parametrotipomonitoraggio
               WHERE codmonit = '%s'
            """ % monit

def sql_get_monit_except_plancton(region, year, monit, campaign):
    return """SELECT a.staz, c.descr as fornit, d.descr as monit, DATE_FORMAT(data, '%%e-%%c-%%Y') as data, campag, distanza, distsup, progrprel, codparam, valore
                FROM analisiprelievo a
                JOIN stazionedimonitoraggio b ON (b.fornit = a.fornit AND b.staz = a.staz)
                JOIN entefornitore c ON (idfornit = b.fornit)
                JOIN tipodimonitoraggio d ON (monit = codmonit)
                WHERE a.fornit = '%s'
                    AND anno_campag = '%s'
                    AND monit = '%s'
                    AND campag = '%s'
                    ORDER BY monit, campag, staz, data, progrprel, distsup, codparam
        """ % (region, year, monit, campaign)

#def sql_get_monit_benthos_plancton(region, year, monit, campaign):
#    return """SELECT
#                staz, fornit, monit, DATE_FORMAT(data, '%%e-%%c-%%Y') as data, campag, distsup, progrprel, codparam, valore, nome_specie
#              FROM listaspecie
#              JOIN entefornitore c ON (idfornit = fornit)
#              WHERE fornit = '%s'
#                AND anno_campag = '%s'
#                AND monit = '%s'
#                AND campag = '%s'
#              ORDER BY monit, campag, staz, data, progrprel, distsup, codparam, nome_specie
#            """ % (region, year, monit, campaign)

def sql_get_monit_benthos_plancton(region, year, monit, campaign):
    return """SELECT 
                    staz, b.descr as fornit, c.descr as monit, DATE_FORMAT(a.data, '%%e-%%c-%%Y') as data, 
                    campag, distsup, progrprel, d.descr as codparam, nome_specie, valore
                FROM listaspecie a
                JOIN entefornitore b ON (idfornit = a.fornit)
                JOIN tipodimonitoraggio c ON (codmonit = monit)
                JOIN parametromarino d ON (d.codparam = a.codparam)
                WHERE a.fornit = '%s'
                    AND anno_campag = '%s'
                    AND monit = '%s'
                    AND campag = '%s'
                ORDER BY monit, campag, staz, data, progrprel, distsup, codparam, nome_specie
            """ % (region, year, monit, campaign)

def sql_water_info(station, region, year, campag, monit):
    return """SELECT a.codparam, a.unitamissint, a.descr, valore
                FROM parametromarino a, analisiprelievo b
                WHERE a.codparam = b.codparam
                    AND staz = '%s'
                    AND fornit = '%s'
                    AND campag = '%s'
                    AND anno_campag = '%s'
                    AND monit = '%s'
            """ % (station, region, campag, year, monit)

def sql_sediments_data(region, year, campag, monit):
    return """SELECT b.descr, a.codparam ,valore, c.staz, c.descr as station
                FROM analisiprelievo a, parametromarino b, stazionedimonitoraggio c
                WHERE b.codparam = a.codparam
                AND (c.staz = a.staz and c.fornit = a.fornit)
                AND monit = '%s'
                AND a.fornit = '%s'
                AND anno_campag = '%s'
                AND campag = '%s'
                ORDER BY codparam
            """ % (monit, region, year, campag)

def sql_molluschi_data(region, year, campag, monit):
    return """SELECT b.descr, a.codparam ,valore, c.staz, c.descr as station
                FROM analisiprelievo a, parametromarino b, stazionedimonitoraggio c
                WHERE b.codparam = a.codparam
                AND (c.staz = a.staz and c.fornit = a.fornit)
                AND monit = '%s'
                AND a.fornit = '%s'
                AND anno_campag = '%s'
                AND campag = '%s'
                ORDER BY codparam
            """ % (monit, region, year, campag)


def sql_plancton_data(region, year, campag, monit, station):
    return """SELECT b.descr, a.codparam, valore, c.staz, c.descr as station, unitamissint, nome_specie
                FROM listaspecie a
                JOIN parametromarino b ON (b.codparam=a.codparam)
                JOIN stazionedimonitoraggio c ON (c.staz = a.staz and c.fornit = a.fornit)
                WHERE monit = '%s'
                AND c.fornit = '%s'
                AND anno_campag = '%s'
                AND campag = '%s'
                AND c.staz = '%s'
                AND c.anno = '2001'
                ORDER BY codparam
            """ % (monit, region, year, campag, station)


#def sql_plancton_data(region, year, campag, monit, station):
#    return """SELECT b.descr, a.codparam ,valore, c.staz, c.descr as station, unitamissint, nome_specie
#                FROM analisiprelievo a, parametromarino b, stazionedimonitoraggio c
#                WHERE b.codparam = a.codparam
#                AND (c.staz = a.staz and c.fornit = a.fornit)
#                AND monit = '%s'
#                AND a.fornit = '%s'
#                AND anno_campag = '%s'
#                AND campag = '%s'
#                AND c.staz = '%s'
#                ORDER BY codparam
#            """ % (monit, region, year, campag, station)

def sql_benthos_data(region, year, campag, monit, station):
    return """SELECT descr, a.codparam ,valore, fornit, monit, DATE_FORMAT(data, '%%e-%%c-%%Y') as data, staz, distsup
                FROM analisiprelievo a, parametromarino b
                WHERE b.codparam = a.codparam
                AND monit = '%s'
                AND anno_campag = '%s'
                AND campag = '%s'
                AND staz = '%s'
                AND fornit = '%s'
                ORDER BY descr
            """ % (monit, year, campag, station, region)

def sql_anual_indices(region, year):
    return """SELECT a.staz, a.descr, distanza, campag, indice
                FROM stazionedimonitoraggio a, indicecam b
                WHERE a.staz = b.staz
                AND a.fornit = b.fornit
                AND b.fornit = '%s'
                AND anno_campag = '%s'
            """ % (region, year)

def sql_water_scale_info(region, year, campag, monit):
    return """SELECT fornit, b.codparam, b.descr, min(valore), max(valore)
                FROM analisiprelievo a
                JOIN parametromarino b
                ON (b.codparam = a.codparam)
                WHERE fornit='%s'
                AND monit='%s'
                AND campag='%s'
                AND anno_campag = '%s'
                GROUP BY b.codparam
            """ % (region, monit, campag, year)

def sql_station_info(station, region, year, campag, monit):
    return """ SELECT a.staz, a.descr, b.descr, codistat, tipo_staz, prof_tot, indice, a.fornit
                FROM stazionedimonitoraggio a, entefornitore b, indicecam c
                WHERE a.fornit = idfornit
                    AND c.staz = a.staz
                    AND c.fornit = a.fornit
                    AND campag = '%s'
                    AND anno_campag = '%s'
                    AND c.staz = '%s'
                    AND c.fornit = '%s'
                    AND c.anno = '2001'
            """ % (campag, year, station, region)

def sql_last_campaign_water():
    return """SELECT anno_campag, campag 
                FROM indicecam 
                WHERE staz IN 
                (SELECT staz 
                    FROM stazionetipomonitoraggio 
                    WHERE codmonit = 'W') 
                    ORDER BY anno_campag DESC, campag DESC LIMIT 1
            """

def sql_gis_stations_interval(minx, miny, maxx, maxy, year, campag, monit):
    """ return stations """
    return """SELECT s.staz AS staz, 
                s.fornit AS fornit, 
                s.descr AS descr,
                s.latg AS latg, 
                s.latp AS latp, 
                s.lats AS lats, 
                s.latpc AS latpc,
                s.longg AS longg, 
                s.longp AS longp, 
                s.longs AS longs, 
                s.longpc AS longpc, 
                s.lat AS lat, 
                s.lon AS lon, 
                s.laty AS laty, 
                s.longx AS longx, 
                s.anno AS anno, 
                s.prof_tot AS prof_tot, 
                s.distanza AS distanza, 
                s.tipo_staz AS tipo_staz, 
                s.frequenza AS frequenza, 
                s.dim_staz AS dim_staz, 
                s.posizione AS posizione, 
                s.codistat AS codistat,
                i.campag AS campag, 
                i.indice AS indice, 
                i.anno_campag AS anno_campag
                FROM (select 
                    stazionedimonitoraggio.staz, 
                    stazionedimonitoraggio.fornit, 
                    stazionedimonitoraggio.descr,
                    stazionedimonitoraggio.latg, 
                    stazionedimonitoraggio.latp, 
                    stazionedimonitoraggio.lats, 
                    stazionedimonitoraggio.latpc,
                    stazionedimonitoraggio.longg, 
                    stazionedimonitoraggio.longp, 
                    stazionedimonitoraggio.longs, 
                    stazionedimonitoraggio.longpc, 
                    stazionedimonitoraggio.lat, 
                    stazionedimonitoraggio.lon, 
                    stazionedimonitoraggio.laty, 
                    stazionedimonitoraggio.longx, 
                    stazionedimonitoraggio.anno, 
                    stazionedimonitoraggio.prof_tot, 
                    stazionedimonitoraggio.distanza, 
                    stazionedimonitoraggio.tipo_staz, 
                    stazionedimonitoraggio.frequenza, 
                    stazionedimonitoraggio.dim_staz, 
                    stazionedimonitoraggio.posizione, 
                    stazionedimonitoraggio.codistat
                    from
                    stazionetipomonitoraggio, stazionedimonitoraggio
                    where stazionetipomonitoraggio.codmonit = '%s'
                    and stazionetipomonitoraggio.codstaz = stazionedimonitoraggio.staz  
                    and stazionetipomonitoraggio.codfornit = stazionedimonitoraggio.fornit
                    and stazionedimonitoraggio.longx BETWEEN %s AND %s
                    AND stazionedimonitoraggio.laty BETWEEN %s AND %s) as s
                    LEFT JOIN (select * from indicecam where anno_campag = '%s' and campag = '%s') as i
                    ON s.staz = i.staz and s.fornit = i.fornit order by indice
                """ % (monit, minx, maxx, miny, maxy, year, campag)

def sql_gis_stations_monit(minx, maxx, miny, maxy, year, monit, campag):
    return """SELECT s.staz AS staz, 
                s.fornit AS fornit, 
                s.descr AS descr,
                s.latg AS latg, 
                s.latp AS latp, 
                s.lats AS lats, 
                s.latpc AS latpc,
                s.longg AS longg, 
                s.longp AS longp, 
                s.longs AS longs, 
                s.longpc AS longpc, 
                s.lat AS lat, 
                s.lon AS lon, 
                s.laty AS laty, 
                s.longx AS longx, 
                s.anno AS anno, 
                s.prof_tot AS prof_tot, 
                s.distanza AS distanza, 
                s.tipo_staz AS tipo_staz, 
                s.frequenza AS frequenza, 
                s.dim_staz AS dim_staz, 
                s.posizione AS posizione, 
                s.codistat AS codistat, 
                a.anno_campag as anno_campag,
                a.campag as campag,
            COUNT(a.anno_campag) FROM
           (SELECT 
                stazionedimonitoraggio.staz AS staz, 
                            stazionedimonitoraggio.fornit AS fornit, 
                            stazionedimonitoraggio.descr AS descr,
                            stazionedimonitoraggio.latg AS latg, 
                            stazionedimonitoraggio.latp AS latp, 
                            stazionedimonitoraggio.lats AS lats, 
                            stazionedimonitoraggio.latpc AS latpc,
                            stazionedimonitoraggio.longg AS longg, 
                            stazionedimonitoraggio.longp AS longp, 
                            stazionedimonitoraggio.longs AS longs, 
                            stazionedimonitoraggio.longpc AS longpc, 
                            stazionedimonitoraggio.lat AS lat, 
                            stazionedimonitoraggio.lon AS lon, 
                            stazionedimonitoraggio.laty AS laty, 
                            stazionedimonitoraggio.longx AS longx, 
                            stazionedimonitoraggio.anno AS anno, 
                            stazionedimonitoraggio.prof_tot AS prof_tot, 
                            stazionedimonitoraggio.distanza AS distanza, 
                            stazionedimonitoraggio.tipo_staz AS tipo_staz, 
                            stazionedimonitoraggio.frequenza AS frequenza, 
                            stazionedimonitoraggio.dim_staz AS dim_staz, 
                            stazionedimonitoraggio.posizione AS posizione, 
                            stazionedimonitoraggio.codistat AS codistat 
            FROM
                stazionetipomonitoraggio, stazionedimonitoraggio
            WHERE stazionetipomonitoraggio.codmonit = '%s'
                AND stazionetipomonitoraggio.codstaz = stazionedimonitoraggio.staz  
                AND stazionetipomonitoraggio.codfornit = stazionedimonitoraggio.fornit  
                AND stazionedimonitoraggio.longx BETWEEN %s AND %s
                AND stazionedimonitoraggio.laty BETWEEN %s AND %s) AS s
            LEFT JOIN (SELECT * FROM analisiprelievo WHERE anno_campag = '%s' AND campag = '%s' AND monit = '%s') AS a ON
            (s.staz = a.staz and s.fornit = a.fornit)

            GROUP BY s.staz, s.fornit
            """ % (monit, minx, maxx, miny, maxy, year, campag, monit)


def sql_gis_stations_plancton(minx, maxx, miny, maxy, year, campag):
    return """SELECT s.staz AS staz, 
                s.fornit AS fornit, 
                s.descr AS descr,
                s.latg AS latg, 
                s.latp AS latp, 
                s.lats AS lats, 
                s.latpc AS latpc,
                s.longg AS longg, 
                s.longp AS longp, 
                s.longs AS longs, 
                s.longpc AS longpc, 
                s.lat AS lat, 
                s.lon AS lon, 
                s.laty AS laty, 
                s.longx AS longx, 
                s.anno AS anno, 
                s.prof_tot AS prof_tot, 
                s.distanza AS distanza, 
                s.tipo_staz AS tipo_staz, 
                s.frequenza AS frequenza, 
                s.dim_staz AS dim_staz, 
                s.posizione AS posizione, 
                s.codistat AS codistat, 
                a.anno_campag as anno_campag,
                a.campag as campag,
            COUNT(a.anno_campag) FROM
           (SELECT 
                stazionedimonitoraggio.staz AS staz, 
                            stazionedimonitoraggio.fornit AS fornit, 
                            stazionedimonitoraggio.descr AS descr,
                            stazionedimonitoraggio.latg AS latg, 
                            stazionedimonitoraggio.latp AS latp, 
                            stazionedimonitoraggio.lats AS lats, 
                            stazionedimonitoraggio.latpc AS latpc,
                            stazionedimonitoraggio.longg AS longg, 
                            stazionedimonitoraggio.longp AS longp, 
                            stazionedimonitoraggio.longs AS longs, 
                            stazionedimonitoraggio.longpc AS longpc, 
                            stazionedimonitoraggio.lat AS lat, 
                            stazionedimonitoraggio.lon AS lon, 
                            stazionedimonitoraggio.laty AS laty, 
                            stazionedimonitoraggio.longx AS longx, 
                            stazionedimonitoraggio.anno AS anno, 
                            stazionedimonitoraggio.prof_tot AS prof_tot, 
                            stazionedimonitoraggio.distanza AS distanza, 
                            stazionedimonitoraggio.tipo_staz AS tipo_staz, 
                            stazionedimonitoraggio.frequenza AS frequenza, 
                            stazionedimonitoraggio.dim_staz AS dim_staz, 
                            stazionedimonitoraggio.posizione AS posizione, 
                            stazionedimonitoraggio.codistat AS codistat 
            FROM
                stazionetipomonitoraggio, stazionedimonitoraggio
            WHERE stazionetipomonitoraggio.codmonit = 'P'
                AND stazionetipomonitoraggio.codstaz = stazionedimonitoraggio.staz
                AND stazionetipomonitoraggio.codfornit = stazionedimonitoraggio.fornit
                AND stazionedimonitoraggio.longx BETWEEN '%s' AND '%s'
                AND stazionedimonitoraggio.laty BETWEEN '%s' AND '%s') AS s
            LEFT JOIN (SELECT * FROM listaspecie WHERE anno_campag = '%s' AND campag = '%s' AND monit = 'P') AS a ON
            (s.staz = a.staz and s.fornit = a.fornit)
            GROUP BY s.staz, s.fornit
        """ % (minx, maxx, miny, maxy, year, campag)

#------------ end work -----------------------------------------------------#


