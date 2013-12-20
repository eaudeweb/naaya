
__doc__ = """
    Google Earth KML template module.
"""

DEFAULT_STYLE = '''<Style id="myDefaultStyles">
    <IconStyle id="IconStyle">
        <color>ff0ff0ff</color>
        <Icon>
            <href>root://icons/palette-4.png</href>
            <x>160</x>
            <y>128</y>
            <w>32</w>
            <h>32</h>
        </Icon>
    </IconStyle>
    <LabelStyle id="defaultLabelStyle">
        <color>7fffaaff</color>
        <scale>1.5</scale>
    </LabelStyle>
    <LineStyle id="defaultLineStyle">
        <color>ff0000ff</color>
        <width>15</width>
    </LineStyle>
    <PolyStyle id="defaultPolyStyle">
        <color>ff0000ff</color>
        <fill>1</fill>
        <outline>1</outline>
    </PolyStyle>
</Style>'''

class kml_generator:

    def __init__(self):
        """ constructor """
        pass

    def get_default_style(self):
        return DEFAULT_STYLE

    def open_style(self, id):
        return '<Style id="%s">' % id

    def close_style(self):
        return '</Style>'
