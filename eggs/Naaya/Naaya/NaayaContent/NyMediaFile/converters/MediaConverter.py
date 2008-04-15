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

# Python imports
import os
from popen2 import popen3, popen4 # TODO Python 2.5: use the new subprocess module
import sys
from threading import Thread

# Zope imports
from zLOG import LOG, WARNING, DEBUG


class MediaConverterError(Exception):
    """Media Convertor Error"""
    pass

class MediaConverter(Thread):
    """ Media Converter
    """
    def __init__(self, finput, foutput, fdone):
        self.finput = finput
        self.foutput = foutput
        if sys.platform == 'win32':
            self.fdone = os.path.basename(fdone)
        else:
            self.fdone = fdone
        Thread.__init__(self)
    
    def execute(self, cmd):
        """ Execute fs cmd"""
        LOG('NaayaContent.NyMediaFile.convertors.MediaConverter', DEBUG, 'executing command: %s' % cmd)
        return os.popen4(cmd)

    def run(self):
        """Converts media to flash video (flv) files"""
        if sys.platform == 'win32':
            # TODO: Improve (fix) conversion on Win Platform
            cmd = "ffmpeg -y -v 0 " \
                    "-benchmark " \
                    "-i %(in)s " \
                    "-ar 22050 -s 320x240 -b 500k -f flv " \
                    "%(out)s > %(done)s.log " \
                    "&& del %(in)s "
            if _is_flvtool2_available:
                cmd += "&& flvtool2 -U %(out)s >> %(done)s.log "
            else:
                LOG('NaayaContent.NyMediaFile.convertors.MediaConverter', WARNING, 'can not update FLV with an onMetaTag event, because flvtool2 is not available')
            cmd += "&& rename %(out)s %(done)s"
        else:
            cmd = "ffmpeg -y -v 0 " \
                    "-benchmark " \
                    "-i %(in)s " \
                    "-ar 22050 -s 320x240 -b 500k -f flv " \
                    "%(out)s > %(done)s.log " \
                    "&& rm %(in)s "
            if _is_flvtool2_available:
                cmd += "&& flvtool2 -U %(out)s >> %(done)s.log "
            else:
                LOG('NaayaContent.NyMediaFile.convertors.MediaConverter', WARNING, 'can not update FLV with an onMetaTag event, because flvtool2 is not available')
            cmd += "&& mv %(out)s %(done)s"
        cmd = cmd % {"in": self.finput,
                     "out": self.foutput,
                     "done": self.fdone}
        return self.execute(cmd)


def _check_ffmpeg():
    """Checks if ffmpeg is available.

        If ffmpeg is not installed with the proper options (libmp3lame)
        a MediaConverterError exception will be raised.
    """
    status = os.system("ffmpeg -h")
    if sys.platform != 'win32' and os.WIFEXITED(status): # TODO: portable way to get the exit code
        exit_code = os.WEXITSTATUS(status)
    else:
        exit_code = status
    if exit_code:
        raise MediaConverterError('could not run ffmpeg: "ffmpeg -h" has exited with code %s' % (exit_code, ))
    child_stdout_and_stderr, child_stdin = popen4("ffmpeg -h")
    error = child_stdout_and_stderr.read()
    if "--enable-libmp3lame" not in error:
        raise MediaConverterError('ffmpeg was not compiled with --enable-libmp3lame; ffmpeg -h returned: %s' % (error, ))

def _check_flvtool2():
    """Checks if flvtool2 is available.

        If flvtool2 is not installed a MediaConverterError exception will be raised.
    """
    status = os.system("flvtool2 -H")
    if sys.platform != 'win32' and os.WIFEXITED(status): # TODO: portable way to get the exit code
        exit_code = os.WEXITSTATUS(status)
    else:
        exit_code = status
    if exit_code:
        raise MediaConverterError('could not run flvtool2: "flvtool2 -H" has exited with code %s' % (exit_code, ))
    return True

_is_ffmepg_available = _is_flvtool2_available = False
try:
    _check_ffmpeg()
    _is_ffmepg_available = True
    _check_flvtool2()
    _is_flvtool2_available = True
except MediaConverterError, ex:
    LOG('NaayaContent.NyMediaFile.convertors', WARNING, "%s" % (ex, ))

def can_convert():
    return _is_ffmepg_available

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
    if not can_convert():
        return "Can not convert (are tools available?)"
    
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
