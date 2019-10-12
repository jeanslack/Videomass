# -*- coding: UTF-8 -*-

#########################################################
# Name: task_processing.py
# Porpose: module for long processing task
# Compatibility: Python3, wxPython4 Phoenix (for Ms Windows only)
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec 27 2018, Sept.07.2019
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
import sys
import os
from threading import Thread
import time
from pubsub import pub
from videomass3.vdms_IO.make_filelog import write_log

# Setting global variables to communicate status between processes:
CHANGE_STATUS = None
STATUS_ERROR = None
# path to the configuration directory:
get = wx.GetApp()
DIRconf = get.DIRconf
ffmpeg_url = get.ffmpeg_url
ffmpeg_loglev = get.ffmpeg_loglev

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
        
#----------------------------------------------------------------#
########################################################################

class GeneralProcess(wx.Panel):
    """
    This panel is shown in all conversion finalization processes. 
    It displays a text control for the output log, a progress bar, 
    and a progressive percentage text label. This class must be used 
    in combination with separate threads for process tasks.
    It also implements the buttons to stop the current process and 
    close the panel during final activities.
    
    """
    def __init__(self, parent, panel, varargs, duration, OS):
        """
        In the 'previous' attribute is stored an ID string used to
        recover the previous panel from which the process is started.
        The 'logname' attribute is the name_of_panel.log file in which 
        log messages will be written
        
        """
        self.parent = parent # main frame
        self.previus = panel # stores the panel from which  it starts
        self.countmax = varargs[9]# the multiple task number
        self.count = 0 # initial setting of the counter
        self.logname = varargs[8] # example: Videomass_VideoConversion.log
        self.duration = duration # total duration or partial if set timeseq
        self.time_seq = self.parent.time_seq # a time segment
        self.OS = OS # operative sistem name Identifier
        self.varargs = varargs # tuple data
        
        wx.Panel.__init__(self, parent=parent)
        """ Constructor """

        lbl = wx.StaticText(self, label=_("Log View Console:"))
        self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                                   style = wx.TE_MULTILINE | 
                                   wx.TE_READONLY | 
                                   wx.TE_RICH2
                                    )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY,(_("Suppress excess "
                                                        "output")))
        self.barProg = wx.Gauge(self, wx.ID_ANY, range = 0)
        self.labPerc = wx.StaticText(self, label="Percentage: 0%")
        self.button_stop = wx.Button(self, wx.ID_STOP, _("Abort"))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(1, 2, 5, 5)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.OutText, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        sizer.Add(self.labPerc, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5 )
        sizer.Add(self.barProg, 0, wx.EXPAND|wx.ALL, 5 )
        sizer.Add(grid, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        grid.Add(self.button_stop, 0, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)

        # set_properties:
        if OS == 'Darwin':
            self.OutText.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.OutText.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            
        #self.OutText.SetBackgroundColour((217, 255, 255))
        #self.ckbx_text.SetToolTip(_("Show FFmpeg messages in real time "
                                    #"in the log view console, useful for "
                                    #"knowledge the all exit status as "
                                    #"errors and warnings."
                                           #))
        self.ckbx_text.SetToolTip(_('If activated, hides all FFmpeg '
                                    'output messages.'))
        self.button_stop.SetToolTip(_("Stops current process"))
        self.SetSizerAndFit(sizer)

        # bind
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        
        #------------------------------------------
        print ('[VIDEOMASS] Initial log:')
        write_log(self.logname, "%s/log" % DIRconf) # set initial file LOG
        
        time.sleep(.1)
        self.button_stop.Enable(True)
        self.button_close.Enable(False)

        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
        
        self.startThread()
        
    def startThread(self):
        """
        Thread redirection
        """
        if self.varargs[0] == 'common':# from all panels
            Common_Thread(self.varargs, self.duration,
                          self.logname, self.time_seq,
                          ) 
        elif self.varargs[0] == 'doublepass': # from Vidconv/Prstmng panels
            TwoPass_Video(self.varargs, self.duration,
                          self.logname, self.time_seq
                          )
        elif self.varargs[0] == 'EBU normalization':# from Vidconv/Aconv panels
            TwoPass_Loudnorm(self.varargs, self.duration, 
                             self.logname, self.time_seq
                            )
    #-------------------------------------------------------------------#
    def update_display(self, output, duration, status):
        """
        Receive message from thread of the second loops process
        by wxCallafter and pubsub UPDATE_EVT.
        The received 'output' is parsed for calculate the bar 
        progress value, percentage label and errors management.
        This method can be used even for non-loop threads.
        
        NOTE: During conversion the ffmpeg errors do not stop all 
              others tasks, if an error occurred it will be marked 
              with 'failed' but continue; if it has finished without 
              errors it will be marked with 'completed' on update_count
              method. Since not all ffmpeg messages are errors, sometimes 
              it happens to see more output marked with yellow color. 
              
        This strategy consists first of capturing all the output and 
        marking it in yellow, then in capturing the error if present, 
        but exiting immediately after the function.
        
        """
        #if self.ckbx_text.IsChecked(): # ffmpeg output messages in real time:
            #self.OutText.AppendText(output)
            
        if not status == 0:# error, exit status of the p.wait
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText(_(' ...Failed\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            return # must be return here
            
        if 'time=' in output:# ...in processing
            i = output.index('time=')+5
            pos = output[i:i+8].split(':')
            hours, minutes, seconds = pos[0],pos[1],pos[2]
            timesum = (int(hours)*60 + int(minutes))*60 + int(seconds)
            self.barProg.SetValue(timesum)
            percentage = timesum / duration * 100
            self.labPerc.SetLabel("Percentage: %s%%" % str(int(percentage)))
            del output, duration

        else:# append all others lines on the textctrl and log file
            if not self.ckbx_text.IsChecked():# not print the output
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
                self.OutText.AppendText(' %s' % output)
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
                
            with open("%s/log/%s" %(DIRconf, self.logname),"a") as logerr:
                logerr.write("[FFMPEG]: %s" % (output))
                # write a row error into file log
            
    #-------------------------------------------------------------------#
    def update_count(self, count, duration, fname, end):
        """
        Receive message from first 'for' loop in the thread process.
        This method can be used even for non-loop threads.
        
        """
        if end == 'ok':
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 164, 30)))
            self.OutText.AppendText(_(' ...Completed\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            return
            
        if STATUS_ERROR == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200, 183, 47)))
            self.OutText.AppendText('\n  %s\n' % (count))
            self.labPerc.SetLabel("Percentage: 0%")
        else:
            self.barProg.SetRange(duration)#set la durata complessiva
            self.barProg.SetValue(0)# resetto la prog bar
            self.labPerc.SetLabel("Percentage: 100%")
            self.OutText.AppendText('\n  %s : "%s"\n' % (count,fname))
    #-------------------------------------------------------------------#
    
    def on_stop(self, event):
        """
        The user change idea and was stop process
        """
        global CHANGE_STATUS
        CHANGE_STATUS = 1
        event.Skip()
    #-------------------------------------------------------------------#
    def on_close(self, event):
        """
        close dialog and show main frame
        
        """
        global CHANGE_STATUS
        global STATUS_ERROR
        STATUS_ERROR = None
        CHANGE_STATUS = None
        self.OutText.Clear()# reset textctrl before close
        self.parent.panelShown(self.previus)# retrieve at previusly panel
        event.Skip()
    #-------------------------------------------------------------------#
    def end_proc(self):
        """
        At the end of the process
        """
        if STATUS_ERROR == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText(_('\n Sorry, tasks failed !\n'))
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        elif CHANGE_STATUS == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(164, 30, 164)))
            self.OutText.AppendText(_('\n Interrupted Process !\n'))
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        else:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 62, 164)))
            self.OutText.AppendText(_('\n Done !\n'))
            self.labPerc.SetLabel("Percentage: 100%")
            self.button_stop.Enable(False)
            self.button_close.Enable(True)
            self.barProg.SetValue(0)

