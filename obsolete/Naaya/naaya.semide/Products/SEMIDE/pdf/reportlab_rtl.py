#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web

# This a ReportLab
from reportlab.platypus.paragraph import Paragraph
from reportlab.pdfgen.canvas import Canvas

import textobjectRTL
from copy import copy

class CanvasRTL(Canvas):
    def beginTextRTL(self, x=0, y=0):
        """Returns a fresh text object.  Text objects are used
           to add large amounts of text.  See textobject.PDFTextObject"""
        return textobjectRTL.PDFTextObjectRTL(self, x, y)

class ParagraphRTL(Paragraph):
    """ Used for Right to left languages """
    def beginText(self, x, y):
        canvas = CanvasRTL(self.canv._filename)
        canvas.__dict__ = self.canv.__dict__
        return canvas.beginTextRTL(x, y)