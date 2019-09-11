# -*- coding: UTF-8 -*-

#########################################################
# Name: ffplay_reproduction.py 
# Porpose: simple media player with x-window-terminal-emulator for Ms Windows
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
import time
from threading import Thread
from videomass3.vdms_IO.make_filelog import write_log # write initial log

########################################################################
# get data from bootstrap
get = wx.GetApp()
DIRconf = get.DIRconf # path to the configuration directory
#########################################################################

def msg_Error(msg):
    """
    Receive error messages from Play(Thread) via wxCallafter
    
    """
    wx.MessageBox("FFplay ERROR:  %s" % (msg), 
                      "Videomass: FFplay", 
                      wx.ICON_ERROR
                      )
#-----------------------------------------------------------------#
def msg_Info(msg):
    """
    Receive info messages from Play(Thread) via wxCallafter
    
    """
    wx.MessageBox("FFplay INFORMATION:  %s" % (msg), 
                      "Videomass: FFplay", 
                      wx.ICON_INFORMATION
                      )
#########################################################################

class Play(Thread):
    """
    Run a separate process thread for media reproduction with
    a called at ffplay witch need x-window-terminal-emulator 
    to show files streaming.
    
    """
    def __init__(self, filepath, timeseq, ffplay_link, 
                 param, ffplay_loglevel, OS):
        """
        The self.ffplay_loglevel flag has 'error -hide_banner' 
        by default (see conf. file).
        NOTE: Do not use '-stats' option do not work.
        
        """
        Thread.__init__(self)
        ''' constructor'''

        self.filename = filepath # file name selected
        self.ffplay = ffplay_link, # command process
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
        In this thread the ffplay subprocess is managed so as to direct
        the output of "p.returncode" and the "OSError" exception on the 
        errors, while all the rest of the output as information given by 
        "error [1]" .
        
        On Python3.7.4 of the MS Windows 7 64bit the ffplay_link 
        becomes a tuple here, I think for security reasons given
        the lack of shlex
        
        """
        #time.sleep(.5)
        command = '%s -loglevel %s %s -i "%s" %s' % (self.ffplay[0],
                                                     self.ffplay_loglevel,
                                                     self.time_seq,
                                                     self.filename,
                                                     self.param,)
        self.logWrite(command)
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(command,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 startupinfo=startupinfo,
                                 )
            error =  p.communicate()
        
        except OSError as err:
            pyerror = ("%s: 'ffplay.exe'") % (err)
            wx.CallAfter(Messages, pyerror)
            self.logError(pyerror) # append log error
            return
        
        else: # WARNING else fa parte del blocco try
            if p.returncode: # ffplay error 
                if error[1]:
                    msg = error[1]
                else: 
                    msg = "Unrecognized error"
                
                wx.CallAfter(msg_Error, error[1])
                self.logError(error[1]) # append log error
                return
            
        if error[1]: # ffplay info
            wx.CallAfter(msg_Info, error[1])
            self.logWrite(error[1]) # append log info
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
        
