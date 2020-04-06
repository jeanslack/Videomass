# -*- coding: UTF-8 -*-

#########################################################
# Name: one_pass.py 
# Porpose: FFmpeg long processing task on one pass conversion
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov 16 2019
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
import itertools
import os
from threading import Thread
import time
from pubsub import pub

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf # path to the configuration directory:
ffmpeg_url = get.ffmpeg_url
ffmpeg_loglev = get.ffmpeg_loglev
threads = get.threads

if not OS == 'Windows':
    import shlex
    
not_exist_msg =  _("Is 'ffmpeg' installed on your system?")

#----------------------------------------------------------------#    
def logWrite(cmd, sterr, logname):
    """
    writes ffmpeg commands and status error during threads below
    
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
        
    else:
        apnd = "%s\n\n" % (cmd)
        
    with open("%s/log/%s" % (DIRconf, logname), "a") as log:
        log.write(apnd)
        
#------------------------------ THREADS -------------------------------#
"""
NOTE MS Windows:

subprocess.STARTUPINFO() 

https://stackoverflow.com/questions/1813872/running-
a-process-in-pythonw-with-popen-without-a-console?lq=1>

NOTE capturing output in real-time (Windows, Unix):

https://stackoverflow.com/questions/1388753/how-to-get-output-
from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

"""
class OnePass(Thread):
    """
    This class represents a separate thread for running processes, which 
    need to read the stdout/stderr in real time.
    """
    def __init__(self, varargs, duration, logname, timeseq):
        """
        Some attribute can be empty, this depend from conversion type. 
        If the format/container is not changed on a conversion, the 
        'extoutput' attribute will have an empty value.
        The 'volume' attribute may also have an empty value, but it will 
        have no influence on the type of conversion.
        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False # process terminate
        self.filelist = varargs[1] # list of files (elements)
        self.command = varargs[4] # comand set on single pass
        self.outputdir = varargs[3] # output path
        self.extoutput = varargs[2] # format (extension)
        self.duration = duration # duration list
        self.volume = varargs[7]# (lista norm.)se non richiesto rimane None
        self.count = 0 # count first for loop
        self.countmax = len(varargs[1]) # length file list
        self.logname = logname # title name of file log
        self.time_seq = timeseq # a time segment

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        
        """
        for (files,
             folders,
             volume,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.outputdir, 
                                                self.volume, 
                                                self.duration,
                                                fillvalue='',
                                                ):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione
            source_ext = os.path.splitext(basename)[1].split('.')[1]# ext
            outext = source_ext if not self.extoutput else self.extoutput
                
            cmd = ('%s %s %s -i "%s" %s %s %s '
                   '-y "%s/%s.%s"' %(ffmpeg_url, 
                                     self.time_seq,
                                     ffmpeg_loglev,
                                     files, 
                                     self.command,
                                     volume,
                                     threads,
                                     folders, 
                                     filename,
                                     outext,
                                     ))
            self.count += 1
            count = 'File %s/%s' % (self.count, self.countmax,)
            com = "%s\n%s" % (count, cmd)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(com, '', self.logname)# write n/n + command only
            
            if not OS == 'Windows':
                cmd = shlex.split(cmd)
                info = None
            else: # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                with subprocess.Popen(cmd,
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True,
                                      startupinfo=info,) as p:
                    for line in p.stderr:
                        #print(line, end=''),
                        
                        wx.CallAfter(pub.sendMessage, 
                                    "UPDATE_EVT", 
                                    output=line, 
                                    duration=duration,
                                    status=0,
                                    )
                        if self.stop_work_thread:
                            p.terminate()
                            break # break second 'for' loop
                        
                    if p.wait(): # error
                        wx.CallAfter(pub.sendMessage, 
                                    "UPDATE_EVT", 
                                    output=line, 
                                    duration=duration,
                                    status=p.wait(),
                                    )
                        logWrite('', 
                                 "Exit status: %s" % p.wait(),
                                 self.logname)
                                 #append exit error number
                    else: # ok
                        wx.CallAfter(pub.sendMessage, 
                                        "COUNT_EVT", 
                                        count='', 
                                        duration='',
                                        fname='',
                                        end='ok'
                                        )
            except OSError as err:
                e = "%s\n  %s" % (err, not_exist_msg)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             end='error',
                             )
                break
            
            if self.stop_work_thread:
                p.terminate()
                break # break second 'for' loop
                
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
    #--------------------------------------------------------------------#
    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True