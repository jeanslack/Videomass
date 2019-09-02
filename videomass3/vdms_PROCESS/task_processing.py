# -*- coding: UTF-8 -*-

#########################################################
# Name: task_processing.py 
# Porpose: module for system processing commands
# Compatibility: Python3, wxPython4 Phoenix (OS Unix-like only)
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec 27 2018, Aug 28 2019
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

"""
This module rapresent the main unit of videomas program for all processes 
that involve the subprocess module, classes for separate threads and all 
dialogs and windows for show information on progress process.
"""
import wx
import subprocess
import itertools
import sys
import shlex
import os
from threading import Thread
import re
import time
from pubsub import pub
from videomass3.vdms_SYS.os_interaction import copy_restore
from videomass3.vdms_IO.make_filelog import write_log

# Setting global variables to communicate status between processes:
CHANGE_STATUS = None
STATUS_ERROR = None
# path to the configuration directory:
get = wx.GetApp()
DIRconf = get.DIRconf

########################################################################

class GeneralProcess(wx.Panel):
    """
    This panel is shown in all conversion finalization processes. 
    It displays a text control for the output log, a progress bar, and 
    a progressive percentage text label. This class must be used in 
    combination with separate threads for process tasks.
    It also implements the buttons to stop the current process and 
    close the panel during final activities.
    
    """
    def __init__(self, parent, path_log, panel, varargs,  duration, OS):
        """
        In the 'previous' attribute is stored an ID string used to recover 
        the previous panel from which the process is started.
        The 'logname' attribute contains the name of the log in the which
        write the log text
        
        """
        self.parent = parent # this window is a child of a window parent
        self.previus = panel # memorizza il pannello da cui parte
        self.lenghmax = varargs[9]# the multiple task number
        self.count = 0 # setting iniziale del contatore
        self.logname = varargs[8] # example: Videomass_VideoConversion.log
        self.path_log = path_log # for save a copy if user want
        self.STATUS_ERROR = None # used if error in err_list
        self.CHANGE_STATUS = None #  1 = process interrupted 
        
        self.duration = duration
        self.time_seq = self.parent.time_seq
        self.OS = OS
        self.varargs = varargs
        
        wx.Panel.__init__(self, parent=parent)
        """ Constructor """

        lbl = wx.StaticText(self, label=_("Log View Console:"))
        self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
                                    )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY,(_("Enable the FFmpeg "
                                            "scroll output in real time")))
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
        #self.OutText.SetBackgroundColour((217, 255, 255))
        self.ckbx_text.SetToolTip(_("Show FFmpeg messages in real time "
                                    "in the log view console, useful for "
                                    "knowledge the all exit status as "
                                    "errors and warnings."
                                           ))
        #self.button_stop.SetMinSize((200, 30))
        self.button_stop.SetToolTip(_("Stops current process"))
        #self.button_close.SetMinSize((200, 30))
        #self.SetSizer(sizer)
        self.SetSizerAndFit(sizer)

        # bind
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        
        #------------------------------------------
        initlog = ('\nInitial log:\n')
        print ('\n\n[VIDEOMASS]\n%s' % initlog)
        #self.OutText.AppendText("%s" % initlog)
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
        """
        if self.varargs[0] == 'normal':# from video and audio conv panels
            ProcThread(self.varargs, self.duration,
                       self.OS, self.logname, self.time_seq,
                       ) 
        elif self.varargs[0] == 'doublepass': # from video conv panel
            DoublePassThread(self.varargs, self.duration,
                             self.OS, self.logname, self.time_seq
                             )
        elif self.varargs[0] == 'saveimages': # from video conv panel
            SingleProcThread(self.varargs, self.duration,
                             self.OS, self.logname,
                             )
        elif self.varargs[0] == 'grabaudio':# from audio conv panel
            GrabAudioProc(self.varargs, self.duration,
                          self.OS, self.logname, self.time_seq
                          )
    #-------------------------------------------------------------------#
    def update_display(self, output, duration):
        """
        Receive message from thread of the 'while' loop process. 
        The received 'output' is parsed for calculate the bar 
        progress value, percentage label and errors management.
        """
        if self.ckbx_text.IsChecked(): # ffmpeg output messages in real time:
            self.OutText.AppendText(output)
            
        if 'time=' in output:# ...sta processando
            i = output.index('time=')+5
            pos = output[i:i+8].split(':')
            hours, minutes, seconds = pos[0],pos[1],pos[2]
            timesum = (int(hours)*60 + int(minutes))*60 + int(seconds)
            self.barProg.SetValue(timesum)
            percentage = timesum / duration * 100
            self.labPerc.SetLabel("Percentage: %s%%" % str(int(percentage)))
            del output, duration

        elif self.STATUS_ERROR == None:
            err_list = ('not found', 
                        'Invalid data found when processing input',
                        'Error', 
                        'Invalid', 
                        'Option not found', 
                        'Unknown',
                        'No such file or directory',
                        'does not contain any stream',
                        'Output file is empty, nothing was encoded',)
            
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
            self.OutText.AppendText('\n%s' % output)
            with open("%s/log/%s" %(DIRconf, self.logname),"a") as logerr:
                logerr.write("[FFMPEG] ERRORS:\n%s\n\n" % (output))
                # write a row error into file log
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
                
            for err in err_list:
                global STATUS_ERROR
                if err in output:
                    self.STATUS_ERROR = 1
                    STATUS_ERROR = 1
            #if self.STATUS_ERROR == 1:
                #pass
    #-------------------------------------------------------------------#
    def update_count(self, count, duration, fname):
        """
        Receive message from 'for' loop in the thread process.
        """
        if STATUS_ERROR == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200, 183, 47)))
            self.OutText.AppendText("\n  %s\n" % (count))
            self.labPerc.SetLabel("Percentage: 0%")
        else:
            self.barProg.SetRange(duration)#set la durata complessiva
            self.barProg.SetValue(0)# resetto la prog bar
            self.labPerc.SetLabel("Percentage: 100%")
            self.OutText.AppendText("\n  %s\n  '%s'\n" % (count,fname))

    #-------------------------------------------------------------------#
    def on_stop(self, event):
        """
        The user change idea and was stop process
        """
        self.CHANGE_STATUS = 1
        global CHANGE_STATUS
        CHANGE_STATUS = 1
        event.Skip()
    #-------------------------------------------------------------------#
    def on_close(self, event):
        """
        close dialog and show main frame
        
        """
        self.STATUS_ERROR = None
        self.CHANGE_STATUS = None
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
        if self.STATUS_ERROR == 1 or STATUS_ERROR == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText('\n  Failed !\n\n')
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        elif self.CHANGE_STATUS == 1 or CHANGE_STATUS == 1:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(164, 30, 164)))
            self.OutText.AppendText('\n  ..Interrupted Process !\n\n')
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        else:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 164, 30)))
            self.OutText.AppendText('\n  Done !\n\n')
            self.labPerc.SetLabel("Percentage: 100%")
            self.button_stop.Enable(False)
            self.button_close.Enable(True)
            self.barProg.SetValue(0)

        #if user want file log in a specified path
        if not 'none' in self.path_log : 
            copy_restore("%s/log/%s" % (DIRconf, self.logname),
                         "%s/%s" % (self.path_log, self.logname))

########################################################################
not_exist_msg =  _("Is 'ffmpeg' installed on your system?")
########################################################################

#------------------------------ THREADS -------------------------------#
class ProcThread(Thread):
    """
    This class represents a separate thread for running processes, which 
    need to read the stdout/stderr in real time.
    """
    def __init__(self, varargs, duration, OS, logname, timeseq):
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
        self.ffmpeg_link = varargs[6] # bin executable path-name
        self.duration = duration # duration list
        self.volume = varargs[7]# (lista norm.)se non richiesto rimane None
        self.OS = OS # operative sistem Identifier
        self.count = 0 # count number loop
        self.lenghmax = len(varargs[1]) # lengh file list
        self.logname = logname # title name of file log
        self.time_seq = timeseq

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        status = None
        
        for (files,
             folders,
             volume,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.outputdir, 
                                                self.volume, 
                                                self.duration):

            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione
            
            if volume == None:
                volume = '' #altrimenti inserisce None nei comandi sotto
                
            if self.extoutput == '': # Copy Video Codec and only norm.
                cmd = '%s %s -i "%s" %s %s "%s/%s"' % (self.ffmpeg_link, 
                                                       self.time_seq,
                                                       files, 
                                                       volume, 
                                                       self.command,
                                                       folders, 
                                                       os.path.basename(files)
                                                       )
            else:# single pass
                cmd = '%s %s -i "%s" %s %s "%s/%s.%s"' % (self.ffmpeg_link,
                                                          self.time_seq,
                                                          files, 
                                                          volume, 
                                                          self.command, 
                                                          folders, 
                                                          filename, 
                                                          self.extoutput
                                                          )
            if self.OS == 'Windows':
                args = cmd
            else:
                args = shlex.split(cmd)
                
            self.count += 1
            count = 'File %s/%s' % (self.count, self.lenghmax,)
            com = "%s\n%s" % (count, cmd)
            print("\n%s\n" % com)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files
                         )
            self.logWrite(com)
            
            try:
                '''
                https://stackoverflow.com/questions/1388753/how-to-get-output-
                from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1
                '''
                with subprocess.Popen(args, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True) as p:
                    for line in p.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print(line, end=''),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration
                                     )
                        if CHANGE_STATUS == 1:
                            p.terminate()
                            break

            except OSError as err:
                e = "%s\n  %s" % (err, not_exist_msg)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files
                             )
                STATUS_ERROR = 1
                break
            
            if CHANGE_STATUS == 1:
                p.terminate()
                break
                    
            status = p.wait()

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc('Error:', status)
        elif CHANGE_STATUS == 1:
            self.endProc('Interrupted:', status)
        else:
            self.endProc('Done,',status)
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write all ffmpeg commands
        
        """
        with open("%s/log/%s" % (DIRconf, self.logname), "a") as log:
            log.write("%s\n\n" % (cmd))
    #----------------------------------------------------------------#
    def endProc(self, mess, status):
        """
        print end messagess to console
        """
        print('\n...%s exit status %s\n' % (mess,status))
