# -*- coding: UTF-8 -*-
# Name: mpv_url.py
# Porpose: playback URLs video via mpv
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: May.07.2020 *PEP8 compatible*
# WARNING orphan, no longer used, only for reading
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
try:
    import mpv
except OSError:
    pass
import subprocess
import platform
if not platform.system() == 'Windows':
    import shlex
import os
from threading import Thread
from videomass3.vdms_io.make_filelog import write_log  # write initial log


def msg_Error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox("%s" % (msg),
                  "Videomass: mpv ERROR",
                  wx.ICON_ERROR
                  )


def msg_Info(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox("MPV message information:  %s" % (msg),
                  "Videomass: mpv INFORMATION",
                  wx.ICON_INFORMATION
                  )


class Url_Play(Thread):
    """
    subprocess.Popen class to run mpv media
    player for playback URLs .

    """
    def __init__(self, url, quality, logdir, mpv_url):
        """
        quality: is flag to set media quality result
        """
        self.url = url
        self.quality = quality
        self.logdir = logdir
        self.mpv = mpv_url
        self.logf = os.path.join(self.logdir, 'Videomass_mpv.log')
        write_log('Videomass_mpv.log', self.logdir)  # set initial file LOG

        Thread.__init__(self)
        ''' constructor'''
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output and errors on p.returncode instance and on
        exceptions. Otherwise the getted output as information
        given by output .
        """
        cmd = ('%s --ytdl-raw-options=no-check-certificate= %s '
               '--ytdl-format=%s %s' % (self.mpv,
                                        self.url,
                                        self.quality,
                                        self.url
                                        ))

        if platform.system() == 'Windows':
            shell = False
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.SW_HIDE
        else:
            cmd = shlex.split(cmd)
            info = None
            shell = False

        self.logWrite(cmd)
        try:
            p = subprocess.Popen(cmd,
                                 shell=shell,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            error, output = p.communicate()

        except (OSError, FileNotFoundError) as err:  # exec. do not exists
            wx.CallAfter(msg_Error, _('{}\n\nYou need mpv to play the urls '
                                      'but mpv was not found.').format(err))
            self.logError(err)  # append log error
            return

        else:
            if p.returncode:  # mpv error
                if error:
                    msg = error
                else:
                    msg = "Unrecognized error"
                wx.CallAfter(msg_Error, error)
                self.logError(error)  # append log error
                return

        if output:  # mpv info
            wx.CallAfter(msg_Info, output)
            self.logWrite(output)  # append log info
            return
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write mpv command log
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write mpv errors
        """
        with open(self.logf, "a") as logerr:
            logerr.write("[MPV] MESSAGE:\n%s\n\n" % (error))


class Libmpv_Play(Thread):
    """
    Playback online video stream via python-mpv interface.
    Need libmpv.so either locally (in your current working
    directory) or somewhere in your system library search path.
    """
    def __init__(self, url, quality):
        """
        quality: is flag to set media quality result
        """
        Thread.__init__(self)
        ''' constructor'''
        self.url = url
        self.quality = quality

        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output and errors on p.returncode instance and on
        exceptions. Otherwise the getted output as information
        given by output .
        """
        try :
            # Enable the on-screen controller and keyboard shortcuts
            player = mpv.MPV(input_default_bindings=True,
                             input_vo_keyboard=True,
                             osc=True,
                             ytdl=True,
                             ytdl_format=self.quality
                             )

            # Alternative version using the old "floating box" style on-screen controller
            #player = mpv.MPV(ytdl=True, player_operation_mode='pseudo-gui',
                            #script_opts=('osc-layout=box,osc-seekbarstyle=bar,'
                                        #'osc-deadzonesize=0,osc-minmousemove=3'),
                            #input_default_bindings=True,
                            #input_vo_keyboard=True,
                            #osc=True,
                            #ytdl_format=self.quality
                            #)

            #player.fullscreen = False
            player.play(self.url)
            player.wait_for_playback()
            #player.wait_for_shutdown()
            player.terminate()  # this or use player.quit
            #player.quit()
            print('ok')


        except Exception as err:
            wx.CallAfter(msg_Error, '%s' % err)
            #self.logError(err)  # append log error
            return
