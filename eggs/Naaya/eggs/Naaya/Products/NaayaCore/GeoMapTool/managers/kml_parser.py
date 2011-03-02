
from xml.sax import handler, make_parser

class KMLHandler(handler.ContentHandler):
    current_placemark = {}
    current_element = ''
    is_point = False
    all_placemarks = []

    def startDocument(self):
        self.current_placemark = {}
        self.current_element = ''
        self.is_point = False
        self.all_placemarks = []

    def startElement(self, name, attrs):
        self.current_element = name
        if name == 'Point':
            self.is_point = True

    def characters(self, content):
        if self.current_element == 'name':
            self.current_placemark['name'] = content
        if self.current_element == 'description':
            self.current_placemark['description'] = content
        if self.is_point and self.current_element == 'coordinates':
            longitude, latitude = content.split(',')[0:2]
            self.current_placemark['latitude'] = latitude
            self.current_placemark['longitude'] = longitude

    def endElement(self, name):
        if name == 'Placemark':
            self.all_placemarks.append(self.current_placemark)
            self.current_placemark = {}
        elif name == 'Point':
            self.is_point = False
        else:
            self.current_element=''

    def endDocument(self):
        self.all_placemarks = filter(lambda pl: pl.has_key('latitude'),
                                     self.all_placemarks)

    def get_placemarks(self):
        return self.all_placemarks

def parse_kml(kml_file):
    """
    Parse kml file and return a dictionary
    with title, description and coordinates
    """
    handler = KMLHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.parse(kml_file)
    return handler.get_placemarks()
