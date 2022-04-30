# -*- coding: UTF-8 -*-
"""
Name: preferences.py
Porpose: videomass setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.12.2022
Code checker: pylint, flake8
########################################################

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
import shutil
import sys
import webbrowser
import wx
import wx.lib.agw.hyperlink as hpl
from videomass.vdms_utils.utils import detect_binaries
from videomass.vdms_sys.settings_manager import ConfigManager


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
                     ("verbose (Same as `info`, except more verbose.)"),
                     ("debug (Show everything, including debugging info.)")
                     ]
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) settings already loaded from main_frame .
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
        """constructor"""
        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGen = wx.BoxSizer(wx.VERTICAL)
        sizerGen.Add((0, 15))
        self.checkbox_cacheclr = wx.CheckBox(tabOne, wx.ID_ANY, (
                        _("Clear the cache when exiting the application")))
        sizerGen.Add(self.checkbox_cacheclr, 0, wx.ALL, 5)
        sizerGen.Add((0, 15))
        self.checkbox_logclr = wx.CheckBox(tabOne, wx.ID_ANY, (
                        _("Delete the contents of the log files "
                          "when exiting the application")))
        sizerGen.Add(self.checkbox_logclr, 0, wx.ALL, 5)
        sizerGen.Add((0, 15))
        self.checkbox_exit = wx.CheckBox(tabOne, wx.ID_ANY, (
                                         _("Warn on exit")))
        sizerGen.Add(self.checkbox_exit, 0, wx.ALL, 5)

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
        sizeFFdirdest.Add(self.btn_fsave, 0, wx.RIGHT |
                          wx.ALIGN_CENTER_VERTICAL |
                          wx.ALIGN_CENTER_HORIZONTAL, 5
                          )
        descr = _("Save each file in the same folder as input file")
        self.ckbx_dir = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_dir, 0, wx.ALL, 5)
        sizeSamedest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeSamedest, 0, wx.EXPAND)
        descr = _("Assign optional suffix to output file names:")
        self.lab_suffix = wx.StaticText(tabTwo, wx.ID_ANY, (descr))
        sizeSamedest.Add(self.lab_suffix, 0, wx.LEFT |
                         wx.ALIGN_CENTER_VERTICAL, 5)
        self.text_suffix = wx.TextCtrl(tabTwo, wx.ID_ANY, "", size=(90, -1))
        sizeSamedest.Add(self.text_suffix, 1, wx.ALL | wx.CENTER, 5)

        descr = _("Move source file to the Videomass trash "
                  "folder after successful encoding")
        self.ckbx_trash = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_trash, 0, wx.ALL, 5)
        sizetrash = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizetrash, 0, wx.EXPAND)
        self.txtctrl_trash = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                         style=wx.TE_READONLY
                                         )
        sizetrash.Add(self.txtctrl_trash, 1, wx.ALL, 5)
        self.txtctrl_trash.AppendText(self.appdata['trashfolder'])
        self.btn_trash = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizetrash.Add(self.btn_trash, 0, wx.RIGHT |
                      wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
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
        self.txtctrl_YDLpath.AppendText(self.appdata['outputdownload'])
        self.btn_YDLpath = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.RIGHT |
                           wx.ALIGN_CENTER_VERTICAL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
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
        self.checkbox_exeFFmpeg = wx.CheckBox(tabThree, wx.ID_ANY, (
                                _("Enable another location to run FFmpeg")))
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
        self.checkbox_exeFFprobe = wx.CheckBox(tabThree, wx.ID_ANY, (
                                _("Enable another location to run FFprobe")))
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
        self.checkbox_exeFFplay = wx.CheckBox(tabThree, wx.ID_ANY, (
                                  _("Enable another location to run FFplay")))
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

        labFFthreads = wx.StaticText(tabThree, wx.ID_ANY,
                                     (_("Threads used for transcoding "
                                        "(from 0 to 32):")))
        gridSizopt.Add(labFFthreads, 0,
                       wx.LEFT |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        self.spinctrl_threads = wx.SpinCtrl(tabThree, wx.ID_ANY, "%s" %
                                            self.appdata['ffthreads'][9:],
                                            size=(-1, -1), min=0, max=32,
                                            style=wx.TE_PROCESS_ENTER
                                            )
        gridSizopt.Add(self.spinctrl_threads, 1, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        # ----
        tabThree.SetSizer(sizerFFmpeg)
        notebook.AddPage(tabThree, _("FFmpeg"))

        # -----tab 4
        self.tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizerYdl = wx.BoxSizer(wx.VERTICAL)
        sizerYdl.Add((0, 15))
        labydl0 = wx.StaticText(self.tabFour, wx.ID_ANY, (''))
        sizerYdl.Add(labydl0, 0, wx.ALL | wx.CENTRE, 5)

        if self.appdata['app'] not in ('pyinstaller', 'appimage', 'embed'):
            url = ('https://packaging.python.org/tutorials/'
                   'installing-packages/#upgrading-packages')
            static0 = _("How to upgrade a Python package")
            instpkg = hpl.HyperLinkCtrl(self.tabFour, -1, static0, URL=url)
            sizerYdl.Add(instpkg, 0, wx.ALL | wx.CENTRE, 2)

        if self.appdata['ostype'] == 'Windows':
            url = ('https://download.microsoft.com/download/1/6/5/165255E7-'
                   '1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe')
            static1 = _("Required: Microsoft Visual C++ 2010 Service Pack 1 "
                        "Redistributable Package (x86)")
            MSVCR = hpl.HyperLinkCtrl(self.tabFour, -1, static1, URL=url)
            sizerYdl.Add(MSVCR, 0, wx.ALL | wx.CENTRE, 2)

        elif (self.appdata['ostype'] == 'Linux' and
              self.appdata['app'] not in ('pyinstaller', 'appimage')):
            url = ('https://packaging.python.org/guides/'
                   'installing-using-linux-tools/')
            static2 = _("How to install pip on your Linux distribution")
            instpip = hpl.HyperLinkCtrl(self.tabFour, -1, static2, URL=url)
            sizerYdl.Add(instpip, 0, wx.ALL | wx.CENTRE, 2)
        sizerYdl.Add((0, 15))

        self.rdbDownloader = wx.RadioBox(self.tabFour, wx.ID_ANY,
                                         (_("Downloader preferences")),
                                         choices=[('disabled'),
                                                  ('youtube_dl'),
                                                  ('yt_dlp')],
                                         majorDimension=1,
                                         style=wx.RA_SPECIFY_COLS
                                         )
        sizerYdl.Add(self.rdbDownloader, 0, wx.ALL | wx.EXPAND, 5)

        grdydlLoc = wx.BoxSizer(wx.HORIZONTAL)
        sizerYdl.Add(grdydlLoc, 0, wx.ALL | wx.EXPAND, 5)
        labydl2 = wx.StaticText(self.tabFour, wx.ID_ANY, _('Current path:'))
        grdydlLoc.Add(labydl2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)

        self.ydlPath = wx.TextCtrl(self.tabFour, wx.ID_ANY, "",
                                   style=wx.TE_READONLY)
        grdydlLoc.Add(self.ydlPath, 1, wx.ALL | wx.EXPAND, 5)

        # ---- BEGIN set youtube-dl radiobox
        ydlmsg = _("Make sure you are using the latest available "
                   "version of\n'{}'. This allows you to avoid download "
                   "problems.\n").format(self.appdata['downloader'])

        if self.appdata['app'] == 'pyinstaller':

            if self.appdata['downloader'] == 'disabled':
                self.rdbDownloader.SetSelection(0)
                self.ydlPath.WriteText(_('Disabled'))
            else:
                if self.appdata['downloader'] == 'youtube_dl':
                    self.rdbDownloader.SetSelection(1)

                elif self.appdata['downloader'] == 'yt_dlp':
                    self.rdbDownloader.SetSelection(2)

                if self.appdata['PYLIBYDL'] is None:
                    self.ydlPath.WriteText(str(self.appdata['YDLSITE']))
                else:
                    self.ydlPath.WriteText(_('Not found'))

        elif self.appdata['app'] == 'appimage':

            tip1 = _('Menu bar > Tools > Update {}'
                     ).format(self.appdata['downloader'])

            if self.appdata['downloader'] == 'disabled':
                self.rdbDownloader.SetSelection(0)
                self.ydlPath.WriteText(_('Disabled'))
            else:
                if self.appdata['downloader'] == 'youtube_dl':
                    self.rdbDownloader.SetSelection(1)

                elif self.appdata['downloader'] == 'yt_dlp':
                    self.rdbDownloader.SetSelection(2)

                if self.appdata['PYLIBYDL'] is None:
                    labydl0.SetLabel('%s%s' % (ydlmsg, tip1))
                    self.ydlPath.WriteText(str(self.appdata['YDLSITE']))
                else:
                    self.ydlPath.WriteText(_('Not Installed'))
        else:
            if self.appdata['downloader'] == 'disabled':
                self.rdbDownloader.SetSelection(0)
                self.ydlPath.WriteText(_('Disabled'))
            else:
                if self.appdata['downloader'] == 'youtube_dl':
                    self.rdbDownloader.SetSelection(1)

                elif self.appdata['downloader'] == 'yt_dlp':
                    self.rdbDownloader.SetSelection(2)

                if self.appdata['PYLIBYDL'] is None:
                    labydl0.SetLabel('%s' % (ydlmsg))
                    self.ydlPath.WriteText(str(self.appdata['YDLSITE']))
                else:
                    self.ydlPath.WriteText(_('Not Installed'))
        # ---- END

        # ----
        self.tabFour.SetSizer(sizerYdl)
        notebook.AddPage(self.tabFour, _("Downloader"))

        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        sizerAppearance = wx.BoxSizer(wx.VERTICAL)
        sizerAppearance.Add((0, 15))
        labTheme = wx.StaticText(tabFive, wx.ID_ANY, _('Icon themes'))
        sizerAppearance.Add(labTheme, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("The chosen icon theme will only change the icons,\n"
                "background and foreground of some text fields.")
        labIcons = wx.StaticText(tabFive, wx.ID_ANY, (msg))
        sizerAppearance.Add(labIcons, 0, wx.ALL |
                            wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.cmbx_icons = wx.ComboBox(tabFive, wx.ID_ANY,
                                      choices=[
                                          ("Videomass-Light"),
                                          ("Videomass-Dark"),
                                          ("Videomass-Colours"),
                                          ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        sizerAppearance.Add(self.cmbx_icons, 0,
                            wx.ALL |
                            wx.ALIGN_CENTER_HORIZONTAL, 5
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

        self.checkbox_tbtext = wx.CheckBox(tabFive, wx.ID_ANY, (
                                _("Shows the text in the toolbar buttons")))
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
        self.rdbFFmpeg = wx.RadioBox(
                                tabSix, wx.ID_ANY,
                                ("Set logging level flags used by FFmpeg"),
                                choices=SetUp.FFMPEG_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
                                     )
        sizerLog.Add(self.rdbFFmpeg, 0, wx.ALL | wx.EXPAND, 5)
        self.rdbFFplay = wx.RadioBox(
                                tabSix, wx.ID_ANY,
                                ("Set logging level flags used by FFplay"),
                                choices=SetUp.FFPLAY_LOGLEV, majorDimension=1,
                                style=wx.RA_SPECIFY_COLS
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
            labfile.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFopt.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labydl0.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTheme.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            labfile.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFopt.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labydl0.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTheme.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        #  tooltips
        tip = (_("By assigning an additional suffix you could avoid "
                 "overwriting files"))
        self.text_suffix.SetToolTip(tip)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffplay, self.rdbFFplay)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbFFmpeg)
        self.Bind(wx.EVT_SPINCTRL, self.on_threads, self.spinctrl_threads)
        self.Bind(wx.EVT_BUTTON, self.on_ffmpegPath, self.btn_fsave)
        self.Bind(wx.EVT_CHECKBOX, self.set_Samedest, self.ckbx_dir)
        self.Bind(wx.EVT_TEXT, self.set_Suffix, self.text_suffix)
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_BUTTON, self.on_browse_trash, self.btn_trash)
        self.Bind(wx.EVT_BUTTON, self.on_downloadPath, self.btn_YDLpath)
        self.Bind(wx.EVT_CHECKBOX, self.on_playlistFolder, self.ckbx_playlist)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_ffprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.checkbox_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_ffplay)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)

        self.Bind(wx.EVT_RADIOBOX, self.on_toolbarPos, self.rdbTBpref)
        self.Bind(wx.EVT_COMBOBOX, self.on_toolbarSize, self.cmbx_iconsSize)
        self.Bind(wx.EVT_CHECKBOX, self.on_toolbarText, self.checkbox_tbtext)
        self.Bind(wx.EVT_CHECKBOX, self.exit_warn, self.checkbox_exit)

        self.Bind(wx.EVT_CHECKBOX, self.clear_Cache, self.checkbox_cacheclr)
        self.Bind(wx.EVT_CHECKBOX, self.clear_logs, self.checkbox_logclr)
        self.Bind(wx.EVT_RADIOBOX, self.on_Ydl_preferences, self.rdbDownloader)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file
        """
        self.cmbx_icons.SetValue(self.appdata['icontheme'][0])
        self.cmbx_iconsSize.SetValue(str(self.appdata['toolbarsize']))
        self.rdbTBpref.SetSelection(self.appdata['toolbarpos'])

        self.checkbox_cacheclr.SetValue(self.appdata['clearcache'])
        self.checkbox_tbtext.SetValue(self.appdata['toolbartext'])
        self.checkbox_exit.SetValue(self.appdata['warnexiting'])
        self.checkbox_logclr.SetValue(self.appdata['clearlogfiles'])
        self.ckbx_playlist.SetValue(self.appdata['playlistsubfolder'])
        self.ckbx_trash.SetValue(self.settings['move_file_to_trash'])

        if self.ckbx_trash.IsChecked() is False:
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

        if self.appdata['ffmpeg_islocal'] is False:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(True)

        if self.appdata['ffprobe_islocal'] is False:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(True)

        if self.appdata['ffplay_islocal'] is False:
            self.btn_ffplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.checkbox_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.checkbox_exeFFplay.SetValue(True)

        if self.appdata['outputfile_samedir'] is False:
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

    def on_threads(self, event):
        """set cpu number threads used as option on ffmpeg"""
        sett = self.spinctrl_threads.GetValue()
        self.settings['ffthreads'] = f'-threads {sett}'
    # ---------------------------------------------------------------------#

    def on_downloadPath(self, event):
        """set up a custom user path for file downloads"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save the "
                                   "file downloads"),
                           self.appdata['outputdownload'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_YDLpath.AppendText(getpath)
            self.settings['outputdownload'] = getpath
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_playlistFolder(self, event):
        """auto-create subfolders when downloading playlists"""
        if self.ckbx_playlist.IsChecked():
            self.settings['playlistsubfolder'] = True
        else:
            self.settings['playlistsubfolder'] = False
    # ---------------------------------------------------------------------#

    def on_ffmpegPath(self, event):
        """set up a custom user path for file export"""

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
        trashdir = os.path.join(self.appdata['confdir'], 'Trash')
        if self.ckbx_trash.IsChecked():
            self.settings['move_file_to_trash'] = True
            self.settings['trashfolder'] = trashdir
            self.txtctrl_trash.AppendText(trashdir)
            self.txtctrl_trash.Enable()
            self.btn_trash.Enable()
            if not os.path.exists(trashdir):
                os.mkdir(trashdir, mode=0o777)
        else:
            if not os.listdir(self.settings['trashfolder']):
                os.rmdir(self.settings['trashfolder'])  # deleting if empty
            self.txtctrl_trash.Clear()
            self.txtctrl_trash.Disable()
            self.btn_trash.Disable()
            self.settings['move_file_to_trash'] = False
            self.settings['trashfolder'] = ""

    # --------------------------------------------------------------------#

    def on_browse_trash(self, event):
        """
        Browse to set a trash folder.
        """
        oldtrash = self.txtctrl_trash.GetValue()
        dlg = wx.DirDialog(self, _("Choose a new destination for the "
                                   "files to be trashed"),
                           self.appdata['trashfolder'], wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_trash.Clear()
            newtrash = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_trash.AppendText(newtrash)
            self.settings['trashfolder'] = newtrash
            if not os.path.exists(newtrash):
                os.makedirs(newtrash, mode=0o777)
            if os.path.exists(oldtrash):
                if not oldtrash == newtrash:
                    if not os.listdir(oldtrash):  # recheck if is empty
                        os.rmdir(oldtrash)  # deleting old trash folder

            dlg.Destroy()
    # --------------------------------------------------------------------#

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

    def on_Ydl_preferences(self, event):
        """
        set youtube-dl preferences
        """
        index = self.rdbDownloader.GetSelection()
        self.settings['downloader'] = self.rdbDownloader.GetString(index)
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if self.appdata['GETLANG'] in self.appdata['SUPP_LANGs']:
            lang = self.appdata['GETLANG'].split('_')[0]
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/%s/2-Startup_and_Setup_%s.pdf' % (lang, lang))
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/2-Startup_and_Setup_en.pdf')

        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def getvalue(self):
        """
        Retrives data from here before destroyng this dialog.
        See main_frame --> on_setup method
        """
        if wx.MessageBox(_("Changes will take effect once the program "
                           "has been restarted.\n\n"
                           "Do you want to exit the application now?"),
                         _('Exit'),
                         wx.ICON_QUESTION
                         | wx.YES_NO, self) == wx.YES:
            return True

        return None
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Applies all changes writing the new entries on
        `settings.json` file aka file configuration.
        """
        self.confmanager.write_options(**self.settings)

        event.Skip()
