""" Collection of classes and function used to convert media to mp4 video.
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


def media2mp4(mediafile):
    """ Convert media to mp4 and add metadata
    """
    if not can_convert():
        return "Can not convert (are tools available?)"

    tempdir = tempfile.mkdtemp(prefix="convert-")

    finput = mediafile.get_filename()
    fpath, fname = os.path.split(finput)
    tcv_path = finput
    cvd_path = os.path.join(tempdir, fname + ".cvd")  # converted
    log = open(os.path.join(tempdir, fname + '.log'), 'wr+')

    resolution = get_resolution(tcv_path)
    width = int(resolution[0])/8*8
    height = int(resolution[1])/8*8

    cmd = [CONVERSION_TOOL, "-y", "-v", "0", "-benchmark", "-i", tcv_path,
           "-s", "%sx%s" % (width, height), "-c:v", "libx264", "-crf", "20",
           "-c:a", "libfdk_aac", "-q:a", "100", "-f", "mp4", cvd_path]
    process = subprocess.Popen(cmd, stdout=log, stderr=log)

    TIMEOUT = 3 * 3600  # seconds
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

    return _finish(mediafile, tempdir, cvd_path, log)


def _finish(mediafile, tempdir, cvd_path, log):
    """ Rename output to done and cleanup """

    # Update the blob contents
    try:
        #  update the file size based on converted result
        mediafile.size = os.stat(cvd_path).st_size
        mediafile._blob.consumeFile(cvd_path)
    except Exception, err:
        logger.exception(err)
        log.write(
            'MediaConverterError: Could not finish conversion %s' % err)

    log.seek(0)
    mediafile._conversion_log = log.read()
    mediafile._p_changed = True

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
        try:
            process = subprocess.Popen([tool, "-h"],
                                       shell=False, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            stdout = process.stdout.read()
            process.wait()

            if process.returncode != 0:
                continue

            if tool == 'ffmpeg' and "--enable-libfdk_aac" not in stdout:
                raise MediaConverterError(
                    'ffmpeg was not compiled with --enable-libfdk_aac '
                    '- Audio compression not possible')

            if (tool == 'ffmpeg') and ("--enable-libx264" not in stdout):
                raise MediaConverterError(
                    'ffmpeg was not compiled with --enable-libx264 '
                    '- Video compression not possible')

            return tool
        except OSError, e:
            if e == '[Errno 2] No such file or directory':
                continue

    raise MediaConverterError("Could not find either ffmpeg or avconv "
                              "as video convertors")


#
# Private variables
#

CONVERSION_TOOL = None
try:
    CONVERSION_TOOL = _get_convertor_tool()
except MediaConverterError, media_err:
    logger.warn("ffmpeg2 or avconv are not available")


#
# Public interface
#

def can_convert():
    """ Is ffmpeg/avconv installed?
    """
    return bool(CONVERSION_TOOL)


def get_conversion_errors(fpath, suffix=".log"):
    """ Open error file and parse it for errors
    """
    error_path = fpath + suffix

    # If mp4 file exists conversion is done
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
            m = re.search(r'Video: .*\ (\d+)x(\d+)', line)
            if m is not None:
                return float(m.group(1)), float(m.group(2))
    raise ValueError('Cannot parse ffmpeg output')
