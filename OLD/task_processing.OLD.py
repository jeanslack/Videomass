# -*- coding: UTF-8 -*-

#########################################################
# Name: os_processing.py (for wxpython >= 2.8)
# Porpose: module for system processing commands
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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
#
# Rev (06) 24/08/2014
# Rev (07) 12/01/2015
# Rev (08) 20/04/2015
# Rev (09) 12 july 2018
#########################################################

"""
This module rapresent the main unit of videomas program for all processes 
that involve the subprocess module, classes for separate threads and all 
dialogs and windows for show information on progress process.
"""
from __future__ import division
import wx
import subprocess
import sys
import shlex
import fcntl
import select
import os
from threading import Thread
import re
import time
# pubsub’s old API (Publisher) not work on wxPython >= 2.9
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub # work on wxPython >= 2.9 = 3.0
from vdms_SYS.os_interaction import copy_restore
from vdms_IO.make_filelog import write_log

# Set a global variables for some communication from threads process:
CHANGE_STATUS = None
STATUS_ERROR = None

# current user directory:

DIRNAME = os.path.expanduser('~') # /home/user

########################################################################
class GeneralProcess(wx.Panel):
    """
    This panel is shown in all conversion finalization processes. 
    Displays a text control for the output log, a progress bar, and 
    a progressive percentage text label. This class must be used in 
    combination with separate threads for process tasks.
    It also implements the buttons to stop the current process and 
    close the panel during final activities.
    """
    def __init__(self, parent, path_log, panel, varargs):
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
        
        wx.Panel.__init__(self, parent=parent)
        """ Constructor """
        
        lbl = wx.StaticText(self, label="Log View:")
        self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
                                    )
        self.barProg = wx.Gauge(self, wx.ID_ANY, range = 0)
        self.labPerc = wx.StaticText(self, label=" 0%")
        self.button_stop = wx.Button(self, wx.ID_STOP, "")
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(1, 2, 5, 5)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.OutText, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.labPerc, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5 )
        sizer.Add(self.barProg, 0, wx.EXPAND|wx.ALL, 5 )
        sizer.Add(grid)
        grid.Add(self.button_stop, 0, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)

        # set_properties:
        self.OutText.SetBackgroundColour((217, 255, 255))
        #self.button_stop.SetMinSize((200, 30))
        self.button_stop.SetToolTipString("Stops current process")
        #self.button_close.SetMinSize((200, 30))
        #self.SetSizer(sizer)
        self.SetSizerAndFit(sizer)

        # bind
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        
        #------------------------------------------
        initlog = ('[VIDEOMASS]\n\nInitial LOG:\n')
        print '\n%s' % initlog
        self.OutText.AppendText("%s" % initlog)
        write_log(self.logname) # set initial file LOG
        
        time.sleep(.1)
        self.initProcess()
        
    def initProcess(self):
        """
        """
        self.button_stop.Enable(True)
        self.button_close.Enable(False)

        pub.subscribe(self.updateDisplay, "UPDATE_EVT")
        pub.subscribe(self.updateCount, "COUNT_EVT")
        pub.subscribe(self.endProc, "END_EVT")
    #-------------------------------------------------------------------#
    def updateDisplay(self, output, duration):
        """
        Receive message from thread of the 'while' loop process. 
        The received 'output' is parsed for calculate the bar 
        progress value, percentage label and errors management.
        """
        #self.OutText.AppendText(output)
        if 'time=' in output:# ...sta processando
            i = output.index('time=')+5
            pos = output[i:i+8].split(':')
            hours, minutes, seconds = pos[0],pos[1],pos[2]
            timesum = (int(hours)*60 + int(minutes))*60 + int(seconds)
            self.barProg.SetValue(timesum)
            percentage = timesum / duration * 100
            self.labPerc.SetLabel("%s%%" % str(int(percentage)))

        elif self.STATUS_ERROR == None:
            err_list = ('not found', 
                        'Invalid data found when processing input',
                        'Error', 
                        'Invalid', 
                        'Option not found', 
                        'Unknown',
                        'No such file or directory')
            for err in err_list:
                if err in output:
                    self.STATUS_ERROR = 1
            if self.STATUS_ERROR == 1:
                self.OutText.AppendText('\n%s' % output)
                # write a row error into file log:
                with open("%s/.videomass/%s" % (DIRNAME, self.logname), 
                                                        "a") as logerr:
                    logerr.write("[FFMPEG] ERRORS:\n%s" % (output))

    #-------------------------------------------------------------------#
    def updateCount(self, cmd, duration):
        """
        Receive message from 'for' loop in thread process.
        """
        self.count += 1 # per ogni ciclo for aumenta di uno
        textlog = ('\nFile queue: %s of %s\n'
                   '---------------------------\n'
                   '%s\n---------------------------\n' % (self.count, 
                                                          self.lenghmax, 
                                                          cmd))
        self.barProg.SetRange(duration)#set la durata complessiva
        self.barProg.SetValue(0)# resetto la prog bar
        self.labPerc.SetLabel("100%")
        print '%s' % textlog
        self.OutText.AppendText("%s" % textlog)
        # write all ffmpeg commands
        with open("%s/.videomass/%s" % (DIRNAME, 
                                        self.logname), "a") as log:
            log.write("%s\n\n" % (cmd))

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
        self.OutText.Clear()# reset textctrl before close
        self.parent.panelShown(self.previus)# retrieve at previusly panel
        event.Skip()
    #-------------------------------------------------------------------#
    def endProc(self, msg):
        """
        At the end of the process
        """
        global CHANGE_STATUS
        global STATUS_ERROR
        if self.STATUS_ERROR == 1 or STATUS_ERROR == 1:
            self.STATUS_ERROR = None
            STATUS_ERROR = None
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.RED))
            self.OutText.AppendText('\n Failed!\n')
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        elif CHANGE_STATUS == 1:
            CHANGE_STATUS = None
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.BLUE))
            self.OutText.AppendText('\n ..Interrupted Process!\n')
            self.button_stop.Enable(False)
            self.button_close.Enable(True)

        else:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.GREEN))
            self.OutText.AppendText('\n *** Process successfully! ***\n')
            self.labPerc.SetLabel("100%")
            self.button_stop.Enable(False)
            self.button_close.Enable(True)
            self.barProg.SetValue(0)

        #if user want file log in a specified path
        if not 'none' in self.path_log : 
            copy_restore("%s/.videomass/%s" % (DIRNAME, self.logname),
                            "%s/%s" % (self.path_log, self.logname))

