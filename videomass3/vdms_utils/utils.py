# -*- coding: UTF-8 -*-
# Name: utils.py
# Porpose: Group the utilities needed for some requests
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
    It return a number 'float'
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


def time_seconds(time):
    """
    convert time human to seconds e.g. time_seconds('00:02:00')
    """
    if time == 'N/A':
        return int('0')

    pos = time.split(':')
    h, m, s = pos[0], pos[1], pos[2]
    duration = (int(h) * 3600 + int(m) * 60 + float(s))

    return duration
# ------------------------------------------------------------------------


def time_human(seconds):
    """
    Convert from seconds to time human. Accept integear only e.g.
    time_human(2300)
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
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
