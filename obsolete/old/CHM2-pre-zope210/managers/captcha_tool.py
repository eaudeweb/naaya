# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila
#

#Python imports
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