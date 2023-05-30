# -*- coding: UTF-8 -*-
"""
Name: utils.py
Porpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.09.2023
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
import re
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


def open_default_application(pathname):
    """
    Given a path to a specific file or directory, opens the
    operating system's default application according to the
    user-set file type association. Currently supported platforms
    are Windows, Darwin and Linux. Note that Linux uses xdg-open
    which should also be used by other OSes that may support
    it, eg freebsd.

    Return error if any error, None otherwise.
    """
    if platform.system() == 'Windows':
        try:
            os.startfile(os.path.realpath(pathname))
        except FileNotFoundError as error:
            return str(error)

        return None

    if platform.system() == "Darwin":
        cmd = ['open', pathname]
    else:  # Linux, FreeBSD or any supported
        cmd = ['xdg-open', pathname]
    try:
        subprocess.run(cmd, check=True, shell=False, encoding='utf8')
    except subprocess.CalledProcessError as error:
        return str(error)

    return None
# ------------------------------------------------------------------------


def get_volume_data(filename, detect: list,
                    gain='-1.0', target='PEAK', audiomap='') -> tuple:
    """
    Given a filename, a detect object from `VolumeDetectThread`
    and a target level, it returns a volumedata object with
    the values expressed in dBFS of the maximum volume, average
    volume, offset, gain and the audio filter argument in FFmpeg
    syntax. Get 'PEAK' or 'RMS', default is 'PEAK'. It also
    supports audio map indexing if the audio stream itself is
    contained within a video.
    """
    volumedata = []
    volumedata.append(filename)
    if target == 'PEAK':
        maxvol = detect[0].split('dB')[0].strip()
        volumedata.append(maxvol)
        meanvol = detect[1].split('dB')[0].strip()
        volumedata.append(meanvol)
        offset = float(maxvol) - float(gain)
        volumedata.append(str(offset))
        result = float(maxvol) - float(offset)
        volumedata.append(str(result))
        if float(maxvol) == float(gain):
            volume = '  '
        else:
            volume = f'-filter:a:{audiomap} volume={-offset:f}dB'
        volumedata.append(volume)

    elif target == 'RMS':
        maxvol = detect[0].split('dB')[0].strip()
        volumedata.append(maxvol)
        meanvol = detect[1].split('dB')[0].strip()
        volumedata.append(meanvol)
        offset = float(meanvol) - float(gain)
        volumedata.append(str(offset))
        result = float(maxvol) - offset
        volumedata.append(str(result))
        if offset == 0.0:
            volume = '  '
        else:
            volume = f'-filter:a:{audiomap} volume={-offset:f}dB'
        volumedata.append(volume)

    return tuple(volumedata)


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
    Returns a string object of time format e.g. HOURS:MM:SS.MILLIS,
    as in 00:00:00.000 .

    """
    minutes, sec = divmod(milliseconds, 60000)
    hours, minutes = divmod(minutes, 60)
    seconds = float(sec) / 1000
    # return "%02d:%02d:%06.3f" % (hours, minutes, seconds)
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}"
# ------------------------------------------------------------------------


def milliseconds2clocksec(milliseconds):
    """
    Like milliseconds2clock but differs in the returned object
    which does not have milliseconds.
    Returns a string object in 24-hour clock of time units
    e.g. HOURS:MM:SS, as in 00:00:00 .

    """
    minutes, sec = divmod(milliseconds, 60000)
    hours, minutes = divmod(minutes, 60)
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

        if fileExists:
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


