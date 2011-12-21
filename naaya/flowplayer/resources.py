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
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/flowplayer-3.2.7.swf'

class FlowPlayerJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer-3.2.6.js'

class ConfigJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer.config.js'

class ControlsPlugin(FlowPlayerBase):
    @property
    def resource(self):
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/plugins/controls/flowplayer.controls-3.2.3.swf'

class ControlsTubePlugin(FlowPlayerBase):
    @property
    def resource(self):
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/plugins/controls/flowplayer.controls-tube-3.1.4.swf'

class CaptionPlugin(FlowPlayerBase):
    @property
    def resource(self):
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/plugins/caption/flowplayer.captions-3.2.3.swf'

class ContentPlugin(FlowPlayerBase):
    @property
    def resource(self):
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/plugins/content/flowplayer.content-3.2.0.swf'

class AudioPlugin(FlowPlayerBase):
    @property
    def resource(self):
        self.request.response.enableHTTPCompression(disable=True)
        return '/++resource++flowplayer/plugins/audio/flowplayer.audio-3.2.2.swf'

class SubRip(BrowserView):
    """ Get subtitle property """
    def __call__(self, **kwargs):
        self.request.response.setHeader('content-type', 'application/octet-stream')
        return getattr(self.context, 'subtitle', '')

class StartupImage(BrowserView):
    """ Get startup image """
    def __call__(self, **kwargs):
        self.request.response.setHeader('content-type', 'image/jpeg')
        return self.context.startup_image.send_data(self.request.response, as_attachment=False)