#------------------------------ THREADS -------------------------------#
########################################################################
class ProcThread(Thread):
    """
    This class represents a separate thread for running processes, which 
    need to read the stdout/stderr in real time.
    """
    def __init__(self, varargs, duration):
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

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        NOTE: subprocess se non ha shell=True, con gli operatori di 
        controllo && fallisce in doppia passata video, ma non sarà possibile 
        usare self.process.terminate() per fare lo stop di subprocess.
        Inoltre, con communicate, wait e poll non potrà funzionare la lettura
        dell'output in tempo reale.
        Inspired by: <https://gist.github.com/dpetzold/541290>
        <https://derrickpetzold.com/p/capturing-output-from-ffmpeg-python/>
        <https://stackoverflow.com/questions/1388753/how-to-get-output-from-
        subprocess-popen-proc-stdout-readline-blocks-no-dat>
        """
        global STATUS_ERROR
        
        for files, folders, volume, duration in map(None,
                                                    self.filelist, 
                                                    self.outputdir, 
                                                    self.volume, 
                                                    self.duration):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione

            if volume == None:
                volume = '' #altrimenti inserisce None nei comandi sotto
                
            if self.extoutput == '': # Copy Video Codec and only norm.
                cmd = "%s -i '%s' %s %s '%s/%s'" % (self.ffmpeg_link, 
                                                    files, 
                                                    volume, 
                                                    self.command,
                                                    folders, 
                                                    os.path.basename(files)
                                                    )
            else:# single pass
                cmd = "%s -i '%s' %s %s '%s/%s.%s'" % (self.ffmpeg_link,
                                                       files, 
                                                       volume, 
                                                       self.command, 
                                                       folders, 
                                                       filename, 
                                                       self.extoutput
                                                       )
            try:
                p = subprocess.Popen(shlex.split(cmd), 
                                     stderr=subprocess.PIPE, 
                                     close_fds=True
                                     )
            except OSError as err:
                e = "%s\nffmpeg exist?" % (err), 
                wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=e, 
                         duration=0
                         )
                STATUS_ERROR = 1
                break
            except UnicodeEncodeError as err:
                e = '%s\n'% (err) + 'filename: Support ASCII/UTF-8 only.\n'
                wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=e, 
                         duration=0
                         )
                STATUS_ERROR = 1
                break
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=cmd, 
                         duration=duration
                         )

            fcntl.fcntl(p.stderr.fileno(),
                        fcntl.F_SETFL,
                        fcntl.fcntl(p.stderr.fileno(), 
                        fcntl.F_GETFL) | os.O_NONBLOCK,
                        )
            while True:
                time.sleep(.5)# 1/2 seconds can be enough?
                if CHANGE_STATUS == 1:
                    p.terminate()
                    break
                output = select.select([p.stderr.fileno()], [], [])[0]
                if output:
                    chunk = p.stderr.read()
                    if chunk == '':
                        break
                    else:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=chunk, 
                                     duration=duration
                                     )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')
        
########################################################################
class DoublePassThread(Thread):
    """
    This class represents a separate thread which need to read the 
    stdout/stderr in real time mode. The subprocess module is instantiated 
    twice for two different tasks: the process on the first video pass and 
    the process on the second video pass for video only.
    """
    def __init__(self, varargs, duration):
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
        self.volume = varargs[7]# lista norm, se non richiesto rimane None
        
        self.start()# start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        NOTE: subprocess se non ha shell=True, con gli operatori di 
        controllo && fallisce in doppia passata video, ma non sarà possibile 
        usare self.process.terminate() per fare lo stop di subprocess.
        Inoltre con communicate, wait e poll non potrà funzionare la lettura
        dell'output in tempo reale
        Inspired by: <https://gist.github.com/dpetzold/541290>
        <https://derrickpetzold.com/p/capturing-output-from-ffmpeg-python/>
        <https://stackoverflow.com/questions/1388753/how-to-get-output-from-
        subprocess-popen-proc-stdout-readline-blocks-no-dat>
        """
        for files, folders, volume, duration in map(None,
                                                    self.filelist, 
                                                    self.outputdir, 
                                                    self.volume, 
                                                    self.duration):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione

            if volume == None:
                volume = '' #altrimenti inserisce None nei comandi sotto
            
            #--------------- first pass
            pass1 = "%s -i '%s' %s" % (self.ffmpeg_link, 
                                    files, 
                                    self.passList[0],
                                    )
            try:
                p1 = subprocess.Popen(shlex.split(pass1), 
                                    stderr=subprocess.PIPE, 
                                    close_fds=True
                                    )
            except OSError as err:
                e = "%s\nffmpeg exist?" % (err)
                wx.CallAfter(pub.sendMessage, 
                            "COUNT_EVT", 
                            cmd=e, 
                            duration=0
                            )
                STATUS_ERROR = 1
                break

            except UnicodeEncodeError as err:
                e = '%s\n'% (err) + 'filename: Support ASCII/UTF-8 only.\n'
                wx.CallAfter(pub.sendMessage, 
                            "COUNT_EVT", 
                            cmd=e, 
                            duration=0
                            )
                STATUS_ERROR = 1
                break

            wx.CallAfter(pub.sendMessage, 
                        "COUNT_EVT", 
                        cmd=pass1, 
                        duration=duration
                        )

            fcntl.fcntl(p1.stderr.fileno(),
                        fcntl.F_SETFL,
                        fcntl.fcntl(p1.stderr.fileno(), 
                        fcntl.F_GETFL) | os.O_NONBLOCK,
                        )
            while True:
                time.sleep(.5)# 1/2 seconds can be enough?
                if CHANGE_STATUS == 1:
                    p1.terminate()
                    break
                output = select.select([p1.stderr.fileno()], [], [])[0]
                if output:
                    chunk = p1.stderr.read()
                    if chunk == '':
                        break
                    else:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        wx.CallAfter(pub.sendMessage, 
                                    "UPDATE_EVT", 
                                    output=chunk, 
                                    duration=duration
                                    )
            if CHANGE_STATUS == 1:
                break # fermo il ciclo for, altrimenti passa avanti
            
            #--------------- second pass
            pass2 = "%s -i '%s' %s %s '%s/%s.%s'" % (self.ffmpeg_link, 
                                                    files, 
                                                    volume,
                                                    self.passList[1], 
                                                    folders, 
                                                    filename,
                                                    self.extoutput,
                                                    )
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=pass2, 
                         duration=duration
                         )
            p2 = subprocess.Popen(shlex.split(pass2), 
                                  stderr=subprocess.PIPE, 
                                  close_fds=True,
                                  )
            fcntl.fcntl(p2.stderr.fileno(),
                        fcntl.F_SETFL,
                        fcntl.fcntl(p2.stderr.fileno(), 
                        fcntl.F_GETFL) | os.O_NONBLOCK,
                        )
            while True:
                time.sleep(.5)# 1/2 seconds can be enough?
                if CHANGE_STATUS == 1:
                    p2.terminate()
                    break
                output = select.select([p2.stderr.fileno()], [], [])[0]
                if output:
                    chunk = p2.stderr.read()
                    if chunk == '':
                        break
                    else:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=chunk, 
                                     duration=duration
                                     )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')
        
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
    def __init__(self, varargs, duration):
        """
        self.cmd contains a unique string that comprend filename input
        and filename output also.
        """
        Thread.__init__(self)
        """initialize"""
        self.cmd = varargs[4] # comand set on single pass
        self.duration = 0 # duration list

        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        global STATUS_ERROR
        try:
            p = subprocess.Popen(shlex.split(self.cmd), 
                                 stderr=subprocess.PIPE,
                                 )
            error =  p.communicate()
            
        except OSError as err_0:
            if err_0[1] == 'No such file or directory':
                e = "%s: \nProbably '%s' do not exist in your system" % (
                err_0, self.cmd.split()[0])
            else:
                e = "%s: " % (err_0)
                
            wx.CallAfter(pub.sendMessage, 
                            "COUNT_EVT", 
                            cmd=e, 
                            duration=self.duration
                            )
            STATUS_ERROR = 1
            wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')
            return
        except UnicodeEncodeError as err:
                e = '%s\n'% (err) + 'filename: Support ASCII/UTF-8 only.\n'
                wx.CallAfter(pub.sendMessage, 
                            "COUNT_EVT", 
                            cmd=e, 
                            duration=0
                            )
                STATUS_ERROR = 1
                wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')
                return
        else:
            if error[1]:# ffmpeg error
                e = "%s\n\n%s" % (self.cmd, error[1])
                wx.CallAfter(pub.sendMessage, 
                                "COUNT_EVT", 
                                cmd=e, 
                                duration=self.duration
                                )
                STATUS_ERROR = 1
                wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')
                return
        
        wx.CallAfter(pub.sendMessage, 
                     "COUNT_EVT", 
                     cmd=self.cmd, 
                     duration=self.duration
                     )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')

