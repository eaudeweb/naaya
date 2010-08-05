#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)


__doc__ = """
    GML to KML converter module.
"""


from Products.NaayaCore.GeoMapTool.kml_generator  import KMLGenerator
from Products.NaayaCore.GeoMapTool.gml import GMLStructure
from Products.NaayaCore.GeoMapTool.gml_parser import gml_import
from Products.NaayaCore.GeoMapTool.gml_sd_parser import gml_sd_import
from Products.NaayaCore.GeoMapTool.utils import utOpen, utGMLEncode
from Products.NaayaCore.GeoMapTool.managers.geo_utils import transcalc
from Products.NaayaCore.GeoMapTool.constants import *

import sys, os
import optparse
try:
    import msvcrt
except:
    pass

def gml_to_kml(gml_file, schema_file, path):
    #generate name
    name = gml_file[:gml_file.rfind('.')]

    #file read
    input_gml = utOpen(gml_file)
    if not schema_file:
        schema_file = XSD_FILE
    input_schema = utOpen(schema_file)

    conv_gml = GMLStructure()

    #fill schema(dbf) information
    try:
        conv_gml = gml_sd_import(input_schema.read())
    except Exception, strerror:
        return "", strerror

    conv_gml.setGeo_name(name)

    # fill geometry
    conv_gml = gml_import(input_gml.read(),conv_gml)

    # GML output
    kml_generator = KMLGenerator()

    kml_data = kml_generator.fillKMLHeader()
    kml_data += kml_generator.fillKMLStyle()
    for m in range(len(conv_gml.getShp_records())):
        for n in range (len(conv_gml.getShp_records()[m])):
            x,y = transcalc((conv_gml.getShp_records()[m][n])[0][0],(conv_gml.getShp_records()[m][n])[0][1],10)
        recdbf_toadd = {}
        for l in range (len(conv_gml.getDbf_records()[m])):
            ntag, valtag = conv_gml.getDbf_records()[m][l]
            recdbf_toadd[ntag] = utGMLEncode(str(valtag),'')

        kml_template = []
        ka = kml_template.append
        ka('Category: <b>%s</b>' % str(recdbf_toadd['symbol_label']))
        ka('<br><br>')
        ka('<img src="%s/getSymbolPicture?id=%s" />' % (path, str(recdbf_toadd['symbol_id'])))
        ka('<br><br>')
        ka('Title: <b><a href="%s">%s</a></b>' % (str(recdbf_toadd['identifier']), str(recdbf_toadd['title'])))
        ka(' <br><br>')
        ka('Url: <i>%s</i>' % str(recdbf_toadd['url']))
        my_kml = '\n'.join(kml_template)

        kml_data += kml_generator.fillKMLPoint(str(recdbf_toadd['title']), my_kml, '%s/getSymbolPicture?id=%s' % (path, str(recdbf_toadd['symbol_id'])), \
        x, y)

    kml_data += kml_generator.fillKMLFooter()
    return kml_data

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option('--gml')
    parser.add_option('--schema')
    parser.add_option('--path')

    try:    options, args = parser.parse_args()
    except: options = None

    if not options or not options.gml:
        print __doc__
        print "For help use --help"
    else:
        if sys.platform == "win32":
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        sys.stdout.write(gml_to_kml(gml_file=options.gml, schema_file=options.schema, path=options.path))