########################################################################
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
class Common_Thread(Thread):
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
        global STATUS_ERROR
        
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
                
            cmd = ('%s -nostdin %s -loglevel %s -i "%s" %s '
                   '%s -y "%s/%s.%s"' %(ffmpeg_url, 
                                        self.time_seq,
                                        ffmpeg_loglev,
                                        files, 
                                        self.command,
                                        volume,
                                        folders, 
                                        filename,
                                        outext,
                                        ))
            self.count += 1
            count = 'File %s/%s' % (self.count, self.countmax,)
            com = "%s\n%s" % (count, cmd)
            print("%s" % com)
            
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(com, '', self.logname)# write n/n + command only
            
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                with subprocess.Popen(cmd,
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True,
                                      startupinfo=startupinfo,) as p:
                    for line in p.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print(line, end=''),
                        
                        wx.CallAfter(pub.sendMessage, 
                                    "UPDATE_EVT", 
                                    output=line, 
                                    duration=duration,
                                    status=0,
                                    )
                        if CHANGE_STATUS == 1:# break second 'for' loop
                            p.terminate()
                            break
                        
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
                        print('...Done\n')
                        
            except OSError as err:
                e = "%s: 'ffmpeg.exe'" % (err)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             end='',
                             )
                print('...%s' % (e))
                STATUS_ERROR = 1
                break
            
            if CHANGE_STATUS == 1:# break first 'for' loop
                p.terminate()
                print('...Interrupted process')
                break
                
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")

