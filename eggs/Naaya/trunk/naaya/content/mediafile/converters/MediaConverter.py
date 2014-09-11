""" Collection of classes and function used to convert media to flash video.
"""

# Python imports
import re
import os
import logging
import subprocess
from threading import Timer
logger = logging.getLogger('mediafile.converters')
#
# Media converter
#


class MediaConverterError(Exception):
    """Media Convertor Error"""
    pass


def media2flv(ex_file):
    """ Convert media to flv and add metadata
    """
    if not can_convert():
        return "Can not convert (are tools available?)"

    finput = ex_file.get_filename()
    tcv_path = finput + ".tcv"  # to convert
    cvd_path = finput + ".cvd"  # converted
    log = open(finput + '.log', 'w')
    os.rename(finput, tcv_path)

    resolution = get_resolution(tcv_path)
    width = int(resolution[0])/8*8
    height = int(resolution[1])/8*8
    bitrate = width/320 * height/180 * 22050

    cmd = ["ffmpeg", "-y", "-v", "0", "-benchmark", "-i", tcv_path, "-ar",
           bitrate, "-s", "%sx%s" % (width, height), "-b", "1024k",
           "-f", "flv", cvd_path]
    process = subprocess.Popen(cmd, stdout=log, stderr=log)

    TIMEOUT = 3 * 3600  # seconds
    timer = Timer(TIMEOUT, lambda x: x.kill(), [process])
    timer.start()

    exit_code = process.wait()
    timer.cancel()

    if exit_code != 0:
        error = 'MediaConverterError: Exit code %s' % exit_code
        return finish(tcv_path, cvd_path, finput, log, error)
    process = None

    """ Update video index using flvtool2 or finish """
    if not can_index():
        logger.debug("Can not index video (is flvtool2 installed?)")
        return finish(tcv_path, cvd_path, finput, log)
    cmd = ["flvtool2", "-U", cvd_path]
    process = subprocess.Popen(cmd, stdout=log, stderr=log)

    timer = Timer(TIMEOUT, lambda x: x.kill(), [process])
    timer.start()

    exit_code = process.wait()
    timer.cancel()

    if exit_code != 0:
        logger.exception('An error occured while indexing video file.')

    return finish(tcv_path, cvd_path, finput, log)


def finish(tcv_path, cvd_path, finput, log, error=None):
    """ Rename output to done and cleanup """
    if error:
        logger.exception(error)
        log.write(error)
        try:
            os.unlink(cvd_path)
        except Exception, err:
            logger.exception(err)
    else:
        # Cleanup input file
        try:
            os.unlink(tcv_path)
        except Exception, err:
            logger.exception(err)

        # Rename output file to done file
        try:
            os.rename(cvd_path, finput)
        except Exception, err:
            logger.exception(err)
            log.write(
                'MediaConverterError: Could not finish conversion %s' % err)

    # Close log
    log.close()

#
# Private interface
#


def _check_ffmpeg():
    """Checks if ffmpeg is available.

        If ffmpeg is not installed with the proper options (libmp3lame)
        a MediaConverterError exception will be raised.
    """
    process = subprocess.Popen(["ffmpeg", "-h"], shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
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
       If flvtool2 is not installed a MediaConverterError exception
       will be raised.
    """
    process = subprocess.Popen(["flvtool2", "-H"], shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

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
    # logger.exception(media_err)
    logger.warn("ffmpeg2 is not available")
else:
    _is_ffmepg_available = True

_is_flvtool2_available = False
try:
    _check_flvtool2()
except MediaConverterError, media_err:
    # logger.exception(media_err)
    logger.warn("flvtool2 is not available")
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


def get_resolution(video_path):
    txt = subprocess.Popen(['ffmpeg', '-i', video_path],
                           stderr=subprocess.PIPE).communicate()[1]

    for line in txt.splitlines():
        if 'Video: ' in line:
            m = re.search(r'(\d+)x(\d+)', line)
            if m is not None:
                return float(m.group(1)), float(m.group(2))
    raise ValueError('Cannot parse ffmpeg output')
