# -*- coding: UTF-8 -*-
"""
Name: utils.py
Porpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.20.2025
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
        subprocess.run(cmd, check=True, shell=False, encoding='utf-8')
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


def to_bytes(string):
    """
    Convert given size string to bytes, e.g.
    out = to_bytes('9.45MiB')
    It return a number 'float' object.
    Updated on Aug 20 2025.
    """
    value = 0.0
    unit = {"Yibyte": 0, "Ybyte": 0, "Zibyte": 1, "Zbyte": 1,
            "Eibyte": 2, "Ebyte": 2, "Pibyte": 3, "Pbyte": 3,
            "Tibyte": 4, "Tbyte": 4, "Gibyte": 5, "Gbyte": 5,
            "Mbyte": 6, "Mibyte": 6, "Kibyte": 7, "Kbyte": 7,
            "byte": 8,
            }
    maxint = list(unit.values())
    const = 1024.0

    for metric, val in unit.items():
        if metric in string:
            value = float(string.split(metric)[0])
            exponent = val * (-1) + (max(maxint))
            break

    return round(value * (const ** exponent), 2)
# ------------------------------------------------------------------------


def time_to_integer(timef: str = '0', sec=False, rnd=False) -> int:
    """
    Converts strings representing the 24-hour format to an
    integer equivalent to the time duration in milliseconds
    (default).

    ARGUMENTS:
    ---------
    timef: Accepts a string representing the 24-hour clock in the
           following valid string formats:

            '0' | '00' | '00.0' | '00.00' | 00:0 | '00:00:00'
            '0:00:00' | '0:0:0' | '00:00.000' | '00:00:00.000

           Default is '0' .
           Any other representation passed as a string argument will
           be returned as an integer object equal to 0 (int).
           If the argument passed is an object other than the string
           object (str) the exception `TypeError` will be raised.

    sec: if `True`, returns the duration in seconds instead
         of milliseconds.

    rnd: if `True` rounds the result, i.e. "00:00:02.999" > 3000
         milliseconds instead of 2999 milliseconds or 3 seconds
         instead of 2 seconds using `sec=True` argument.

    Return an int object.
    Raise `TypeError` if argument != `str` .

    """
    if not isinstance(timef, str):
        raise TypeError("Only a string (str) object is expected.")

    # adds leading zeros to fill up possibly non-existing fields.
    hours, minutes, seconds = (["0", "0"] + timef.split(":"))[-3:]

    try:
        hours = int(hours)
        minutes = int(minutes)
        seconds = float(seconds)
        if rnd:
            seconds = round(seconds)
    except ValueError:
        return 0

    if sec:
        return int(hours * 3600 + minutes * 60 + seconds)
    return int(hours * 3600000 + minutes * 60000 + seconds * 1000)

# ------------------------------------------------------------------------


def integer_to_time(integer: int = 0, mills=True, rnd=False) -> str:
    """
    Converts integers to 24-hour clock format calculating in
    sexagesimal format. Accept an `int` object, such as 2998.
    Float numbers, such as 2000.999, must be rounded using
    `round()` function first.

    ARGUMENTS:
    ---------
    integer: Any int object, default is 0.

    mills: Include milliseconds like "HH:MM:SS.MIL" (default).
           Milliseconds will be excluded and ignored if set
           to `False`. You could instead use the `rnd` argument
           to round them and add the offset to the seconds.

    rnd: If `True` rounds the result. This argument will have
         no effect with `mills=True` default argument.

    Returns a string object.
    Raise `TypeError` if argument != `int` .

    """
    if not isinstance(integer, int):
        raise TypeError("An integer (int) object is expected.")

    minutes, sec = divmod(integer, 60000)
    hours, minutes = divmod(minutes, 60)

    if mills:
        seconds = float(sec) / 1000
        # return "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        return f"{hours:02}:{minutes:02}:{seconds:06.3f}"

    if rnd:
        seconds = round(sec / 1000)
    else:
        seconds = int(sec / 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02}"
# ------------------------------------------------------------------------


def copy_missing_data(srcd, destd):
    """
    Copy missing files and directories to a given destination
    path using the same names as the source path.

    """
    srclist = os.listdir(srcd)
    destlist = os.listdir(destd)
    for f in srclist:
        if f not in destlist:
            if os.path.isfile(os.path.join(srcd, f)):
                copy_restore(os.path.join(srcd, f), os.path.join(destd, f))
            elif os.path.isdir(os.path.join(srcd, f)):
                copydir_recursively(os.path.join(srcd, f), destd)
# ------------------------------------------------------------------------


def copy_restore(srcfile, destfile):
    """
    Copy the contents (no metadata) of the file named
    srcfile to a file named destfile. Please visit doc webpage at
    <https://docs.python.org/3/library/shutil.html#shutil.copyfile>

    """
    try:
        shutil.copyfile(str(srcfile), str(destfile))
    except FileNotFoundError as err:
        # file srcfile not exists
        return str(err)
    except shutil.SameFileError as err:
        # srcfile and destfile are the same file and same dir.
        return str(err)
    except OSError as err:
        # The destfile location must be writable
        return str(err)

    return None
# ------------------------------------------------------------------#


def copydir_recursively(srcdir, destdir, extraname=None):
    """
    recursively copies an entire directory tree rooted
    at `srcdir`. If you do not provide the `extraname`
    argument, the destination will have the same name as
    the file in srcdir, otherwise `extraname` is assumed
    as the final name.

    """
    if extraname:
        dest = os.path.join(destdir, extraname)
    else:
        dest = os.path.join(destdir, os.path.basename(srcdir))
    try:
        shutil.copytree(str(srcdir), str(dest))

    except FileExistsError as err:  # dest dir already exists
        return err
    except FileNotFoundError as err:  # srcdir not exists
        return err

    return None
# ------------------------------------------------------------------#


def copy_on(ext, sourcedir, destdir, overw=True):
    """
    This function copy file based on given extension (`ext`).
    It use `glob` module to finds in the `sourcedir` pathname
    all the files matching a specified `ext`.
    If default "overw" argument is `False`, it does not
    overwrite existing file names in the destination path.

    Returns None on success, returns the error otherwise.

    ARGUMENTS:
    ext: files extension without dot
    sourcedir: path to the source directory
    destdir: path to the destination directory
    overw: `True`, overwrite file destination

    """
    destpath = os.listdir(destdir)
    files = glob.glob(f"{sourcedir}/*.{ext}")
    if not files:
        return f'ERROR: No files found in this format: ".{ext}"'
    for fln in files:
        if not overw:
            if os.path.basename(fln) in destpath:
                continue
        try:
            shutil.copy(fln, f'{destdir}')
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
    with open(filename, "r+", encoding='utf-8') as fname:
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
        raise TypeError("Only a string (str) object is expected.")

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
        raise TypeError("Only a string (str) object is expected.")

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
    millis = time_to_integer(duration)
    if not millis:
        clock = {'duration': '00:00:00', 'millis': 0}
    else:
        if os.path.exists(fileclock):
            with open(fileclock, "r", encoding='utf-8') as atime:
                clockread = atime.read().strip()
                if time_to_integer(clockread) <= millis:
                    clock = {'duration': clockread, 'millis': millis}
                else:
                    clock = {'duration': duration, 'millis': millis}
        else:
            clock = {'duration': '00:00:00', 'millis': millis}

    return clock
# ------------------------------------------------------------------#


def update_timeseq_duration(time_seq, duration):
    """
    Return an updated dict with time/duration
    """
    if time_seq:
        ms = time_to_integer(time_seq.split()[3])  # -t duration
        splseq = time_seq.split()
        tseq = f'{splseq[0]} {splseq[1]}', f'{splseq[2]} {splseq[3]}'
        dur = [ms for n in duration]
        duration = dur
        timestart = tseq[0]
        endtime = tseq[1]
    else:
        timestart, endtime = '', ''

    return duration, timestart, endtime
# ------------------------------------------------------------------#


def detect_binaries(name, extradir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    name = name of executable without extension
    extradir = additional dirname to perform search

    Given an executable (binary) file name, it looks for it
    in the operating system using the `which` function, if it
    doesn't find it, it tries to look for it in the optional
    `extradir` .

        Return (None, path) if found in the OS $PATH.
        Return ('provided', path) if found on the `extradir`
        Return ('not installed', None) if both failed.

    """
    execpath = shutil.which(name)
    if execpath:
        return None, execpath
    if extradir:  # check onto extradir
        execpath = os.path.join(extradir, "bin", name)
        if os.path.isfile(execpath):
            return 'provided', execpath
    return 'not installed', None
