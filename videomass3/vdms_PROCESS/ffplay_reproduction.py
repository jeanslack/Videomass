# -*- coding: UTF-8 -*-

#########################################################
# Name: ffplay_reproduction.py 
# Porpose: simple media player with x-window-terminal-emulator
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.27.2018, Sept.05.2019
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
import shlex
import time
from threading import Thread
from videomass3.vdms_SYS.os_interaction import copy_restore # if copy fiile log
from videomass3.vdms_IO.make_filelog import write_log # write initial log

#########################################################################
not_exist_msg =  _('exist in your system?')

# get data from bootstrap
get = wx.GetApp()
DIRconf = get.DIRconf # path to the configuration directory
#########################################################################

def Messages(msg):
    """
    Receive error messages from Play(Thread) via wxCallafter
    
    """
    wx.MessageBox("FFplay ERROR:  %s" % (msg), 
                      "Videomass: FFplay", 
                      wx.ICON_ERROR
                      )
#########################################################################
class Play(Thread):
    """
    Run a separate process thread for media reproduction with a called 
    at ffplay witch need x-window-terminal-emulator for show files streaming.
    
    """
    def __init__(self, filepath, timeseq, ffplay_link, 
                 param, ffplay_loglevel, OS):
        """
        The self.ffplay_loglevel has 'error -stats' (see conf. file)
        then use error only with this class.
        
        """
        Thread.__init__(self)
        ''' constructor'''

        self.filename = filepath # file name selected
        self.ffplay = ffplay_link # command process
        self.ffplay_loglevel = ffplay_loglevel
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
        NOTE 1: the loglevel is set on 'error'. Do not use 
               'self.ffplay_loglevel' because -stats  option do not work.
    
        NOTE 2: The p.returncode always returns 0 value even when there 
                is an error. But since ffplay always returns the error 
                on the PIPE of the stderr, then I use the 'error' 
                variable of p.communicate ()
        """
        #time.sleep(.5)
        cmd = '%s -loglevel %s %s -i "%s" %s' % (self.ffplay,
                                                    self.ffplay_loglevel,
                                                    self.time_seq,
                                                    self.filename,
                                                    self.param,
                                                    )
        self.logWrite(cmd)
        
        if self.OS == 'Windows':
                command = cmd
        else:
            command = shlex.split(cmd)
        
        try:
            p = subprocess.Popen(command,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                )
            error =  p.communicate()
        
        except OSError as err_0:
            
            if err_0[1] == 'No such file or directory':
                pyerror = ("%s: \n'%s' %s") % (err_0, command[0], 
                                                not_exist_msg)
            else:
                pyerror = "%s: " % (err_0)
                
            wx.CallAfter(Messages, pyerror)
            self.logError(pyerror) # append log error
            return
        
        else:
            if error[1]:
                wx.CallAfter(Messages, error[1])
                self.logError(error[1]) # append log error
                return
            
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
