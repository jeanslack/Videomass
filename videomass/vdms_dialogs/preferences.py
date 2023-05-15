# -*- coding: UTF-8 -*-
"""
Name: preferences.py
Porpose: videomass setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Jan.21.2023
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import webbrowser
import wx
from videomass.vdms_utils.utils import detect_binaries
from videomass.vdms_io import io_tools
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_sys.app_const import supLang


class SetUp(wx.Dialog):
    """
    Represents settings and configuration
    storing of the program.
    """
    FFPLAY_LOGLEV = [("quiet (Show nothing at all)"),
                     ("fatal (Only show fatal errors)"),
                     ("error (Show all errors)"),
                     ("warning (Show all warnings and errors)"),
                     ("info (Show informative messages during processing)")
                     ]
    FFMPEG_LOGLEV = [("error (Show all errors)"),
                     ("warning (Show all warnings and errors)"),
                     ("info (Show informative messages during processing)"),
                     ("verbose (Same as `info`, except more verbose)"),
                     ("debug (Show everything, including debugging info)")
                     ]
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) default settings already loaded.
        self.confmanager: instance to ConfigManager class
        self.settings: (dict) current user settings from file conf.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.settings = self.confmanager.read_options()

        if self.appdata['ostype'] == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGen = wx.BoxSizer(wx.VERTICAL)
        sizerGen.Add((0, 15))
        self.checkbox_exit = wx.CheckBox(tabOne, wx.ID_ANY,
                                         (_("Warn on exit"))
                                         )
        sizerGen.Add(self.checkbox_exit, 0, wx.ALL, 5)
        sizerGen.Add((0, 15))
        lablang = wx.StaticText(tabOne, wx.ID_ANY, _('Application Language'))
        sizerGen.Add(lablang, 0, wx.ALL | wx.EXPAND, 5)
        langs = [lang[1] for lang in supLang.values()]
        self.cmbx_lang = wx.ComboBox(tabOne, wx.ID_ANY,
                                     choices=langs,
                                     size=(-1, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        sizerGen.Add(self.cmbx_lang, 0, wx.ALL | wx.EXPAND, 5)
        sizerGen.Add((0, 15))
        labconf = wx.StaticText(tabOne, wx.ID_ANY, _('Configuration folder'))
        sizerGen.Add(labconf, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_conf = wx.Button(tabOne, wx.ID_ANY, "...", size=(35, -1),
                                  name='config dir')
        self.txtctrl_conf = wx.TextCtrl(tabOne, wx.ID_ANY,
                                        self.appdata['confdir'],
                                        style=wx.TE_READONLY,
                                        )
        sizerconf = wx.BoxSizer(wx.HORIZONTAL)
        sizerGen.Add(sizerconf, 0, wx.EXPAND)
        sizerconf.Add(self.txtctrl_conf, 1, wx.ALL, 5)
        sizerconf.Add(self.btn_conf, 0, wx.RIGHT | wx.CENTER, 5)
        sizerGen.Add((0, 15))
        labcache = wx.StaticText(tabOne, wx.ID_ANY, _('Cache folder'))
        sizerGen.Add(labcache, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_cache = wx.Button(tabOne, wx.ID_ANY, "...", size=(35, -1),
                                   name='cache dir')
        self.txtctrl_cache = wx.TextCtrl(tabOne, wx.ID_ANY,
                                         self.appdata['cachedir'],
                                         style=wx.TE_READONLY,
                                         )
        sizercache = wx.BoxSizer(wx.HORIZONTAL)
        sizerGen.Add(sizercache, 0, wx.EXPAND)
        sizercache.Add(self.txtctrl_cache, 1, wx.ALL, 5)
        sizercache.Add(self.btn_cache, 0, wx.RIGHT | wx.CENTER, 5)
        msg = _("Clear the cache when exiting the application")
        self.checkbox_cacheclr = wx.CheckBox(tabOne, wx.ID_ANY, (msg))
        sizerGen.Add(self.checkbox_cacheclr, 0, wx.ALL, 5)
        sizerGen.Add((0, 15))
        lablog = wx.StaticText(tabOne, wx.ID_ANY, _('Log folder'))
        sizerGen.Add(lablog, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_log = wx.Button(tabOne, wx.ID_ANY, "...", size=(35, -1),
                                 name='log dir')
        self.txtctrl_log = wx.TextCtrl(tabOne, wx.ID_ANY,
                                       self.appdata['logdir'],
                                       style=wx.TE_READONLY,
                                       )
        sizerlog = wx.BoxSizer(wx.HORIZONTAL)
        sizerGen.Add(sizerlog, 0, wx.EXPAND)
        sizerlog.Add(self.txtctrl_log, 1, wx.ALL, 5)
        sizerlog.Add(self.btn_log, 0, wx.RIGHT | wx.CENTER, 5)
        msg = _("Delete the contents of the log files "
                "when exiting the application")
        self.checkbox_logclr = wx.CheckBox(tabOne, wx.ID_ANY, (msg))
        sizerGen.Add(self.checkbox_logclr, 0, wx.ALL, 5)
        sizerGen.Add((0, 5))

        tabOne.SetSizer(sizerGen)
        notebook.AddPage(tabOne, _("Miscellanea"))

        # -----tab 2
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        sizerFiles = wx.BoxSizer(wx.VERTICAL)
        sizerFiles.Add((0, 15))
        msg = _("Where do you prefer to save your transcodes?")
        labfile = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFiles.Add(labfile, 0, wx.ALL | wx.EXPAND, 5)
        sizeFFdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeFFdirdest, 0, wx.EXPAND)
        self.txtctrl_FFpath = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizeFFdirdest.Add(self.txtctrl_FFpath, 1, wx.ALL, 5)
        self.txtctrl_FFpath.AppendText(self.appdata['outputfile'])
        self.btn_fsave = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizeFFdirdest.Add(self.btn_fsave, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        sizerFiles.Add((0, 15))
        descr = _("Save each file in the same folder as input file")
        self.ckbx_dir = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_dir, 0, wx.ALL, 5)
        sizeSamedest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeSamedest, 0, wx.EXPAND)
        descr = _("Assign optional suffix to output file names:")
        self.lab_suffix = wx.StaticText(tabTwo, wx.ID_ANY, (descr))
        sizeSamedest.Add(self.lab_suffix, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        self.text_suffix = wx.TextCtrl(tabTwo, wx.ID_ANY, "", size=(90, -1))
        sizeSamedest.Add(self.text_suffix, 1, wx.ALL | wx.CENTER, 5)
        descr = _("Always move source files to the Videomass\n"
                  "trash folder after successful encoding")
        self.ckbx_trash = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_trash, 0, wx.ALL, 5)
        sizetrash = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizetrash, 0, wx.EXPAND)
        self.txtctrl_trash = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                         style=wx.TE_READONLY
                                         )
        sizetrash.Add(self.txtctrl_trash, 1, wx.ALL, 5)
        self.txtctrl_trash.AppendText(self.appdata['user_trashdir'])
        self.btn_trash = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizetrash.Add(self.btn_trash, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        sizerFiles.Add((0, 15))
        line0 = wx.StaticLine(tabTwo, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerFiles.Add(line0, 0, wx.ALL | wx.EXPAND, 5)
        sizerFiles.Add((0, 15))
        msg = _("Where do you prefer to save your downloads?")
        labdown = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFiles.Add(labdown, 0, wx.ALL | wx.EXPAND, 5)
        sizeYDLdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeYDLdirdest, 0, wx.EXPAND)
        self.txtctrl_YDLpath = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizeYDLdirdest.Add(self.txtctrl_YDLpath, 1, wx.ALL | wx.CENTER, 5)
        self.txtctrl_YDLpath.AppendText(self.appdata['dirdownload'])
        self.btn_YDLpath = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        descr = _("Auto-create subfolders when downloading playlists")
        self.ckbx_playlist = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_playlist, 0, wx.ALL, 5)
        tabTwo.SetSizer(sizerFiles)
        notebook.AddPage(tabTwo, _("File Preferences"))

        # -----tab 3
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerFFmpeg = wx.BoxSizer(wx.VERTICAL)
        sizerFFmpeg.Add((0, 15))
        labFFexec = wx.StaticText(tabThree, wx.ID_ANY,
                                  _('Path to the executables'))
        sizerFFmpeg.Add(labFFexec, 0, wx.ALL | wx.EXPAND, 5)
        # ----
        msg = _("Enable another location to run FFmpeg")
        self.checkbox_exeFFmpeg = wx.CheckBox(tabThree, wx.ID_ANY, (msg))
        self.btn_ffmpeg = wx.Button(tabThree, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_ffmpeg = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizerFFmpeg.Add(self.checkbox_exeFFmpeg, 0, wx.ALL, 5)
        gridFFmpeg = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFmpeg, 0, wx.EXPAND)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALL, 5)
        gridFFmpeg.Add(self.btn_ffmpeg, 0, wx.RIGHT | wx.CENTER, 5)
        # ----
        sizerFFmpeg.Add((0, 15))
        msg = _("Enable another location to run FFprobe")
        self.checkbox_exeFFprobe = wx.CheckBox(tabThree, wx.ID_ANY, (msg))
        self.btn_ffprobe = wx.Button(tabThree, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_ffprobe = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizerFFmpeg.Add(self.checkbox_exeFFprobe, 0, wx.ALL, 5)
        gridFFprobe = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFprobe, 0, wx.EXPAND)
        gridFFprobe.Add(self.txtctrl_ffprobe, 1, wx.ALL, 5)
        gridFFprobe.Add(self.btn_ffprobe, 0, wx.RIGHT | wx.CENTER, 5)
        # ----
        sizerFFmpeg.Add((0, 15))
        msg = _("Enable another location to run FFplay")
        self.checkbox_exeFFplay = wx.CheckBox(tabThree, wx.ID_ANY, (msg))
        self.btn_ffplay = wx.Button(tabThree, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_ffplay = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizerFFmpeg.Add(self.checkbox_exeFFplay, 0, wx.ALL, 5)
        gridFFplay = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFplay, 0, wx.EXPAND)
        gridFFplay.Add(self.txtctrl_ffplay, 1, wx.ALL, 5)
        gridFFplay.Add(self.btn_ffplay, 0, wx.RIGHT | wx.CENTER, 5)
        sizerFFmpeg.Add((0, 15))
        labFFopt = wx.StaticText(tabThree, wx.ID_ANY, _('Other options'))
        sizerFFmpeg.Add(labFFopt, 0, wx.ALL | wx.EXPAND, 5)
        gridSizopt = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridSizopt, 0, wx.EXPAND)
        msg = _("Threads used for transcoding (from 0 to 32):")
        labFFthreads = wx.StaticText(tabThree, wx.ID_ANY, (msg))
        gridSizopt.Add(labFFthreads, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        self.spinctrl_threads = wx.SpinCtrl(tabThree, wx.ID_ANY,
                                            f"{self.appdata['ffthreads'][9:]}",
                                            size=(-1, -1), min=0, max=32,
                                            style=wx.TE_PROCESS_ENTER
                                            )
        gridSizopt.Add(self.spinctrl_threads, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        # ----
        tabThree.SetSizer(sizerFFmpeg)
        notebook.AddPage(tabThree, _("FFmpeg"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizerytdlp = wx.BoxSizer(wx.VERTICAL)
        sizerytdlp.Add((0, 30))
        msg = _('Download videos from YouTube.com and other video sites')
        labytdlp = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizerytdlp.Add(labytdlp, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("Enable/Disable yt-dlp")
        self.checkbox_ytdlp = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerytdlp.Add(self.checkbox_ytdlp, 0, wx.ALL, 5)
        sizerytdlp.Add((0, 15))
        labdw = wx.StaticText(tabFour, wx.ID_ANY,
                              _('External Downloader Preferences'))
        sizerytdlp.Add(labdw, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("In addition to the default (native) one, yt-dlp currently\n"
                "supports the following external downloaders:\n"
                "aria2c, avconv, axel, curl, ffmpeg, httpie, wget.\n"
                "Please note that if you enable an external downloader, you\n"
                "will not be able to view the progress bar during download\n"
                "operations.")
        labdwmsg = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        sizerytdlp.Add(labdwmsg, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        msg = _("External downloader executable path")
        labextdw = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizerytdlp.Add(labextdw, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        exedw = str(self.appdata["external_downloader"])
        self.txtctrl_extdw = wx.TextCtrl(tabFour, wx.ID_ANY, exedw)
        sizerytdlp.Add(self.txtctrl_extdw, 0, wx.EXPAND | wx.LEFT | wx.RIGHT
                       | wx.BOTTOM, 5)
        labextdwargs = wx.StaticText(tabFour, wx.ID_ANY,
                                     _("External downloader arguments"))
        sizerytdlp.Add(labextdwargs, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        val = self.appdata["external_downloader_args"]
        args = " ".join(val) if isinstance(val, list) else 'None'
        self.txtctrl_extdw_args = wx.TextCtrl(tabFour, wx.ID_ANY, args)
        sizerytdlp.Add(self.txtctrl_extdw_args, 0, wx.EXPAND | wx.LEFT
                       | wx.RIGHT | wx.BOTTOM, 5)
        # ----
        tabFour.SetSizer(sizerytdlp)
        notebook.AddPage(tabFour, "yt-dlp")

        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        sizerAppearance = wx.BoxSizer(wx.VERTICAL)
        sizerAppearance.Add((0, 15))
        labTheme = wx.StaticText(tabFive, wx.ID_ANY, _('Icon themes'))
        sizerAppearance.Add(labTheme, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("The chosen icon theme will only change the icons,\n"
                "background and foreground of some text fields.")
        labIcons = wx.StaticText(tabFive, wx.ID_ANY, (msg))
        sizerAppearance.Add(labIcons, 0, wx.ALL
                            | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.cmbx_icons = wx.ComboBox(tabFive, wx.ID_ANY,
                                      choices=[("Videomass-Light"),
                                               ("Videomass-Dark"),
                                               ("Videomass-Colours"),
                                               ("Ubuntu-Light-Aubergine"),
                                               ("Ubuntu-Dark-Aubergine"),
                                               ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        sizerAppearance.Add(self.cmbx_icons, 0,
                            wx.ALL
                            | wx.ALIGN_CENTER_HORIZONTAL, 5
                            )
        sizerAppearance.Add((0, 15))
        labTB = wx.StaticText(tabFive, wx.ID_ANY, _("Toolbar customization"))
        sizerAppearance.Add(labTB, 0, wx.ALL | wx.EXPAND, 5)
        tbchoice = [_('At the top of window (default)'),
                    _('At the bottom of window'),
                    _('At the right of window'),
                    _('At the left of window')]
        self.rdbTBpref = wx.RadioBox(tabFive, wx.ID_ANY,
                                     (_("Place the toolbar")),
                                     choices=tbchoice,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS
                                     )
        sizerAppearance.Add(self.rdbTBpref, 0, wx.ALL | wx.EXPAND, 5)

        gridTBsize = wx.FlexGridSizer(0, 2, 0, 5)
        sizerAppearance.Add(gridTBsize, 0, wx.ALL, 5)
        lab1_appearance = wx.StaticText(tabFive, wx.ID_ANY,
                                        _('Icon size:'))
        gridTBsize.Add(lab1_appearance, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmbx_iconsSize = wx.ComboBox(tabFive, wx.ID_ANY,
                                          choices=[("16"), ("24"), ("32"),
                                                   ("64")], size=(120, -1),
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY
                                          )
        gridTBsize.Add(self.cmbx_iconsSize, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        if 'wx.svg' not in sys.modules:  # only in wx version 4.1 to up
            self.cmbx_iconsSize.Disable()
            lab1_appearance.Disable()
        msg = _("Show text next to toolbar buttons")
        self.checkbox_tbtext = wx.CheckBox(tabFive, wx.ID_ANY, (msg))
        sizerAppearance.Add(self.checkbox_tbtext, 0, wx.ALL, 5)

        tabFive.SetSizer(sizerAppearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tabFive, _("Appearance"))

        # -----tab 6
        tabSix = wx.Panel(notebook, wx.ID_ANY)
        sizerLog = wx.BoxSizer(wx.VERTICAL)
        sizerLog.Add((0, 15))

        msglog = _("The following settings affect output messages and\n"
                   "the log messages during transcoding processes.\n"
                   "Change only if you know what you are doing.\n")
        labLog = wx.StaticText(tabSix, wx.ID_ANY, (msglog))
        sizerLog.Add(labLog, 0, wx.ALL | wx.CENTRE, 5)
        msg = "Set logging level flags used by FFmpeg"
        self.rdbFFmpeg = wx.RadioBox(tabSix, wx.ID_ANY, (msg),
                                     choices=SetUp.FFMPEG_LOGLEV,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS,
                                     )
        sizerLog.Add(self.rdbFFmpeg, 0, wx.ALL | wx.EXPAND, 5)
        msg = "Set logging level flags used by FFplay"
        self.rdbFFplay = wx.RadioBox(tabSix, wx.ID_ANY, (msg),
                                     choices=SetUp.FFPLAY_LOGLEV,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS,
                                     )
        sizerLog.Add(self.rdbFFplay, 0, wx.ALL | wx.EXPAND, 5)

        tabSix.SetSizer(sizerLog)
        notebook.AddPage(tabSix, _("FFmpeg logging levels"))
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
        sizer_base.Add(grdBtn, 0, wx.EXPAND)
        # ------ set sizer
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------#
        self.SetTitle(_("Settings"))
        # set font
        if self.appdata['ostype'] == 'Darwin':
            lablang.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labconf.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablog.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labcache.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labfile.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFopt.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labytdlp.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdw.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdwmsg.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTheme.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lablang.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labconf.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablog.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labcache.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labfile.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFopt.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labytdlp.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdw.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdwmsg.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTheme.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        #  tooltips
        tip = (_("By assigning an additional suffix you could avoid "
                 "overwriting files"))
        self.text_suffix.SetToolTip(tip)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_set_lang, self.cmbx_lang)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_conf)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_log)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_cache)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffplay, self.rdbFFplay)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbFFmpeg)
        self.Bind(wx.EVT_SPINCTRL, self.on_threads, self.spinctrl_threads)
        self.Bind(wx.EVT_BUTTON, self.on_outputfile, self.btn_fsave)
        self.Bind(wx.EVT_CHECKBOX, self.set_Samedest, self.ckbx_dir)
        self.Bind(wx.EVT_TEXT, self.set_Suffix, self.text_suffix)
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_BUTTON, self.on_browse_trash, self.btn_trash)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_ffprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.checkbox_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_ffplay)
        self.Bind(wx.EVT_BUTTON, self.on_downloadfile, self.btn_YDLpath)
        self.Bind(wx.EVT_CHECKBOX, self.on_playlistFolder, self.ckbx_playlist)
        self.Bind(wx.EVT_CHECKBOX, self.on_ytdlp_pref, self.checkbox_ytdlp)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)
        self.Bind(wx.EVT_RADIOBOX, self.on_toolbarPos, self.rdbTBpref)
        self.Bind(wx.EVT_COMBOBOX, self.on_toolbarSize, self.cmbx_iconsSize)
        self.Bind(wx.EVT_CHECKBOX, self.on_toolbarText, self.checkbox_tbtext)
        self.Bind(wx.EVT_CHECKBOX, self.exit_warn, self.checkbox_exit)
        self.Bind(wx.EVT_CHECKBOX, self.clear_Cache, self.checkbox_cacheclr)
        self.Bind(wx.EVT_CHECKBOX, self.clear_logs, self.checkbox_logclr)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_TEXT, self.on_ext_downl, self.txtctrl_extdw)
        self.Bind(wx.EVT_TEXT, self.on_ext_downl_args, self.txtctrl_extdw_args)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file
        """
        if self.appdata['locale_name'] in supLang:
            lang = supLang[self.appdata['locale_name']][1]
        else:
            lang = supLang["en_US"][1]
        self.cmbx_lang.SetValue(lang)
        self.cmbx_icons.SetValue(self.appdata['icontheme'][0])
        self.cmbx_iconsSize.SetValue(str(self.appdata['toolbarsize']))
        self.rdbTBpref.SetSelection(self.appdata['toolbarpos'])

        self.checkbox_cacheclr.SetValue(self.appdata['clearcache'])
        self.checkbox_tbtext.SetValue(self.appdata['toolbartext'])
        self.checkbox_exit.SetValue(self.appdata['warnexiting'])
        self.checkbox_logclr.SetValue(self.appdata['clearlogfiles'])
        self.ckbx_trash.SetValue(self.settings['move_file_to_trash'])
        self.ckbx_playlist.SetValue(self.appdata['playlistsubfolder'])
        self.checkbox_ytdlp.SetValue(self.settings['use-downloader'])

        if not self.settings['move_file_to_trash']:
            self.txtctrl_trash.Disable()
            self.btn_trash.Disable()

        for strs in range(self.rdbFFplay.GetCount()):
            if (self.appdata['ffplayloglev'].split()[1] in
               self.rdbFFplay.GetString(strs).split()[0]):
                self.rdbFFplay.SetSelection(strs)

        for strs in range(self.rdbFFmpeg.GetCount()):
            if (self.appdata['ffmpegloglev'].split()[1] in
               self.rdbFFmpeg.GetString(strs).split()[0]):
                self.rdbFFmpeg.SetSelection(strs)

        if not self.appdata['ffmpeg_islocal']:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(True)

        if not self.appdata['ffprobe_islocal']:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(True)

        if not self.appdata['ffplay_islocal']:
            self.btn_ffplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.checkbox_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.checkbox_exeFFplay.SetValue(True)

        if not self.appdata['outputfile_samedir']:
            self.lab_suffix.Disable()
            self.text_suffix.Disable()
            self.ckbx_dir.SetValue(False)
        else:
            self.lab_suffix.Enable()
            self.text_suffix.Enable()
            self.ckbx_dir.SetValue(True)
            self.btn_fsave.Disable()
            self.txtctrl_FFpath.Disable()
            if not self.appdata['filesuffix'] == "":
                self.text_suffix.AppendText(self.appdata['filesuffix'])
    # --------------------------------------------------------------------#

    def opendir(self, event):
        """
        Open the configuration folder with file manager
        """
        name = event.GetEventObject().GetName()
        if name == 'config dir':
            io_tools.openpath(self.appdata['confdir'])
        elif name == 'log dir':
            io_tools.openpath(self.appdata['logdir'])
        elif name == 'cache dir':
            io_tools.openpath(self.appdata['cachedir'])
    # -------------------------------------------------------------------#

    def on_set_lang(self, event):
        """set application language"""

        for key, val in supLang.items():
            if val[1] == self.cmbx_lang.GetValue():
                lang = key
        self.settings['locale_name'] = lang
    # --------------------------------------------------------------------#

    def on_playlistFolder(self, event):
        """auto-create subfolders when downloading playlists"""
        if self.ckbx_playlist.IsChecked():
            self.settings['playlistsubfolder'] = True
        else:
            self.settings['playlistsubfolder'] = False
    # ---------------------------------------------------------------------#

    def on_threads(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_threads.GetValue()
        self.settings['ffthreads'] = f'-threads {sett}'
    # ---------------------------------------------------------------------#

    def on_outputfile(self, event):
        """set up a custom user path for file exporting"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save "
                                   "exported files"),
                           self.appdata['outputfile'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_FFpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_FFpath.AppendText(getpath)
            self.settings['outputfile'] = getpath
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def set_Samedest(self, event):
        """Save the FFmpeg output files in the same source folder"""
        if self.ckbx_dir.IsChecked():
            self.lab_suffix.Enable()
            self.text_suffix.Enable()
            self.btn_fsave.Disable()
            self.txtctrl_FFpath.Disable()
            self.settings['outputfile_samedir'] = True
        else:
            self.text_suffix.Clear()
            self.lab_suffix.Disable()
            self.text_suffix.Disable()
            self.btn_fsave.Enable()
            self.txtctrl_FFpath.Enable()
            self.settings['outputfile_samedir'] = False
            self.settings['filesuffix'] = ""
    # --------------------------------------------------------------------#

    def set_Suffix(self, event):
        """Set a custom suffix to append at the output file names"""
        msg = _('Enter only alphanumeric characters. You can also use the '
                'hyphen ("-") and the underscore ("_"). Spaces are '
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
                        self.settings['filesuffix'] = ""
                        return

            self.settings['filesuffix'] = suffix
        else:
            self.settings['filesuffix'] = ""
    # --------------------------------------------------------------------#

    def on_file_to_trash(self, event):
        """
        enable/disable "Move file to trash" after successful encoding
        """
        if self.ckbx_trash.IsChecked():
            self.settings['move_file_to_trash'] = True
            self.settings['user_trashdir'] = self.appdata['conf_trashdir']
            self.txtctrl_trash.Enable()
            self.btn_trash.Enable()
            if not os.path.exists(self.appdata['conf_trashdir']):
                os.mkdir(self.appdata['conf_trashdir'], mode=0o777)
        else:
            self.txtctrl_trash.Clear()
            self.txtctrl_trash.AppendText(self.appdata['conf_trashdir'])
            self.txtctrl_trash.Disable()
            self.btn_trash.Disable()
            self.settings['move_file_to_trash'] = False
            self.settings['user_trashdir'] = self.appdata['conf_trashdir']
    # --------------------------------------------------------------------#

    def on_browse_trash(self, event):
        """
        Browse to set a trash folder.
        """
        dlg = wx.DirDialog(self, _("Choose a new destination for the "
                                   "files to be trashed"),
                           self.appdata['user_trashdir'], wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_trash.Clear()
            newtrash = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_trash.AppendText(newtrash)
            self.settings['user_trashdir'] = newtrash
            if not os.path.exists(newtrash):
                os.makedirs(newtrash, mode=0o777)
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def on_downloadfile(self, event):
        """set up a custom user path for file downloads"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save the "
                                   "file downloads"),
                           self.appdata['dirdownload'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_YDLpath.AppendText(getpath)
            self.settings['dirdownload'] = getpath
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_ext_downl(self, event):
        """
        Event on entering executable path of external downloader
        """
        val = str(self.txtctrl_extdw.GetValue()).strip()
        downloader = None if val in ("", "None", "none") else val
        self.settings["external_downloader"] = downloader
    # -------------------------------------------------------------------#

    def on_ext_downl_args(self, event):
        """
        Event on entering arguments for external downloader
        """
        val = str(self.txtctrl_extdw_args.GetValue()).strip()
        args = None if val in ("", "None", "none") else val.split()
        self.settings["external_downloader_args"] = args
    # -------------------------------------------------------------------#

    def logging_ffplay(self, event):
        """specifies loglevel type for ffplay."""
        strn = self.rdbFFplay.GetStringSelection().split()[0]
        self.settings['ffplayloglev'] = f'-loglevel {strn}'
    # --------------------------------------------------------------------#

    def logging_ffmpeg(self, event):
        """specifies loglevel type for ffmpeg"""
        strn = self.rdbFFmpeg.GetStringSelection().split()[0]
        self.settings['ffmpegloglev'] = f'-loglevel {strn}'
    # --------------------------------------------------------------------#

    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg local binary"""
        if self.checkbox_exeFFmpeg.IsChecked():
            self.btn_ffmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.settings['ffmpeg_islocal'] = True
        else:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.settings['ffmpeg_islocal'] = False

            status = detect_binaries(self.ffmpeg,
                                     self.appdata['FFMPEG_videomass_pkg']
                                     )
            if status[0] == 'not installed':
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write(status[0])
                self.settings['ffmpeg_cmd'] = ''
            else:
                self.txtctrl_ffmpeg.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffmpeg.write(getpath)
                self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffmpeg), "", "",
                           f"ffmpeg binary (*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffmpeg:
                    self.txtctrl_ffmpeg.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffmpeg.write(getpath)
                    self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exeFFprobe(self, event):
        """Enable or disable ffprobe local binary"""
        if self.checkbox_exeFFprobe.IsChecked():
            self.btn_ffprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.settings['ffprobe_islocal'] = True

        else:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.settings['ffprobe_islocal'] = False

            status = detect_binaries(self.ffprobe,
                                     self.appdata['FFMPEG_videomass_pkg']
                                     )
            if status[0] == 'not installed':
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write(status[0])
                self.settings['ffprobe_cmd'] = ''
            else:
                self.txtctrl_ffprobe.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffprobe.write(getpath)
                self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffprobe), "", "",
                           f"ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffprobe:
                    self.txtctrl_ffprobe.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffprobe.write(getpath)
                    self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exeFFplay(self, event):
        """Enable or disable ffplay local binary"""
        if self.checkbox_exeFFplay.IsChecked():
            self.btn_ffplay.Enable()
            self.txtctrl_ffplay.Enable()
            self.settings['ffplay_islocal'] = True

        else:
            self.btn_ffplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.settings['ffplay_islocal'] = False

            status = detect_binaries(self.ffplay,
                                     self.appdata['FFMPEG_videomass_pkg']
                                     )
            if status[0] == 'not installed':
                self.txtctrl_ffplay.Clear()
                self.txtctrl_ffplay.write(status[0])
                self.settings['ffplay_cmd'] = ''
            else:
                self.txtctrl_ffplay.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffplay.write(getpath)
                self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffplay(self, event):
        """Indicates a new ffplay path-name"""
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffplay), "", "",
                           f"ffplay binary "
                           f"(*{self.ffplay})|*{self.ffplay}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffplay:
                    self.txtctrl_ffplay.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffplay.write(getpath)
                    self.settings['ffplay_cmd'] = getpath
    # ---------------------------------------------------------------------#

    def on_ytdlp_pref(self, event):
        """
        set yt-dlp preferences
        """
        if self.checkbox_ytdlp.GetValue():
            self.settings['use-downloader'] = True
        else:
            self.settings['use-downloader'] = False
    # --------------------------------------------------------------------#

    def on_Iconthemes(self, event):
        """
        Set themes of icons
        """
        self.settings['icontheme'] = self.cmbx_icons.GetStringSelection()
    # --------------------------------------------------------------------#

    def on_toolbarSize(self, event):
        """
        Set the size of the toolbar buttons and the size of its icons
        """
        size = self.cmbx_iconsSize.GetStringSelection()
        self.settings['toolbarsize'] = size
    # --------------------------------------------------------------------#

    def on_toolbarPos(self, event):
        """
        Set toolbar position on main frame
        """
        self.settings['toolbarpos'] = self.rdbTBpref.GetSelection()
    # --------------------------------------------------------------------#

    def on_toolbarText(self, event):
        """
        Show or hide text along toolbar buttons
        """
        if self.checkbox_tbtext.IsChecked():
            self.settings['toolbartext'] = True
        else:
            self.settings['toolbartext'] = False
    # --------------------------------------------------------------------#

    def exit_warn(self, event):
        """
        Enable or disable the warning message before
        exiting the program
        """
        if self.checkbox_exit.IsChecked():
            self.settings['warnexiting'] = True
        else:
            self.settings['warnexiting'] = False
    # --------------------------------------------------------------------#

    def clear_Cache(self, event):
        """
        if checked, set to clear cached data on exit
        """
        if self.checkbox_cacheclr.IsChecked():
            self.settings['clearcache'] = True
        else:
            self.settings['clearcache'] = False
    # --------------------------------------------------------------------#

    def clear_logs(self, event):
        """
        if checked, set to clear all log files on exit
        """
        if self.checkbox_logclr.IsChecked():
            self.settings['clearlogfiles'] = True
        else:
            self.settings['clearlogfiles'] = False
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if self.appdata['GETLANG'] in self.appdata['SUPP_LANGs']:
            lang = self.appdata['GETLANG'].split('_')[0]
            page = (f'https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    f'languages/{lang}/2-Startup_and_Setup_{lang}.pdf')
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/2-Startup_and_Setup_en.pdf')

        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Writes the new changes to configuration file aka `settings.json`
        """
        self.confmanager.write_options(**self.settings)
        event.Skip()
