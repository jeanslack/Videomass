# -*- coding: UTF-8 -*-
# Name: settings.py
# Porpose: videomass setup dialog
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.31.2020
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
import sys
import webbrowser
from videomass3.vdms_utils.utils import detect_binaries


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
    FF_LOCALDIR = get.FFMPEGlocaldir
    FF_OUTPATH = get.FFMPEGoutdir
    YDL_OUTPATH = get.YDLoutdir
    SAMEDIR = get.SAMEdir
    FILESUFFIX = get.FILEsuffix
    CLEARCACHE = get.CLEARcache
    YDL_PREF = get.YDL_pref
    EXECYDL = get.execYdl
    SITEPKGYDL = get.YDLsite

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
                 Just uncomment it.
                 - POSITION, the number index of self.rowsNum items (how many
                   objects it contains).
                 - ROW, is the current numeric rows on the file configuration
                 - VALUE, is the value as writing in the file configuration
        """

        # Make a items list of
        self.rowsNum = []  # rows number list
        dic = {}  # used for debug
        with open(Setup.FILE_CONF, 'r') as f:
            self.full_list = f.readlines()
        for a, b in enumerate(self.full_list):
            if not b.startswith('#'):
                if not b == '\n':
                    self.rowsNum.append(a)

                    """
                    dic [a] = b.strip()# used for easy reading print debug
        #USEFUL FOR DEBUGGING (see Setup.__init__.__doc__)
        #uncomment the following code for a convenient reading
        print("\nPOSITION:    ROW:     VALUE:")
        for n, k in enumerate(sorted(dic)):
            print(n, ' -------> ', k, ' --> ', dic[k])
        """

        dirname = os.path.expanduser('~')  # /home/user/
        self.pathFF = dirname if not Setup.FF_OUTPATH else Setup.FF_OUTPATH
        self.pathYDL = dirname if not Setup.YDL_OUTPATH else Setup.YDL_OUTPATH
        self.iconset = iconset
        self.getfileconf = Setup.FILE_CONF

        if Setup.OS == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""
        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 10)
        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGeneral = wx.BoxSizer(wx.VERTICAL)
        msg = _("Where do you prefer to save your transcodes?")
        boxFFmpegoutpath = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY,
                                                          (msg)), wx.VERTICAL)
        sizerGeneral.Add(boxFFmpegoutpath, 0, wx.ALL | wx.EXPAND, 15)
        boxFFmpegoutpath.Add((0, 10))
        sizeFFdirdest = wx.BoxSizer(wx.HORIZONTAL)
        boxFFmpegoutpath.Add(sizeFFdirdest, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_FFpath = wx.Button(tabOne, wx.ID_ANY, _("Browse.."))
        sizeFFdirdest.Add(self.btn_FFpath, 0, wx.ALL |
                          wx.ALIGN_CENTER_VERTICAL |
                          wx.ALIGN_CENTER_HORIZONTAL, 5
                          )
        self.txtctrl_FFpath = wx.TextCtrl(tabOne, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizeFFdirdest.Add(self.txtctrl_FFpath, 1, wx.ALL |
                          wx.ALIGN_CENTER_VERTICAL |
                          wx.ALIGN_CENTER_HORIZONTAL, 5
                          )
        self.txtctrl_FFpath.AppendText(self.pathFF)
        descr = _(" Save to the same source folder")
        self.ckbx_dir = wx.CheckBox(tabOne, wx.ID_ANY, (descr))
        boxFFmpegoutpath.Add(self.ckbx_dir, 0, wx.ALL, 5)
        sizeSamedest = wx.BoxSizer(wx.HORIZONTAL)
        boxFFmpegoutpath.Add(sizeSamedest, 0, wx.EXPAND)
        descr = _("Optional suffix assignment (example, _convert):")
        self.lab_suffix = wx.StaticText(tabOne, wx.ID_ANY, (descr))
        sizeSamedest.Add(self.lab_suffix, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 10)
        self.text_suffix = wx.TextCtrl(tabOne, wx.ID_ANY, "", size=(150, -1))
        sizeSamedest.Add(self.text_suffix, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5)
        msg = _("Where do you prefer to save your downloads?")
        boxYdloutpath = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY,
                                                       (msg)), wx.VERTICAL)
        sizerGeneral.Add(boxYdloutpath, 0, wx.ALL | wx.EXPAND, 15)
        boxYdloutpath.Add((0, 10))
        sizeYDLdirdest = wx.BoxSizer(wx.HORIZONTAL)
        boxYdloutpath.Add(sizeYDLdirdest, 0, wx.ALL | wx.EXPAND, 5)

        self.btn_YDLpath = wx.Button(tabOne, wx.ID_ANY, _("Browse.."))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.ALL |
                           wx.ALIGN_CENTER_VERTICAL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        self.txtctrl_YDLpath = wx.TextCtrl(tabOne, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizeYDLdirdest.Add(self.txtctrl_YDLpath, 1, wx.ALL |
                           wx.ALIGN_CENTER_VERTICAL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        self.txtctrl_YDLpath.AppendText(self.pathYDL)
        boxLabCache = wx.StaticBoxSizer(wx.StaticBox(tabOne, wx.ID_ANY, (
                                        _("Cache Settings"))), wx.VERTICAL)
        sizerGeneral.Add(boxLabCache, 1, wx.ALL | wx.EXPAND, 15)
        gridCache = wx.BoxSizer(wx.VERTICAL)

        self.checkbox_cacheclr = wx.CheckBox(tabOne, wx.ID_ANY, (
                        _(" Clear the cache when exiting the application")))
        gridCache.Add(self.checkbox_cacheclr, 0, wx.ALL, 5)
        boxLabCache.Add(gridCache, 1, wx.ALL | wx.EXPAND, 10)
        tabOne.SetSizer(sizerGeneral)
        notebook.AddPage(tabOne, _("Files Preferences"))
        # -----tab 2
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        sizerFFmpeg = wx.BoxSizer(wx.VERTICAL)
        gridExec = wx.StaticBoxSizer(wx.StaticBox(tabTwo, wx.ID_ANY,
                                     _('Path to the executables')),
                                     wx.VERTICAL)
        sizerFFmpeg.Add(gridExec, 1, wx.ALL | wx.EXPAND, 15)
        # ----
        gridExec.Add((0, 10))
        self.checkbox_exeFFmpeg = wx.CheckBox(tabTwo, wx.ID_ANY, (
                                _(" Enable another location to run FFmpeg")))
        self.btn_pathFFmpeg = wx.Button(tabTwo, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffmpeg = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        gridExec.Add(self.checkbox_exeFFmpeg, 0, wx.ALL, 5)
        gridFFmpeg = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFmpeg, 0, wx.ALL | wx.EXPAND, 5)
        gridFFmpeg.Add(self.btn_pathFFmpeg, 0, wx.ALL, 5)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALL, 5)
        # ----
        self.checkbox_exeFFprobe = wx.CheckBox(tabTwo, wx.ID_ANY, (
                                _(" Enable another location to run FFprobe")))
        self.btn_pathFFprobe = wx.Button(tabTwo, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffprobe = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        gridExec.Add(self.checkbox_exeFFprobe, 0, wx.ALL, 5)
        gridFFprobe = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFprobe, 0, wx.ALL | wx.EXPAND, 5)
        gridFFprobe.Add(self.btn_pathFFprobe, 0, wx.ALL, 5)
        gridFFprobe.Add(self.txtctrl_ffprobe, 1, wx.ALL, 5)
        # ----
        self.checkbox_exeFFplay = wx.CheckBox(tabTwo, wx.ID_ANY, (
                                  _(" Enable another location to run FFplay")))
        self.btn_pathFFplay = wx.Button(tabTwo, wx.ID_ANY, _("Browse.."))
        self.txtctrl_ffplay = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        gridExec.Add(self.checkbox_exeFFplay, 0, wx.ALL, 5)
        gridFFplay = wx.BoxSizer(wx.HORIZONTAL)
        gridExec.Add(gridFFplay, 0, wx.ALL | wx.EXPAND, 5)
        gridFFplay.Add(self.btn_pathFFplay, 0, wx.ALL, 5)
        gridFFplay.Add(self.txtctrl_ffplay, 1, wx.ALL, 5)

        gridFFopt = wx.StaticBoxSizer(wx.StaticBox(tabTwo, wx.ID_ANY,
                                                   _('Other options')),
                                      wx.VERTICAL)
        sizerFFmpeg.Add(gridFFopt, 0, wx.ALL | wx.EXPAND, 15)
        gridSizopt = wx.FlexGridSizer(0, 2, 0, 0)
        gridFFopt.Add(gridSizopt, 0, wx.ALL, 5)

        labFFthreads = wx.StaticText(tabTwo, wx.ID_ANY,
                                     (_("Threads used for transcoding "
                                        "(from 0 to 32)")))
        gridSizopt.Add(labFFthreads, 0,
                       wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        self.spinctrl_threads = wx.SpinCtrl(tabTwo, wx.ID_ANY,
                                            "%s" % Setup.FF_THREADS[9:],
                                            size=(-1, -1), min=0, max=32,
                                            style=wx.TE_PROCESS_ENTER
                                            )
        gridSizopt.Add(self.spinctrl_threads, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        # ----
        tabTwo.SetSizer(sizerFFmpeg)
        notebook.AddPage(tabTwo, _("FFmpeg"))

        # -----tab 3
        self.tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerYdl = wx.BoxSizer(wx.VERTICAL)

        gridYdldl = wx.StaticBoxSizer(wx.StaticBox(self.tabThree, wx.ID_ANY,
                                      ''), wx.VERTICAL)
        sizerYdl.Add(gridYdldl, 1, wx.ALL | wx.EXPAND, 15)
        # if AppImage
        if '/tmp/.mount_' in sys.executable or \
           os.path.exists(os.getcwd() + '/AppRun'):
            dldlist = [
                _('Disable youtube-dl'),
                _('Use the one included in the AppImage (recommended)'),
                _('Use a local copy of youtube-dl')]
            ydlmsg = _(
                'Make sure you are using the latest available version of '
                'youtube-dl.\nThis allows you to avoid download problems.')
            labydl0 = wx.StaticText(self.tabThree, wx.ID_ANY, (ydlmsg))
            gridYdldl.Add(labydl0, 0, wx.TOP | wx.CENTRE, 5)
        else:
            dldlist = [
                _('Disable youtube-dl'),
                _('Use the one installed in your O.S. (recommended)'),
                _('Use a local copy of youtube-dl updatable by Videomass')]
            ydlmsg = _(
                'Make sure you are using the latest available version of '
                'youtube-dl.\nThis allows you to avoid download problems. '
                'Note that the versions\ninstalled with the package '
                'manager of your O.S. they may be out of\ndate and not '
                'upgradeable. It is recommended to remove those versions\n'
                'and update youtube-dl with pip3, e.g.')
            labydl0 = wx.StaticText(self.tabThree, wx.ID_ANY, (ydlmsg))
            gridYdldl.Add(labydl0, 0, wx.TOP | wx.CENTRE, 5)
            labydl1 = wx.StaticText(self.tabThree, wx.ID_ANY,
                                    ('pip3 install --user -U youtube-dl'))
            gridYdldl.Add(labydl1, 0, wx.ALL | wx.CENTRE, 10)
            if Setup.OS == 'Darwin':
                labydl1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                        wx.BOLD, 0, ""))
            else:
                labydl1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,
                                        wx.BOLD, 0, ""))
        self.rdbDownloader = wx.RadioBox(self.tabThree, wx.ID_ANY,
                                         (_("Downloader preferences")),
                                         choices=dldlist,
                                         majorDimension=1,
                                         style=wx.RA_SPECIFY_COLS
                                         )
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.rdbDownloader.EnableItem(1, enable=False)
        sizerYdl.Add(self.rdbDownloader, 0, wx.ALL | wx.EXPAND, 15)

        grdydlLoc = wx.BoxSizer(wx.HORIZONTAL)
        sizerYdl.Add(grdydlLoc, 0, wx.ALL | wx.EXPAND, 10)
        labydl2 = wx.StaticText(self.tabThree, wx.ID_ANY, _('Current path'))
        grdydlLoc.Add(labydl2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)

        self.ydlPath = wx.TextCtrl(self.tabThree, wx.ID_ANY, "",
                                   style=wx.TE_READONLY)
        grdydlLoc.Add(self.ydlPath, 1, wx.ALL | wx.EXPAND, 5)
        # ----
        self.tabThree.SetSizer(sizerYdl)
        notebook.AddPage(self.tabThree, _("youtube-dl"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        gridappearance = wx.BoxSizer(wx.VERTICAL)
        boxLabIcons = wx.StaticBoxSizer(wx.StaticBox(tabFour, wx.ID_ANY, (
                                        _("Icon themes"))), wx.VERTICAL)
        gridappearance.Add(boxLabIcons, 1, wx.ALL | wx.EXPAND, 15)
        msg = _("setting the icons will also change the background\n"
                "and foreground of some text fields.")
        lab_appearance = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        boxLabIcons.Add(lab_appearance, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL,
                        15)
        self.cmbx_icons = wx.ComboBox(tabFour, wx.ID_ANY,
                                      choices=[
                                          ("Breeze"),
                                          ("Breeze-Dark"),
                                          ("Breeze-Blues"),
                                          ("Papirus"),
                                          ("Papirus-Dark"),
                                          ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        boxLabIcons.Add(self.cmbx_icons, 0,
                        wx.ALL |
                        wx.ALIGN_CENTER_HORIZONTAL, 15
                        )
        self.cmbx_icons.SetValue(self.iconset)
        tabFour.SetSizer(gridappearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tabFour, _("Appearance"))
        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        gridLog = wx.BoxSizer(wx.VERTICAL)
        msglog = _("The following settings affect output messages and\n"
                   "the log messages during transcoding processes.\n"
                   "Change only if you know what you are doing.\n")
        labLOGmsg = wx.StaticText(tabFive, wx.ID_ANY, (msglog))
        gridLOGmsg = wx.StaticBoxSizer(wx.StaticBox(tabFive, wx.ID_ANY,
                                       ''), wx.VERTICAL)
        gridLog.Add(gridLOGmsg, 0, wx.ALL | wx.EXPAND, 15)
        gridLOGmsg.Add(labLOGmsg, 0, wx.ALL | wx.CENTRE, 5)
        self.rdbFFmpeg = wx.RadioBox(
                                tabFive, wx.ID_ANY,
                                ("Set logging level flags used by FFmpeg"),
                                choices=Setup.OPT_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
                                     )
        gridLog.Add(self.rdbFFmpeg, 0, wx.ALL | wx.EXPAND, 15)
        self.rdbFFplay = wx.RadioBox(
                                tabFive, wx.ID_ANY,
                                ("Set logging level flags used by FFplay"),
                                choices=Setup.OPT_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
                                     )
        gridLog.Add(self.rdbFFplay, 0, wx.ALL | wx.EXPAND, 15)
        tabFive.SetSizer(gridLog)
        notebook.AddPage(tabFive, _("FFmpeg logging levels"))
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
        self.SetTitle(_("Videomass Setup"))
        tip = (_("Assign an additional suffix to FFmpeg output files"))
        self.text_suffix.SetToolTip(tip)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffplay, self.rdbFFplay)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbFFmpeg)
        self.Bind(wx.EVT_SPINCTRL, self.on_threads, self.spinctrl_threads)
        self.Bind(wx.EVT_BUTTON, self.on_ffmpegPath, self.btn_FFpath)
        self.Bind(wx.EVT_BUTTON, self.on_downloadPath, self.btn_YDLpath)
        self.Bind(wx.EVT_CHECKBOX, self.set_Samedest, self.ckbx_dir)
        self.Bind(wx.EVT_TEXT, self.set_Suffix, self.text_suffix)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_pathFFmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_pathFFprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.checkbox_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_pathFFplay)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)
        self.Bind(wx.EVT_CHECKBOX, self.clear_Cache, self.checkbox_cacheclr)
        self.Bind(wx.EVT_RADIOBOX, self.on_Ydl_preferences, self.rdbDownloader)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file

        """
        if Setup.CLEARCACHE == 'false':
            self.checkbox_cacheclr.SetValue(False)
        else:
            self.checkbox_cacheclr.SetValue(True)

        if Setup.YDL_PREF == 'disabled':
            self.rdbDownloader.SetSelection(0)
            self.ydlPath.WriteText(_('Disabled'))
        elif Setup.YDL_PREF == 'system':
            self.rdbDownloader.SetSelection(1)
            if Setup.SITEPKGYDL is None:
                self.ydlPath.WriteText(_('Not Installed'))
            else:
                self.ydlPath.WriteText(str(Setup.SITEPKGYDL))
        elif Setup.YDL_PREF == 'local':
            self.rdbDownloader.SetSelection(2)
            if os.path.exists(Setup.EXECYDL):
                self.ydlPath.WriteText(str(Setup.EXECYDL))
            else:
                self.ydlPath.WriteText(_('Not found'))

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
            self.txtctrl_ffmpeg.AppendText(Setup.FFMPEG_LINK)
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(Setup.FFMPEG_LINK)
            self.checkbox_exeFFmpeg.SetValue(True)

        if Setup.FFPROBE_CHECK == 'false':
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(Setup.FFPROBE_LINK)
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(Setup.FFPROBE_LINK)
            self.checkbox_exeFFprobe.SetValue(True)

        if Setup.FFPLAY_CHECK == 'false':
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.AppendText(Setup.FFPLAY_LINK)
            self.checkbox_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(Setup.FFPLAY_LINK)
            self.checkbox_exeFFplay.SetValue(True)

        if Setup.SAMEDIR == 'false':
            self.lab_suffix.Disable()
            self.text_suffix.Disable()
            self.ckbx_dir.SetValue(False)
        else:
            self.lab_suffix.Enable()
            self.text_suffix.Enable()
            self.ckbx_dir.SetValue(True)
            self.btn_FFpath.Disable(), self.txtctrl_FFpath.Disable()
            if not Setup.FILESUFFIX == 'none':
                self.text_suffix.AppendText(Setup.FILESUFFIX)
    # --------------------------------------------------------------------#

    def on_threads(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_threads.GetValue()
        self.full_list[self.rowsNum[2]] = '-threads %s\n' % sett
    # ---------------------------------------------------------------------#

    def on_downloadPath(self, event):
        """set up a custom user path for file downloads"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save the "
                                   "file downloads"), "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            self.txtctrl_YDLpath.AppendText(dlg.GetPath())
            self.full_list[self.rowsNum[19]] = '%s\n' % (dlg.GetPath())
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_ffmpegPath(self, event):
        """set up a custom user path for file export"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save "
                                   "exported files"), "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_FFpath.Clear()
            self.txtctrl_FFpath.AppendText(dlg.GetPath())
            self.full_list[self.rowsNum[1]] = '%s\n' % (dlg.GetPath())
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def set_Samedest(self, event):
        """Save the FFmpeg output files in the same source folder"""
        if self.ckbx_dir.IsChecked():
            self.lab_suffix.Enable(), self.text_suffix.Enable()
            self.btn_FFpath.Disable(), self.txtctrl_FFpath.Disable()
            self.full_list[self.rowsNum[17]] = 'true\n'
        else:
            self.text_suffix.Clear()
            self.lab_suffix.Disable(), self.text_suffix.Disable()
            self.btn_FFpath.Enable(), self.txtctrl_FFpath.Enable()
            self.full_list[self.rowsNum[17]] = 'false\n'
            self.full_list[self.rowsNum[18]] = 'none\n'
    # --------------------------------------------------------------------#

    def set_Suffix(self, event):
        """Set a custom suffix to append at the output file names"""
        msg = _('Enter only alphanumeric characters. You can also use the '
                'hyphen ("-") and the underscore ("_"). Blank spaces are '
                'not allowed.')
        suffix = self.text_suffix.GetValue()

        if self.text_suffix.GetBackgroundColour() == (152, 131, 19, 255):
            # html: ('#988313') == rgb: (152, 131, 19, 255) =
            self.text_suffix.SetBackgroundColour(wx.NullColour)
            self.text_suffix.Clear()

        if not suffix == '':
            for c in suffix:
                if c not in ('_', '-'):
                    if not c.isalnum():  # is not alphanumeric
                        self.text_suffix.SetBackgroundColour('#988313')
                        wx.MessageBox(msg, 'WARNING', wx.ICON_WARNING)
                        self.full_list[self.rowsNum[18]] = 'none\n'
                        return

            self.full_list[self.rowsNum[18]] = '%s\n' % (suffix)
        else:
            self.full_list[self.rowsNum[18]] = 'none\n'
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
    # --------------------------------------------------------------------#

    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg local binary"""
        if self.checkbox_exeFFmpeg.IsChecked():
            self.btn_pathFFmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.full_list[self.rowsNum[5]] = 'true\n'
        else:
            self.btn_pathFFmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.full_list[self.rowsNum[5]] = 'false\n'

            status = detect_binaries(Setup.OS, 'ffpl', Setup.FF_LOCALDIR)

            if status[0] == 'not installed':
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write(status[0])
                self.full_list[self.rowsNum[6]] = '%s\n' % 'none'
            else:
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write(status[1])
                self.full_list[self.rowsNum[6]] = '%s\n' % status[1]
    # --------------------------------------------------------------------#

    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        with wx.FileDialog(self, _("Choose the ffmpeg executable "
                                   "(e.g. a static build)"), "", "",
                           "ffmpeg binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffmpeg, self.ffmpeg),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_OK:
                if os.path.basename(fd.GetPath()) == self.ffmpeg:
                    self.txtctrl_ffmpeg.Clear()
                    self.txtctrl_ffmpeg.write(fd.GetPath())
                    self.full_list[self.rowsNum[6]] = '%s\n' % (fd.GetPath())
    # --------------------------------------------------------------------#

    def exeFFprobe(self, event):
        """Enable or disable ffprobe local binary"""
        if self.checkbox_exeFFprobe.IsChecked():
            self.btn_pathFFprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.full_list[self.rowsNum[7]] = 'true\n'

        else:
            self.btn_pathFFprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.full_list[self.rowsNum[7]] = 'false\n'

            status = detect_binaries(Setup.OS, self.ffprobe, Setup.FF_LOCALDIR)

            if status[0] == 'not installed':
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write(status[0])
                self.full_list[self.rowsNum[8]] = '%s\n' % 'none'
            else:
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write(status[1])
                self.full_list[self.rowsNum[8]] = '%s\n' % status[1]
    # --------------------------------------------------------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        with wx.FileDialog(self, _("Choose the ffprobe executable "
                                   "(e.g. a static build)"), "", "",
                           "ffprobe binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffprobe, self.ffprobe),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_OK:
                if os.path.basename(fd.GetPath()) == self.ffprobe:
                    self.txtctrl_ffprobe.Clear()
                    self.txtctrl_ffprobe.write(fd.GetPath())
                    self.full_list[self.rowsNum[8]] = '%s\n' % (fd.GetPath())
    # --------------------------------------------------------------------#

    def exeFFplay(self, event):
        """Enable or disable ffplay local binary"""
        if self.checkbox_exeFFplay.IsChecked():
            self.btn_pathFFplay.Enable()
            self.txtctrl_ffplay.Enable()
            self.full_list[self.rowsNum[9]] = 'true\n'

        else:
            self.btn_pathFFplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.full_list[self.rowsNum[9]] = 'false\n'

            status = detect_binaries(Setup.OS, self.ffplay, Setup.FF_LOCALDIR)

            if status[0] == 'not installed':
                self.txtctrl_ffplay.Clear()
                self.txtctrl_ffplay.write(status[0])
                self.full_list[self.rowsNum[10]] = '%s\n' % 'none'
            else:
                self.txtctrl_ffplay.Clear()
                self.txtctrl_ffplay.write(status[1])
                self.full_list[self.rowsNum[10]] = '%s\n' % status[1]
    # --------------------------------------------------------------------#

    def open_path_ffplay(self, event):
        """Indicates a new ffplay path-name"""
        with wx.FileDialog(self, _("Choose the ffplay executable "
                                   "(e.g. a static build)"), "", "",
                           "ffplay binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffplay, self.ffplay),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:

            if fd.ShowModal() == wx.ID_OK:
                if os.path.basename(fd.GetPath()) == self.ffprobe:
                    self.txtctrl_ffplay.Clear()
                    self.txtctrl_ffplay.write(fd.GetPath())
                    self.full_list[self.rowsNum[10]] = '%s\n' % (fd.GetPath())
    # ---------------------------------------------------------------------#

    def on_Iconthemes(self, event):
        """
        Set themes of icons
        """
        choice = "%s\n" % self.cmbx_icons.GetStringSelection()
        self.full_list[self.rowsNum[11]] = choice
    # --------------------------------------------------------------------#

    def clear_Cache(self, event):
        """
        if checked, set to clear cached data on exit
        """
        if self.checkbox_cacheclr.IsChecked():
            self.full_list[self.rowsNum[15]] = 'true\n'
        else:
            self.full_list[self.rowsNum[15]] = 'false\n'
    # --------------------------------------------------------------------#

    def on_Ydl_preferences(self, event):
        """
        set youtube-dl preferences
        """
        if self.rdbDownloader.GetSelection() == 0:
            self.full_list[self.rowsNum[16]] = 'disabled\n'
        elif self.rdbDownloader.GetSelection() == 1:
            self.full_list[self.rowsNum[16]] = 'system\n'
        elif self.rdbDownloader.GetSelection() == 2:
            self.full_list[self.rowsNum[16]] = 'local\n'
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        """
        page = 'https://jeanslack.github.io/Videomass/Pages/Startup/Setup.html'
        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def okmsg(self):
        wx.MessageBox(_("Changes will take effect once the program "
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
