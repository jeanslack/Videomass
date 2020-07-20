# -*- coding: UTF-8 -*-
# Name: settings.py
# Porpose: videomass setup dialog
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: May.09.2020
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
import os
import webbrowser


class Setup(wx.Dialog):
    """
    Main settings of the videomass program and configuration storing.
    """
    # get videomass wx.App attribute
    get = wx.GetApp()
    OS = get.OS
    FF_THREADS = get.FFthreads
    PWD = get.WORKdir
    FILE_CONF = get.FILEconf
    FFMPEG_LINK = get.FFMPEG_url
    FFPLAY_LINK = get.FFPLAY_url
    FFPROBE_LINK = get.FFPROBE_url
    FFMPEG_LOGLEVEL = get.FFMPEG_loglev
    FFPLAY_LOGLEVEL = get.FFPLAY_loglev
    FFMPEG_CHECK = get.FFMPEG_check
    FFPROBE_CHECK = get.FFPROBE_check
    FFPLAY_CHECK = get.FFPLAY_check
    MPV_LINK = get.MPV_url
    MPV_CHECK = get.MPV_check
    OUTSAVE = get.USERfilesave

    MSGLOG = _("The following settings affect output messages "
               "and the log messages\nduring processes. "
               "Change only if you know what you are doing."
               )
    OPT_LOGLEV = [("quiet (Show nothing at all)"),
                  ("fatal (Only show fatal errors)"),
                  ("error (Show all errors)"),
                  ("warning (Show all warnings and errors)"),
                  ("info (Show informative messages during processing)")]
    # -----------------------------------------------------------------

    def __init__(self, parent, iconset):
        """
        NOTE 0): self.rowsNum attribute is a sorted list with a exatly number
                 index corresponding to each read line of the videomass.conf.
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
        self.rowsNum = []  # rows number list
        dic = {}  # used for debug
        with open(Setup.FILE_CONF, 'r') as f:
            self.full_list = f.readlines()
        for a, b in enumerate(self.full_list):
            if not b.startswith('#'):
                if not b == '\n':
                    self.rowsNum.append(a)

                    #dic [a] = b.strip()# used for easy reading print debug

        ##USEFUL FOR DEBUGGING (see Setup.__init__.__doc__)
        ##uncomment the following code for a convenient reading
        #print("\nPOSITION:    ROW:     VALUE:")
        #for n, k in enumerate(sorted(dic)):
            #print(n, ' -------> ', k, ' --> ', dic[k])
        dirname = os.path.expanduser('~')  # /home/user/
        self.userpath = dirname if not Setup.OUTSAVE else Setup.OUTSAVE
        self.iconset = iconset
        self.getfileconf = Setup.FILE_CONF

        if Setup.OS == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
            self.mpv = 'mpv.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'
            self.mpv = 'mpv'
        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 10)
        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGeneral = wx.BoxSizer(wx.VERTICAL)
        boxLabThreads = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY, (
                                    _("FFmpeg threads option"))), wx.VERTICAL)
        sizerGeneral.Add(boxLabThreads, 1, wx.ALL | wx.EXPAND, 15)
        gridThreads = wx.BoxSizer(wx.VERTICAL)
        boxLabThreads.Add(gridThreads, 1, wx.ALL | wx.EXPAND, 15)
        lab1_pane1 = wx.StaticText(tabOne, wx.ID_ANY,
                                   (_("Set the number of threads "
                                      "(from 0 to 32)")))
        gridThreads.Add(lab1_pane1, 0,
                        wx.ALL |
                        wx.ALIGN_CENTER_VERTICAL |
                        wx.ALIGN_CENTER_HORIZONTAL, 5
                        )
        self.spinctrl_threads = wx.SpinCtrl(tabOne, wx.ID_ANY,
                                            "%s" % Setup.FF_THREADS[9:],
                                            size=(-1, -1), min=0, max=32,
                                            style=wx.TE_PROCESS_ENTER
                                            )
        gridThreads.Add(self.spinctrl_threads, 0, wx.ALL |
                        wx.ALIGN_CENTER_VERTICAL |
                        wx.ALIGN_CENTER_HORIZONTAL, 5
                        )
        msg = _("Where do you prefer to save all the output files?")
        boxUserpath = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY,
                                                     (msg)), wx.VERTICAL)
        sizerGeneral.Add(boxUserpath, 1, wx.ALL | wx.EXPAND, 15)
        gridUserpath = wx.BoxSizer(wx.HORIZONTAL)
        boxUserpath.Add(gridUserpath, 1, wx.ALL | wx.EXPAND, 15)

        self.btn_userpath = wx.Button(tabOne, wx.ID_ANY, _("Browse.."))
        gridUserpath.Add(self.btn_userpath, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL |
                         wx.ALIGN_CENTER_HORIZONTAL, 5
                         )
        self.txtctrl_userpath = wx.TextCtrl(tabOne, wx.ID_ANY, "",
                                            style=wx.TE_READONLY
                                            )
        gridUserpath.Add(self.txtctrl_userpath, 1, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL |
                         wx.ALIGN_CENTER_HORIZONTAL, 5
                         )
        self.txtctrl_userpath.AppendText(self.userpath)
        tabOne.SetSizer(sizerGeneral)
        notebook.AddPage(tabOne, _("General"))

        # -----tab 2
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        gridExec = wx.BoxSizer(wx.VERTICAL)
        gridExec.Add((0, 25), 0,)
        # ----
        self.checkbox_exeFFmpeg = wx.CheckBox(tabThree, wx.ID_ANY, (
                                       _(" Use a custom path to run FFmpeg")))
        self.btn_pathFFmpeg = wx.Button(tabThree, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffmpeg = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        gridExec.Add(self.checkbox_exeFFmpeg, 0, wx.ALL, 15)
        gridFFmpeg = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFmpeg, 0, wx.ALL | wx.EXPAND, 15)
        gridFFmpeg.Add(self.btn_pathFFmpeg, 0, wx.ALL, 5)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALIGN_CENTER_VERTICAL, 5)
        # ----
        self.checkbox_exeFFprobe = wx.CheckBox(tabThree, wx.ID_ANY, (
                                       _(" Use a custom path to run FFprobe")))
        self.btn_pathFFprobe = wx.Button(tabThree, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffprobe = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        gridExec.Add(self.checkbox_exeFFprobe, 0, wx.ALL, 15)
        gridFFprobe = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFprobe, 0, wx.ALL | wx.EXPAND, 15)
        gridFFprobe.Add(self.btn_pathFFprobe, 0, wx.ALL, 5)
        gridFFprobe.Add(self.txtctrl_ffprobe, 1, wx.ALIGN_CENTER_VERTICAL, 5)
        # ----
        self.checkbox_exeFFplay = wx.CheckBox(tabThree, wx.ID_ANY, (
                                       _(" Use a custom path to run FFplay")))
        self.btn_pathFFplay = wx.Button(tabThree, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffplay = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        gridExec.Add(self.checkbox_exeFFplay, 0, wx.ALL, 15)
        gridFFplay = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFplay, 0, wx.ALL | wx.EXPAND, 15)
        gridFFplay.Add(self.btn_pathFFplay, 0, wx.ALL, 5)
        gridFFplay.Add(self.txtctrl_ffplay, 1, wx.ALIGN_CENTER_VERTICAL, 5)
        # ----
        self.checkbox_exeMpv = wx.CheckBox(tabThree, wx.ID_ANY, (
                                    _(" Use a custom path to run mpv player")))
        self.btn_pathMpv = wx.Button(tabThree, wx.ID_ANY, _("Browse.."))
        self.txtctrl_mpv = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                       style=wx.TE_READONLY
                                       )
        gridExec.Add(self.checkbox_exeMpv, 0, wx.ALL, 15)
        gridMpv = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridMpv, 0, wx.ALL | wx.EXPAND, 15)
        gridMpv.Add(self.btn_pathMpv, 0, wx.ALL, 5)
        gridMpv.Add(self.txtctrl_mpv, 1, wx.ALIGN_CENTER_VERTICAL, 5)
        # ----
        tabThree.SetSizer(gridExec)
        notebook.AddPage(tabThree, _("Executable paths"))
        # -----tab 3
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        gridappearance = wx.BoxSizer(wx.VERTICAL)
        boxLabIcons = wx.StaticBoxSizer(wx.StaticBox(tabFour, wx.ID_ANY, (
                                        _("Set Icon Themes"))), wx.VERTICAL)
        gridappearance.Add(boxLabIcons, 1, wx.ALL | wx.EXPAND, 15)
        self.cmbx_icons = wx.ComboBox(tabFour, wx.ID_ANY,
                                      choices=[
                                          ("Videomass_Sign_Icons"),
                                          ("Material_Design_Icons_black"),
                                          ("Material_Design_Icons_white")
                                          ],
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        boxLabIcons.Add(self.cmbx_icons, 0,
                        wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 15
                        )
        self.cmbx_icons.SetValue(self.iconset)
        boxLabColor = wx.StaticBoxSizer(wx.StaticBox(tabFour, wx.ID_ANY, (
                                    _("Color customization"))), wx.VERTICAL)
        gridappearance.Add(boxLabColor, 1, wx.ALL | wx.EXPAND, 15)
        gridTBColor = wx.FlexGridSizer(3, 2, 0, 0)
        boxLabColor.Add(gridTBColor)
        labTBColor = wx.StaticText(tabFour, wx.ID_ANY,
                                   _("Change color at the button bar:")
                                   )
        gridTBColor.Add(labTBColor, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        btn_TBcolor = wx.Button(tabFour, wx.ID_ANY, _("Bar Colour"))
        gridTBColor.Add(btn_TBcolor, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 15
                        )
        labTBColorBtn = wx.StaticText(tabFour, wx.ID_ANY, (
                                      _("Change color of bar buttons:")))
        gridTBColor.Add(labTBColorBtn, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        btn_TBcolorBtn = wx.Button(tabFour, wx.ID_ANY, _("Buttons Colour"))
        gridTBColor.Add(btn_TBcolorBtn, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 15
                        )
        labFontColor = wx.StaticText(tabFour, wx.ID_ANY, (
                                _("Color setting for button fonts:")))
        gridTBColor.Add(labFontColor, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        btn_Fontcolor = wx.Button(tabFour, wx.ID_ANY, _("Font Colour"))
        gridTBColor.Add(btn_Fontcolor, 0, wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 15
                        )
        self.default_theme = wx.Button(tabFour, wx.ID_CLEAR,
                                       _("Restore default settings"))
        gridappearance.Add(self.default_theme, 0, wx.ALL |
                           wx.EXPAND, 15
                           )
        tabFour.SetSizer(gridappearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tabFour, _("Appearance"))
        # -----tab 4
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        gridLog = wx.BoxSizer(wx.VERTICAL)
        lab3_pane2 = wx.StaticText(tabTwo, wx.ID_ANY, (Setup.MSGLOG))
        gridLog.Add(lab3_pane2, 0, wx.ALL, 15)
        self.rdbFFmpeg = wx.RadioBox(
                                tabTwo, wx.ID_ANY,
                                ("Set logging level flags used by FFmpeg"),
                                choices=Setup.OPT_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
                                     )
        gridLog.Add(self.rdbFFmpeg, 0, wx.ALL | wx.EXPAND, 15)
        self.rdbFFplay = wx.RadioBox(
                                tabTwo, wx.ID_ANY,
                                ("Set logging level flags used by FFplay"),
                                choices=Setup.OPT_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
                                     )
        gridLog.Add(self.rdbFFplay, 0, wx.ALL | wx.EXPAND, 15)
        tabTwo.SetSizer(gridLog)
        notebook.AddPage(tabTwo, _("Logging levels"))
        # ------ btns bottom
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        grdexit.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        sizer_base.Add(grdBtn, 0, wx.ALL | wx.EXPAND, 5)
        # ------ set sizer
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------#
        self.SetTitle(_("Videomass: setup"))
        msg = _("Enable custom paths for the executables. If the check boxes "
                "are disabled or if the path field is empty, the search for "
                "the executables is entrusted to the environment variables.")
        tabThree.SetToolTip(msg)
        self.txtctrl_ffmpeg.SetMinSize((200, -1))
        self.txtctrl_ffprobe.SetMinSize((200, -1))
        self.txtctrl_ffplay.SetMinSize((200, -1))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffplay, self.rdbFFplay)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbFFmpeg)
        self.Bind(wx.EVT_SPINCTRL, self.on_threads, self.spinctrl_threads)
        self.Bind(wx.EVT_BUTTON, self.set_Userpath, self.btn_userpath)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_pathFFmpeg)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffmpeg, self.txtctrl_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_pathFFprobe)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffprobe, self.txtctrl_ffprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.checkbox_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_pathFFplay)
        self.Bind(wx.EVT_TEXT_ENTER, self.txtffplay, self.txtctrl_ffplay)
        self.Bind(wx.EVT_CHECKBOX, self.exe_MPV, self.checkbox_exeMpv)
        self.Bind(wx.EVT_BUTTON, self.open_path_MPV, self.btn_pathMpv)
        self.Bind(wx.EVT_TEXT_ENTER, self.txt_MPV, self.txtctrl_mpv)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)
        self.Bind(wx.EVT_BUTTON, self.onColorDlg, btn_TBcolor)
        self.Bind(wx.EVT_BUTTON, self.onColorDlg, btn_TBcolorBtn)
        self.Bind(wx.EVT_BUTTON, self.onColorDlg, btn_Fontcolor)
        self.Bind(wx.EVT_BUTTON, self.onAppearanceDefault, self.default_theme)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file

        """
        for s in range(self.rdbFFplay.GetCount()):
            if (Setup.FFPLAY_LOGLEVEL.split()[1] in
               self.rdbFFplay.GetString(s).split()[0]):
                self.rdbFFplay.SetSelection(s)

        for s in range(self.rdbFFmpeg.GetCount()):
            if (Setup.FFMPEG_LOGLEVEL.split()[1] in
               self.rdbFFmpeg.GetString(s).split()[0]):
                self.rdbFFmpeg.SetSelection(s)

        if Setup.FFMPEG_CHECK == 'false':
            self.btn_pathFFmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.SetValue("")
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(Setup.FFMPEG_LINK)
            self.checkbox_exeFFmpeg.SetValue(True)

        if Setup.FFPROBE_CHECK == 'false':
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.SetValue("")
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(Setup.FFPROBE_LINK)
            self.checkbox_exeFFprobe.SetValue(True)

        if Setup.FFPLAY_CHECK == 'false':
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.SetValue("")
            self.checkbox_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(Setup.FFPLAY_LINK)
            self.checkbox_exeFFplay.SetValue(True)

        if Setup.MPV_CHECK == 'false':
            self.btn_pathMpv.Disable()
            self.txtctrl_mpv.Disable()
            self.txtctrl_mpv.SetValue("")
            self.checkbox_exeMpv.SetValue(False)
        else:
            self.txtctrl_mpv.AppendText(Setup.MPV_LINK)
            self.checkbox_exeMpv.SetValue(True)
    # --------------------------------------------------------------------#

    def on_threads(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_threads.GetValue()
        self.full_list[self.rowsNum[2]] = '-threads %s\n' % sett
    # ---------------------------------------------------------------------#

    def set_Userpath(self, event):
        """write a custom user path name where saving exported files"""

        dlg = wx.DirDialog(self, _("Set a default directory to save files"),
                           "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_userpath.Clear()
            self.txtctrl_userpath.AppendText(dlg.GetPath())
            self.full_list[self.rowsNum[1]] = '%s\n' % (dlg.GetPath())
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def logging_ffplay(self, event):
        """specifies loglevel type for ffplay."""
        s = self.rdbFFplay.GetStringSelection().split()[0]
        self.full_list[self.rowsNum[3]] = '-loglevel %s -hide_banner \n' % s
    # --------------------------------------------------------------------#

    def logging_ffmpeg(self, event):
        """specifies loglevel type for ffmpeg"""
        s = self.rdbFFmpeg.GetStringSelection().split()[0]
        self.full_list[self.rowsNum[4]] = ('-loglevel %s -stats -hide_banner '
                                           '-nostdin\n' % s)

    # ----------------------ffmpeg path checkbox--------------------------#

    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg binary esecutable"""
        if self.checkbox_exeFFmpeg.IsChecked():
            self.btn_pathFFmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.txtctrl_ffmpeg.SetValue("")
            self.full_list[self.rowsNum[5]] = 'true\n'
        else:
            self.btn_pathFFmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.SetValue("")
            self.full_list[self.rowsNum[5]] = 'false\n'
            self.full_list[self.rowsNum[6]] = '%s\n' % self.ffmpeg

    # ----------------------ffmpeg path open dialog----------------------#
    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        dialogfile = wx.FileDialog(self, _("Videomass: Where is the ffmpeg "
                                           "executable located?"), "", "",
                                   "ffmpeg binarys (*%s)|*%s| All files "
                                   "(*.*)|*.*" % (self.ffmpeg, self.ffmpeg),
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                   )

        if dialogfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffmpeg.SetValue("")
            self.txtctrl_ffmpeg.AppendText(dialogfile.GetPath())
            self.full_list[self.rowsNum[6]] = '%s\n' % (dialogfile.GetPath())
            dialogfile.Destroy()
    # ---------------------------------------------------------------------#

    def txtffmpeg(self, event):
        """write ffmpeg pathname"""
        t = self.txtctrl_ffmpeg.GetValue()
        self.full_list[self.rowsNum[6]] = '%s\n' % (t)

    # ----------------------ffprobe path checkbox--------------------------#

    def exeFFprobe(self, event):
        """Enable or disable ffprobe binary esecutable"""
        if self.checkbox_exeFFprobe.IsChecked():
            self.btn_pathFFprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.txtctrl_ffprobe.SetValue("")
            self.full_list[self.rowsNum[7]] = 'true\n'

        else:
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.SetValue("")
            self.full_list[self.rowsNum[7]] = 'false\n'
            self.full_list[self.rowsNum[8]] = '%s\n' % self.ffprobe

    # ----------------------ffprobe path open dialog----------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        dialfile = wx.FileDialog(self, _("Videomass: Where is the ffprobe "
                                         "executable located?"), "", "",
                                 "ffprobe binarys (*%s)|*%s| All files "
                                 "(*.*)|*.*" % (self.ffprobe, self.ffprobe),
                                 wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                 )
        if dialfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffprobe.SetValue("")
            self.txtctrl_ffprobe.AppendText(dialfile.GetPath())
            self.full_list[self.rowsNum[8]] = '%s\n' % (dialfile.GetPath())
            dialfile.Destroy()
    # ---------------------------------------------------------------------#

    def txtffprobe(self, event):
        """write ffprobe pathname"""
        t = self.txtctrl_ffprobe.GetValue()
        self.full_list[self.rowsNum[8]] = '%s\n' % (t)

    # ----------------------ffplay path checkbox--------------------------#

    def exeFFplay(self, event):
        """Enable or disable ffplay binary esecutable"""
        if self.checkbox_exeFFplay.IsChecked():
            self.btn_pathFFplay.Enable()
            self.txtctrl_ffplay.Enable()
            self.txtctrl_ffplay.SetValue("")
            self.full_list[self.rowsNum[9]] = 'true\n'

        else:
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.SetValue("")
            self.full_list[self.rowsNum[9]] = 'false\n'
            self.full_list[self.rowsNum[10]] = '%s\n' % self.ffplay

    # ----------------------ffplay path open dialog----------------------#

    def open_path_ffplay(self, event):
        """Indicates a new ffplay path-name"""
        dialfile = wx.FileDialog(self, _("Videomass: Where is the ffplay "
                                         "executable located?"), "", "",
                                 "ffplay binarys (*%s)|*%s| All files "
                                 "(*.*)|*.*" % (self.ffplay, self.ffplay),
                                 wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                 )

        if dialfile.ShowModal() == wx.ID_OK:
            self.txtctrl_ffplay.SetValue("")
            self.txtctrl_ffplay.AppendText(dialfile.GetPath())
            self.full_list[self.rowsNum[10]] = '%s\n' % (dialfile.GetPath())

            dialfile.Destroy()
    # ---------------------------------------------------------------------#

    def txtffplay(self, event):
        """write ffplay pathname"""
        t = self.txtctrl_ffplay.GetValue()
        self.full_list[self.rowsNum[10]] = '%s\n' % (t)

    # ----------------------mpv path checkbox--------------------------#

    def exe_MPV(self, event):
        """Enable or disable ffmpeg binary esecutable"""
        if self.checkbox_exeMpv.IsChecked():
            self.btn_pathMpv.Enable()
            self.txtctrl_mpv.Enable()
            self.txtctrl_mpv.SetValue("")
            self.full_list[self.rowsNum[11]] = 'true\n'
        else:
            self.btn_pathMpv.Disable()
            self.txtctrl_mpv.Disable()
            self.txtctrl_mpv.SetValue("")
            self.full_list[self.rowsNum[11]] = 'false\n'
            self.full_list[self.rowsNum[12]] = '%s\n' % self.mpv

    # ----------------------ffmpeg path open dialog----------------------#
    def open_path_MPV(self, event):
        """Indicates a new mpv path-name"""
        dialogfile = wx.FileDialog(self, _("Videomass: Where is the mpv "
                                           "executable located?"), "", "",
                                   "mpv binarys (*%s)|*%s| All files "
                                   "(*.*)|*.*" % (self.mpv, self.mpv),
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                   )

        if dialogfile.ShowModal() == wx.ID_OK:
            self.txtctrl_mpv.SetValue("")
            self.txtctrl_mpv.AppendText(dialogfile.GetPath())
            self.full_list[self.rowsNum[12]] = '%s\n' % (dialogfile.GetPath())
            dialogfile.Destroy()
    # ---------------------------------------------------------------------#

    def txt_MPV(self, event):
        """write ffmpeg pathname"""
        t = self.txtctrl_mpv.GetValue()
        self.full_list[self.rowsNum[12]] = '%s\n' % (t)

    # --------------------------------------------------------------------#

    def on_Iconthemes(self, event):
        """
        Set themes of icons
        """
        choice = "%s\n" % self.cmbx_icons.GetStringSelection()
        self.full_list[self.rowsNum[13]] = choice

        if choice == "Material_Design_Icons_white\n":
            self.full_list[self.rowsNum[15]] = '26, 26, 26, 255\n'
            self.full_list[self.rowsNum[16]] = '229, 229, 229, 255\n'
        else:
            self.full_list[self.rowsNum[15]] = '176, 176, 176, 255\n'
            self.full_list[self.rowsNum[16]] = '0, 0, 0\n'

        if not self.default_theme.IsEnabled():
            self.default_theme.Enable()
    # ------------------------------------------------------------------#

    def onColorDlg(self, event):
        """
        Colorize the toolbar bar
        """
        btn = event.GetEventObject()
        identity = btn.GetLabelText()

        dlg = wx.ColourDialog(self)

        # Ensure the full colour dialog is displayed,
        # not the abbreviated version.
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            rgb = str(data.GetColour().Get())
            choice = rgb.replace('(', '').replace(')', '').strip()

            if identity == _('Bar Colour'):
                self.full_list[self.rowsNum[14]] = "%s\n" % choice
            elif identity == _('Buttons Colour'):
                self.full_list[self.rowsNum[15]] = "%s\n" % choice
            elif identity == _("Font Colour"):
                self.full_list[self.rowsNum[16]] = "%s\n" % choice
            if not self.default_theme.IsEnabled():
                self.default_theme.Enable()

        dlg.Destroy()
    # ----------------------------------------------------------------------#

    def onAppearanceDefault(self, event):
        """
        Restore to default settings colors and icons set
        """
        self.full_list[self.rowsNum[13]] = "Material_Design_Icons_black\n"
        if Setup.OS == 'Windows':
            self.full_list[self.rowsNum[14]] = '40, 148, 255, 255\n'
        else:
            self.full_list[self.rowsNum[14]] = '228, 21, 68\n'
        self.full_list[self.rowsNum[15]] = '176, 176, 176, 255\n'
        self.full_list[self.rowsNum[16]] = '0, 0, 0\n'
        self.default_theme.Disable()
    # ----------------------------------------------------------------------#

    def on_help(self, event):
        """
        """
        page = 'https://jeanslack.github.io/Videomass/Pages/Startup/Setup.html'
        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def okmsg(self):
        wx.MessageBox(_("Changes will take affect once the program "
                        "has been restarted"))
    # --------------------------------------------------------------------#

    def on_close(self, event):
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Applies all changes writing the new entries
        """
        with open(self.getfileconf, 'w') as fconf:
            for i in self.full_list:
                fconf.write('%s' % i)
        # self.Destroy() # WARNING on mac not close corretly, on linux ok
        self.okmsg()
        self.Close()