def trailing_name_with_prog_digit(destpath, argname) -> str:
    """
    Returns a new name with the same name as `argname`
    but adds a trailing progressive digit to the new name
    starting from `01`. If the new name already exists, the
    progressive digit will start from `02`, and so on.
    This function is useful for renaming both files and
    directories as it uses a filter to file system sanitize
    to removing illegal chars for some OS like:

            ^` ~ " # ' % & * : < > ? / \\ { | }.
    Args:
    -----
    destpath (str): destination path as a string object.
    argname (str): It expects an item name as a string object.

    Raise `TypeError` if args not type `str`
    Returns str(newdirname)
    """
    if not isinstance(destpath, str) or not isinstance(argname, str):
        raise TypeError("Expects str object only")

    name, ext = os.path.splitext(argname)
    name = re.sub(r"[\'\^\`\~\"\#\'\%\&\*\:\<\>\?\/\\\{\|\}]", '', name)
    name = name.strip().strip('.')  # removes lead./trail. spaces and dots
    ext = ext.strip()  # removes lead./trail. spaces
    alreadynumbered = []

    for items in os.listdir(destpath):
        match = items.rsplit(sep=' - ', maxsplit=1)
        if len(match) == 2:
            if match[0] == name and match[1].strip().isdigit():
                alreadynumbered.append(int(match[1]))  # append digit as int

    if alreadynumbered:
        prog = max(alreadynumbered) + 1
        newdirname = os.path.join(destpath,
                                  f'{name} - {str(prog).zfill(2)}' + ext)
    else:
        newdirname = os.path.join(destpath, f'{name} - 01' + ext)

    return newdirname
# ------------------------------------------------------------------#


def leading_name_with_prog_digit(destpath, argname) -> str:
    """
    Returns a new name with the same name as `argname`
    but adds a leading progressive digit to the new name
    starting from `01`. If the new name already exists, the
    progressive digit will start from `02`, and so on.
    This function is useful for renaming both files and
    directories as it uses a filter to file system sanitize
    to removing illegal chars for some OS like:

            ^` ~ " # ' % & * : < > ? / \\ { | }.
    Args:
    -----
    destpath (str): destination path as a string object.
    argname (str): It expects an item name as a string object.

    Raise `TypeError` if args not type `str`
    Returns str(newdirname)
    """
    if not isinstance(destpath, str) or not isinstance(argname, str):
        raise TypeError("Expects str object only")

    name, ext = os.path.splitext(argname)
    name = re.sub(r"[\'\^\`\~\"\#\'\%\&\*\:\<\>\?\/\\\{\|\}]", '', name)
    name = name.strip().strip('.')  # removes lead./trail. spaces and dots
    ext = ext.strip()  # removes lead./trail. spaces
    alreadynumbered = []

    for items in os.listdir(destpath):
        match = items.split(sep=' - ', maxsplit=1)
        if len(match) == 2:
            if match[1] == name and match[0].strip().isdigit():
                alreadynumbered.append(int(match[0]))

    if alreadynumbered:
        prog = max(alreadynumbered) + 1
        newdirname = os.path.join(destpath,
                                  f'{str(prog).zfill(2)} - {name}' + ext)
    else:
        newdirname = os.path.join(destpath, f'01 - {name}' + ext)

    return newdirname
# ------------------------------------------------------------------#


def clockset(duration, fileclock):
    """
    Evaluate the consistency between overall tempo values on
    different media that have the same name but different
    contents and a possible time position previously saved to
    file. Returns a clock object of type dict conforming to the
    referenced media file.
    """
    duration = duration.split('.')[0]
    millis = get_milliseconds(duration)
    if not millis:
        clock = {'duration': '00:00:00', 'millis': 0}
    else:
        if os.path.exists(fileclock):
            with open(fileclock, "r", encoding='utf8') as atime:
                clockread = atime.read().strip()
                if get_milliseconds(clockread) <= millis:
                    clock = {'duration': clockread, 'millis': millis}
                else:
                    clock = {'duration': duration, 'millis': millis}
        else:
            clock = {'duration': '00:00:00', 'millis': millis}

    return clock
# ------------------------------------------------------------------#


def detect_binaries(executable, additionaldir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    executable = name of executable without extension
    additionaldir = additional dirname to perform search

    Given an executable (binary) file name, it looks for it
    in the operating system using the `which` function, if it
    doesn't find it, it tries to look for it in the optional
    `additionaldir` .

        Return (None, executable) if found in the OS $PATH.
        Return ('provided', executable) if found on the `additionaldir`
        Return ('not installed', None) if both failed.

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
