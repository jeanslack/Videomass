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
try:
    import youtube_dl
except (ModuleNotFoundError, ImportError) as nomodule:
    pass


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
# ------------------------------------------------------------------------#


class MyLogger(object):
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd31
    57df2457df7274d0c842421945#embedding-youtube-dl>
    """
    def debug(self, msg):
        #print('DEBUG: ', msg)
        if '[download]' in msg:  # ...in processing
            if 'Destination' in msg:
                print(msg)
                pub.sendMessage("START_FFPLAY_EVT",
                                output=msg.split()[2]
                                )
            elif 'has already been downloaded' in msg:
                print(msg)
                pub.sendMessage("START_FFPLAY_EVT",
                                output=msg.split()[1]
                                )
        self.msg = msg

    def warning(self, msg):
        msg = 'WARNING: %s' % msg
        print(msg)
        #wx.CallAfter(pub.sendMessage,
                     #"UPDATE_YDL_FROM_IMPORT_EVT",
                     #output=msg,
                     #duration='',
                     #status='WARNING',
                     #)

    def error(self, msg):
        print('ERROR: ', msg)
        #wx.CallAfter(pub.sendMessage,
                     #"UPDATE_YDL_FROM_IMPORT_EVT",
                     #output=msg,
                     #duration='',
                     #status='ERROR',
                     #)
# -------------------------------------------------------------------------#


class Url_Play(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output in real time during downloading and conversion .
    For a list of available options see:

    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L279>
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/options.py>

    or by help(youtube_dl.YoutubeDL)

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    OS = get.OS
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    CACHEDIR = get.CACHEdir

    def __init__(self, url, quality):
        """
        define attributes:

        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate value
        self.url = url  # single url
        self.quality = quality  # output quality e.g. worst, best, Format code
        self.outputdir = Url_Play.CACHEDIR  # pathname destination
        self.outtmpl = '%(title)s_{}.%(ext)s'.format(self.quality)  # filename
        #self.logname = logname  # file name to log messages for logging
        if Url_Play.OS == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.nocheckcertificate = True
        else:
            self.nocheckcertificate = False
    # --------------------------------------------------------------#

    def run(self):
        """
        """
        if self.stop_work_thread:
            return

        ydl_opts = {
                'format': self.quality,
                'outtmpl': '{}/{}'.format(self.outputdir, self.outtmpl),
                'restrictfilenames': True,
                'nopart': True,
                'ignoreerrors': True,
                'no_warnings': False,
                'noplaylist': True,
                'no_color': True,
                'nocheckcertificate': self.nocheckcertificate,
                'ffmpeg_location': '{}'.format(Url_Play.FFMPEG_URL),
                'logger': MyLogger(),
                    }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(["{}".format(self.url)])
    # --------------------------------------------------------------#

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
    #Play_Streaming.THR.join()  # if join, wait end process
    if os.path.isfile(filename):
        os.remove(filename)
    return

def listener(output):
    """
    Riceiver
    """
    play = File_Play(output)
    play.start()
    return
