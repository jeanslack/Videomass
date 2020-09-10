# -*- coding: UTF-8 -*-
# Name: ffplay_url.py
# Porpose: playback online media streams with ffplay media player
#          using youtube-dl as executable.
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: September.09.2020 *PEP8 compatible*
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


def msg_Error(msg):
    """
    Receive error messages
    """
    #wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_ERROR)
    print(msg)
# ------------------------------------------------------------------------#


class Exec_Download_Stream(Thread):
    """
    Download media stream to the videomass cache directory with
    the same quality defined in the `quality` parameter. The download
    progress continues until an interruption signal is detected.
    The interruption signal is defined by `self.stop_work_thread`
    attribute based from boolean values.
    This Thread use youtube-dl as executable with subprocess class.

    The file name form stored on cache dir. is

            "title_" + "quality" + ".format"

    NOTE see also ffplay_url_lib.py on sources directory.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    FFMPEG_URL = get.FFMPEG_url
    CACHEDIR = get.CACHEdir
    BINLOCAL = get.execYdl
    EXECUTABLE_NOT_FOUND_MSG = ("Is 'youtube-dl' installed on your system?")

    if platform.system() == 'Windows':
        if BINLOCAL:
            EXECYDL = os.path.join(CACHEDIR, 'youtube-dl.exe')
        else:
            try:
                import youtube_dl
                pypath = youtube_dl.__file__.split('lib')[0]
                EXECYDL = os.path.join(pypath, 'bin', 'youtube-dl.exe')
            except Exception as e:
                print(e)
        if os.path.isfile(EXECYDL):
            LINE_MSG = ('\nRequires MSVCR100.dll\nTo resolve this problem '
                          'install: Microsoft Visual C++ 2010 Redistributable '
                          'Package (x86)')
        else:
            LINE_MSG = ('Unrecognized error')

    else:
        if BINLOCAL:
            EXECYDL = os.path.join(CACHEDIR, 'youtube-dl')
        else:
            try:
                import youtube_dl
                pypath = youtube_dl.__file__.split('lib')[0]
                EXECYDL = os.path.join(pypath, 'bin', 'youtube-dl')
            except Exception as e:
                print(e)

        LINE_MSG = ('Unrecognized error')
    # -----------------------------------------------------------------------#

    def __init__(self, url, quality):
        """
        Accept a single url as a string and a quality parameter
        in the form required by youtube-dl, e.g one of the
        following strings can be valid:

            "worst", "best" or a Format Code.
        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate valur
        self.startffplay = False  # to start ffplay
        self.url = url
        self.quality = quality
        if platform.system() == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.ssl = '--no-check-certificate'
        else:
            self.ssl = ''
    # ----------------------------------------------------------------------#

    def run(self):
        """
        Starting thread.
        """
        cmd = ('"{0}" {1} --newline --ignore-errors -o '
               '"{2}/%(title)s_{3}.%(ext)s" --format {3} '
               '--no-playlist --no-part --ignore-config '
               '--restrict-filenames "{4}" '
               '--ffmpeg-location "{5}"'.format(Exec_Download_Stream.EXECYDL,
                                                self.ssl,
                                                Exec_Download_Stream.CACHEDIR,
                                                self.quality,
                                                self.url,
                                                Exec_Download_Stream.FFMPEG_URL,
                                                ))
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
                    else:  # self.stop_work_thread:  # break 'for' loop
                        p.terminate()
                        break

                if p.wait():  # error
                    if 'line' not in locals():
                        line = Exec_Download_Stream.LINE_MSG
                    #msg_Error('Error: {}\n{}'.format(p.wait(), line))
                    msg_Error('{}'.format(line))

        except (OSError, FileNotFoundError) as err:
            msg_Error("%s\n  %s" % (
                       err, Exec_Download_Stream.EXECUTABLE_NOT_FOUND_MSG))
            return

        if self.stop_work_thread:  # break first 'for' loop
            p.terminate()
            return
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#


class Exec_Streaming(object):
    """
    Handling Threads to download and playback media streams via
    youtube-dl and ffmpeg executables.

    DOWNLOAD class variable makes the object's attributes available
    even outside of class, see `stop_download()`
    FIXME put RICEIVER LISTENER function as methods of this class. For
          now does not work (???)

    """
    DOWNLOAD = None  # set instance thread
    # ---------------------------------------------------------------#

    def __init__(self, url=None, quality=None):
        """
        topic "START_FFPLAY_EVT" subscribes a start download listener
        to run ffplay at a certain time.
        topic "STOP_DOWNLOAD_EVT" subscribes a stop download listener
        which call the stop() method of `Exec_Download_Stream` class
        to stop the download and delete file on cache diretrory when
        ffplay has finished.
        """
        pub.subscribe(stop_download, "STOP_DOWNLOAD_EVT")
        pub.subscribe(listener, "START_FFPLAY_EVT")

        self.thread_download = Exec_Download_Stream(url, quality)
        Exec_Streaming.DOWNLOAD = self.thread_download
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        call Exec_Download_Stream(Thread) to run() method
        """
        Exec_Streaming.DOWNLOAD.start()
        return


# --------- RECEIVER LISTENERS
def stop_download(filename):
    """
    Receive message from ffplay_file.File_Play class
    for handle interruption
    """
    Exec_Streaming.DOWNLOAD.stop()
    Exec_Streaming.DOWNLOAD.join()
    if os.path.isfile(filename):
        os.remove(filename)
    return

def listener(output):
    """
    Riceive message from Exec_Download_Stream class to start
    ffplay in this time.
    """
    IO_tools.stream_play(output, '', '')
    return
