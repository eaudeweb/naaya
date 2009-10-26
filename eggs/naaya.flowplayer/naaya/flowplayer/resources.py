from Products.Five import BrowserView

class FlowPlayerBase(BrowserView):
    """
    Hack view to avoid ++resource++ in url as Adobe Flash
    interpret '+' as a 'space'
    """
    @property
    def resource(self):
        """ To be overrided
        """
        raise NotImplementedError

    def __call__(self, **kwargs):
        """ Get resource
        """
        res = self.context.unrestrictedTraverse(self.resource)
        return res.GET()

class FlowPlayer(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer-3.1.5.swf'

class FlowPlayerJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer-3.1.4.min.js'

class ConfigJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer.config.js'

class ControlsPlugin(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/plugins/controls/flowplayer.controls-3.1.5.swf'

class ControlsTubePlugin(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/plugins/controls/flowplayer.controls-tube-3.1.4.swf'

class CaptionPlugin(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/plugins/caption/flowplayer.captions-3.1.4.swf'

class ContentPlugin(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/plugins/content/flowplayer.content-3.1.0.swf'

class SubRip(BrowserView):
    """ Get subtitle property """
    def __call__(self, **kwargs):
        self.request.response.setHeader('content-type', 'application/octet-stream')
        return getattr(self.context, 'subtitle', '')
