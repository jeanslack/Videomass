# -*- coding: UTF-8 -*-

#########################################################
# Name: ffplay_reproduction.py 
# Porpose: simple media player with x-window-terminal-emulator for Ms Windows
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/19 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

# Rev: Aug.24.2014, Gen.12.2015, Apr.20.2015, sept.01.2018, Oct.13.2018,
#      Sept.02.2019
#########################################################

import wx
import subprocess
import time
from threading import Thread
from videomass2.vdms_SYS.os_interaction import copy_restore # if copy fiile log
from videomass2.vdms_IO.make_filelog import write_log # write initial log

########################################################################
non_ascii_msg = _(u'Non-ASCII/UTF-8 character string not supported. '
                  u'Please, check the filename and correct it.')
not_exist_msg =  _(u'exist in your system?')

# get data from bootstrap
get = wx.GetApp()
DIRconf = get.DIRconf # path to the configuration directory
PATH_log = get.path_log # if not 'none' save the log in other place
#########################################################################

def Messages(msg):
    """
    Receive error messages from Play(Thread) via wxCallafter
    """

    wx.MessageBox("[playback] Error:  %s" % (msg), 
                      "Videomass: FFplay", 
                      wx.ICON_ERROR
                      )
#########################################################################

class Play(Thread):
    """
    Run a separate process thread for media reproduction with a called 
    at ffplay witch need x-window-terminal-emulator for show files streaming.
    NOTE: the loglevel is set on 'error'. Do not use 'self.loglevel_type' 
          because -stats option do not work.
    """
    def __init__(self, filepath, timeseq, 
                 ffplay_link, param, loglevel_type, OS):
        """
        costructor
        """
        Thread.__init__(self)
        """initialize"""
        self.filename = filepath # file name selected
        self.ffplay = ffplay_link # command process
        self.loglevel_type = loglevel_type # not used (used error)
        self.time_seq = timeseq # seeking
        self.param = param # additional parameters if present
        self.OS = OS # tipo di sistema operativo
        self.logf = "%s/log/%s" %(DIRconf, 'Videomass_FFplay.log')
        
        write_log('Videomass_FFplay.log', "%s/log" % DIRconf) 
        # set initial file LOG

        self.start() # start the thread (va in self.run())
        
    #----------------------------------------------------------------#
    def run(self):
        """
        NOTE for subprocess.STARTUPINFO() 
        < Windows: https://stackoverflow.com/questions/1813872/running-
        a-process-in-pythonw-with-popen-without-a-console?lq=1>
        """
        #time.sleep(.5)
        loglevel_type = 'error'
        command = '%s %s -i "%s" %s -loglevel %s' % (self.ffplay,
                                                     self.time_seq,
                                                     self.filename,
                                                     self.param,
                                                     loglevel_type,
                                                     )
        self.logWrite(command)
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(command,
                                stderr=subprocess.PIPE,
                                startupinfo=startupinfo,
                                )
            error =  p.communicate()
            
            if error[1]:
                err = error[1].decode()
                wx.CallAfter(Messages, err)
                self.logError(err) # append log error
                self.pathLog() # log in other place?
                return
        
        except OSError as err_0:
            if err_0[1] == 'No such file or directory':
                pyerror = (u"%s: \n'%s' %s") % (err_0, command[0], 
                                                not_exist_msg)
            else:
                pyerror = "%s: " % (err_0)
            wx.CallAfter(Messages, pyerror)
            self.logError(pyerror) # append log error
            self.pathLog() # log in other place?
            return
        
        except UnicodeEncodeError as err:
            e = (non_ascii_msg
                 )
            wx.CallAfter(Messages, e)
            return
        
        self.pathLog() # log in other place?
        
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write ffmpeg command log
        
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
            
    #----------------------------------------------------------------# 
    def logError(self, error):
        """
        write ffmpeg volumedected errors
        
        """
        print(error)
        with open(self.logf,"a") as logerr:
            logerr.write("[FFMPEG] FFplay "
                         "ERRORS:\n%s\n\n" % (error))
    #----------------------------------------------------------------#
    def pathLog(self):
        """
        if user want file log in a specified path
        
        """
        if not 'none' in PATH_log: 
            copy_restore(self.logf, "%s/%s" % (PATH_log, 
                                               'Videomass_FFplay.log'))