########################################################################

class TwoPass_Video(Thread):
    """
    This class represents a separate thread which need to read the 
    stdout/stderr in real time mode. The subprocess module is instantiated 
    twice for two different tasks: the process on the first video pass and 
    the process on the second video pass for video only.
    """
    def __init__(self, varargs, duration, logname, timeseq):
        """
        The 'volume' attribute may have an empty value, but it will 
        have no influence on the type of conversion.
        """
        Thread.__init__(self)
        """initialize"""

        self.filelist = varargs[1] # list of files (elements)
        self.passList = varargs[5] # comand list set for double-pass
        self.outputdir = varargs[3] # output path
        self.extoutput = varargs[2] # format (extension)
        self.duration = duration # duration list
        self.time_seq = timeseq # a time segment
        self.volume = varargs[7]# volume compensation data
        self.count = 0 # count first for loop
        self.countmax = len(varargs[1]) # length file list
        self.logname = logname # title name of file log
        self.nul = 'NUL' # only for Windows (/dev/null for Unix like)
        
        self.start()# start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        
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
            
            #--------------- first pass
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
                
            pass1 = ('%s -nostdin -loglevel %s %s -i "%s" %s %s"%s/%s.log" '
                     '-y %s' % (ffmpeg_url, 
                                ffmpeg_loglev,
                                self.time_seq,
                                files, 
                                self.passList[0],
                                passpar,
                                folders, 
                                filename,
                                self.nul,
                                ))  
            self.count += 1
            count = 'File %s/%s - Pass One' % (self.count, self.countmax,)
            cmd = "%s\n%s" % (count, pass1)
            print("%s" % cmd)
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)# write n/n + command only
            
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                with subprocess.Popen(pass1, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True,
                                      startupinfo=startupinfo,) as p1:
                    
                    for line in p1.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print (line, end=''),
                        
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=0
                                     )
                        if CHANGE_STATUS == 1:# break second 'for' loop
                            p1.terminate()
                            break
                        
                    if p1.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p1.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p1.wait(),
                                 self.logname)
                                 #append exit error number
                    
            except OSError as err:
                e = "%s: 'ffmpeg.exe'" % (err)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             end=''
                             )
                STATUS_ERROR = 1
                break
                    
            if CHANGE_STATUS == 1:# break first 'for' loop
                p1.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p1.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
            
            #--------------- second pass ----------------#
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
                
            pass2 = ('%s -nostdin -loglevel %s %s -i "%s" %s %s %s'
                     '"%s/%s.log" -y "%s/%s.%s"' % (ffmpeg_url,
                                                    ffmpeg_loglev,
                                                    self.time_seq,
                                                    files, 
                                                    self.passList[1], 
                                                    volume,
                                                    passpar,
                                                    folders, 
                                                    filename,
                                                    folders, 
                                                    filename,
                                                    self.extoutput,
                                                    ))
            count = 'File %s/%s - Pass Two' % (self.count, self.countmax,)
            cmd = "%s\n%s" % (count, pass2)
            print("%s" % cmd)
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(pass2, 
                                  stderr=subprocess.PIPE, 
                                  bufsize=1, 
                                  universal_newlines=True,
                                  startupinfo=startupinfo,) as p2:
                    
                    for line2 in p2.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print (line2, end=''),
                        
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line2, 
                                     duration=duration,
                                     status=0,
                                     )
                        if CHANGE_STATUS == 1:
                            p2.terminate()
                            break
                    
                    if p2.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p2.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p2.wait(), 
                                 self.logname)
                                 #append exit error number
                        
            if CHANGE_STATUS == 1:# break first 'for' loop
                p2.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p2.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
            
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc(e)
        elif CHANGE_STATUS == 1:
            self.endProc('Interrupted process')
        else:
            self.endProc('Done')
    #----------------------------------------------------------------#
    def endProc(self, mess):
        """
        print end messagess to console
        """
        print('...%s' % (mess))
