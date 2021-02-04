# -*- coding: UTF-8 -*-
# Name: utils.py
# Porpose: It groups useful functions that are called several times
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: January.05.2021 *PEP8 compatible*
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import shutil
import os
import glob
import math


def format_bytes(n):
    """
    Given a float number (bytes) returns size output
    strings human readable, e.g.
    out = format_bytes(9909043.20)
    It return a string digit with metric suffix
    """
    unit = ["B", "KiB", "MiB", "GiB", "TiB",
            "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0
    if n == 0.0:  # if 0.0 or 0 raise ValueError: math domain error
        exponent = 0
    else:
        exponent = int(math.log(n, const))  # get unit index

    suffix = unit[exponent]  # unit index
    output_value = n / (const ** exponent)

    return "%.2f%s" % (output_value, suffix)
# ------------------------------------------------------------------------


def to_bytes(string):
    """
    Convert given size string to bytes, e.g.
    out = to_bytes('9.45MiB')
    It return a number 'float' object.
    """
    value = 0.0
    unit = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0

    for index, metric in enumerate(reversed(unit)):
        if metric in string:
            value = float(string.split(metric)[0])
            break

    exponent = index * (-1) + (len(unit) - 1)

    return round(value * (const ** exponent), 2)
# ------------------------------------------------------------------------


def get_seconds(timeformat):
    """
    This is the old implementation to get time human to seconds,
    e.g. get_seconds('00:02:00'). Return int(seconds) object.
    """
    if timeformat == 'N/A':
        return int('0')

    pos = timeformat.split(':')
    h, m, s = int(pos[0]), int(pos[1]), float(pos[2])

    return (h * 3600 + m * 60 + s)
# ------------------------------------------------------------------------


def timehuman(seconds):
    """
    This is the old implementation to converting seconds to
    time format. Accept integear only e.g timehuman(2300).
    Useb by youtube-dl downloader, returns a string object
    in time format i.e '00:38:20' .

    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)
# ------------------------------------------------------------------------


def get_milliseconds(timeformat):
    """
    Convert time format to milliseconds (duration). Accepts various
    forms of time unit string, e.g. '30.5', '00:00:00', '0:00:00',
    '0:0:0', '00:00.000', '00:00:00.000. The first line adds leading
    zeros to fill up possibly non-existing fields.
    Return an int object (milliseconds).

    HACK add 'N/A' (no time) to parser?

            if timeformat == 'N/A':
                return int('0')
    """
    hours, minutes, seconds = (["0", "0"] + timeformat.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)

    return int(hours * 3600000 + minutes * 60000 + seconds * 1000)
# ------------------------------------------------------------------------


def milliseconds2timeformat(milliseconds):
    """
    Converts milliseconds (duration) to time units in sexagesimal
    format (e.g. HOURS:MM:SS.MILLISECONDS, as in 00:00:00.000).
    Accept an int object, such as 2000 or float, such as 2000.999.
    Returns a string object in time format.

    """
    m, s = divmod(milliseconds, 60000)
    h, m = divmod(m, 60)
    sec = float(s) / 1000
    return "%02d:%02d:%06.3f" % (h, m, sec)
# ------------------------------------------------------------------------


def copy_restore(src, dest):
    """
    copy a specific file from src to dest. If dest exists,
    it will be overwritten with src without confirmation.
    If src does not exists return FileNotFoundError.
    """
    try:
        shutil.copyfile(str(src), str(dest))
    except FileNotFoundError as err:
        return err
    except Exception as err:
        return err

    return
# ------------------------------------------------------------------#


def copydir_recursively(source, destination, extraname=None):
    """
    recursively copies an entire directory tree rooted at source.
    If you do not provide the extraname argument, the destination
    will have the same name as the source, otherwise extraname is
    assumed as the final name.

    """
    if extraname:
        dest = os.path.join(destination, extraname)
    else:
        dest = os.path.join(destination, os.path.basename(source))
    try:
        shutil.copytree(str(source), str(dest))
    except Exception as err:
        return err

    return None
# ------------------------------------------------------------------#


def copy_on(ext, source, destination):
    """
    Given a source (dirname), use glob for a given file extension (ext)
    and iterate to move files to another directory (destination).
    Returns None on success, otherwise returns the error.

    ARGUMENTS:
    ext: files extension without dot
    source: path to the source directory
    destination: path to the destination directory
    """
    files = glob.glob("%s/*.%s" % (source, ext))
    if not files:
        return 'Error: No such file with ".%s" format found' % ext
    for f in files:
        try:
            shutil.copy(f, '%s' % (destination))
        except Exception as error:
            return error
    return None
# ------------------------------------------------------------------#


def detect_binaries(platform, executable, additionaldir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    Given an executable name (binary), find it on the O.S.
    via which function, if not found try to find it on the
    optional `additionaldir` .

        If both failed return ('not installed', None)
        If found on the O.S. return (None, executable)
        If found on the additionaldir return ('provided', executable).

    platform = platform name get by `platform.system()`
    executable = name of executable without extension
    additionaldir = additional dirname to perform search

    """
    local = False

    if shutil.which(executable):
        installed = True

    else:
        if platform == 'Windows':
            installed = False

        elif platform == 'Darwin':

            if os.path.isfile("/usr/local/bin/%s" % executable):
                local = True
                installed = True
            else:
                local = False
                installed = False

        else:  # Linux, FreeBSD, etc.
            installed = False

    if not installed:

        if additionaldir:  # check onto additionaldir

            if not os.path.isfile(os.path.join("%s" % additionaldir,
                                               "bin", "%s" % executable)):
                provided = False

            else:
                provided = True

            if not provided:
                return 'not installed', None

            else:
                # only if ffmpeg is not installed, offer it if found
                return 'provided', os.path.join("%s" % additionaldir,
                                                "bin", "%s" % executable)
        else:
            return 'not installed', None

    else:  # only for MacOs
        if local:
            return None, "/usr/local/bin/%s" % executable

        else:
            return None, shutil.which(executable)
