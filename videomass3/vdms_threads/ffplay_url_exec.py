# -*- coding: UTF-8 -*-
"""
Name: ffplay_url_exec.py
Porpose: playback online media streams with ffplay player
         using youtube-dl as executable.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import os
import sys
from threading import Thread
import subprocess
import platform
import wx
from pubsub import pub
from videomass3.vdms_io import io_tools
from videomass3.vdms_io.make_filelog import write_log  # write initial log
if not platform.system() == 'Windows':
    import shlex
if 'youtube_dl' in sys.modules:
    import youtube_dl


def msg_error(msg, title="Videomass"):
    """
    Receive error messages
    """
    wx.MessageBox("%s" % (msg), title, wx.ICON_ERROR)
# ------------------------------------------------------------------------#


class DownloadStreamExec(Thread):
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
    EXCEPTION = None
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset

    if platform.system() == 'Windows':
        pyname = 'Scripts', 'youtube-dl.exe'
    else:
        pyname = 'bin', 'youtube-dl'

    if appdata['enable_youtubedl'] == 'disabled':
        EXCEPTION = 'error: youtube-dl is disabled, check preferences.'
        EXECYDL = appdata['EXECYDL']

    elif appdata['app'] == 'pyinstaller':
        if appdata['EXECYDL'] is not False:
            EXECYDL = appdata['EXECYDL']
        else:
            EXCEPTION = 'Not found: %s' % appdata['EXECYDL']

    else:
        if 'youtube_dl' in sys.modules:
            # see also inspect: `inspect.getfile(youtube_dl)`
            # or the best: shutil.which('python')
            pypath = youtube_dl.__file__.split('lib')[0]
            pathexec = os.path.join(pypath, pyname[0], pyname[1])
            EXECYDL = appdata['getpath'](pathexec)
        else:
            EXECYDL = False

    if platform.system() == 'Windows':
        if os.path.isfile(EXECYDL):
            LINE_MSG = ('\nRequires MSVCR100.dll\nTo resolve this problem '
                        'install: Required: Microsoft Visual C++ 2010 '
                        'Service Pack 1 Redistributable Package (x86)')
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
        self.tmp = os.path.join(DownloadStreamExec.appdata['cachedir'],
                                'tmp')
        self.logf = os.path.join(DownloadStreamExec.appdata['logdir'],
                                 'ffplay.log')
        self.stop_work_thread = False  # process terminate value
        self.url = url
        self.quality = quality

        if (platform.system() == 'Windows' or
                DownloadStreamExec.appdata['app'] == 'appimage'):

            self.ssl = '--no-check-certificate'

        else:
            self.ssl = ''

        write_log('ffplay.log', DownloadStreamExec.appdata['logdir'])

        if DownloadStreamExec.EXCEPTION:
            wx.CallAfter(msg_error, DownloadStreamExec.EXCEPTION)
            self.logerror(DownloadStreamExec.EXCEPTION)  # append log error
            return

        Thread.__init__(self)
    # ----------------------------------------------------------------------#

    def run(self):
        """
        Starting thread.
        """
        cmd = ('"{0}" {1} --prefer-ffmpeg --newline --ignore-errors -o '
               '"{2}/%(title)s_{3}.%(ext)s" --continue --format {3} '
               '--no-playlist --no-part --ignore-config '
               '--restrict-filenames "{4}" --ffmpeg-location '
               '"{5}"'.format(DownloadStreamExec.EXECYDL,
                              self.ssl,
                              self.tmp,
                              self.quality,
                              self.url,
                              DownloadStreamExec.appdata['ffmpeg_bin'],
                              ))
        self.logwrite(cmd)  # append log cmd
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
                                  startupinfo=info,) as proc:

                for line in proc.stdout:
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
                        proc.terminate()
                        break

                if proc.wait():  # error at end process
                    if 'line' not in locals():
                        line = DownloadStreamExec.LINE_MSG
                    if '[download]' in line:
                        return
                    wx.CallAfter(msg_error,
                                 line,
                                 'Videomass: Error %s' % proc.wait()
                                 )
                    self.logerror(line)  # append log error
                    return

        except OSError as err:
            wx.CallAfter(msg_error, err, 'Videomass: OSError')
            self.logerror(err)  # append log error
            return
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a", encoding='utf8') as log:
            log.write("%s\n" % (cmd))
    # ----------------------------------------------------------------#

    def logerror(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a", encoding='utf8') as logerr:
            logerr.write("\n[FFMPEG] FFplay "
                         "ERRORS:\n%s\n" % (error))
# ------------------------------------------------------------------------#


class ExecStreaming():
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
          which call the stop() method of `DownloadStreamExec` class to
          stop the download when ffplay has finished or been closed by
          the user.

        """
        pub.subscribe(stop_download_listener, "STOP_DOWNLOAD_EVT")
        pub.subscribe(start_palying_listener, "START_FFPLAY_EVT")

        ExecStreaming.DOWNLOAD = DownloadStreamExec(url, quality)
        ExecStreaming.TIMESTAMP = timestamp
        ExecStreaming.AUTOEXIT = autoexit

        self.start_download()
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        call DownloadStreamExec(Thread) to run() method

        """
        if not DownloadStreamExec.EXCEPTION:
            ExecStreaming.DOWNLOAD.start()

# --------- RECEIVER LISTENERS


def stop_download_listener(filename):
    """
    Receive message from ffplay_file.FilePlay class
    for handle interruption

    """
    ExecStreaming.DOWNLOAD.stop()
    ExecStreaming.DOWNLOAD.join()


def start_palying_listener(output):
    """
    Riceive message from DownloadStreamExec class to start
    ffplay in at a given time.

    """
    io_tools.stream_play(output, '', ExecStreaming.TIMESTAMP,
                         ExecStreaming.AUTOEXIT)
