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
import logging
import subprocess
import threading
logger = logging.getLogger('mediafile.converters')
#
# Media converter
#
class MediaConverterError(Exception):
    """Media Convertor Error"""
    pass

class MediaConverter(threading.Thread):
    """ Convert any video file to FlashVideoFile (.flv) using ffmpeg and index
    is with flvtool2.
    """
    def __init__(self, fin, fout, fdone, flog):
        threading.Thread.__init__(self)

        self.fin = fin
        self.fout = fout
        self.fdone = fdone

        self.log = open(flog, 'w')
        self.exit_code = 0
        self.process = None

    def step_1(self):
        """ Convert video to flv
        """
        logger.debug('Conversion step 1')

        if not can_convert():
            return self.finish('Can not convert (are tools available?)')

        cmd = ["ffmpeg", "-y", "-v", "0", "-benchmark", "-i", self.fin, "-ar",
               "22050", "-s", "320x240", "-b", "500k", "-f", "flv", self.fout]
        self.process = subprocess.Popen(cmd, stdout=self.log, stderr=self.log)
        return self.step_2()

    def step_2(self):
        """ Wait for step 1 to finish and launch step 3 or exit
        """
        logger.debug('Conversion step 2')

        self.exit_code = self.process.wait()
        if self.exit_code != 0:
            return self.finish('Exit code %s' % self.exit_code)

        self.process = None
        return self.step_3()

    def step_3(self):
        """ Update video index using flvtool2 or finish
        """
        logger.debug('Conversion step 3')

        if not can_index():
            logger.debug("Can not index video (is flvtool2 installed?)")
            return self.finish()

        cmd = ["flvtool2", "-U", self.fout]
        self.process = subprocess.Popen(cmd, stdout=self.log, stderr=self.log)
        return self.step_4()

    def step_4(self):
        """ Wait for step 3 and finish
        """
        logger.debug('Conversion step 4')

        self.exit_code = self.process.wait()
        if self.exit_code != 0:
            logger.exception('An error occured while indexing video file.')
        return self.finish()

    def finish(self, error=None):
        """ If no error rename output to done and cleanup
        """
        if error:
            error = 'MediaConverterError: %s' % error
            logger.exception(error)
            self.log.write(error)

            # Cleanup output file
            try:
                os.unlink(self.fout)
            except Exception, err:
                logger.exception(err)
        else:
            # Cleanup input file
            try:
                os.unlink(self.fin)
            except Exception, err:
                logger.exception(err)

            # Rename output file to done file
            try:
                os.rename(self.fout, self.fdone)
            except Exception, err:
                logger.exception(err)
                self.log.write(
                    'MediaConverterError: Could not finish conversion %s' % err)

        # Close log
        self.log.close()

    def run(self):
        """ Run converter step by step
        """
        return self.step_1()
#
# Private interface
#
def _check_ffmpeg():
    """Checks if ffmpeg is available.

        If ffmpeg is not installed with the proper options (libmp3lame)
        a MediaConverterError exception will be raised.
    """
    process = subprocess.Popen(["ffmpeg", "-h"],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.stdout.read()
    process.wait()

    if process.returncode != 1:
        raise MediaConverterError(
            'could not run ffmpeg: "ffmpeg -h" has exited with code %s' % (
                process.returncode, ))

    if "--enable-libmp3lame" not in stdout:
        raise MediaConverterError(
            'ffmpeg was not compiled with --enable-libmp3lame')

def _check_flvtool2():
    """Checks if flvtool2 is available.

        If flvtool2 is not installed a MediaConverterError exception will be raised.
    """
    process = subprocess.Popen(["flvtool2", "-H"],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.stdout.read()

    process.wait()

    if process.returncode:
        raise MediaConverterError(
            'could not run flvtool2: "flvtool2 -H" has exited with code %s' % (
                process.returncode, ))
#
# Private variables
#
_is_ffmepg_available = False
try:
    _check_ffmpeg()
except MediaConverterError, media_err:
    logger.exception(media_err)
else:
    _is_ffmepg_available = True

_is_flvtool2_available = False
try:
    _check_flvtool2()
except MediaConverterError, media_err:
    logger.exception(media_err)
else:
    _is_flvtool2_available = True

#
# Public interface
#
def can_convert():
    """ Is ffmpeg installed?
    """
    return _is_ffmepg_available

def can_index():
    """ Is flvtool2 installed?
    """
    return _is_flvtool2_available

def media2flv(finput, suffix=""):
    """ Convert media to flv and add metadata
    """
    if not can_convert():
        return "Can not convert (are tools available?)"

    fin = finput + suffix
    tcv = finput + ".tcv" # to convert
    cvd = finput + ".cvd" # converted
    os.rename(fin, tcv)
    media_converter = MediaConverter(tcv, cvd, finput, finput + '.log')
    media_converter.start()

def get_conversion_errors(fpath, suffix=".log"):
    """ Open error file and parse it for errors
    """
    error_path = fpath + suffix

    # If flv file exists conversion is done
    if os.path.isfile(fpath):
        return ""

    try:
        error_file = open(error_path, "r")
    except IOError:
        return ""

    for error in error_file.readlines():
        if "MediaConverterError:" in error:
            error_file.close()
            return error

    error_file.close()
    return ""
