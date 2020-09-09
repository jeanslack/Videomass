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
    Receive error messages via wxCallafter
    """
    #wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_ERROR)
    print(msg)
# ------------------------------------------------------------------------#


class Exe_Download_Stream(Thread):
    """
    Starts the download of only one media stream at a time and
    saves it in the videomass cache directory until the stored
    file is cleared. The filename form is:

        title_quality.format

    This Thread use youtube-dl as executable with subprocess class
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    FFMPEG_URL = get.FFMPEG_url
    #EXECYDL = get.execYdl
    CACHEDIR = get.CACHEdir

    if not platform.system() == 'Windows':
        EXECYDL = os.path.join(CACHEDIR, 'youtube-dl')
        LINE_MSG = ('Unrecognized error')
    else:
        EXECYDL = os.path.join(CACHEDIR, 'youtube-dl.exe')
        if os.path.isfile(EXECYDL):
            LINE_MSG = ('\nRequires MSVCR100.dll\nTo resolve this problem '
                          'install: Microsoft Visual C++ 2010 Redistributable '
                          'Package (x86)')
        else:
            LINE_MSG = ('Unrecognized error')

    EXECUTABLE_NOT_FOUND_MSG = ("Is 'youtube-dl' installed on your system?")
    # -----------------------------------------------------------------------#

    def __init__(self, url, quality):
        """
        Accept a single url as a string.
        The quality parameter sets the quality of the stream
        in the form required by youtube-dl, e.g one of the
        following strings can be valid:
            worst, best, bestvideo+bestaudio, Format Code
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
        Subprocess initialize thread.
        """
        cmd = ('"{0}" {1} --newline --ignore-errors -o '
               '"{2}/%(title)s_{3}.%(ext)s" --format {3} '
               '--no-playlist --no-part --ignore-config '
               '--restrict-filenames "{4}" '
               '--ffmpeg-location "{5}"'.format(Exe_Download_Stream.EXECYDL,
                                                self.ssl,
                                                Exe_Download_Stream.CACHEDIR,
                                                self.quality,
                                                self.url,
                                                Exe_Download_Stream.FFMPEG_URL,
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
                        line = Exe_Download_Stream.LINE_MSG
                    msg_Error('Error: {}\n{}'.format(p.wait(), line))

        except (OSError, FileNotFoundError) as err:
            msg_Error("%s\n  %s" % (
                       err, Exe_Download_Stream.EXECUTABLE_NOT_FOUND_MSG))
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


class Exe_Streaming(object):
    """
    Handling Threads to download and playback media streams via
    youtube-dl and ffmpeg executables.
    """
    DOWNLOAD = None  # set instance thread
    # ---------------------------------------------------------------#

    def __init__(self, url=None, quality=None):
        """
        """
        pub.subscribe(stop_download, "STOP_DOWNLOAD_EVT")
        pub.subscribe(listener, "START_FFPLAY_EVT")

        self.thread_download = Exe_Download_Stream(url, quality)
        Exe_Streaming.DOWNLOAD = self.thread_download
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        """
        #self.thread_download.start()
        #Exe_Streaming.DOWNLOAD = self.thread_download
        Exe_Streaming.DOWNLOAD.start()
        return


# --------- RECEIVER LISTENERS
def stop_download(filename):
    """
    Receive message from ffplay_file.File_Play class
    for handle interruption
    """
    Exe_Streaming.DOWNLOAD.stop()
    Exe_Streaming.DOWNLOAD.join()
    if os.path.isfile(filename):
        os.remove(filename)
    return

def listener(output):
    """
    Riceive message from Exe_Download_Stream class
    """
    IO_tools.stream_play(output, '', '')
    return