########################################################################
class GrabAudioProc(Thread):
    """
    This class represents a separate thread for running processes, which 
    need to read the stdout/stderr in real time.
    It is reserved for extracting multiple audio files with codecs and 
    different formats from different video formats.
    """
    def __init__(self, varargs, duration):
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
        
        self.start() # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        NOTE: subprocess se non ha shell=True, con gli operatori di 
        controllo && fallisce in doppia passata video, ma non sarà possibile 
        usare self.process.terminate() per fare lo stop di subprocess.
        Inoltre, con communicate, wait e poll non potrà funzionare la lettura
        dell'output in tempo reale.
        Inspired by: <https://gist.github.com/dpetzold/541290>
        <https://derrickpetzold.com/p/capturing-output-from-ffmpeg-python/>
        <https://stackoverflow.com/questions/1388753/how-to-get-output-from-
        subprocess-popen-proc-stdout-readline-blocks-no-dat>
        """
        global STATUS_ERROR
        for files, codec, folders, ext, duration in map(None, 
                                                        self.filelist, 
                                                        self.codec, 
                                                        self.outputdir, 
                                                        self.ext,
                                                        self.duration,
                                                        ):
            basename = os.path.basename(files) #nome file senza path
            filename = os.path.splitext(basename)[0]#nome senza estensione

            cmd = "%s -i '%s' %s %s %s '%s/%s.%s'" % (self.ffmpeg_link, 
                                                      files, 
                                                      self.cmd_1, 
                                                      codec, 
                                                      self.cmd_2, 
                                                      folders, 
                                                      filename, 
                                                      ext,
                                                      )
            try:
                p = subprocess.Popen(shlex.split(cmd), 
                                     stderr=subprocess.PIPE, 
                                     close_fds=True
                                     )
            except OSError as err:
                e = "%s\nffmpeg exist?" % (err), 
                wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=e, 
                         duration=0
                         )
                STATUS_ERROR = 1
                break
            except UnicodeEncodeError as err:
                e = '%s\n'% (err) + 'filename: Support ASCII/UTF-8 only.\n'
                wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=e, 
                         duration=0
                         )
                STATUS_ERROR = 1
                break
            
            wx.CallAfter(pub.sendMessage, 
                         "COUNT_EVT", 
                         cmd=cmd, 
                         duration=duration
                         )

            fcntl.fcntl(p.stderr.fileno(),
                        fcntl.F_SETFL,
                        fcntl.fcntl(p.stderr.fileno(), 
                        fcntl.F_GETFL) | os.O_NONBLOCK,
                        )
            while True:
                time.sleep(.5)# 1/2 seconds can be enough?
                if CHANGE_STATUS == 1:
                    p.terminate()
                    break
                output = select.select([p.stderr.fileno()], [], [])[0]
                if output:
                    chunk = p.stderr.read()
                    if chunk == '':
                        break
                    else:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        wx.CallAfter(pub.sendMessage, 
                                     "UPDATE_EVT", 
                                     output=chunk, 
                                     duration=duration
                                     )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg='..end')

########################################################################