########################################################################

class TwoPass_Loudnorm(Thread):
    """
    This class represents a separate thread which need to read the 
    stdout/stderr in real time mode. The subprocess module is instantiated 
    twice for two different tasks: the process on the first video pass and 
    the process on the second video pass for video only.
    """
    def __init__(self, var, duration, logname, timeseq):
        """
        """
        Thread.__init__(self)
        """initialize"""

        self.filelist = var[1] # list of files (elements)
        self.ext = var[4]
        self.passList = var[5] # comand list set for double-pass
        self.outputdir = var[3] # output path
        self.duration = duration # duration list
        self.time_seq = timeseq # a time segment
        self.count = 0 # count first for loop 
        self.countmax = len(var[1]) # length file list
        self.logname = logname # title name of file log
        self.nul = 'NUL' # only for Windows (/dev/null for Unix like)
        
        self.start()# start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        summary = {'Input Integrated:': None, 'Input True Peak:': None, 
                   'Input LRA:': None, 'Input Threshold:': None, 
                   'Output Integrated:': None, 'Output True Peak:': None, 
                   'Output LRA:': None, 'Output Threshold:': None, 
                   'Normalization Type:': None, 'Target Offset:': None
                   }
        muxers = {'mkv': 'matroska', 'avi': 'avi', 'flv': 'flv', 'mp4': 'mp4',
                  'm4v': 'null', 'ogg': 'ogg', 'webm': 'webm',}
        for (files,
             folders,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.outputdir, 
                                                self.duration,
                                                fillvalue='',
                                                ):
            basename = os.path.basename(files) # name.ext 
            filename = os.path.splitext(basename)[0]# name
            source_ext = os.path.splitext(basename)[1].split('.')[1]# ext
            outext = source_ext if not self.ext else self.ext
            if self.passList[3]: # True(2pass video) or False(copy/std)
                force = '-f %s' % muxers[outext]
            else:
                force = '-f null'
            
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
            
            #--------------- first pass
            pass1 = ('{0} -nostdin -loglevel info -stats -hide_banner '
                     '{1} -i "{2}" {3} {9}"{4}/{5}.log" -af {6} '
                     '{7} -y {8}'.format(ffmpeg_url, 
                                         self.time_seq,
                                         files, 
                                         self.passList[0],
                                         folders,
                                         filename,
                                         self.passList[2],#loudnorm
                                         force,# -f 
                                         self.nul,
                                         passpar,
                                        )) 
            self.count += 1
            count = ('Loudnorm af: Getting statistics for measurements...\n  '
                     'File %s/%s - Pass One' % (self.count, self.countmax,))
            cmd = "%s\n%s" % (count, pass1)
            print("%s" % cmd)
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)# write n/n + command only
            
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                with subprocess.Popen(pass1, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True,
                                      startupinfo=startupinfo,) as p1:
                    
                    for line in p1.stderr:
                        print (line, end='', ),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=0
                                     )
                        if CHANGE_STATUS == 1:# break second 'for' loop
                            p1.terminate()
                            break
                        
                        for k in summary.keys():
                            if line.startswith(k):
                                summary[k] = line.split(':')[1].split()[0]
                        
                    if p1.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p1.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p1.wait(),
                                 self.logname)
                                 #append exit error number
                        break
                    
            except OSError as err:
                e = "%s: 'ffmpeg.exe'" % (err)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             end=''
                             )
                STATUS_ERROR = 1
                break
                    
            if CHANGE_STATUS == 1:# break first 'for' loop
                p1.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p1.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
            #--------------- second pass ----------------#
            filters = ('%s:measured_I=%s:measured_LRA=%s:measured_TP=%s:'
                       'measured_thresh=%s:offset=%s:linear=true:dual_mono='
                       'true' %(self.passList[2],
                                summary["Input Integrated:"], 
                                summary["Input LRA:"],
                                summary["Input True Peak:"], 
                                summary["Input Threshold:"], 
                                summary["Target Offset:"]
                                )
                       )
            time.sleep(.5)
            if 'libx265' in self.passList[1]:
                passpar = '-x265-params pass=1:stats='
            else:
                passpar = '-pass 1 -passlogfile '
                
            pass2 = ('{0} -nostdin -loglevel info -stats -hide_banner '
                     '{1} -i "{2}" {3} {8}"{5}/{6}.log" -af '
                     '{4} -y "{5}/{6}.{7}"'.format(ffmpeg_url, 
                                                   self.time_seq,
                                                   files,
                                                   self.passList[1],
                                                   filters,
                                                   folders, 
                                                   filename,
                                                   outext,
                                                   passpar,
                                                   ))
            print(pass2)
            count = ('Loudnorm af: apply EBU R128...\n  '
                     'File %s/%s - Pass Two' % (self.count, self.countmax,))
            cmd = "%s\n%s" % (count, pass2)
            print("%s" % cmd)
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname)
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(pass2, 
                                  stderr=subprocess.PIPE, 
                                  bufsize=1, 
                                  universal_newlines=True,
                                  startupinfo=startupinfo,) as p2:
                    
                    for line2 in p2.stderr:
                        print (line2, end=''),
                        
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line2, 
                                     duration=duration,
                                     status=0,
                                     )
                        if CHANGE_STATUS == 1:
                            p2.terminate()
                            break
                    
                    if p2.wait(): # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration,
                                     status=p2.wait(),
                                     )
                        logWrite('', 
                                 "Exit status: %s" % p2.wait(), 
                                 self.logname)
                                 #append exit error number
                        
            if CHANGE_STATUS == 1:# break first 'for' loop
                p2.terminate()
                break # fermo il ciclo for, altrimenti passa avanti
            
            if p2.wait() == 0: # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count='', 
                             duration='',
                             fname='',
                             end='ok'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc(e)
        elif CHANGE_STATUS == 1:
            self.endProc('Interrupted process')
        else:
            self.endProc('Done')
    #----------------------------------------------------------------#
    def endProc(self, mess):
        """
        print end messagess to console
        """
        print('...%s' % (mess))
