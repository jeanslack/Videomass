# -*- coding: UTF-8 -*-

#########################################################
# Name: settings.py
# Porpose: videomass2 setup dialog
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

# Rev (03) 20/07/2014
# Rev (04) 12/01/2015
# Rev (05) 19 Aug 2018
#########################################################

import wx
import os
import webbrowser

dirname = os.path.expanduser('~/') # /home/user/
filename = '%s/.videomass2/videomass2.conf' % (dirname)
PWD = os.getcwd()

class Setup(wx.Dialog):
    """
    Main settings of the videomass2 program and configuration storing.
    """
    def __init__(self, parent, threads, cpu_used, save_log, path_log, 
                 ffmpeg_link, ffmpeg_check, ffprobe_link, ffprobe_check, 
                 ffplay_link, ffplay_check, writeline_exec, OS):
        """
        NOTE 0): self.rowsNum attribute is a sorted list with a exatly number 
                 index corresponding to each read line of the videomass2.conf.
        NOTE 1): The code block (USEFUL FOR DEBUGGING) prints in console a 
                 convenient representation of the parsing, which can also be 
                 efforting consulted for future implementations.
                 - POSITION, the number index of self.rowsNum items (how many 
                   objects it contains).
                 - ROW, is the current numeric rows on the file configuration
                 - VALUE, is the value as writing in the file configuration
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""
        # Make a items list of
        self.rowsNum = []#rows number list
        dic = {} # used for debug
        with open (filename, 'r') as f:
            self.full_list = f.readlines()
        for a,b in enumerate(self.full_list):
            if not b.startswith('#'):
                if not b == '\n':
                    self.rowsNum.append(a)
                    #dic [a] = b.strip()# used for easy reading print debug

        ##USEFUL FOR DEBUGGING (see Setup.__init__.__doc__)
        ##uncomment the following code for a convenient reading
        #print "\nPOSITION:    ROW:     VALUE:"
        #for n, k in enumerate(sorted(dic)):
            #print n, ' -------> ', k, ' --> ', dic[k]

        self.threads = threads
        self.cpu_used = cpu_used
        self.save_log = save_log
        self.path_log = path_log
        self.ffmpeg_link = ffmpeg_link
        self.ffmpeg_check = ffmpeg_check
        self.ffprobe_link = ffprobe_link
        self.ffprobe_check = ffprobe_check
        self.ffplay_link = ffplay_link
        self.ffplay_check = ffplay_check
        self.writeline_exec = writeline_exec
        self.OS = OS
        
        if self.OS == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'
        #----------------------------set notebook and tabs pages
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        notebook.AddPage(tabOne, "General")
        
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        notebook.AddPage(tabTwo, "Log")
        
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        notebook.AddPage(tabThree, "Executables")
        # make a sizer base and grid base. Note that grid base contains
        # buttons close and apply. First add notebook then the buttons at bottom
        sizer = wx.BoxSizer(wx.VERTICAL)
        gridBase = wx.FlexGridSizer(2, 1, 0, 0)# ntbook + buttons ok,close
        gridBase.Add(notebook, 1, wx.ALL|wx.EXPAND, 15)
        #--------------------------------------------------TAB 1
        gridGeneral = wx.FlexGridSizer(3, 1, 0, 0)
        tabOne.SetSizer(gridGeneral)#aggiungo il sizer su tab 1
        boxLabThreads = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY, (
                                    "Settings CPU:")), wx.VERTICAL)
        gridGeneral.Add(boxLabThreads, 1, wx.ALL|wx.EXPAND, 15)
        gridThreads = wx.FlexGridSizer(4, 1, 0, 0)
        boxLabThreads.Add(gridThreads, 1, wx.ALL|wx.EXPAND, 15)
        lab1_pane1 = wx.StaticText(tabOne, wx.ID_ANY,(
                               "Set the number of threads (from 0 to 32):"))
        gridThreads.Add(lab1_pane1, 0, wx.ALL, 5)
        self.spinctrl_threads = wx.SpinCtrl(tabOne, wx.ID_ANY, 
                                            "%s" % threads[9:],
                                            size=(-1,-1), min=0, max=32, 
                                            style=wx.TE_PROCESS_ENTER
                                             )
        gridThreads.Add(self.spinctrl_threads, 0, wx.ALL |
                                                  wx.ALIGN_CENTER_VERTICAL, 
                                                  5)
        lab2_pane1 = wx.StaticText(tabOne, wx.ID_ANY, (
                            "Quality/Speed ratio modifier (from -16 to 16):"))
        gridThreads.Add(lab2_pane1, 0, wx.ALL, 5)
        gridctrl = wx.FlexGridSizer(1, 2, 0, 0)
        gridThreads.Add(gridctrl)
        self.spinctrl_cpu = wx.SpinCtrl(tabOne, wx.ID_ANY, 
                                        "%s" % cpu_used[9:], min=-16, max=16, 
                                        size=(-1,-1), style=wx.TE_PROCESS_ENTER
                                             )
        gridctrl.Add(self.spinctrl_cpu, 0, wx.ALL, 5)
        #gridctrl.Add(self.ckbx_autoThreads, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        boxLabOthers = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY, (
                                    "Other Settings:")), wx.VERTICAL)
        gridGeneral.Add(boxLabOthers, 0, wx.ALL|wx.EXPAND, 15)
        gridOthers = wx.GridSizer(1, 1, 0, 0)
        boxLabOthers.Add(gridOthers, 1, wx.ALL|wx.EXPAND, 15)
        self.check_cmdline = wx.CheckBox(tabOne, wx.ID_ANY, (
            "Enable text writing on the command line\n"
            "reading tab in the Presets Manager panel.\n"
            "Warning! use this function at your own risk!"))
        gridOthers.Add(self.check_cmdline, 0, wx.ALL, 5)
        #--------------------------------------------------TAB 2
        gridLog = wx.FlexGridSizer(4, 1, 0, 0)
        tabTwo.SetSizer(gridLog)#aggiungo il sizer su tab 2
        #self.check_ffmpeglog = wx.CheckBox(tabTwo, wx.ID_ANY, 
                                           #(" Generates ffmpeg log files"))
        #gridLog.Add(self.check_ffmpeglog, 0, wx.ALL, 15)
        self.check_cmdlog = wx.CheckBox(tabTwo, wx.ID_ANY, 
                                (" Specifies a custom path to save the log"))
        gridLog.Add(self.check_cmdlog, 0, wx.ALL, 15)
        lab3_pane2 = wx.StaticText(tabTwo, wx.ID_ANY, 
                               ("Where do you want to save the log?"))
        gridLog.Add(lab3_pane2, 0, wx.ALL, 15)
        grid_logBtn = wx.FlexGridSizer(1, 2, 0, 0)
        gridLog.Add(grid_logBtn)
        self.btn_log = wx.Button(tabTwo, wx.ID_ANY, "Browse..")
        grid_logBtn.Add(self.btn_log, 0, wx.ALL, 15)
        self.txt_pathlog = wx.TextCtrl(tabTwo, wx.ID_ANY, "")
        grid_logBtn.Add(self.txt_pathlog, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 15)
        #--------------------------------------------------TAB 3
        gridExec = wx.FlexGridSizer(6, 1, 0, 0)
        tabThree.SetSizer(gridExec)#aggiungo il sizer su tab 3

        self.checkbox_exeFFmpeg = wx.CheckBox(tabThree, wx.ID_ANY,(
                                       " Use a custom path to run FFmpeg"))
        self.btn_pathFFmpeg = wx.Button(tabThree, wx.ID_ANY, "Browse..")
        self.txtctrl_ffmpeg = wx.TextCtrl(tabThree, wx.ID_ANY, "")
        gridExec.Add(self.checkbox_exeFFmpeg, 1, wx.TOP|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        gridFFmpeg = wx.FlexGridSizer(1, 2, 0, 0)
        gridExec.Add(gridFFmpeg)
        gridFFmpeg.Add(self.btn_pathFFmpeg, 0, wx.ALL, 15)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        self.checkbox_exeFFprobe = wx.CheckBox(tabThree, wx.ID_ANY, (
                                       " Use a custom path to run FFprobe"))
        self.btn_pathFFprobe = wx.Button(tabThree, wx.ID_ANY, "Browse..")
        self.txtctrl_ffprobe = wx.TextCtrl(tabThree, wx.ID_ANY, "")
        gridExec.Add(self.checkbox_exeFFprobe, 1, wx.TOP|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        gridFFprobe = wx.FlexGridSizer(1, 2, 0, 0)
        gridExec.Add(gridFFprobe)
        gridFFprobe.Add(self.btn_pathFFprobe, 0, wx.ALL, 15)
        gridFFprobe.Add(self.txtctrl_ffprobe, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        self.checkbox_exeFFplay = wx.CheckBox(tabThree, wx.ID_ANY, (
                                       " Use a custom path to run FFplay"))
        self.btn_pathFFplay = wx.Button(tabThree, wx.ID_ANY, "Browse..")
        self.txtctrl_ffplay = wx.TextCtrl(tabThree, wx.ID_ANY, "")
        gridExec.Add(self.checkbox_exeFFplay, 1, wx.TOP|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        gridFFplay = wx.FlexGridSizer(1, 2, 0, 0)
        gridExec.Add(gridFFplay)
        gridFFplay.Add(self.btn_pathFFplay, 0, wx.ALL, 15)
        gridFFplay.Add(self.txtctrl_ffplay, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        #------------------------------------------------------bottom
        gridBottom = wx.GridSizer(1, 2, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        gridhelp.Add(btn_help, 0, wx.ALL, 5)
        gridBottom.Add(gridhelp, 0, wx.ALL, 10)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit = wx.GridSizer(1, 2, 0, 0)
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        btn_ok = wx.Button(self, wx.ID_APPLY, "")
        gridexit.Add(btn_ok, 0, wx.ALL, 5)
        gridBottom.Add(gridexit, 0, wx.ALL, 10)
        gridBase.Add(gridBottom)#, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        sizer.Add(gridBase,1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        
        #----------------------Properties----------------------#
        self.SetTitle("Setup - Videomass2")
        self.spinctrl_cpu.SetToolTipString("Quality/Speed ratio modifier "
                                            "(from -16 to 16) (default 1)")
        self.check_cmdline.SetToolTipString("Allows the text writing to "
                                            "performs your custom parameters."
                                            )
        #self.check_ffmpeglog.SetToolTipString("At each conversion process, is "
                              #"also generated a log file of ffmpeg. Note that "
                              #"can reach considerable size. This feature is "
                              #"disabled in batch processes."
                                              #)
        self.check_cmdlog.SetToolTipString("Generates a log file command in "
                              "the directory specified below. Log file is a "
                              "file containing the parameters of the "
                              "execution process, info and error messages."
                                           )
        self.btn_log.SetToolTipString("Open Path")
        self.txt_pathlog.SetMinSize((200, -1))
        self.txt_pathlog.SetToolTipString("Path generation file")
        
        self.checkbox_exeFFmpeg.SetToolTipString("Enable custom search for "
                       "the executable FFmpeg. If the checkbox is disabled or "
                       "if the path field is empty, the search of the "
                       "executable is entrusted to the system.")
        
        self.btn_pathFFmpeg.SetToolTipString("Open path FFmpeg")
        self.txtctrl_ffmpeg.SetMinSize((200, -1))
        self.txtctrl_ffmpeg.SetToolTipString(
                                    "path to executable binary FFmpeg"
                                                    )
        self.checkbox_exeFFprobe.SetToolTipString("Path generation file")
        
        self.checkbox_exeFFmpeg.SetToolTipString("Enable custom search for "
                        "the executable FFprobe. If the checkbox is disabled or "
                        "if the path field is empty, the search of the "
                        "executable is entrusted to the system.")
        
        self.btn_pathFFprobe.SetToolTipString("Open path FFprobe")
        self.txtctrl_ffprobe.SetMinSize((200, -1))
        self.txtctrl_ffprobe.SetToolTipString(
                                    "path to executable binary FFprobe"
                                                    )
        self.checkbox_exeFFplay.SetToolTipString("Path generation file"
                                                 )
        self.checkbox_exeFFmpeg.SetToolTipString("Enable custom search for "
                        "the executable FFplay. If the checkbox is disabled or "
                        "if the path field is empty, the search of the "
                        "executable is entrusted to the system."
                                                  )
        self.btn_pathFFplay.SetToolTipString("Open path FFplay")
        self.txtctrl_ffplay.SetMinSize((200, -1))
        self.txtctrl_ffplay.SetToolTipString(
                                     "path to executable binary FFplay")
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_direct_cmd, self.check_cmdline)
        #self.Bind(wx.EVT_CHECKBOX, self.log_ffmpeg, self.check_ffmpeglog)
        self.Bind(wx.EVT_CHECKBOX, self.log_command, self.check_cmdlog)
        self.Bind(wx.EVT_BUTTON, self.save_path_log, self.btn_log)
        #self.Bind(wx.EVT_TEXT, self.text_save, self.txt_pathlog)
        self.Bind(wx.EVT_SPINCTRL, self.on_threads, self.spinctrl_threads)
        self.Bind(wx.EVT_SPINCTRL, self.on_cpu_used, self.spinctrl_cpu)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_pathFFmpeg)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffmpeg, self.txtctrl_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_pathFFprobe)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffprobe, self.txtctrl_ffprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.checkbox_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_pathFFplay)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffplay, self.txtctrl_ffplay)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

        #--------------------------------------------#
        self.current_settings() # call function for initialize setting layout 

    def current_settings(self):
        """
        Setto l'abilitazione/disabilitazione in funzione del file di conf.
        Setting enable/disable on according to the configuration file
        """
            
        if self.save_log == 'true':
            self.check_cmdlog.SetValue(True) # set on
            self.txt_pathlog.AppendText(self.path_log)
            self.btn_log.Enable(), self.txt_pathlog.Enable()
            
        elif self.save_log == 'false': 
            # Button and textctrl for file log set disable
            self.btn_log.Disable(), self.txt_pathlog.Disable()
            self.txt_pathlog.SetValue("")
            
        if self.ffmpeg_check == 'false':
            self.btn_pathFFmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.SetValue("")
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.ffmpeg_link)
            self.checkbox_exeFFmpeg.SetValue(True)
            
        if self.ffprobe_check == 'false':
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.SetValue("")
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.ffprobe_link)
            self.checkbox_exeFFprobe.SetValue(True)
            
        if self.ffplay_check == 'false':
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.SetValue("")
            self.checkbox_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(self.ffplay_link)
            self.checkbox_exeFFplay.SetValue(True)
            
        if self.writeline_exec == 'true':
            self.check_cmdline.SetValue(True)
    
    #--------------------------------------------------------------------#
    def on_threads(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_threads.GetValue()
        self.full_list[self.rowsNum[2]] = '-threads %s\n' % sett
    #--------------------------------------------------------------------#
    def on_cpu_used(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_cpu.GetValue()
        self.full_list[self.rowsNum[3]] = '-cpu-used %s\n' % sett
    #--------------------------------------------------------------------#
    #--------------------------------------------------------------------#
    def log_command(self, event):
        """if true, it allow set a specified save of the log."""
        if self.check_cmdlog.IsChecked():
            self.full_list[self.rowsNum[4]] = 'true\n'
            self.btn_log.Enable(), self.txt_pathlog.Enable()
            
        else:
            self.full_list[self.rowsNum[4]] = 'false\n'
            self.txt_pathlog.SetValue("")
            self.full_list[self.rowsNum[5]] = 'none'
            self.btn_log.Disable(), self.txt_pathlog.Disable()

    #--------------------------------------------------------------------#
    def save_path_log(self, event):
        """specifies a path to save the log"""
        dialdir = wx.DirDialog(self, "Where do you want to save the log file?")
            
        if dialdir.ShowModal() == wx.ID_OK:
            self.txt_pathlog.SetValue("")
            self.txt_pathlog.AppendText(dialdir.GetPath())
            self.full_list[self.rowsNum[5]] = '%s\n' % (dialdir.GetPath())
            dialdir.Destroy()

    #--------------------------------------------------------------------#
    #def text_save(self, event):
        
        ##save = self.txt_pathlog.GetValue()
        ##self.full_list[28] = 'PATH = %s\n' % (save)
        #event.Skip()
        
    #----------------------ffmpeg path checkbox--------------------------#
    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg binary esecutable"""
        if self.checkbox_exeFFmpeg.IsChecked():
            self.btn_pathFFmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.txtctrl_ffmpeg.SetValue("")
            self.full_list[self.rowsNum[7]] = 'true\n'

        else:
            self.btn_pathFFmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.SetValue("")
            self.full_list[self.rowsNum[7]] = 'false\n'
            self.full_list[self.rowsNum[8]] = '%s\n' % self.ffmpeg

    #----------------------ffmpeg path open dialog----------------------#
    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        dialogfile = wx.FileDialog(self, 
                        "Indicates where the binary ffmpeg", "", "", 
                        "ffmpeg binarys (*%s)|*%s| All files (*.*)|*.*"
                        % (self.ffmpeg, self.ffmpeg), 
                        wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
        if dialogfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffmpeg.SetValue("")
            self.txtctrl_ffmpeg.AppendText(dialogfile.GetPath())
            self.full_list[self.rowsNum[8]] = '%s\n' % (dialogfile.GetPath())
            dialogfile.Destroy()
    #---------------------------------------------------------------------#
    def txtffmpeg(self, event):
        """write ffmpeg pathname"""
        t = self.txtctrl_ffmpeg.GetValue()
        self.full_list[self.rowsNum[8]] = '%s\n' % (t)

    #----------------------ffprobe path checkbox--------------------------#
    def exeFFprobe(self, event):
        """Enable or disable ffprobe binary esecutable"""
        if self.checkbox_exeFFprobe.IsChecked():
            self.btn_pathFFprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.txtctrl_ffprobe.SetValue("")
            self.full_list[self.rowsNum[9]] = 'true\n'

        else:
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.SetValue("")
            self.full_list[self.rowsNum[9]] = 'false\n'
            self.full_list[self.rowsNum[10]] = '%s\n' % self.ffprobe

    #----------------------ffprobe path open dialog----------------------#
    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        dialfile = wx.FileDialog(self, 
                    "Indicates where the binary ffprobe", "", "", 
                    "ffprobe binarys (*%s)|*%s| All files (*.*)|*.*"
                    % (self.ffprobe, self.ffprobe), 
                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
        if dialfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffprobe.SetValue("")
            self.txtctrl_ffprobe.AppendText(dialfile.GetPath())
            self.full_list[self.rowsNum[10]] = '%s\n' % (dialfile.GetPath())
            dialfile.Destroy()
    #---------------------------------------------------------------------#
    def txtffprobe(self, event):
        """write ffprobe pathname"""
        t = self.txtctrl_ffprobe.GetValue()
        self.full_list[self.rowsNum[10]] = '%s\n' % (t)

    #----------------------ffplay path checkbox--------------------------#
    def exeFFplay(self, event):
        """Enable or disable ffplay binary esecutable"""
        if self.checkbox_exeFFplay.IsChecked():
            self.btn_pathFFplay.Enable()
            self.txtctrl_ffplay.Enable()
            self.txtctrl_ffplay.SetValue("")
            self.full_list[self.rowsNum[11]] = 'true\n'

        else:
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.SetValue("")
            self.full_list[self.rowsNum[11]] = 'false\n'
            self.full_list[self.rowsNum[12]] = '%s\n' % self.ffplay

    #----------------------ffplay path open dialog----------------------#
    def open_path_ffplay(self, event):
        """Indicates a new ffplay path-name"""
        dialfile = wx.FileDialog(self, 
                    "Indicates where the binary ffplay", "", "", 
                    "ffplay binarys (*%s)|*%s| All files (*.*)|*.*"
                    % (self.ffplay, self.ffplay), 
                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
        if dialfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffplay.SetValue("")
            self.txtctrl_ffplay.AppendText(dialfile.GetPath())
            self.full_list[self.rowsNum[12]] = '%s\n' % (dialfile.GetPath())
            
            dialfile.Destroy()
    #---------------------------------------------------------------------#
    def txtffplay(self, event):
        """write ffplay pathname"""
        t = self.txtctrl_ffplay.GetValue()
        self.full_list[self.rowsNum[12]] = '%s\n' % (t)
            
    #--------------------------------------------------------------------#
    def on_direct_cmd(self, event):
        """
        enable or disable direct text command editable
        """
        if self.check_cmdline.IsChecked():
            self.full_list[self.rowsNum[13]] = 'true\n'
    
        else:
            self.full_list[self.rowsNum[13]] = 'false\n'
    #------------------------------------------------------------------#
    def on_help(self, event):
        """
        """
        page = 'https://jeanslack.github.io/Videomass2/Pages/Startup/Setup.html'
        webbrowser.open(page)
            
    #--------------------------------------------------------------------#
    def on_close(self, event):
        event.Skip()
    #--------------------------------------------------------------------#
    def on_ok(self, event):
        """
        Applies all changes writing the new entries
        """
            
            
        # if self.checkbox_exeFFmpeg.IsChecked():
        #     if not self.txtctrl_ffmpeg.GetValue() == '':
        #         ffmpeg_src = self.txtctrl_ffmpeg.GetValue()
        #         if not self.ffmpeg_link == ffmpeg_src:# if not modified
        #             if os.path.exists("%s/FFMPEG_BIN/bin" % PWD):
        #                 os.symlink(ffmpeg_src, "%s/FFMPEG_BIN/bin/ffmpeg" % PWD)
        #             
        # if self.checkbox_exeFFprobe.IsChecked():
        #     if not self.txtctrl_ffprobe.GetValue() == '':
        #         ffprobe_src = self.txtctrl_ffprobe.GetValue()
        #         if not self.ffprobe_link == ffprobe_src:# if not modified
        #             if os.path.exists("%s/FFMPEG_BIN" % PWD):
        #                 os.symlink(ffprobe_src, "%s/FFMPEG_BIN/bin/ffprobe" % PWD)
        # 
        # if self.checkbox_exeFFplay.IsChecked():
        #     if not self.txtctrl_ffplay.GetValue() == '':
        #         ffplay_src = self.txtctrl_ffplay.GetValue()
        #         if not self.ffplay_link == ffplay_src:# if not modified
        #             if os.path.exists("%s/FFMPEG_BIN" % PWD):
        #                 os.symlink(ffplay_src, "%s/FFMPEG_BIN/bin/ffplay" % PWD)

        if self.check_cmdlog.IsChecked() and self.txt_pathlog.GetValue() == "":
            wx.MessageBox("Warning, The log command has no set path name ", 
                            "WARNING - Videomass2", wx.ICON_WARNING)
        else:
            with open (filename, 'w') as fileconf:
                for i in self.full_list:
                    fileconf.write('%s' % i)
            wx.MessageBox(u"\nChanges need to restart the program")
            
            #self.Destroy() # WARNING on mac not close corretly, on linux ok
            self.Close()
        event.Skip()
        
