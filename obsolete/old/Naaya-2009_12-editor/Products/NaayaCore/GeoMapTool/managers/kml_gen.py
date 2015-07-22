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
    Google Earth KML template module.
"""

class kml_generator:

    def __init__(self):
        """ constructor """
        pass

    def header(self):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<kml xmlns="http://earth.google.com/kml/2.2">\n'
            '<Document>'
            )

    def style(self):
        return (
            '<Style id="myDefaultStyles">\n'
            '<IconStyle id="IconStyle">\n'
            '<color>ff0ff0ff</color>\n'
            '<Icon>\n'
            '<href>root://icons/palette-4.png</href>\n'
            '<x>160</x>\n'
            '<y>128</y>\n'
            '<w>32</w>\n'
            '<h>32</h>\n'
            '</Icon>\n'
            '</IconStyle>\n'
            '<LabelStyle id="defaultLabelStyle">\n'
            '<color>7fffaaff</color>\n'
            '<scale>1.5</scale>\n'
            '</LabelStyle>\n'
            '<LineStyle id="defaultLineStyle">\n'
            '<color>ff0000ff</color>\n'
            '<width>15</width>\n'
            '</LineStyle>\n'
            '<PolyStyle id="defaultPolyStyle">\n'
            '<color>ff0000ff</color>\n'
            '<fill>1</fill>\n'
            '<outline>1</outline>\n'
            '</PolyStyle>\n'
            '</Style>'
            )

    def add_point(self, id, title, description, icon_url, in_long, in_lat, geo_type, map_path, item_path, item_url, item_address):
        return (
            '<Placemark>\n'
            '<Style id="%s">\n'
            '<IconStyle id="%s">\n'
            '<Icon>\n'
            '<href>%s</href>\n'
            '<x>128</x>\n'
            '<y>64</y>\n'
            '<w>32</w>\n'
            '<h>32</h>\n'
            '</Icon>\n'
            '</IconStyle>\n'
            '</Style>\n'
            '<name>%s</name>\n'
            '<description><![CDATA[%s]]></description>\n'
            '<visibility>1</visibility>\n'
            '<styleUrl>#%s</styleUrl>\n'
            '<Point id="%s">\n'
            '<coordinates>%s,%s,0.0</coordinates>\n'
            '</Point>\n'
            '</Placemark>'
            ) % (id, id, icon_url, title, \
                self.add_description(item_path, title, item_address, description, icon_url, geo_type, item_url), \
                id, id, in_long, in_lat)

    def add_description(self, ipath, ititle, iaddr, idescr, msymurl, msym, iurl):
        return (
            '<img src="%s" />'
            '<b><a href="%s">%s</a></b>'
            '<BR><BR>%s'
            '<BR><BR>'
            '<b>%s</b><BR>'
            'Category: %s'
            '<BR>'
            'Details: %s'
            ) % (msymurl, ipath, ititle, idescr, iaddr, msym, iurl)

    def footer(self):
        return (
            '</Document>\n'
            '</kml>'
            )