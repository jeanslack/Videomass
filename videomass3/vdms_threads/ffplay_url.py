# -*- coding: UTF-8 -*-
# Name: ffplay_url.py
# Porpose: long processing task with youtube-dl executable
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: September.05.2020 *PEP8 compatible*
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


def msg_Error(msg):
    """
    Receive error messages via wxCallafter
    """
    #wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_ERROR)
    print("%s" % (msg))
# ------------------------------------------------------------------------#


def msg_Info(msg):
    """
    Receive info messages via wxCallafter
    """
    #wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_INFORMATION)
    print("%s" % (msg))
# ------------------------------------------------------------------------#


class File_Play(Thread):
    """
    Simple multimedia playback with subprocess.Popen class to run ffplay
    by FFmpeg (ffplay is a player which need x-window-terminal-emulator)

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    LOGDIR = get.LOGdir
    FFPLAY_URL = get.FFPLAY_url
    FFPLAY_LOGLEV = get.FFPLAY_loglev

    def __init__(self, fname):
        """
        The self.FFPLAY_loglevel has flag 'error -hide_banner'
        by default (see videomass.conf).
        NOTE: Do not use '-stats' option it do not work.
        """
        Thread.__init__(self)
        ''' constructor'''
        self.filename = fname  # file name selected
        self.logdir = File_Play.LOGDIR
        self.ffplay = File_Play.FFPLAY_URL
        self.ffplay_loglev = File_Play.FFPLAY_LOGLEV
        #self.logf = os.path.join(self.logdir, 'Videomass_FFplay.log')
        #write_log('Videomass_FFplay.log', self.logdir)
        # set initial file LOG

        #self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and on
        OSError exception. Otherwise the getted output as information
        given by error [1] .
        """

        # time.sleep(.5)
        cmd = '%s %s -i "%s"' % (self.ffplay,
                                 self.ffplay_loglev,
                                 self.filename,
                                 )
        #self.logWrite(cmd)
        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
            shell = False
        else:
            # NOTE: info flag do not work with ffplay
            # on MS-Windows. Fixed with shell=True flag.
            shell = True
            info = None
            # info = subprocess.STARTUPINFO()
            # info.dwFlags |= subprocess.SW_HIDE
        try:
            p = subprocess.Popen(cmd,
                                 shell=shell,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            error = p.communicate()

        except OSError as err:  # subprocess error
            #wx.CallAfter(msg_Error, err)
            #self.logError(err)  # append log error
            pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
            return

        else:
            if p.returncode:  # ffplay error
                if error[1]:
                    msg = error[1]
                else:
                    msg = "Unrecognized error"

                #wx.CallAfter(msg_Error, error[1])
                #self.logError(error[1])  # append log error
                pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
                return
            else:
                #Threads_Handling.stop_download(self, self.filename)
                pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
                return

        if error[1]:  # ffplay info
            #wx.CallAfter(msg_Info, error[1])
            #self.logWrite(error[1])  # append log info
            pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
            return
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a") as logerr:
            logerr.write("[FFMPEG] FFplay "
                         "ERRORS:\n%s\n\n" % (error))
# ------------------------------------------------------------------------#


class Url_Play(Thread):
    """
    Url_Play represents a separate thread for running
    youtube-dl executable with subprocess class and capturing its
    stdout/stderr output in real time .

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    #EXECYDL = get.execYdl
    CACHEDIR = get.CACHEdir

    if not platform.system() == 'Windows':
        EXECYDL = os.path.join(CACHEDIR, 'youtube-dl')
        LINE_MSG = ('Unrecognized error')
    else:
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

        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate valur
        self.startffplay = False  # to start ffplay
        self.url = url
        self.quality = quality
        #self.logname = 'Stream_playback.log'
        if platform.system() == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.ssl = '--no-check-certificate'
        else:
            self.ssl = ''

        #self.start()
    # ----------------------------------------------------------------------#

    def run(self):
        """
        Subprocess initialize thread.

        """
        cmd = ('"{0}" {1} --newline --ignore-errors -o '
               '"{2}/%(title)s_{3}.%(ext)s" --format {3} '
               '--no-playlist --no-part --ignore-config '
               '--restrict-filenames "{4}" '
               '--ffmpeg-location "{5}"'.format(Url_Play.EXECYDL,
                                                self.ssl,
                                                Url_Play.CACHEDIR,
                                                self.quality,
                                                self.url,
                                                Url_Play.FFMPEG_URL,
                                                ))

        #count = 'URL'
        #com = "%s\n%s" % (count, cmd)
        #logWrite(com, '', self.logname, Url_Play.LOGDIR)  # command only

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
                    else:# self.stop_work_thread:  # break 'for' loop
                        p.terminate()
                        break

                if p.wait():  # error
                    if 'line' not in locals():
                        line = Url_Play.LINE_MSG
                    msg_Error('Error: {}\n{}'.format(p.wait(), line))
                    #logWrite('',
                             #"Exit status: %s" % p.wait(),
                             #self.logname,
                             #Url_Play.LOGDIR,
                             #)  # append exit error number

        except (OSError, FileNotFoundError) as err:
            e = "%s\n  %s" % (err, Url_Play.EXECUTABLE_NOT_FOUND_MSG)
            msg_Error(e)
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


class Play_Streaming(object):
    """
    """
    THR = None  # set instance thread
    # ---------------------------------------------------------------#

    def __init__(self, url=None, quality=None):
        """
        """
        pub.subscribe(stop_download, "STOP_DOWNLOAD_EVT")
        pub.subscribe(listener, "START_FFPLAY_EVT")
        #pub.subscribe(self.listener_1, "START_FFPLAY_EVT")

        self.thread_download = Url_Play(url, quality)
        Play_Streaming.THR = Url_Play(url, quality)
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        """
        #self.thread_download.start()
        #Play_Streaming.THR = self.thread_download
        Play_Streaming.THR.start()
        return


# --------- RECEIVER LISTENERS
def stop_download(filename):
    """
    Receiver
    """
    Play_Streaming.THR.stop()
    Play_Streaming.THR.join()
    if os.path.isfile(filename):
        os.remove(filename)
    return

def listener(output):
    """
    Riceiver
    """
    #start_play(output)
    play = File_Play(output)
    play.start()
    return

#dwl = Play_Streaming('https://www.youtube.com/watch?v=L6WFAfdsuyA', '249')
#dwl.start_download()