########################################################################

class DoublePassThread(Thread):
    """
    This class represents a separate thread which need to read the 
    stdout/stderr in real time mode. The subprocess module is instantiated 
    twice for two different tasks: the process on the first video pass and 
    the process on the second video pass for video only.
    """
    def __init__(self, varargs, duration, OS, logname, timeseq):
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
        self.ffmpeg_link = varargs[6] # bin executable path-name
        self.duration = duration # duration list
        self.time_seq = timeseq
        self.volume = varargs[7]# lista norm, se non richiesto rimane None
        self.OS = OS # operative sistem Identifier
        self.count = 0 # count number loop
        self.lenghmax = len(varargs[1]) # lengh file list
        self.logname = logname # title name of file log
        
        if self.OS == 'Windows':
            self.nul = 'NUL'
        else:
            self.nul = '/dev/null'
        
        self.start()# start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        status = None
        
        for (files,
             folders,
             volume,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.outputdir, 
                                                self.volume, 
                                                self.duration):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione

            if volume == None:
                volume = ''
            
            #--------------- first pass
            pass1 = ('%s %s -i "%s" %s -passlogfile "%s/%s.log" '
                    '-pass 1 -y %s' % (self.ffmpeg_link, 
                                       self.time_seq,
                                       files, 
                                       self.passList[0],
                                       folders, 
                                       filename,
                                       self.nul,
                                       )) 
            if self.OS == 'Windows':
                args = pass1
            else:
                args = shlex.split(pass1)

            self.count += 1
            count = 'File %s/%s - Pass 1' % (self.count, self.lenghmax,)
            cmd = "%s\n%s" % (count, pass1)
            print("\n%s\n" % cmd)
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         )
            self.logWrite(cmd)
            
            try:
                with subprocess.Popen(args, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True) as p1:
                    
                    for line in p1.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print (line, end=''),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration
                                     )
                        if CHANGE_STATUS == 1:
                            p.terminate()
                            break
                    
            except OSError as err:
                e = "%s\n  %s" % (err, not_exist_msg)
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files,
                             )
                STATUS_ERROR = 1
                break
                    
            status = p1.wait()
            if CHANGE_STATUS == 1 or status:
                break # fermo il ciclo for, altrimenti passa avanti
            
            #--------------- second pass ----------------#
            pass2 = ('%s %s -i "%s" %s %s -passlogfile "%s/%s.log" '
                     '-pass 2 -y "%s/%s.%s"' % (self.ffmpeg_link, 
                                                self.time_seq,
                                                files, 
                                                volume,
                                                self.passList[1], 
                                                folders, 
                                                filename,
                                                folders, 
                                                filename,
                                                self.extoutput,
                                                ))
            if self.OS == 'Windows':
                args = pass2
            else:
                args = shlex.split(pass2)
                
            count = 'File %s/%s - Pass 2' % (self.count, self.lenghmax,)
            cmd = "%s\n%s" % (count, pass2)
            print("\n%s\n" % cmd)
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files,
                         )
            self.logWrite(cmd)
            
            with subprocess.Popen(args, 
                                  stderr=subprocess.PIPE, 
                                  bufsize=1, 
                                  universal_newlines=True) as p2:
                    
                    for line2 in p2.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print (line2, end=''),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line2, 
                                     duration=duration
                                     )
                        if CHANGE_STATUS == 1:
                            p2.terminate()
                            break
                    
            status = p2.wait()
            
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc('Error:', status)
        elif CHANGE_STATUS == 1:
            self.endProc('Interrupted:', status)
        else:
            self.endProc('Done,',status)
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write all ffmpeg commands
        
        """
        with open("%s/log/%s" % (DIRconf, self.logname), "a") as log:
            log.write("%s\n\n" % (cmd))
    #----------------------------------------------------------------#
    def endProc(self, mess, status):
        """
        print end messagess to console
        """
        print('\n...%s exit status %s\n' % (mess,status))
        
########################################################################
class SingleProcThread(Thread):
    """
    This class represents a separate thread for running simple single 
    processes, it is used by 'saveimages' feature in video conversion.
    NOTE: Quando di un processo non si necessita della lettura dell'output 
          in tempo reale ma solo di una gestione dei log e degli errori,
          questa classe ne è la risposta. Dal 'loglevel_type' predefinito
          viene esclusa l'opzione -stats al suo interno ma vi è ancora la 
          presenza di 'error'.
    """
    def __init__(self, varargs, duration, OS, logname):
        """
        self.cmd contains a unique string that comprend filename input
        and filename output also.
        """
        Thread.__init__(self)
        """initialize"""
        self.cmd = varargs[4] # comand set on single pass
        self.duration = 0 # duration list
        self.OS = OS
        self.logname = logname # title name of file log
        self.fname = varargs[1][0] # file name

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        
        if self.OS == 'Windows':
            args = self.cmd
        else:
            args = shlex.split(self.cmd)
            
        count = 'File %s/%s' % ('1','1',)
        com = "%s\n%s" % (count, self.cmd)
        print("\n%s\n" % com)
        wx.CallAfter(pub.sendMessage, 
                     "COUNT_EVT", 
                     count=count, 
                     duration=self.duration,
                     fname=self.fname
                     )
        self.logWrite(com)
        
        try:
            p = subprocess.Popen(args, stderr=subprocess.PIPE,)
            error =  p.communicate()
            
        except OSError as err_0:
            if err_0[1] == 'No such file or directory':
                e = "%s\n  %s" % (err_0, not_exist_msg)
            else:
                e = "%s: " % (err_0)
                
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=self.duration,
                         fname=self.fname
                         )
            STATUS_ERROR = 1
            wx.CallAfter(pub.sendMessage, "END_EVT")
            return
        
        else:
            if error[1]:# ffmpeg error
                e = "%s\n  %s" % (self.cmd, error[1])
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=count, 
                             duration=self.duration,
                             fname=self.fname
                             )
                STATUS_ERROR = 1
                wx.CallAfter(pub.sendMessage, "END_EVT")
                return
        
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc('Error:', '1')
        else:
            self.endProc('Done,','0')
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write all ffmpeg commands
        
        """
        with open("%s/log/%s" % (DIRconf, self.logname), "a") as log:
            log.write("%s\n\n" % (cmd))
    #----------------------------------------------------------------#
    def endProc(self, mess, status):
        """
        print end messagess to console
        """
        print('\n...%s exit status %s\n' % (mess,status))

