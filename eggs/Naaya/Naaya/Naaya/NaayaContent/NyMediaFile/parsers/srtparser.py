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
# Alin Voinea, Eau de Web
""" SubRip parser
"""
import re, sys
from parser import Parser

class SRTParser(Parser):
    """ Parse subtitle text of type srt
    """
    def parse(self):
        """ Parse text
        """
        text = self.text.replace('\r', '')
        text = text.strip().strip("\n")
        p = re.compile(" *\n *\n")
        
        blocks = p.split(text)
        res = []
        for block in blocks:
            try:
                title, time, subtitle = self._compile_text(block)
                start, stop = self._compile_time(time)
            except AttributeError, IndexError:
                #Invalid block, drop it.
                continue
            res.append({
                "title": title,
                "start": start,
                "stop": stop,
                "subtitle": subtitle
                })
        return res
    
    def _compile_text(self, text):
        pat = r" *(\d+) *\n *(\d\d:\d\d:\d\d,\d\d\d *--> *\d\d:\d\d:\d\d,\d\d\d) *\n *(.+)"
        rex = re.compile(pat, re.MULTILINE | re.DOTALL)
        res = rex.match(text)
        return res.group(1, 2, 3)
    
    def _compile_time(self, text):
        pat = r" *(\d\d):(\d\d):(\d\d),(\d\d\d) *--> *(\d\d):(\d\d):(\d\d),(\d\d\d) *"
        rex = re.compile(pat)
        res = rex.match(text)
        start = [int(x) for x in res.group(1, 2, 3, 4)]
        stop = [int(x) for x in res.group(5, 6, 7, 8)]
        start = start[0] * 3600 + start[1] * 60 + start[2] + start[3] / 1000.0
        start = start
        stop = stop[0] * 3600 + stop[1] * 60 + stop[2] + stop[3] / 1000.0
        stop = stop
        return start, stop

if __name__ == "__main__":
    input = len(sys.argv) >=2 and sys.argv[1] or "input.srt"
    input = open(input, 'r')
    text = input.read()
    input.close()
    
    parser = SRTParser(text)
    print parser.parse()
