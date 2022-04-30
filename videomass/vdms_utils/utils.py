# -*- coding: UTF-8 -*-
"""
Name: utils.py
Porpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.23.2022
Code checker: flake8, pylint .

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess
import platform
import shutil
import os
import glob
import math


class Popen(subprocess.Popen):
    """
    Inherit subprocess.Popen class to set _startupinfo.
    This avoids displaying a console window on MS-Windows
    using GUI's .

    NOTE MS Windows:

    subprocess.STARTUPINFO()

    https://stackoverflow.com/questions/1813872/running-
    a-process-in-pythonw-with-popen-without-a-console?lq=1>
    """
    if platform.system() == 'Windows':
        _startupinfo = subprocess.STARTUPINFO()
        _startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        _startupinfo = None

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        super().__init__(*args, **kwargs, startupinfo=self._startupinfo)

    # def communicate_or_kill(self, *args, **kwargs):
        # return process_communicate_or_kill(self, *args, **kwargs)
# ------------------------------------------------------------------------


def format_bytes(num):
    """
    Given a float number (bytes) returns size output
    strings human readable, e.g.
    out = format_bytes(9909043.20)
    It return a string digit with metric suffix

    """
    unit = ["B", "KiB", "MiB", "GiB", "TiB",
            "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0
    if num == 0.0:  # if 0.0 or 0 raise ValueError: math domain error
        exponent = 0
    else:
        exponent = int(math.log(num, const))  # get unit index

    suffix = unit[exponent]  # unit index
    output_value = num / (const ** exponent)

    # return "%.2f%s" % (output_value, suffix)
    return f"{output_value:.2f}{suffix}"
# ------------------------------------------------------------------------


def to_bytes(string, key='ydl'):
    """
    Convert given size string to bytes, e.g.
    out = to_bytes('9.45MiB')
    It return a number 'float' object.
    Updated on March 23 2022:
        added key default arg.

    """
    value = 0.0
    if key == 'ydl':
        unit = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

    elif key == 'ffmpeg':
        unit = ["byte", "Kibyte", "Mibyte", "Gibyte", "Tibyte",
                "Pibyte", "Eibyte", "Zibyte", "Yibyte"]

    const = 1024.0

    for index, metric in enumerate(reversed(unit)):
        if metric in string:
            value = float(string.split(metric)[0])
            exponent = index * (-1) + (len(unit) - 1)
            break

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
    hours, minutes, seconds = int(pos[0]), int(pos[1]), float(pos[2])

    return hours * 3600 + minutes * 60 + seconds
# ------------------------------------------------------------------------


def timehuman(seconds):
    """
    This is the old implementation to converting seconds to
    time format. Accept integear only e.g timehuman(2300).
    Useb by youtube-dl downloader, returns a string object
    in time format i.e '00:38:20' .

    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # return "%02d:%02d:%02d" % (hours, minutes, seconds)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
# ------------------------------------------------------------------------


