# -*- coding: UTF-8 -*-

#########################################################
# Name: update.py
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
import sys
import wx
from pubsub import pub
from threading import Thread


class CheckNewRelease(Thread):
    """
    This class represents a separate subprocess thread to get
    audio volume peak level when required for audio normalization
    process.
    """
    def __init__(self, package, OS):
        """
        """
        Thread.__init__(self)
        """initialize"""
        self.package = package
        #self.thisvers = thisvers
        self.OS = OS
        self.data = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release with pip tool
        """
        cmd = [sys.executable,
            '-m',
            'pip',
            'search',
            '--disable-pip-version-check',
            '--no-color',
            '--no-python-version-warning',
            '%s' % self.package,
            ]

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
            print('OSERROR: %s' % oserror)
            self.data = ('%s' % oserr, 'error')

        if p.returncode:  # if returncode == 1
            print('returncode')
            self.data = (out[0], 'error')

        else:
            print('ok')
            self.data = (out[0], out[1])

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# --------------------------------------------------------------
