# -*- coding: UTF-8 -*-

#########################################################
# Name: ffplay_reproduction.py 
# Porpose: simple media player with x-window-terminal-emulator for Ms Windows
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/19 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (06) 24/08/2014
# Rev (07) 12/01/2015
# Rev (08) 20/04/2015
# Rev (09) 1 sept. 2018
#########################################################
import subprocess
import time
from threading import Thread

class Play(Thread):
    """
    Run a separate process thread for media reproduction with a called 
    at ffplay witch need x-window-terminal-emulator for show files streaming.
    NOTE: the loglevel is set on 'error'. Do not use 'self.loglevel_type' 
          because -stats option do not work.
    """
    def __init__(self, filepath, ffplay_link, loglevel_type, OS):
        """
        costructor
        """
        Thread.__init__(self)
        """initialize"""
        self.filename = filepath
        self.ffplay = ffplay_link
        self.loglevel_type = loglevel_type
        self.status = None
        self.data = None

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        NOTE for subprocess.STARTUPINFO() 
        < Windows: https://stackoverflow.com/questions/1813872/running-
        a-process-in-pythonw-with-popen-without-a-console?lq=1>
        """
        time.sleep(.5)
        loglevel_type = 'error'

        #try:
        command = [self.ffplay, 
                   '-i', 
                   self.filename, 
                   '-loglevel', 
                   loglevel_type
                   ]
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(command,
                             stderr=subprocess.PIPE,
                             startupinfo=startupinfo,
                             )
        error =  p.communicate()

        # except OSError as err_0:
        #     if err_0[1] == 'No such file or directory':
        #         pyerror = "%s: \nProbably '%s' do not exist in your system" % (
        #         err_0, command[0])
        #         
        #     else:
        #         pyerror = "%s: " % (err_0)
        #         
        #     self.status =  pyerror
        #     
        # #else:
        # if error[1]:
        #     self.status = error[1]
        #     
        # self.data = self.status
