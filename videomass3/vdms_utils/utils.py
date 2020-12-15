# -*- coding: UTF-8 -*-
# Name: utils.py
# Porpose: Group the utilities needed for some requests
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: December.14.2020 *PEP8 compatible*
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


def timehuman1(seconds):
    """
    This is the old implementation to converting seconds to
    time format. Accept integear only e.g timehuman(2300).
    Returns a string object in time format i.e '00:38:20' .

    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)
# ------------------------------------------------------------------------


def time_seconds(timeformat):
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
    milliseconds = int(hours * 3600000 + minutes * 60000 + seconds * 1000)
    return milliseconds
# ------------------------------------------------------------------------


def time_human(ms):
    """
    Converts milliseconds (duration) to time units in sexagesimal
    format (e.g. HOURS:MM:SS.MILLISECONDS, as in 01:23:45.678).
    Accept an int object, such as 2000 or float, such as 2000.999.
    Returns a string object in time format.

    """
    m, s = divmod(ms, 60000)
    h, m = divmod(m, 60)
    sec = float(s) / 1000
    return "%02d:%02d:%06.3f" % (h, m, sec)
# ------------------------------------------------------------------------


def copy_restore(src, dest):
    """
    Restore file. File name is owner choice and can be an preset
    or not. If file exist overwrite it.
    """
    try:
        shutil.copyfile(src, '%s' % (dest))
    except FileNotFoundError as err:
        return err

    return
# ------------------------------------------------------------------#


def copy_backup(src, dest):
    """
    function for file backup. File name is owner choice.
    """
    shutil.copyfile('%s' % (src), dest)
# ------------------------------------------------------------------#


def makedir_move(ext, name_dir):
    """
    this function make directory and move-in file
    (ext, name_dir: extension, directory name)
    """
    try:  # if exist dir not exit OSError, go...
        os.mkdir("%s" % (name_dir))
    except OSError as err:
        return err
    move_on(ext, name_dir)
# ------------------------------------------------------------------#


def move_on(ext, name_dir):
    """
    Cycling on name extension file and move-on in other directory
    """
    files = glob.glob("*%s" % (ext))
    for sposta in files:
        shutil.move(sposta, '%s' % (name_dir))
        # print('%s   %s' % (sposta, name_dir))
# ------------------------------------------------------------------#


def copy_on(ext, name_dir, path_confdir):
    """
    Cycling on path and file extension name for copy files in other directory
    ARGUMENTS:
    ext: files extension with no dot
    name_dir: path name with no basename
    """
    files = glob.glob("%s/*.%s" % (name_dir, ext))
    for copia in files:
        shutil.copy(copia, '%s' % (path_confdir))
# ------------------------------------------------------------------#


def delete(ext):
    """
    function for file group delete with same extension
    """
    files = glob.glob("*%s" % (ext))
    for rimuovi in files:
        os.remove(rimuovi)
