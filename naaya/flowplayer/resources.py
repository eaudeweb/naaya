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

class FlowPlayerJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer-6.0.3.min.js'

class FlowPlayerCSS(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer-6.0.3.functional.css'

class FlowPlayerCSSeot(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/fpicons.eot'

class FlowPlayerCSSsvg(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/fpicons.svg'

class FlowPlayerCSSttf(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/fpicons.ttf'

class FlowPlayerCSSwoff(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/fpicons.woff'

class FlowPlayerCSSimg1(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer.png'

class FlowPlayerCSSimg2(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer@2x.png'

class FlowPlayerCSSimg3(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/play_white.png'

class FlowPlayerCSSimg4(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/play_white@x2.png'

class FlowPlayerCSSimg5(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/play_white_rtl.png'

class FlowPlayerCSSimg6(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/play_white_rtl@x2.png'

class ConfigJs(FlowPlayerBase):
    @property
    def resource(self):
        return '/++resource++flowplayer/flowplayer.config.js'

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
