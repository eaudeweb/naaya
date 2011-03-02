from cStringIO import StringIO
from Captcha.Visual import Text, Backgrounds, Distortions, ImageCaptcha
from Captcha import Words

class captcha_tool(ImageCaptcha):
    """ captcha tool """
    def getLayers(self):
        word = Words.defaultWordList.pick()
        self.addSolution(word)
        return [
            Backgrounds.SolidColor(),
            Text.TextLayer(word, fontFactory=Text.FontFactory((15, 15), "vera"),
                textColor='black', borderSize=0),
            Distortions.WarpBase(),
            ]