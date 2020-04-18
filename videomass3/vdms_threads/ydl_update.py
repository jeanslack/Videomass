# -*- coding: UTF-8 -*-

#########################################################
# Name: ydl_update.py
# Porpose: check new version release
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import subprocess
import ssl
import urllib.request
import wx
from pubsub import pub
from threading import Thread


class CheckNewRelease(Thread):
    """
    This class represents a separate thread to read
    latest version of youtube-dl .
    """
    def __init__(self, url):
        """
        """
        Thread.__init__(self)
        """initialize"""
        self.url = url
        self.data = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        try:
            req = (urllib.request.build_opener().open(
                   self.url).read().decode('utf-8').strip())
            self.data = req, None

        except urllib.error.HTTPError as error:
            self.data = None, error

        except urllib.error.URLError as error:
            self.data = None, error

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# -------------------------------------------------------------------------#


class Update(Thread):
    """
    This class represents a separate thread to update
    installed version of youtube-dl .
    """
    def __init__(self, OS):
        """
        """
        Thread.__init__(self)
        """initialize"""
        self.OS = OS
        self.data = None
        self.status = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        """
        cmd = ['youtube-dl', '--update']

        if self.OS == 'Windows':
            cmd = " ".join(cmd)
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        else:
            info = None

        try:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,  # mod text
                                 startupinfo=info,
                                 )
            out = p.communicate()

        except OSError as oserr:  # executable do not exist
            self.status = ('%s' % oserr, 'error')
            #self.data  = ('%s' % oserr, 'error')
        else:
            if p.returncode:  # if returncode == 1
                self.status = (out[0], 'error')
                #self.data = (out[0], 'error')

            else:
                self.status = (out[0], out[1])

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
