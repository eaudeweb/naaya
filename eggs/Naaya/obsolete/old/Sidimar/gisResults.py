from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from AccessControl.Permissions import view
from OFS.Image import Image
from cStringIO import StringIO
from os.path import join

from Products.Sidimar.Core.drawGraph import drawGraph
from Products.Sidimar.Core.drawCharts import drawCharts
from Products.Sidimar.constants import *

from Core.drawCharts import pie_colors

class gisResults:
    """ """

    security = ClassSecurityInfo()

    def __init__(self):
        """ """
        self.img_path = join(package_home(globals()), 'Core', 'template.png')
        self.font_path = join(package_home(globals()), 'Core', 'pilfonts', 'Arial_10.pil')

    security.declarePrivate('create_directory')
    def create_directory(self, region, year, campaign):
        """ save the graph in the graphs folder """

        root = self.getSite()

        try:    root.manage_addFolder('graphics', '')
        except: pass

        try:    root.graphics.manage_addFolder(year, '')
        except: pass

        try:
            year_folder = getattr(root.graphics, year)
            year_folder.manage_addFolder(campaign[:2], '')
        except: pass

        return getattr(year_folder, campaign[:2])


    security.declarePrivate('_compute_middle')
    def _compute_middle(self, scale):
        """ compute the middle value for scale """
        buf = []
        for s in scale:
            mid = (int(s[-1])-int(s[0]))/3 + int(s[0])
            s.append(float('%.2f' % mid))
            s.sort()
            buf.append(s)
        return buf


    def getSmileyPath(self, row, value):
        """ compute the smiley name """
        return "misc_/Sidimar/s-2%s-%s.gif" % (row, int(value))

    security.declarePrivate('split_seq')
    def split_seq(self, seq, size):
        """ Split up seq in pieces of size """
        return [seq[i:i+size] for i in range(0, len(seq), size)]

    def getSortedDictKeys(self, d):
        """
        Returns a list with dictionary keys sorted.
        """
        keys = d.keys()
        keys.sort()
        return keys

    security.declarePrivate('_prepare_graph')
    def _prepare_graph(self, id, values, xscale='', yscale=''):
        """ prepare """
        graf = drawGraph(self.img_path, self.font_path)
        graf.drawYAxis([yscale])
        #xscale = self._compute_middle(xscale)
        graf.drawXAxis(xscale)
        graf.drawDiagram(values)
        newimg = StringIO()
        graf.saveImage(newimg, 'PNG')
        newimg.seek(0)
        return newimg


    security.declarePrivate('_extract_info')
    def _extract_info(self, records):
        """ """
        info = []
        for rec in records:
            descr = self.mp_codparam(rec)
            if descr not in [TEMP, SALINITA, OXYGEN, PH, CLOROFILLA]:
                info.append(rec)
        return info


    security.declarePrivate('_extract_records')
    def _extract_records(self, records):
        """ """
        temp, sal, ox, ph, clo = [], [], [], [], []
        scale_y = []
        for rec in records:
            buf = []
            cod = self.mp_codparam(rec)
            val = self.mp_valore(rec)
            sca = self.mp_distsup(rec)
            if cod == TEMP:
                temp.append(val)
                scale_y.append(sca)
            elif cod == SALINITA:
                sal.append(val)
            elif cod == OXYGEN:
                ox.append(val)
            elif cod == PH:
                ph.append(val)
            elif cod == CLOROFILLA:
                clo.append(val)
        return [clo, ph, ox, sal, temp], scale_y


    security.declarePrivate('_extract_scales')
    def _extract_scales(self, records):
        """ """
        temp, sal, ox, ph, clo = [], [], [], [], []
        for rec in records:
            buf = []
            cod = self.mp_codparam(rec)
            minval = self.mp_minvalue(rec)
            maxval = self.mp_maxvalue(rec)
            if cod == TEMP:
                temp.append(minval)
                temp.append(maxval)
            elif cod == SALINITA:
                sal.append(minval)
                sal.append(maxval)
            elif cod == OXYGEN:
                ox.append(minval)
                ox.append(maxval)
            elif cod == PH:
                ph.append(minval)
                ph.append(maxval)
            elif cod == CLOROFILLA:
                clo.append(minval)
                clo.append(maxval)
        return [clo, ph, ox, sal, temp]


    security.declarePrivate('generate_graphs')
    def generate_graphs(self, region, year, campaign, scale, data):
        """ """
        scale_data = self._extract_scales(scale)
        buf = {}
        for x in data:
            if not buf.has_key(x['staz']):
                buf[x['staz']] = []
            buf[x['staz']].append(x)

        #create the directory if doesn't exists
        dest_folder = self.create_directory(region, year, campaign)

        for k,v in buf.items():
            #create the graph id
            id_graph = "%s-%s-%s-%s.png" % (region, year, campaign, k)
            graph_data, scale_y = self._extract_records(v) #extract records

            #save the graphs
            try:
                img_data = self._prepare_graph(id, graph_data, scale_data, scale_y)
                if hasattr(dest_folder, id_graph):
                    dest_folder.manage_delObjects([id_graph])
                try:
                    dest_folder.manage_addImage(id_graph, img_data, content_type='image/png')
                    img_ob = dest_folder._getOb(id_graph)
                    img_ob.manage_addProperty('station', k, 'string')
                    img_ob.manage_addProperty('monitor', 'W', 'string')
                    img_ob.manage_addProperty('region', region, 'string')
                except:
                    pass
            except:
                pass

    security.declarePrivate('_get_water_info')
    def _get_water_info(self, station, region, year, campag, monit):
        """  """

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get water information
        info, err = mysql_tool.get_water_info(station, region, year, campag, monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get station description
        stat_descr, err = mysql_tool.get_station_descr(station, region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored description
        data_descr, err = mysql_tool.get_data_monitored_descr(monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get stations information
        station_data, err = mysql_tool.get_station_info(station, region, year, campag, monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        return info, stat_descr, reg_descr, data_descr, year, campag, station_data


    security.declarePublic('getGraph')
    def getGraph(self, region, year, campaign, station):
        """ check if the graph exists """
        id_graph = "%s-%s-%s-%s.png" % (region, year, campaign, station)
        try:
            return self.unrestrictedTraverse('%s/%s/%s/%s' % ('graphics', year, campaign[:2], id_graph))
        except:
            return 0


    security.declarePublic('parseParameters')
    def parseParameters(self, param):
        """ parse the parameters"""
        station, region, year, campag, monit = param.split(',')

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)
        return (reg_descr, campag, station, year, monit)


    security.declarePublic('getWaterInfo')
    def getWaterInfo(self, param, REQUEST=None, RESPONSE=None):
        """ process water information """
        station, region, year, campag, monit = param.split(',')

        records, stat_descr, reg_descr, data_descr, year, campag, station_data = self._get_water_info(station, region, year, campag, monit)

        #remove the graph information
        info = self._extract_info(records)
        return info, stat_descr, reg_descr, data_descr, year, campag, monit, station, region, station_data


    security.declareProtected(view, 'showGraphs')
    def showGraphs(self, region, year, campaign):
        """ """
        results = []
        root = self.getSite()
        graph_folder = root._getOb('graphics')._getOb(year)._getOb(campaign[:2])
        #get all the graphs from this folder
        graphs = graph_folder.objectValues('Image')
        if region:
            results = [x for x in graphs if (x.getId().startswith(region)) and (x.getId().find("-%s-" % campaign) != -1)]
        else:
            results = graphs
        return self.split_seq(results, 2)


    security.declareProtected(view, 'showStations')
    def showStations(self, param='', REQUEST=None, RESPONSE=None):
        """ show the graphs for all stations """
        station, region, year, campaign, monit = param.split(',')
        #get the graph_folder location
        try:
            graph_folder = self.unrestrictedTraverse('%s/%s/%s' % ('graphics', year, campaign[:2]))
        except:
            return 0
        #select all the graphs fom it
        graphs = graph_folder.objectValues('Image')
        #filter the graphs by region
        results = [x for x in graphs if x.region == region]
        return self.split_seq(self.utSortObjsListByAttr(results, 'station', p_desc=0), 4)


    security.declareProtected(view, 'showIndices')
    def showIndices(self, param='', REQUEST=None, RESPONSE=None):
        """ show the indices """
        station, region, year, campaign, monit = param.split(',')
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get water information
        info, err = mysql_tool.get_anual_indices(region, year, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        #process data
        matrix = {}
        for v in info:
            k = v['descr']
            if not matrix.has_key(k):
                matrix[k] = {}
            d = v['distanza']
            if not matrix[k].has_key(d):
                matrix[k][d] = [
                    [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1],
                    [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]
                ]
            mon, poz = int(v['campag'][:2]), v['campag'][2].upper()
            if poz == 'A': poz = 0
            else: poz = 1
            matrix[k][d][mon-1][poz] = v['indice']
        keys = matrix.keys()
        keys.sort()
        return keys, matrix


    security.declareProtected(view, 'getBenthosData')
    def getBenthosData(self, param='', REQUEST=None, RESPONSE=None):
        """ get the benthos data """

        station, region, year, campaign, monit = param.split(',')
        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get water information
        data, err = mysql_tool.get_benthos_data(region, year, campaign, monit, station, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get station description
        stat_descr, err = mysql_tool.get_station_descr(station, region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored description
        data_descr, err = mysql_tool.get_data_monitored_descr(monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        return data, stat_descr, reg_descr, data_descr, station, year


    security.declareProtected(view, 'getPlanctonData')
    def getPlanctonData(self, param='', REQUEST=None, RESPONSE=None):
        """ get the plancton data """
        station, region, year, campaign, monit = param.split(',')
        mysql_tool = self.getMySQLTool()

        charts = drawCharts()

        temp_folder = self.get_temp_folder()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get water information
        data, err = mysql_tool.get_plancton_data(region, year, campaign, monit, station, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get station description
        stat_descr, err = mysql_tool.get_station_descr(station, region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored description
        data_descr, err = mysql_tool.get_data_monitored_descr(monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        fitoplancton = {}
        zooplancton = {}
        for x in list(data):
            if x['codparam'] in FITOPLANCTON_CODES:
                if fitoplancton.has_key(x['descr']):
                    fitoplancton[x['descr']].append(x)
                else:
                    fitoplancton[x['descr']] = [x]
            elif x['codparam'] in ZOOPLANCTON_CODES:
                if zooplancton.has_key(x['descr']):
                    zooplancton[x['descr']].append(x)
                else:
                    zooplancton[x['descr']] = [x]

        #generate 'Fitoplancton' pie chart
        fitoplancton_ob, fitoplancton_legend = self.gen_image_pie_chart(
            temp_folder,
            charts,
            'chart-image-%s-fito-%s-%s-%s.png' % (monit, region, year, campaign),
            'Fitoplancton',
            'Fitoplancton',
            fitoplancton.values())

#        #generate 'Zooplancton' pie chart
        zooplancton_ob, zooplancton_legend = self.gen_image_pie_chart(
            temp_folder,
            charts,
            'chart-image-%s-zoo-%s-%s-%s.png' % (monit, region, year, campaign),
            'Zooplancton',
            'Zooplancton',
            zooplancton.values())


        fito = {}
        sum = 0
        for record in fitoplancton.keys():
            buf = []
            for rec in fitoplancton[record]:
                buf.append((rec['valore'], rec['nome_specie']))
            buf.sort()
            buf.reverse()
            fito[record] = buf

        zoo = {}
        sum = 0
        for record in zooplancton.keys():
            buf = []
            for rec in zooplancton[record]:
                buf.append((rec['valore'], rec['nome_specie']))
            buf.sort()
            buf.reverse()
            zoo[record] = buf

        return fito, zoo, stat_descr, reg_descr, data_descr, station, year, \
            fitoplancton_ob, fitoplancton_legend, zooplancton_ob, zooplancton_legend

    security.declareProtected(view, 'processGenerate')
    def processGenerate(self):
        """ get region, data monitored and year """

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get regions
        regions, err = mysql_tool.get_regions(dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get campaigns
        campaigns,err = mysql_tool.get_campaigns(dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #get years
        years, err = mysql_tool.get_years(dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)
        return (regions, campaigns, years)


    security.declareProtected(view, 'createGraphs') #trebuie protejata cu private
    def createGraphs(self, region, year, campaign, REQUEST=None, RESPONSE=None):
        """ generate graphs """

        mysql_tool = self.getMySQLTool()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get data
        data, err = mysql_tool.get_water_data(year, campaign, region, dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        scale, err = mysql_tool.get_water_scale_info(region, year, campaign, 'W', dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)
        return self.generate_graphs(region, year, campaign, scale, data)

    def get_temp_folder(self):
        """
        Return the temp_folder object.
        """
        return self.getPhysicalRoot()._getOb('temp_folder', None)

    def gen_image_multiple_chart(self, parent, charts, imgid, imgtitle, data):
        """
        Generate an image with a multiple chart.
        """
        keys = data.keys()
        keys.sort()
        glegend, glabels, gvalues = [], [], []
        if len(keys)>0:
            v = data[keys[0]]
            glabels = [x[1] for x in v[1]]
            for i in range(0, len(keys)):
                gvalues.append([])
        index = 0
        for k in keys:
            v = data[k]
            glegend.append(v[0])
            for i in range(0, len(v[1])):
                gvalues[index].append(v[1][i][2])
            index = index + 1
        imgob = parent._getOb(imgid, None)
        imglegend = parent._getOb('legend_%s' % imgid, None)
        if imgob is None:
            if len(glabels) == 0:
                imgsize, imgbuf = charts.geg(
                    gtitle='%s - Dati non disponibili' % imgtitle,
                    gsize='big'
                )
            else:
                imgsize, imgbuf = charts.gmvbg(
                    gtitle=imgtitle,
                    gvalues=gvalues,
                    glabels=glabels,
                    glegend=glegend
                )
            parent.manage_addImage(imgid,
                charts.save_to_string(imgsize, imgbuf),
                title=imgtitle,
                content_type='image/png'
            )
            imgob = parent._getOb(imgid, None)
            #generate legend for this chart
            imgsize, imgbuf = charts.gclegend(glegend=glegend)
            parent.manage_addImage('legend_%s' % imgid,
                charts.save_to_string(imgsize, imgbuf),
                title='Legend %s' % imgtitle,
                content_type='image/png'
            )
            imglegend = parent._getOb('legend_%s' % imgid, None)
        return imgob, imglegend

    def gen_image_simple_chart(self, parent, charts, imgid, imgtitle, codparam, records):
        """
        Generate an image with a simple chart
        """
        gtitle, gstuff = '', []
        for record in records:
            gtitle = record['descr']
            gstuff.append((record['staz'], record['station'], record['valore']))
        gstuff.sort()
        gvalues, glabels =[x[2] for x in gstuff], [x[1] for x in gstuff]
        imgid = imgid % gtitle[:3].lower()
        imgtitle = imgtitle % gtitle
        imgob = parent._getOb(imgid, None)
        if imgob is None:
            if len(glabels) == 0:
                imgsize, imgbuf = charts.geg(
                    gtitle='%s - Dati non disponibili' % gtitle,
                    gsize='small'
                )
            else:
                imgsize, imgbuf = charts.gsvbg(
                    gkey=codparam,
                    gtitle=gtitle,
                    gvalues=gvalues,
                    glabels=glabels
                )
            parent.manage_addImage(imgid,
                charts.save_to_string(imgsize, imgbuf),
                title = imgtitle,
                content_type='image/png'
            )
            imgob = parent._getOb(imgid, None)
        return imgob

    def filter_chart_results(self, results, sum):
        """ """
        chart_values = []
        sum_others = 0
        min_value = sum*2/100
        for res in results:
            if res[0] >= min_value:
                chart_values.append(res)
            else:
                sum_others += res[0]
        return chart_values, sum_others

    def gen_image_pie_chart(self, parent, charts, imgid, imgtitle, gtitle, records, howmany=10):
        """
        Generate an image with a pie chart
        """
        gstuff = []
        sum = 0
        for record in records:
            for r in record:
                sum += r['valore']
                if len(r['nome_specie']) > 40:
                    name = "%s ..." % r['nome_specie'][:30]
                else:
                    name = r['nome_specie']
                gstuff.append((r['valore'], name))

        gstuff.sort()
        gstuff.reverse()
        gstuff, sum_others = self.filter_chart_results(gstuff, sum)
        if len(gstuff)>howmany-1:
            chart_values = gstuff[:howmany]
        else:
            chart_values = gstuff
        chart_values.append((sum_others, 'Others'))
        gvalues, glabels =[x[0] for x in chart_values], [x[1] for x in chart_values]
        imgob = parent._getOb(imgid, None)
        imglegend = parent._getOb('legend_%s' % imgid, None)
        if imgob is None:
            if len(glabels) == 0:
                imgsize, imgbuf = charts.geg(
                    gtitle='%s - Dati non disponibili' % gtitle,
                    gsize='small'
                )
            else:
                imgsize, imgbuf = charts.gpg(
                    gtitle=gtitle,
                    gvalues=gvalues,
                    glabels=glabels
                )
            parent.manage_addImage(imgid,
                charts.save_to_string(imgsize, imgbuf),
                title = imgtitle,
                content_type='image/png'
            )
            imgob = parent._getOb(imgid, None)
            #generate legend for this chart
            imgsize, imgbuf = charts.gclegend(glegend=glabels,
                loc='center', gcolors=pie_colors)
            parent.manage_addImage('legend_%s' % imgid,
                charts.save_to_string(imgsize, imgbuf),
                title='Legend %s' % imgtitle,
                content_type='image/png'
            )
            imglegend = parent._getOb('legend_%s' % imgid, None)
        return imgob, imglegend

    security.declareProtected(view, 'createSedimentiCharts')
    def createSedimentiCharts(self, param, REQUEST=None, RESPONSE=None):
        """
        Generate charts for Sedimenti.
        """
        station, region, year, campaign, monit = param.split(',')

        mysql_tool = self.getMySQLTool()

        charts = drawCharts()

        temp_folder = self.get_temp_folder()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get data
        data, err = mysql_tool.get_sediments_data(region, year, campaign, monit, dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #get station description
        stat_descr, err = mysql_tool.get_station_descr(station, region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored description
        data_descr, err = mysql_tool.get_data_monitored_descr(monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        buf = {}
        for x in data:
            if not buf.has_key(x['codparam']):
                buf[x['codparam']] = []
            buf[x['codparam']].append(x)

        #generate metal charts
        result, others = [], []
        compostiorganoclorurati = {}
        policlorobifenili = {}
        idrocarburi = {}
        granulometria = {}
        for k, v in buf.items():
            if k in SEDIMENTI_METAL_CODES:
                imgid = 'chart-image-%s-met%%s-%s-%s-%s.png' % (monit, region, year, campaign)
                imgtitle = '%%s-%s-%s-%s' % (region, year, campaign)
                result.append(self.gen_image_simple_chart(temp_folder, charts, imgid, imgtitle, k, v))
            elif k == SEDIMENTI_TRIBUTILSTAGNO_CODE:
                imgid = 'chart-image-%s-%%s-%s-%s-%s.png' % (monit, region, year, campaign)
                imgtitle = '%%s-%s-%s-%s' % (region, year, campaign)
                others.insert(0, self.gen_image_simple_chart(temp_folder, charts, imgid, imgtitle, k, v))
            elif k == SEDIMENTI_SPORECLOSTRIDISOLFITORIDUTTORI_CODE:
                imgid = 'chart-image-%s-%%s-%s-%s-%s.png' % (monit, region, year, campaign)
                imgtitle = '%%s-%s-%s-%s' % (region, year, campaign)
                others.append(self.gen_image_simple_chart(temp_folder, charts, imgid, imgtitle, k, v))
            elif k in SEDIMENTI_COMPOSTIORGANOCLORURATI:
                compostiorganoclorurati[k] = (v[0]['descr'], [])
                for x in v:
                    compostiorganoclorurati[k][1].append((x['staz'], x['station'], x['valore']))
                compostiorganoclorurati[k][1].sort()
            elif k in SEDIMENTI_POLICLOROBIFENILI_CODE:
                policlorobifenili[k] = (v[0]['descr'], [])
                for x in v:
                    policlorobifenili[k][1].append((x['staz'], x['station'], x['valore']))
                policlorobifenili[k][1].sort()
            elif k in SEDIMENTI_IDROCARBURI_CODE:
                idrocarburi[k] = (v[0]['descr'], [])
                for x in v:
                    idrocarburi[k][1].append((x['staz'], x['station'], x['valore']))
                idrocarburi[k][1].sort()
            elif k in SEDIMENTI_GRANULOMETRIA_CODE:
                granulometria[k] = (v[0]['descr'], [])
                for x in v:
                    granulometria[k][1].append((x['staz'], x['station'], x['valore']))
                granulometria[k][1].sort()

        result = [(x.title_or_id(), x) for x in result]
        result.sort()
        result = [x[1] for x in result]

        #generate 'Composti Organoclorurati' chart
        compostiorganoclorurati_ob, compostiorganoclorurati_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-idroclor-%s-%s-%s.png' % (monit, region, year, campaign),
            'Composti Organoclorurati',
            compostiorganoclorurati)

        #generate 'Policlorobifenili' chart
        policlorobifenili_ob, policlorobifenili_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-pcb-%s-%s-%s.png' % (monit, region, year, campaign),
            'Policlorobifenili',
            policlorobifenili)

        #generate 'Idrocarburi Policiclici Aromatici' chart
        idrocarburi_ob, idrocarburi_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-ipa-%s-%s-%s.png' % (monit, region, year, campaign),
            'Idrocarburi Policiclici Aromatici',
            idrocarburi)

        #generate 'Granulometria' chart
        granulometria_ob, granulometria_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-gran-%s-%s-%s.png' % (monit, region, year, campaign),
            'Granulometria',
            granulometria)

        return stat_descr, reg_descr, data_descr, station, self.split_seq(result, 2), \
            granulometria_ob, granulometria_legend, \
            compostiorganoclorurati_ob, compostiorganoclorurati_legend, \
            policlorobifenili_ob, policlorobifenili_legend, \
            idrocarburi_ob, idrocarburi_legend, \
            others

    security.declareProtected(view, 'createMolluschiCharts')
    def createMolluschiCharts(self, param, REQUEST=None, RESPONSE=None):
        """
        Generate charts for Molluschi.
        """
        station, region, year, campaign, monit = param.split(',')

        mysql_tool = self.getMySQLTool()

        charts = drawCharts()

        temp_folder = self.get_temp_folder()

        #open connection
        dbconn = mysql_tool.createDbManager()

        #get data
        data, err = mysql_tool.get_molluschi_data(region, year, campaign, monit, dbconn)
        if err: 
            self.setSessionErrors(['Database error'])

        #get station description
        stat_descr, err = mysql_tool.get_station_descr(station, region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get region description
        reg_descr, err = mysql_tool.get_region_descr(region, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #get data monitored description
        data_descr, err = mysql_tool.get_data_monitored_descr(monit, dbconn)
        if err:
            self.setSessionErrors(['Database error'])

        #close connection and return the results
        mysql_tool.destroyDbManager(dbconn)

        buf = {}
        for x in data:
            if not buf.has_key(x['codparam']):
                buf[x['codparam']] = []
            buf[x['codparam']].append(x)

        #generate metal charts
        result, others = [], []
        policlorobifenili = {}
        idrocarburi = {}
        compostiorganoclorurati = {}
        for k, v in buf.items():
            if k in MOLLUSCHI_METAL_CODES:
                imgid = 'chart-image-%s-met%%s-%s-%s-%s.png' % (monit, region, year, campaign)
                imgtitle = '%%s-%s-%s-%s' % (region, year, campaign)
                result.append(self.gen_image_simple_chart(temp_folder, charts, imgid, imgtitle, k, v))
            elif k == MOLLUSCHI_TRIBUTILSTAGNO_CODE:
                imgid = 'chart-image-%s-%%s-%s-%s-%s.png' % (monit, region, year, campaign)
                imgtitle = '%%s-%s-%s-%s' % (region, year, campaign)
                others.insert(0, self.gen_image_simple_chart(temp_folder, charts, imgid, imgtitle, k, v))
            elif k in MOLLUSCHI_COMPOSTIORGANOCLORURATI:
                compostiorganoclorurati[k] = (v[0]['descr'], [])
                for x in v:
                    compostiorganoclorurati[k][1].append((x['staz'], x['station'], x['valore']))
                compostiorganoclorurati[k][1].sort()
            elif k in MOLLUSCHI_POLICLOROBIFENILI_CODE:
                policlorobifenili[k] = (v[0]['descr'], [])
                for x in v:
                    policlorobifenili[k][1].append((x['staz'], x['station'], x['valore']))
                policlorobifenili[k][1].sort()
            elif k in MOLLUSCHI_IDROCARBURI_CODE:
                idrocarburi[k] = (v[0]['descr'], [])
                for x in v:
                    idrocarburi[k][1].append((x['staz'], x['station'], x['valore']))
                idrocarburi[k][1].sort()

        result = [(x.title_or_id(), x) for x in result]
        result.sort()
        result = [x[1] for x in result]

        #generate 'Composti Organoclorurati' chart
        compostiorganoclorurati_ob, compostiorganoclorurati_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-idroclor-%s-%s-%s.png' % (monit, region, year, campaign),
            'Composti Organoclorurati',
            compostiorganoclorurati)

        #generate 'Policlorobifenili' chart
        policlorobifenili_ob, policlorobifenili_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-pcb-%s-%s-%s.png' % (monit, region, year, campaign),
            'Policlorobifenili',
            policlorobifenili)

        #generate 'Idrocarburi Policiclici Aromatici' chart
        idrocarburi_ob, idrocarburi_legend = self.gen_image_multiple_chart(
            temp_folder,
            charts,
            'chart-image-%s-ipa-%s-%s-%s.png' % (monit, region, year, campaign),
            'Idrocarburi Policiclici Aromatici',
            idrocarburi)

        return stat_descr, reg_descr, data_descr, station, self.split_seq(result, 2), \
            compostiorganoclorurati_ob, compostiorganoclorurati_legend, \
            policlorobifenili_ob, policlorobifenili_legend, \
            idrocarburi_ob, idrocarburi_legend, \
            others

InitializeClass(gisResults)
