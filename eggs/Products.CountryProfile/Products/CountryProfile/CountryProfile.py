# -*- coding: utf-8 -*-
"""Using an existing MySQL database display some graphs and statistics. Also
perform searchs on the data
"""
import os
try:
    import json
except ImportError:
    import simplejson as json

from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.component import getUtility

from Products.NaayaCore.LayoutTool.DiskFile import allow_path
from naaya.core.zope2util import force_to_unicode
from naaya.core.StaticServe import StaticServeFromFolder

from MySQLConnector import MySQLConnector
import queries
import utils

TARGET_DIR = os.path.join(CLIENT_HOME, '..', 'country_profile')
try:
    os.mkdir(TARGET_DIR)
except OSError: #Directory exists
    pass

allow_path('Products.PyDigirSearch:www/css/')

manage_add_html = PageTemplateFile('zpt/manage_add', globals())
def manage_add_object(self, id, REQUEST=None):
    """ Create new CountryProfile object from ZMI"""

    ob = CountryProfile(id)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob

class CountryProfile(SimpleItem):
    """CountryProfile"""

    meta_type = 'MedwisCountryProfile'
    icon = 'meta_type.gif'
    security = ClassSecurityInfo()

    manage_options = (
        SimpleItem.manage_options + (
            {'label' : 'Properties', 'action' :'manage_edit_html'},
        )
    )
    _v_conn = None

    www = StaticServeFromFolder("www/", globals())

    index = PageTemplateFile('zpt/index', globals())

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/manage_edit', globals())

    def __init__(self, id):
        self.id = id
        self.mysql_connection = {}
        self.mysql_connection['host'] = 'localhost'
        self.mysql_connection['name'] = 'medwis'
        self.mysql_connection['user'] = 'cornel'
        self.mysql_connection['pass'] = 'cornel'
        self.charts = []

    @property
    def dbconn(self):
        """Create and return a MySQL connection object"""
        if self._v_conn is not None:
            return self._v_conn
        else:
            self._v_conn = MySQLConnector()
            self._v_conn.open(self.mysql_connection['host'],
                              self.mysql_connection['name'],
                              self.mysql_connection['user'],
                              self.mysql_connection['pass'])
            return self._v_conn

    def __del__(self):
        """Close db connection"""
        if self._v_conn is not None:
            self._v_conn.close()

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """Save mysql connection data"""

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            params = dict(REQUEST.form)
        else:
            params = kwargs

        self.mysql_connection = {}
        self.mysql_connection['host'] = params.pop('mysql_host')
        self.mysql_connection['name'] = params.pop('mysql_name')
        self.mysql_connection['user'] = params.pop('mysql_user')
        self.mysql_connection['pass'] = params.pop('mysql_pass')
        refresh = params.pop('refresh_charts')
        if refresh:
            self.charts = []
        self._p_changed = True

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    def index_html(self, REQUEST):
        """ temporary function. only for testing purposes."""
        result = self.query("get_country_code",
                                     label_en='Tunisia')
        if result:
            country_code = result['CNT_CODE']
        else:
            return ""

        indicator = REQUEST.get('indicator', 'U24')
        source = REQUEST.get('source', 'aquastat')
        year = REQUEST.get('year', '2000')
        result = self.query('get_country_comparision', var=indicator, src=source, year=year)

        return self.index(cprofile=self, ccode=country_code, records=result)

    security.declarePublic('get_chart')
    def get_chart_image(self, data, **kw):
        """Return a image file path

        Arguments::

            data -- a list containing the X,Y data representation
        """
        from pygooglechart import SimpleLineChart, Axis

        # Set the vertical range from 0 to 100
        try:
            max_y = max(data['y'])
            min_y = min(data['y'])
        except:
            min_y = 0
            max_y = 100
        width = int(kw.get('width', 600))
        height = int(kw.get('height', 250))
        # Chart size of widthxheight pixels and specifying the range for the Y axis
        chart = SimpleLineChart(width, height, y_range=[min_y, max_y])

        # Add the chart data
        chart.add_data(data['y'])

        # Set the line colour to blue
        chart.set_colours(['0000FF'])

        try:
            step_x = int(100/(len(data['x'])-1))
        except:
            step_x = 0
        chart.set_grid(step_x, 10, 5, 5)

        # The Y axis labels contains min_y to max_y spling it into 10 equal parts,
        #but remove the first number because it's obvious and gets in the way
        #of the first X label.
        left_axis = range(min_y, max_y + 1, (max_y - min_y)/10)
        left_axis[0] = ''
        chart.set_axis_labels(Axis.LEFT, left_axis)

        # X axis labels
        chart.set_axis_labels(Axis.BOTTOM, data['x'])

        #Generate an hash from arguments
        kw_hash = hash(tuple(sorted(kw.items())))
        data_hash = hash(tuple(sorted([(k, tuple(v))
            for k, v in data.iteritems()])))
        args_hash = str(kw_hash) + str(data_hash)

        image_path = os.path.join(TARGET_DIR, "%s.png" % args_hash)

        if bool(kw.get('refresh', False)) or args_hash not in self.charts:
            #Get image from google chart api
            chart.download(image_path)
            self.charts.append(args_hash)
            self._p_changed = True

        return image_path

    def get_chart(self, REQUEST=None, **kw):
        """Respond with an image of the simple line chart"""
        data = {}
        data['x'] = []
        data['y'] = []

        if REQUEST is not None:
            kw.update(REQUEST.form)

        chart_query = {
            'src': kw.pop("src"),
            'var': kw.pop("var"),
            'cnt': kw.pop("cnt"),
        }

        rows = self.query('get_chart_data', **chart_query)
        for row in rows:
            year = str(row['val_year'])
            if year not in data['x']:
                data['x'].append(year)
            data['y'].append(int(row['val']))

        image_path = self.get_chart_image(data, **kw)
        image_fd = open(image_path, 'rb')
        image = image_fd.read()
        image_fd.close()

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Length', len(image))
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/png')
        return image

    def get_bar_chart_image(self, data, **kw):
        """ Return image path of downloaded image from google charts api"""

        if len(data['y']) == 0:
            return ''

        from pygooglechart import StackedHorizontalBarChart, Axis

        width = int(kw.get('width', 400))
        height = int(kw.get('height', 250))

        chart = StackedHorizontalBarChart(width, height,
                                        y_range=[0, len(data['x'])])
        max_y = max(data['y'])

        chart.add_data(data['y'])
        chart.set_colours(['76A4FB'])
        chart.set_axis_labels(Axis.LEFT, data['x'])
        chart.set_axis_labels(Axis.BOTTOM, range(0, max_y + 1,
                                               (max_y)/5))

        #Generate an hash from arguments
        kw_hash = hash(tuple(sorted(kw.items())))
        data_hash = hash(tuple(sorted([(k, tuple(v))
            for k, v in data.iteritems()])))
        args_hash = str(kw_hash) + str(data_hash)
        
        image_path = os.path.join(TARGET_DIR, "%s.png" % args_hash)

        if bool(kw.get('refresh', False)) or args_hash not in self.charts:
            #Get image from google chart api
            chart.download(image_path)
            self.charts.append(args_hash)
            self._p_changed = True
        
        return image_path

    def get_bar_chart(self, REQUEST=None, **kw):
        """Respond with an image of the horizontal stacked line chart"""

        data = {}
        data['x'] = []
        data['y'] = []

        if REQUEST is not None:
            kw.update(REQUEST.form)

        rows = []
        if 'year' in kw:
            chart_query = {
                'var': kw.pop("var"),
                'src': kw.pop("src"),
                'year': kw.pop("year"),
            }

            rows = self.query('get_country_comparision', **chart_query)
        elif 'cnt_code' in kw and 'src' in kw:
            chart_query = {
                'var': kw.pop("var"),
                'src': kw.pop("src"),
                'cnt': kw.pop("cnt_code"),
            }

            rows = self.query('get_year_comparision', **chart_query)
        elif 'cnt_code' in kw and 'var' in kw:
            chart_query = {
                'var': kw.pop("var"),
                'cnt': kw.pop("cnt_code"),
            }

            rows = self.query('get_source_comparision', **chart_query)

        for row in rows:
            try:
                ccode = str(row['val_cnt_code'])
            except KeyError:
                ccode = str(row['val_year'])

            if ccode not in data['x']:
                data['x'].append(ccode)
            data['y'].append(int(row['val']))

        data['x'].reverse()
        kw['height'] = 27 * (len(data['x']) + 1)
        image_path = self.get_bar_chart_image(data, **kw)
        try:
            image_fd = open(image_path, 'rb')
            image = image_fd.read()
            image_fd.close()
        except IOError:
            if REQUEST is not None:
                REQUEST.RESPONSE.setStatus(404)
            return 'Not found'

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Length', len(image))
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/png')
        return image

    security.declarePublic('getUtility')
    def getUtility(self, name):
        if hasattr(utils, name):
            return getattr(utils, name)

    def query(self, name, **kw):
        """Execute some query and return the data"""
        if hasattr(queries, name):
            return getattr(queries, name)(self.dbconn, **kw)

    security.declarePublic('query_select_json')
    def query_select_json(self, name, fval, flabel, REQUEST):
        """ Return a jsoned list of dicts with keys made of `fields` based on
        `query`

        """

        data = []
        if hasattr(queries, name):

            query_args = {} #variable namespacing
            for k, v in REQUEST.form.iteritems():
                if '-' in k:
                    k = k.split('-')[1]
                query_args[k] = v

            rows = getattr(queries, name)(self.dbconn, **query_args)
            if len(rows):
                i = 0
                for row in rows:
                    data.append({})
                    for field, value in row.iteritems():
                        if field == fval:
                            data[i]['val'] = value
                        if field == flabel:
                            data[i]['label'] = value
                    i += 1

        json_data = json.dumps(data)
        REQUEST.RESPONSE.setHeader('Content-Length', len(json_data))
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
        return json_data

InitializeClass(CountryProfile)
