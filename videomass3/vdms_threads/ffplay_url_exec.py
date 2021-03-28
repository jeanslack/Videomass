# -*- coding: UTF-8 -*-
# Name: ffplay_url_exec.py
# Porpose: playback online media streams with ffplay player
#          using youtube-dl as executable.
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Jan.07.2020 *PEP8 compatible*
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
import wx
import subprocess
import platform
if not platform.system() == 'Windows':
    import shlex
import os
import sys
from threading import Thread
import time
from pubsub import pub
from videomass3.vdms_io import IO_tools
from videomass3.vdms_io.make_filelog import write_log  # write initial log
if 'youtube_dl' in sys.modules:
    import youtube_dl


def msg_error(msg, title="Videomass"):
    """
    Receive error messages
    """
    wx.MessageBox("%s" % (msg), title, wx.ICON_ERROR)

# ------------------------------------------------------------------------#


class Exec_Download_Stream(Thread):
    """
    Download media stream to the videomass cache directory with
    the same quality defined in the `quality` parameter. The download
    progress continues until an interruption signal is detected.
    The interruption signal is defined by `self.stop_work_thread`
    attribute based from boolean values.
    This Thread use youtube-dl executable (not module) with
    subprocess.Popen class.

    The file name form stored on cache dir. is

            "title_" + "quality" + ".format"

    NOTE see also ffplay_url_lib.py on sources directory.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    FFMPEG_URL = get.FFMPEG_url
    BINLOCAL = get.execYdl
    EXCEPTION = None
    TMP = get.TMP
    LOGDIR = get.LOGdir
    YDL_PREF = get.YDL_pref

    if platform.system() == 'Windows':
        pyname = 'Scripts', 'youtube-dl.exe'
    else:
        pyname = 'bin', 'youtube-dl'

    if YDL_PREF == 'disabled':
        EXCEPTION = 'error: youtube-dl is disabled, check preferences.'
        EXECYDL = BINLOCAL

    elif YDL_PREF == 'local':
        if BINLOCAL is not False:
            EXECYDL = BINLOCAL
        else:
            EXCEPTION = 'Not found: %s' % BINLOCAL

    elif YDL_PREF == 'system':
        if 'youtube_dl' in sys.modules:
            # see also inspect: `inspect.getfile(youtube_dl)`
            # or the best: shutil.which('python')
            pypath = youtube_dl.__file__.split('lib')[0]
            EXECYDL = os.path.join(pypath, pyname[0], pyname[1])

    if platform.system() == 'Windows':
        if os.path.isfile(EXECYDL):
            LINE_MSG = ('\nRequires MSVCR100.dll\nTo resolve this problem '
                        'install: Microsoft Visual C++ 2010 Redistributable '
                        'Package (x86)')
        else:
            LINE_MSG = ('Unrecognized error')
    else:
        LINE_MSG = ('Unrecognized error')
    # -----------------------------------------------------------------------#

    def __init__(self, url, quality):
        """
        Accept a single url as string and a quality parameter
        in the form required by youtube-dl, e.g one of the
        following quality strings can be valid:

            "worst", "best" "bestvideo+bestaudio" or a "Format Code"
            obtained typing `youtube-dl -F <link>`

        """
        self.logf = os.path.join(Exec_Download_Stream.LOGDIR, 'ffplay.log')
        self.stop_work_thread = False  # process terminate value
        self.url = url
        self.quality = quality

        if (platform.system() == 'Windows' or '/tmp/.mount_' in sys.executable
            or os.path.exists(os.path.dirname(os.path.dirname(os.path.dirname(
             sys.argv[0]))) + '/AppRun')):

            self.ssl = '--no-check-certificate'

        else:
            self.ssl = ''

        write_log('ffplay.log', Exec_Download_Stream.LOGDIR)

        if Exec_Download_Stream.EXCEPTION:
            wx.CallAfter(msg_error, Exec_Download_Stream.EXCEPTION)
            self.logError(Exec_Download_Stream.EXCEPTION)  # append log error
            return

        Thread.__init__(self)
        """initialize Thread class"""
    # ----------------------------------------------------------------------#

    def run(self):
        """
        Starting thread.
        """
        cmd = ('"{0}" {1} --prefer-ffmpeg --newline --ignore-errors -o '
               '"{2}/%(title)s_{3}.%(ext)s" --continue --format {3} '
               '--no-playlist --no-part --ignore-config '
               '--restrict-filenames "{4}" --ffmpeg-location '
               '"{5}"'.format(Exec_Download_Stream.EXECYDL,
                              self.ssl,
                              Exec_Download_Stream.TMP,
                              self.quality,
                              self.url,
                              Exec_Download_Stream.FFMPEG_URL,
                              ))
        self.logWrite(cmd)  # append log cmd
        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
        else:
            # Hide subprocess window on MS Windows
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            with subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  bufsize=1,
                                  universal_newlines=True,
                                  startupinfo=info,) as p:

                for line in p.stdout:
                    if not self.stop_work_thread:
                        if '[download]' in line:  # ...in processing
                            if 'Destination' in line:
                                pub.sendMessage("START_FFPLAY_EVT",
                                                output=line.split()[2]
                                                )
                            elif 'has already been downloaded' in line:
                                pub.sendMessage("START_FFPLAY_EVT",
                                                output=line.split()[1]
                                                )
                    else:  # self.stop_work_thread:
                        p.terminate()
                        break

                if p.wait():  # error at end process
                    if 'line' not in locals():
                        line = Exec_Download_Stream.LINE_MSG
                    if '[download]' in line:
                        return
                    wx.CallAfter(msg_error,
                                 line,
                                 'Videomass: Error %s' % p.wait()
                                 )
                    self.logError(line)  # append log error
                    return

        except OSError as err:
            wx.CallAfter(msg_error, err, 'Videomass: OSError')
            self.logError(err)  # append log error
            return
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a", encoding='utf8') as log:
            log.write("%s\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a", encoding='utf8') as logerr:
            logerr.write("\n[FFMPEG] FFplay "
                         "ERRORS:\n%s\n" % (error))
# ------------------------------------------------------------------------#


class Exec_Streaming(object):
    """
    Handling Threads to download and playback media streams via
    youtube-dl and ffplay executables.

    DOWNLOAD class variable makes the object's attributes available
    even outside of class, see `stop_download()`
    FIXME put RICEIVER LISTENER function as methods of this class. For
          now does not work (???)

    """
    DOWNLOAD = None  # set instance thread
    TIMESTAMP = None
    AUTOEXIT = None
    # ---------------------------------------------------------------#

    def __init__(self, timestamp, autoexit, url=None, quality=None):
        """
        - Topic "START_FFPLAY_EVT" subscribes the start playing
          running ffplay at a certain time.
        - Topic "STOP_DOWNLOAD_EVT" subscribes a stop download listener
          which call the stop() method of `Download_Stream` class to
          stop the download when ffplay has finished or been closed by
          the user.

        """
        pub.subscribe(stop_download_listener, "STOP_DOWNLOAD_EVT")
        pub.subscribe(start_palying_listener, "START_FFPLAY_EVT")

        Exec_Streaming.DOWNLOAD = Exec_Download_Stream(url, quality)
        Exec_Streaming.TIMESTAMP = timestamp
        Exec_Streaming.AUTOEXIT = autoexit

        self.start_download()
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        call Exec_Download_Stream(Thread) to run() method

        """
        if not Exec_Download_Stream.EXCEPTION:
            Exec_Streaming.DOWNLOAD.start()
        return

# --------- RECEIVER LISTENERS


def stop_download_listener(filename):
    """
    Receive message from ffplay_file.File_Play class
    for handle interruption

    """
    Exec_Streaming.DOWNLOAD.stop()
    Exec_Streaming.DOWNLOAD.join()

    return


def start_palying_listener(output):
    """
    Riceive message from Exec_Download_Stream class to start
    ffplay in at a given time.

    """
    IO_tools.stream_play(output, '', Exec_Streaming.TIMESTAMP,
                         Exec_Streaming.AUTOEXIT)
    return
