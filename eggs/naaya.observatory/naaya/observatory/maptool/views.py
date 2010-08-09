import simplejson as json

class MapView(object):
    """A view for the observatory map"""

    def __init__(self, context, request):
        self.context = context
        self.site = context.getSite()
        self.request = request
        self.portal_map = context.getGeoMapTool()

    def xrjs_getClusters(self):
        """ """
        tooltip = """
        <div class="marker-body">
            <small></small>
            <div class="marker-more">
                <a href="http://pivo.edw.ro:7080/test/info/my-geopoint">
                    see more
                </a>
            </div>
        </div>
        """
        return json.dumps(
            {"points":
                [{"lon": "12.58668230000000", "lat": "55.68111860000000",
                    "tooltip": tooltip,
                    "label": "My Geopoint", "icon_name": "mk_symbol271",
                    "id": "my-geopoint"},
                ]
            })

    def xrjs_getTooltip(self):
        """ """
        return """
        <div class="marker-body">
            <small></small>
            <div class="marker-more">
                <a href="http://pivo.edw.ro:7080/test/info/my-geopoint">
                    see more
                </a>
            </div>
        </div>
        """


