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
""" Collection of classes and function used to convert media to flash video.
"""
import os
import sys
from threading import Thread

class MediaConverter(Thread):
    """ Media Converter
    """
    def __init__(self, finput, foutput, fdone):
        self.finput = finput
        self.foutput = foutput
        self.fdone = fdone
        Thread.__init__(self)
    
    def execute(self, com):
        """ Execute fs com
        """
        return os.popen4(com)
    
    def run(self):
        """Converts media to flash video (flv) files"""
        if sys.platform == 'win32':
            # TODO: Handle conversion on Win Platform
            return
        
        return self.execute("ffmpeg -y -v 0 "
                            "-benchmark "
                            "-i %(in)s "
                            "-ar 22050 -s 320x240 -b 500k -f flv "
                            "%(out)s &> %(done)s.log "
                            "&& rm %(in)s "
                            "&& flvtool2 -U %(out)s >> %(done)s.log "
                            "&& mv %(out)s %(done)s" % 
                            {
                                "in": self.finput,
                                "out": self.foutput,
                                "done": self.fdone
                            })

def check_for_tools():
    # Check for ffmpeg
    fin, ferr = os.popen4("ffmpeg")
    error = ferr.read()
    error = error.lower()
    
    # Check for ffmpeg installation
    if "ffmpeg: command not found" in error:
        return "ffmpeg not installed."
    
    # Check for mp3 support
    if "--enable-libmp3lame" not in error:
        return "ffmpeg compile error, you should compile " + \
            "it with --enable-libmp3lame. E.g: ./configure --enable-libmp3lame"
    
    # Check for flvtool2
    fin, ferr = os.popen4("flvtool2")
    error = ferr.read()
    error = error.lower()
    if "flvtool2: command not found" in error:
        return "flvtool2 not installed."
    return ""

def get_conversion_errors(fpath, suffix=".log"):
    """ Open error file and parse it for errors
    """
    error_path = fpath + suffix
    if os.path.isfile(fpath):
        # Clean log files
        os.unlink(error_path)
        return ""
    
    try:
        error_file = open(error_path, "r")
    except IOError:
        return ""
    
    for error in error_file.readlines():
        # flvtool2 errors
        if "ERROR:" in error:
            error_file.close()
            return error
    
        # ffmpeg errors
        # TODO: Better error catch algorithm
        err_str = fpath + ".tcv:"
        if err_str in error:
            error_file.close()
            error = error.replace(err_str, "ERROR:", 1)
            return error
    
    error_file.close()
    return ""

def media2flv(finput, suffix=""):
    """ Convert media to flv and add metadata
    """
    fin = finput + suffix
    # Check for available server tools
    error = check_for_tools()
    if error:
        return error
    
    tcv = finput + ".tcv" # to convert
    cvd = finput + ".cvd" # converted
    os.rename(fin, tcv)
    
    conv = MediaConverter(tcv, cvd, finput)
    conv.start()
    conv.join()
    return ""

if __name__ == "__main__":
    argv = sys.argv
    if(len(argv)>1):
        filepath = sys.argv[1]
    else:
        filepath = "video.flv"
    
    print media2flv(filepath)
