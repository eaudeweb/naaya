""" Collection of classes and function used to convert media to flash video.
"""

from threading import Timer
import logging
import os
import re
import shutil
import subprocess
import tempfile

logger = logging.getLogger('mediafile.converters')


class MediaConverterError(Exception):
    """Media Convertor Error"""
    pass

def media2flv(ex_file):
    """ Convert media to flv and add metadata
    """
    if not can_convert():
        return "Can not convert (are tools available?)"

    tempdir = tempfile.mkdtemp(prefix="convert-")

    finput = ex_file.get_filename()
    fpath, fname = os.path.split(finput)
    tcv_path = finput
    #tcv_path = os.path.join(tempdir, fname + ".tcv") # to convert
    cvd_path = os.path.join(tempdir, fname + ".cvd") # converted
    log = open(os.path.join(tempdir, fname + '.log'), 'w')
    #os.rename(finput, tcv_path)

    resolution = get_resolution(tcv_path)
    aspect_ratio = resolution[0]/resolution[1]
    height = int(320/aspect_ratio)/8*8

    #ex_file.aspect_ratio = aspect_ratio
    #ex_file._p_changed = True

    cmd = [CONVERSION_TOOL, "-y", "-v", "0", "-benchmark", "-i", tcv_path, "-ar",
           "22050", "-s", "320x%s" % height, "-b", "500k", "-f", "flv", cvd_path]
    process = subprocess.Popen(cmd, stdout=log, stderr=log)

    TIMEOUT = 3600 #seconds
    timer = Timer(TIMEOUT, lambda x: x.kill(), [process])
    timer.start()

    exit_code = process.wait()
    timer.cancel()

    if exit_code != 0:
        logger.exception('MediaConverterError: Exit code %s' % exit_code)
        try:
            shutil.rmtree(tempdir)
        except Exception, err:
            logger.exception(err)
        return

    process = None

    """ Update video index using flvtool2 or finish """
    if not can_index():
        logger.debug("Can not index video (is flvtool2/flvmeta installed?)")
        return _finish(ex_file, tempdir, cvd_path, log)

    cmd = [META_TOOL, "-U", cvd_path]
    process = subprocess.Popen(cmd, stdout=log, stderr=log)

    timer = Timer(TIMEOUT, lambda x: x.kill(), [process])
    timer.start()

    exit_code = process.wait()
    timer.cancel()

    if exit_code != 0:
        logger.exception('An error occured while indexing video file.')

    return _finish(ex_file, tempdir, cvd_path, log)


def _finish(ex_file, tempdir, cvd_path, log):
    """ Rename output to done and cleanup """

    # Update the blob contents
    try:
        ex_file._blob.consumeFile(cvd_path)
        ex_file.size = os.stat(cvd_path).st_size  # update the file size based on converted result
    except Exception, err:
        logger.exception(err)
        log.write(
            'MediaConverterError: Could not finish conversion %s' % err)

    log.seek(0)
    ex_file._conversion_log = log.read()
    ex_file._p_changed = True

    # Cleanup the temp directory
    log.close()
    try:
        shutil.rmtree(tempdir)
    except Exception, err:
        logger.exception(err)


#
# Private interface
#
def _get_convertor_tool():
    """
    Retrieves the possible conversion tool for videos.

    FFMpeg and AVConv can be used (they're practically the same thing

    If ffmpeg is not installed with the proper options (libmp3lame)
    a MediaConverterError exception will be raised.

    """
    tools = ['ffmpeg', 'avconv']

    for tool in tools:
        process = subprocess.Popen([tool, "-h"],
                                   shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout = process.stdout.read()
        process.wait()

        if process.returncode != 1:
            continue

        if (tool == 'ffmpeg') and ("--enable-libmp3lame" not in stdout):
            raise MediaConverterError(
                'ffmpeg was not compiled with --enable-libmp3lame')

        return tool

    raise MediaConverterError("Could not find either ffmpeg or avconv "
                              "as video convertors")


def _get_flv_meta_tool():
    """Checks if flvtool2 or flvmeta is available.

        If flvtool2 is not installed a MediaConverterError exception will be raised.
    """
    tools = [('flvtool2', '-H'), ('flvmeta', '-h')]

    for tool, param in tools:
        process = subprocess.Popen([tool, param],
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        process.wait()

        if process.returncode != 1:
            continue

        return tool

    raise MediaConverterError('could not run flvtool2 or flvmeta')

#
# Private variables
#

CONVERSION_TOOL = None
try:
    CONVERSION_TOOL = _get_convertor_tool()
except MediaConverterError, media_err:
    logger.warn("ffmpeg2 or avconv are not available")

META_TOOL = None

try:
    META_TOOL = _get_flv_meta_tool()
except MediaConverterError, media_err:
    logger.warn("flvtool2 or flvmeta is not available")

#
# Public interface
#

def can_convert():
    """ Is ffmpeg/avconv installed?
    """
    return bool(CONVERSION_TOOL)


def can_index():
    """ Is flvtool2/flvmeta installed?
    """
    return bool(META_TOOL)


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
    txt = subprocess.Popen([CONVERSION_TOOL, '-i', video_path],
                           stderr=subprocess.PIPE).communicate()[1]

    for line in txt.splitlines():
        if 'Video: ' in line:
            m = re.search(r'(\d+)x(\d+)', line)
            if m is not None:
                return float(m.group(1)), float(m.group(2))
    raise ValueError('Cannot parse ffmpeg output')