def get_milliseconds(timeformat):
    """
    Convert 24-hour clock unit to milliseconds (duration).
    Accepts different forms of time unit string, e.g.

        '30.5', '00:00:00', '0:00:00', '0:0:0',
        '00:00.000', '00:00:00.000.

    The first line adds leading zeros to fill up possibly
    non-existing fields.

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


def milliseconds2clock(milliseconds):
    """
    Converts milliseconds to 24-hour clock format + milliseconds,
    calculating in sexagesimal format.
    Accept an `int` object, such as 2998. Float numbers, such
    as 2000.999, must be rounded using `round()` function.
    Returns a string object of time units e.g. HOURS:MM:SS.MILLIS,
    as in 00:00:00.000 .

    """
    minutes, sec = divmod(milliseconds, 60000)
    hours, minutes = divmod(minutes, 60)
    seconds = float(sec) / 1000
    # return "%02d:%02d:%06.3f" % (hours, minutes, seconds)
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}"
# ------------------------------------------------------------------------


def milliseconds2clocksec(milliseconds, rounds=False):
    """
    Like milliseconds2clock but differs in the returned object
    which does not have milliseconds. Furthermore you can pass
    `rounds=True` arg to add the millisec offset to the seconds.
    Returns a string object in 24-hour clock of time units
    e.g. HOURS:MM:SS, as in 00:00:00 .

    """
    minutes, sec = divmod(milliseconds, 60000)
    hours, minutes = divmod(minutes, 60)
    if rounds is True:
        seconds = round(float(sec / 1000))
    else:
        seconds = int(sec / 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
# ------------------------------------------------------------------------


def copy_restore(src, dest):
    """
    copy a specific file from src to dest. If dest exists,
    it will be overwritten with src without confirmation.
    """
    try:
        shutil.copyfile(str(src), str(dest))
    except FileNotFoundError as err:
        # file src not exists
        return err
    except SameFileError as err:
        # src and dest are the same file and same dir.
        return err
    except OSError as err:
        # The dest location must be writable
        return err

    return None
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

    except FileExistsError as err:  # dest dir already exists
        return err
    except FileNotFoundError as err:  # source dir not exists
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
    files = glob.glob(f"{source}/*.{ext}")
    if not files:
        return f'Error: No such file with ".{ext}" format found'
    for fln in files:
        try:
            shutil.copy(fln, f'{destination}')
        except IOError as error:
            # problems with permissions
            return error
    return None
# ------------------------------------------------------------------#


def del_filecontents(filename):
    """
    Delete the contents of the file if it is not empty.
    Please be careful as it assumes the file exists.

    HOW to USE:

        if fileExists is True:
            try:
                del_filecontents(logfile)
            except Exception as err:
                print("Unexpected error while deleting "
                      "file contents:\n\n{0}").format(err)

    MODE EXAMPLE SCHEME:

    |          Mode          |  r   |  r+  |  w   |  w+  |  a   |  a+  |
    | :--------------------: | :--: | :--: | :--: | :--: | :--: | :--: |
    |          Read          |  +   |  +   |      |  +   |      |  +   |
    |         Write          |      |  +   |  +   |  +   |  +   |  +   |
    |         Create         |      |      |  +   |  +   |  +   |  +   |
    |         Cover          |      |      |  +   |  +   |      |      |
    | Point in the beginning |  +   |  +   |  +   |  +   |      |      |
    |    Point in the end    |      |      |      |      |  +   |  +   |

    """
    with open(filename, "r+", encoding='utf8') as fname:
        content = fname.read()
        if content:
            fname.flush()  # clear previous content readed
            fname.seek(0)  # it places the file pointer to position 0
            fname.write("")
            fname.truncate()  # truncates the file to the current file point.
# ------------------------------------------------------------------#


def make_newdir_with_id_num(destdir, name):
    """
    Makes a new directory with the same name as `name`
    but adds a progressive number to the trailing, starting
    from `_1` i.e:

        'MyNewDir_1', MyNewDir_33, ect.

    destdir (str): output destination
    name (str): Any valid name OS sanitized

    Returns two items tuple:
        ('ERROR', errormessage) if error.
        (None, newdir): the new dirname otherwise.
    """
    extract = []
    for ddir in os.listdir(destdir):
        if ddir.startswith(name):
            try:
                dig = ddir.rsplit('_', 1)[1]
                if dig.isdigit():
                    extract.append(int(dig))
            except IndexError:
                continue
    if extract:
        prog = max(extract) + 1
        newdir = os.path.join(destdir, f'{name}_{str(prog)}')
    else:
        newdir = os.path.join(destdir, f'{name}_1')
    try:
        os.makedirs(newdir, mode=0o777)
    except (OSError, FileExistsError) as err:
        return 'ERROR', err

    return None, newdir
# ------------------------------------------------------------------#


def detect_binaries(executable, additionaldir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    Given an executable name (binary), find it on the O.S.
    via which function, if not found try to find it on the
    optional `additionaldir` .

        If both failed, return ('not installed', None)
        If found on the O.S., return (None, executable)
        If found on the additionaldir, return ('provided', executable).

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

            if os.path.isfile(f"/usr/local/bin/{executable}"):
                local = True
                installed = True
            else:
                local = False
                installed = False

        else:  # Linux, FreeBSD, etc.
            installed = False

    if not installed:

        if additionaldir:  # check onto additionaldir

            if not os.path.isfile(os.path.join(f"{additionaldir}", "bin",
                                               f"{executable}")):
                provided = False

            else:
                provided = True

            if not provided:
                return 'not installed', None
            # only if ffmpeg is not installed, offer it if found
            return 'provided', os.path.join(f"{additionaldir}",
                                            "bin", f"{executable}")
        return 'not installed', None

    if local:  # only for MacOs
        return None, f"/usr/local/bin/{executable}"
    return None, shutil.which(executable)