########################################################################
class GrabAudioProc(Thread):
    """
    This class represents a separate thread for running processes, which 
    need to read the stdout/stderr in real time.
    It is reserved for extracting multiple audio files from different 
    video formats.
    """
    def __init__(self, varargs, duration, OS, logname, timeseq):
        """
        """
        Thread.__init__(self)
        """initialize"""

        self.ffmpeg_link = varargs[1] # bin executable path-name
        self.filelist = varargs[2] # input file list (items)
        self.outputdir = varargs[3] # output path list (items)
        self.cmd_1 = varargs[4] # comand 1
        self.codec = varargs[5] # codec type list (items)
        self.cmd_2 = varargs[6] # command 2
        self.ext = varargs[7] # format/extension list (items)
        self.logname = varargs[8] #  ~/.videomass/self.logname
        self.duration = duration # duration values list (items)
        self.time_seq = timeseq
        self.OS = OS
        self.count = 0 # count number loop
        self.lenghmax = len(varargs[2]) # lengh file list
        self.logname = logname # title name of file log
        
        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        status = None

        for (files,
             codec,
             folders,
             ext,
             duration) in itertools.zip_longest(self.filelist, 
                                                self.codec, 
                                                self.outputdir, 
                                                self.ext,
                                                self.duration,
                                                ):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione
            out = os.path.join(folders, filename)

            cmd = '%s %s -i "%s" %s %s %s "%s.%s"' % (self.ffmpeg_link,
                                                      self.time_seq,
                                                      files, 
                                                      self.cmd_1, 
                                                      codec, 
                                                      self.cmd_2,
                                                      out,
                                                      ext,
                                                      )
            if self.OS == 'Windows':
                args = cmd
            else:
                args = shlex.split(cmd)
            
            self.count += 1
            count = 'File %s/%s' % (self.count, self.lenghmax,)
            com = "%s\n%s" % (count, cmd)
            print("\n%s\n" % com)
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         count=count, 
                         duration=duration,
                         fname=files
                         )
            self.logWrite(com)
            
            try:
                with subprocess.Popen(args, 
                                      stderr=subprocess.PIPE, 
                                      bufsize=1, 
                                      universal_newlines=True) as p:
                    
                    for line in p.stderr:
                        #sys.stdout.write(line)
                        #sys.stdout.flush()
                        print (line, end=''),
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=line, 
                                     duration=duration
                                     )
                        if CHANGE_STATUS == 1:
                            p.terminate()
                            break
                        
            except OSError as err:
                e = "%s\n'ffmpeg' %s" % (err, not_exist_msg), 
                wx.CallAfter(pub.sendMessage, 
                             "COUNT_EVT", 
                             count=e, 
                             duration=0,
                             fname=files
                             )
                STATUS_ERROR = 1
                break

            if CHANGE_STATUS == 1:
                p.terminate()
                break
            
            status = p.wait()
            
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
        
        if STATUS_ERROR == 1:
            self.endProc('Error:', status)
        elif CHANGE_STATUS == 1:
            self.endProc('Interrupted:', status)
        else:
            self.endProc('Done,',status)
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write all ffmpeg commands
        
        """
        with open("%s/log/%s" % (DIRconf, self.logname), "a") as log:
            log.write("%s\n\n" % (cmd))
    #----------------------------------------------------------------#
    def endProc(self, mess, status):
        """
        print end messagess to console
        """
        print('\n...%s exit status %s\n' % (mess,status))

########################################################################

