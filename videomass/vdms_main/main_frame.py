# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.09.2022
Code checker: pylint, flake8 --ignore=F821,W503
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
import sys
from urllib.parse import urlparse
import webbrowser
import wx
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs import preferences
from videomass.vdms_dialogs import set_timestamp
from videomass.vdms_dialogs import infoprg
from videomass.vdms_dialogs import videomass_check_version
from videomass.vdms_frames import while_playing
from videomass.vdms_frames import ffmpeg_search
from videomass.vdms_dialogs.mediainfo import Mediainfo
from videomass.vdms_dialogs.showlogs import ShowLogs
from videomass.vdms_panels import timeline
from videomass.vdms_panels import choose_topic
from videomass.vdms_panels import filedrop
from videomass.vdms_panels import textdrop
from videomass.vdms_panels import youtubedl_ui
from videomass.vdms_panels import av_conversions
from videomass.vdms_panels import concatenate
from videomass.vdms_panels import video_to_sequence
from videomass.vdms_panels import sequence_to_video
from videomass.vdms_panels.long_processing_task import LogOut
from videomass.vdms_panels import presets_manager
from videomass.vdms_io import io_tools
from videomass.vdms_sys.msg_info import current_release
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.utils import copydir_recursively
if 'youtube_dl' in sys.modules:
    import youtube_dl
elif 'yt_dlp' in sys.modules:
    import yt_dlp


class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # colour rappresentetion in rgb
    AZURE_NEON = 158, 201, 232
    YELLOW_LMN = 255, 255, 0
    BLUE = 0, 7, 12
    # set widget colours with html rappresentation:
    ORANGE = '#f28924'
    YELLOW = '#bd9f00'
    LIMEGREEN = '#87A615'
    DARK_BROWN = '#262222'
    WHITE = '#fbf4f4'
    BLACK = '#060505'
    # AZURE = '#d9ffff'  # rgb form (wx.Colour(217,255,255))
    # RED = '#ea312d'
    # GREENOLIVE = '#6aaf23'
    # GREEN = '#268826'
    # -------------------------------------------------------------#

    def __init__(self):
        """
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.icons = get.iconset
        # -------------------------------#
        self.data_files = []  # list of items in list control
        self.data_url = None  # list of urls in text box
        self.outpath_ffmpeg = None  # path name for FFmpeg file destination
        self.same_destin = False  # same source FFmpeg output destination
        self.outpath_ydl = None  # path name for download file destination
        self.suffix = ''  # append a suffix to FFmpeg output file names
        self.file_src = None  # input files list
        self.filedropselected = None  # selected name on file drop
        self.time_seq = "-ss 00:00:00.000 -t 00:00:00.000"  # FFmpeg time seq.
        self.duration = []  # empty if not file imported
        self.topicname = None  # panel name shown
        self.checktimestamp = True  # show timestamp during playback
        self.autoexit = False  # set autoexit during ffplay playback
        # set fontconfig for timestamp
        if self.appdata['ostype'] == 'Darwin':
            tsfont = '/Library/Fonts/Arial.ttf'
        elif self.appdata['ostype'] == 'Windows':
            tsfont = 'C:\\Windows\\Fonts\\Arial.ttf'
        else:
            tsfont = 'Arial'
        # set command line for timestamp
        ptshms = r"%{pts\:hms}"
        self.cmdtimestamp = (
            f"drawtext=fontfile={tsfont}:text='{ptshms}':fontcolor=White:"
            f"shadowcolor=Black:shadowx=1:shadowy=1:fontsize=32:"
            f"box=1:boxcolor=DeepPink:x=(w-tw)/2:y=h-(2*lh)")

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        # ----------- panel toolbar buttons
        # self.btnpanel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # self.btnpanel.SetBackgroundColour(MainFrame.LIMEGREEN)

        # ---------- others panel instances:
        self.TimeLine = timeline.Timeline(self)
        self.ChooseTopic = choose_topic.Choose_Topic(self,
                                                     self.appdata['ostype'],
                                                     )
        self.ytDownloader = youtubedl_ui.Downloader(self)
        self.VconvPanel = av_conversions.AV_Conv(self,
                                                 self.appdata,
                                                 self.icons,
                                                 )
        self.fileDnDTarget = filedrop.FileDnD(self, self.icons['playback'])
        self.textDnDTarget = textdrop.TextDnD(self)
        self.ProcessPanel = LogOut(self)
        self.PrstsPanel = presets_manager.PrstPan(self,
                                                  self.appdata['srcpath'],
                                                  self.appdata['confdir'],
                                                  self.appdata['workdir'],
                                                  self.appdata['ostype'],
                                                  self.icons['profile_add'],
                                                  self.icons['profile_del'],
                                                  self.icons['profile_edit'],
                                                  self.icons['profile_copy'],
                                                  )
        self.ConcatDemuxer = concatenate.Conc_Demuxer(self,)
        self.toPictures = video_to_sequence.VideoToSequence(self, self.icons)
        self.toSlideshow = sequence_to_video.SequenceToVideo(self, self.icons)
        # hide panels
        self.TimeLine.Hide()
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ProcessPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        # Layout toolbar buttons:
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # grid_pan = wx.BoxSizer(wx.HORIZONTAL)
        # self.btnpanel.SetSizer(grid_pan)  # set panel
        # self.mainSizer.Add(self.btnpanel, 0, wx.EXPAND, 5)
        ####

        # Layout externals panels:
        self.mainSizer.Add(self.TimeLine, 0, wx.EXPAND)
        self.mainSizer.Add(self.ChooseTopic, 1, wx.EXPAND)
        self.mainSizer.Add(self.fileDnDTarget, 1, wx.EXPAND)
        self.mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND)
        self.mainSizer.Add(self.ytDownloader, 1, wx.EXPAND)
        self.mainSizer.Add(self.VconvPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.PrstsPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.ConcatDemuxer, 1, wx.EXPAND)
        self.mainSizer.Add(self.toPictures, 1, wx.EXPAND)
        self.mainSizer.Add(self.toSlideshow, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("Videomass")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['videomass'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((980, 640))
        # self.CentreOnScreen()  # se lo usi, usa CentreOnScreen anziche Centre
        self.SetSizer(self.mainSizer)
        self.Fit()

        # menu bar
        self.videomass_menu_bar()
        # tool bar main
        self.videomass_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'), None)
        # hide toolbar, buttons bar and disable some file menu items
        self.toolbar.Hide()
        # self.btnpanel.Hide()
        self.menu_items()

        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.fileDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.on_FFmpegfsave)
        self.textDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.on_Ytdlfsave)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, bcolor, fcolor=None):
        """
        set the status-bar with messages and color types
        bcolor: background, fcolor: foreground
        """
        if bcolor is None:
            self.sb.SetBackgroundColour(wx.NullColour)
            self.sb.SetForegroundColour(wx.NullColour)
        else:
            self.sb.SetBackgroundColour(bcolor)
            self.sb.SetForegroundColour(fcolor)
        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    # ------------------------------------------------------------------#

    def choosetopicRetrieve(self):
        """
        Retrieve to choose topic panel
        """
        self.topicname = None
        self.textDnDTarget.Hide()
        self.fileDnDTarget.Hide()
        self.TimeLine.Hide()
        if self.ytDownloader.IsShown():
            self.ytDownloader.Hide()

        elif self.VconvPanel.IsShown():
            self.VconvPanel.Hide()

        elif self.PrstsPanel.IsShown():
            self.PrstsPanel.Hide()

        elif self.ConcatDemuxer.IsShown():
            self.ConcatDemuxer.Hide()

        elif self.toPictures.IsShown():
            self.toPictures.Hide()

        elif self.toSlideshow.IsShown():
            self.toSlideshow.Hide()

        self.ChooseTopic.Show()
        self.openmedia.Enable(False)
        self.toolbar.Hide()
        self.avpan.Enable(False)
        self.prstpan.Enable(False)
        self.concpan.Enable(False)
        self.ydlpan.Enable(False)
        self.startpan.Enable(False)
        self.logpan.Enable(False)
        self.viewtimeline.Enable(False)
        self.toseq.Enable(False)
        self.slides.Enable(False)
        self.SetTitle(_('Videomass'))
        self.statusbar_msg(_('Ready'), None)
        self.Layout()
    # ------------------------------------------------------------------#

    def menu_items(self):
        """
        enable or disable some menu items in according by showing panels
        """
        if self.ChooseTopic.IsShown() is True:
            self.avpan.Enable(False)
            self.prstpan.Enable(False)
            self.concpan.Enable(False)
            self.toseq.Enable(False)
            self.slides.Enable(False)
            self.ydlpan.Enable(False),
            self.startpan.Enable(False)
            self.viewtimeline.Enable(False)
            self.logpan.Enable(False)

        if self.appdata['downloader'] != 'disabled':
            if self.appdata['PYLIBYDL'] is not None:  # no module
                self.ydlused.Enable(False)
                self.ydlupdate.Enable(False)
                self.ydllatest.Enable(False)
            else:
                if self.appdata['app'] != 'appimage':
                    self.ydlupdate.Enable(False)  # can update ydl
    # ------------------------------------------------------------------#

    def reset_Timeline(self):
        """
        By adding or deleting files on file drop panel, cause reset
        the timeline data (only if `self.time_seq` attribute is setted)
        """
        if self.time_seq != "-ss 00:00:00.000 -t 00:00:00.000":
            self.TimeLine.resetValues()

    # ---------------------- Event handler (callback) ------------------#

    def ImportInfo(self, event):
        """
        Redirect input files at stream_info for media information
        """
        if self.topicname == 'Youtube Downloader':
            if not self.data_url:
                return
            self.ytDownloader.on_show_statistics()

        elif not self.data_files:
            return

        else:
            miniframe = Mediainfo(self.data_files, self.appdata['ostype'])
            miniframe.Show()
    # ------------------------------------------------------------------#

    def Saveprofile(self, event):
        """
        Store new profile with same current settings of the panel shown
        (A/V Conversions). Every modification on the panel shown will be
        reported when saving a new profile.
        """
        if self.VconvPanel.IsShown():
            self.VconvPanel.Addprof()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        switch to panels or destroy the videomass app.

        """
        def _setsize():
            """
            Write last panel size for next start if changed
            """
            if tuple(self.appdata['panel_size']) != self.GetSize():
                confmanager = ConfigManager(self.appdata['fileconfpath'])
                sett = confmanager.read_options()
                sett['panel_size'] = list(self.GetSize())
                confmanager.write_options(**sett)

        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)
        # elif self.topicname:
        else:
            if self.appdata['warnexiting'] is True:
                if wx.MessageBox(_('Are you sure you want to exit?'),
                                 _('Exit'),  wx.ICON_QUESTION | wx.YES_NO,
                                 self) == wx.YES:
                    _setsize()
                    self.Destroy()
            else:
                _setsize()
                self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        Try to kill application during a process thread
        that does not want to terminate with the abort button

        """
        self.Destroy()

    # -------------   BUILD THE MENU BAR  ----------------###

    def videomass_menu_bar(self):
        """
        Make a menu bar. Per usare la disabilitazione di un menu item devi
        prima settare l'attributo self sull'item interessato - poi lo gestisci
        con self.item.Enable(False) per disabilitare o (True) per abilitare.
        Se vuoi disabilitare l'intero top di items fai per esempio:
        self.menuBar.EnableTop(6, False) per disabilitare la voce Help.
        """
        self.menuBar = wx.MenuBar()

        # ----------------------- file menu
        fileButton = wx.Menu()
        dscrp = (_("Open...\tCtrl+O"),
                 _("Open one or more files"))
        self.openmedia = fileButton.Append(wx.ID_OPEN, dscrp[0], dscrp[1])
        self.openmedia.Enable(False)
        dscrp = (_("Conversions folder\tCtrl+C"),
                 _("Open the default file conversions folder"))
        fold_convers = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Downloads folder\tCtrl+D"),
                 _("Open the default downloads folder"))
        fold_downloads = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Open temporary conversions"),
                 _("Open the temporary file conversions folder"))
        self.fold_convers_tmp = fileButton.Append(wx.ID_ANY, dscrp[0],
                                                  dscrp[1])
        self.fold_convers_tmp.Enable(False)
        dscrp = (_("Open temporary downloads"),
                 _("Open the temporary downloads folder"))
        self.fold_downloads_tmp = fileButton.Append(wx.ID_ANY, dscrp[0],
                                                    dscrp[1])
        self.fold_downloads_tmp.Enable(False)
        fileButton.AppendSeparator()
        dscrp = (_("Trash folder"),
                 _("Open the Videomass Trash folder if it exists"))
        fold_trash = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fold_trash.Enable(self.appdata['move_file_to_trash'])
        dscrp = (_("Empty Trash"),
                 _("Delete all files in the Videomass Trash folder"))
        empty_trash = fileButton.Append(wx.ID_DELETE, dscrp[0], dscrp[1])
        empty_trash.Enable(self.appdata['move_file_to_trash'])

        fileButton.AppendSeparator()
        dscrp = (_("Work Notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Close Videomass"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("FFmpeg help topics"),
                 _("A useful tool to search for FFmpeg help topics and "
                   "options"))
        searchtopic = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()

        if self.appdata['downloader'] != 'disabled':
            dscrp = (_("Update {}").format(self.appdata['downloader']),
                     _("Update the downloader to the latest version"))
            self.ydlupdate = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
            toolsButton.AppendSeparator()
            self.Bind(wx.EVT_MENU, self.youtubedl_uptodater, self.ydlupdate)
        dscrp = (_("Check for new presets"),
                 _("Check new versions of Videomass presets from homepage"))
        self.prstcheck = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Download the latest presets"),
                 _("Download all Videomass presets locally from the homepage"))
        self.prstdownload = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(toolsButton, _("Tools"))

        # ------------------ View menu
        viewButton = wx.Menu()
        ffmpegButton = wx.Menu()  # ffmpeg sub menu
        viewButton.AppendSubMenu(ffmpegButton, "FFmpeg")
        dscrp = (_("Show configuration"),
                 _("Show FFmpeg's built-in configuration capabilities"))
        checkconf = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        dscrp = (_("Muxers and Demuxers"),
                 _("Muxers and demuxers available for used FFmpeg."))
        ckformats = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        ckcoders = ffmpegButton.Append(wx.ID_ANY, _("Encoders"),
                                       _("Shows available encoders for FFmpeg")
                                       )
        dscrp = (_("Decoders"), _("Shows available decoders for FFmpeg"))
        ckdecoders = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffplayButton = wx.Menu()  # ffplay sub menu
        viewButton.AppendSubMenu(ffplayButton, _("FFplay"))
        dscrp = (_("While playing"),
                 _("Show useful shortcut keys when playing or previewing "
                   "with FFplay"))
        playing = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffplayButton.AppendSeparator()
        dscrp = (_("Displays timestamp"),
                 _("Displays timestamp when playing movies with FFplay"))
        self.viewtimestamp = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                                 kind=wx.ITEM_CHECK)


        dscrp = (_("Auto-exit after playback"),
                 _("If checked, the FFplay window will auto-close at the "
                   "end of playback"))
        self.exitplayback = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                                kind=wx.ITEM_CHECK)


        dscrp = (_("Setting timestamp"),
                 _("Change the size and color of the timestamp "
                   "during playback"))
        tscustomize = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])




        if self.appdata['downloader'] != 'disabled':
            # show youtube-dl
            viewButton.AppendSeparator()
            ydlButton = wx.Menu()  # ydl sub menu
            dscrp = (_("Version in Use"),
                     _("Shows the version in use"))
            self.ydlused = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
            dscrp = (_("Show the latest version..."),
                     _("Shows the latest version available on github.com"))
            self.ydllatest = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
            viewButton.AppendSubMenu(ydlButton, self.appdata['downloader'])
            self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
            self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        # timeline
        viewButton.AppendSeparator()
        dscrp = (_("Show Logs\tCtrl+L"),
                 _("Viewing log messages"))
        viewlogs = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        viewButton.AppendSeparator()
        dscrp = (_("Show timeline\tCtrl+T"),
                 _("Show panel for editing timeline (seek/duration)"))
        self.viewtimeline = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                              kind=wx.ITEM_CHECK)
        self.menuBar.Append(viewButton, _("View"))
        self.menuBar.Check(self.viewtimestamp.GetId(), True)

        # ------------------ Go menu
        goButton = wx.Menu()
        self.startpan = goButton.Append(wx.ID_ANY, _("Home panel\tShift+H"),
                                        _("Go to the 'Home' panel"))
        goButton.AppendSeparator()
        self.prstpan = goButton.Append(wx.ID_ANY,
                                       _("Presets Manager\tShift+P"),
                                       _("Go to the 'Presets Manager' panel"))
        self.avpan = goButton.Append(wx.ID_ANY, _("A/V Conversions\tShift+V"),
                                     _("Go to the 'A/V Conversions' panel"))
        self.concpan = goButton.Append(wx.ID_ANY,
                                       _("Concatenate Demuxer\tShift+D"),
                                       _("Go to the 'Concatenate Demuxer' "
                                         "panel"))
        self.slides = goButton.Append(wx.ID_ANY,
                                      _("Still Image Maker\tShift+I"),
                                      _("Go to the 'Still Image Maker' panel"))
        self.toseq = goButton.Append(wx.ID_ANY,
                                     _("From Movie to Pictures\tShift+S"),
                                     _("Go to the 'From Movie to Pictures' "
                                       "panel"))
        goButton.AppendSeparator()
        dscrp = (_("YouTube downloader\tShift+Y"),
                 _("Go to the 'YouTube Downloader' panel"))
        self.ydlpan = goButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])

        goButton.AppendSeparator()
        dscrp = (_("Output Monitor\tShift+O"),
                 _("Keeps track of the output for debugging errors"))
        self.logpan = goButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        goButton.AppendSeparator()
        sysButton = wx.Menu()  # system sub menu
        dscrp = (_("Configuration folder"),
                 _("Opens the Videomass configuration folder"))
        openconfdir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Log folder"),
                 _("Opens the Videomass log folder, if exists"))
        openlogdir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Cache folder"),
                 _("Opens the Videomass cache folder, if exists"))
        opencachedir = sysButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        goButton.AppendSubMenu(sysButton, _("System"))

        self.menuBar.Append(goButton, _("Goto"))

        # ------------------ setup menu
        setupButton = wx.Menu()
        dscrp = (_("Set up a temporary folder for conversions"),
                 _("Use a temporary location to save conversions"))
        setconvers_tmp = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        if self.same_destin:
            setconvers_tmp.Enable(False)
        dscrp = (_("Set up a temporary folder for downloads"),
                 _("Save all downloads to this temporary location"))
        setdownload_tmp = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        setupButton.AppendSeparator()
        dscrp = (_("Restore the default destination folders"),
                 _("Restore the default folders for file conversions "
                   "and downloads"))
        self.resetfolders_tmp = setupButton.Append(wx.ID_ANY, dscrp[0],
                                                   dscrp[1])
        self.resetfolders_tmp.Enable(False)
        setupButton.AppendSeparator()
        setupItem = setupButton.Append(wx.ID_PREFERENCES,
                                       _("Preferences\tCtrl+P"),
                                       _("Application preferences"))
        self.menuBar.Append(setupButton, _("Settings"))
        self.menuBar.Check(self.exitplayback.GetId(), self.autoexit)

        # ------------------ help menu
        helpButton = wx.Menu()
        helpItem = helpButton.Append(wx.ID_HELP, _("User Guide"), "")
        wikiItem = helpButton.Append(wx.ID_ANY, _("Wiki"), "")
        helpButton.AppendSeparator()
        issueItem = helpButton.Append(wx.ID_ANY, _("Issue tracker"), "")
        helpButton.AppendSeparator()
        transItem = helpButton.Append(wx.ID_ANY, _('Translation...'), '')
        helpButton.AppendSeparator()
        DonationItem = helpButton.Append(wx.ID_ANY, _("Donation"), "")
        helpButton.AppendSeparator()
        docFFmpeg = helpButton.Append(wx.ID_ANY, _("FFmpeg documentation"), "")
        helpButton.AppendSeparator()
        dscrp = (_("Check for newer version"),
                 _("Check for the latest Videomass version at "
                   "<https://pypi.org/project/videomass/>"))
        checkItem = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Videomass"), "")
        self.menuBar.Append(helpButton, _("Help"))

        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.open_media_files, self.openmedia)
        self.Bind(wx.EVT_MENU, self.openMyconversions, fold_convers)
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.openMyconversions_tmp,
                  self.fold_convers_tmp)
        self.Bind(wx.EVT_MENU, self.openMydownloads_tmp,
                  self.fold_downloads_tmp)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        self.Bind(wx.EVT_MENU, self.open_trash_folder, fold_trash)
        self.Bind(wx.EVT_MENU, self.empty_trash_folder, empty_trash)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.Search_topic, searchtopic)
        # self.Bind(wx.EVT_MENU, self.youtubedl_uptodater, self.ydlupdate)
        self.Bind(wx.EVT_MENU, self.prst_downloader, self.prstdownload)
        self.Bind(wx.EVT_MENU, self.prst_checkversion, self.prstcheck)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.Check_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.Check_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.Check_enc, ckcoders)
        self.Bind(wx.EVT_MENU, self.Check_dec, ckdecoders)
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.showTimestamp, self.viewtimestamp)
        self.Bind(wx.EVT_MENU, self.timestampCustomize, tscustomize)
        self.Bind(wx.EVT_MENU, self.autoexitFFplay, self.exitplayback)
        # self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        # self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        self.Bind(wx.EVT_MENU, self.View_logs, viewlogs)
        self.Bind(wx.EVT_MENU, self.view_Timeline, self.viewtimeline)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPan, self.startpan)
        self.Bind(wx.EVT_MENU, self.prstPan, self.prstpan)
        self.Bind(wx.EVT_MENU, self.avPan, self.avpan)
        self.Bind(wx.EVT_MENU, self.concPan, self.concpan)
        self.Bind(wx.EVT_MENU, self.on_to_slideshow, self.slides)
        self.Bind(wx.EVT_MENU, self.on_to_images, self.toseq)
        self.Bind(wx.EVT_MENU, self.ydlPan, self.ydlpan)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        self.Bind(wx.EVT_MENU, self.openLog, openlogdir)
        self.Bind(wx.EVT_MENU, self.openConf, openconfdir)
        self.Bind(wx.EVT_MENU, self.openCache, opencachedir)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.on_FFmpegfsave, setconvers_tmp)
        self.Bind(wx.EVT_MENU, self.on_Ytdlfsave, setdownload_tmp)
        self.Bind(wx.EVT_MENU, self.on_Resetfolders_tmp, self.resetfolders_tmp)
        self.Bind(wx.EVT_MENU, self.Setup, setupItem)
        # ----HELP----
        self.Bind(wx.EVT_MENU, self.Helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.Wiki, wikiItem)
        self.Bind(wx.EVT_MENU, self.Issues, issueItem)
        self.Bind(wx.EVT_MENU, self.Translations, transItem)
        self.Bind(wx.EVT_MENU, self.Donation, DonationItem)
        self.Bind(wx.EVT_MENU, self.DocFFmpeg, docFFmpeg)
        self.Bind(wx.EVT_MENU, self.CheckNewReleases, checkItem)
        self.Bind(wx.EVT_MENU, self.Info, infoItem)

    # --------Menu Bar Event handler (callback)
    # --------- Menu  Files
    def open_media_files(self, event):
        """
        Open the file dialog to choose media files.
        The order of selected files only supported by GTK
        """
        if self.topicname in ('Audio/Video Conversions',
                              'Presets Manager',
                              'Concatenate Demuxer',
                              'Image Sequence to Video',
                              'Video to Pictures'):
            self.switch_file_import(self, self.topicname)

        wildcard = ("All files |*.*|*.mkv|*.mkv|*.avi|*.avi|*.mp4|*.mp4|"
                    "*.flv|*.flv|*.m4v|*.m4v|*.wav|*.wav|*.mp3|*.mp3|"
                    "*.ogg|*.ogg|*.flac|*.flac|*.m4a|*.m4a")

        with wx.FileDialog(self, _("Open the selected files"),
                           "", "", wildcard, wx.FD_OPEN | wx.FD_MULTIPLE |
                           wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return
            paths = filedlg.GetPaths()
            for path in paths:
                self.fileDnDTarget.flCtrl.dropUpdate(path)
    # -------------------------------------------------------------------#

    def openMydownload(self, event):
        """
        Open the download folder with file manager

        """
        io_tools.openpath(self.appdata['outputdownload'])
    # -------------------------------------------------------------------#

    def openMyconversions(self, event):
        """
        Open the conversions folder with file manager

        """
        io_tools.openpath(self.appdata['outputfile'])
    # -------------------------------------------------------------------#

    def openMydownloads_tmp(self, event):
        """
        Open the temporary download folder with file manager

        """
        io_tools.openpath(self.outpath_ydl)
    # -------------------------------------------------------------------#

    def openMyconversions_tmp(self, event):
        """
        Open the temporary conversions folder with file manager

        """
        io_tools.openpath(self.outpath_ffmpeg)
    # -------------------------------------------------------------------#

    def open_trash_folder(self, event):
        """
        Open Videomass trash folder if it exists
        """
        path = self.appdata['trashfolder']
        if os.path.exists(path):
            io_tools.openpath(path)
        else:
            wx.MessageBox(_("No such folder '{}'").format(path),
                          "Videomass", wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def empty_trash_folder(self, event):
        """
        Delete permanently all files inside trash folder
        """
        path = self.appdata['trashfolder']
        if os.path.exists(path):
            files = os.listdir(path)
            if len(files) > 0:
                if wx.MessageBox(_("Are you sure to empty trash folder?"),
                                 "Videomass", wx.ICON_QUESTION
                                 | wx.YES_NO, self) == wx.NO:
                    return

                for fname in files:
                    os.remove(os.path.join(path, fname))
            else:
                wx.MessageBox(_("No files to delete"),
                              "Videomass", wx.ICON_INFORMATION, self)
        else:
            wx.MessageBox(_("No such folder '{}'").format(path),
                          "Videomass", wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def Quiet(self, event):
        """
        destroy the videomass.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#
    # --------- Menu Tools  ###

    def Search_topic(self, event):
        """
        Show a dialog box to help you find FFmpeg topics

        """
        dlg = ffmpeg_search.FFmpegSearch(self.appdata['ostype'])
        dlg.Show()
    # -------------------------------------------------------------------#

    def ydl_check_update(self):
        """
        check latest and installed versions of youtube-dl
        and return latest or None if error
        """
        if self.appdata['downloader'] == 'youtube_dl':
            url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
                   "/releases/latest")

        elif self.appdata['downloader'] == 'yt_dlp':
            url = ("https://api.github.com/repos/yt-dlp/yt-dlp/"
                   "releases/latest")

        latest = io_tools.get_github_releases(url, "tag_name")

        if latest[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{latest[0]} {latest[1]}",
                          f"{latest[0]}", wx.ICON_ERROR, self)
            return None

        this = self.ydl_used(self, False)
        if not this:
            return None

        if latest[0].strip() == this:
            wx.MessageBox(_("{0} is already up-to-date {1}"
                            ).format(self.appdata['downloader'], this),
                          "Videomass", wx.ICON_INFORMATION, self)
            return None

        if wx.MessageBox(_("{0} version {1} is available and will "
                           "replace the old version {2}\n\n"
                           "Do you want to update now?").format(
                               self.appdata['downloader'],
                               latest[0].strip(), this),
                         "Videomass", wx.ICON_QUESTION
                         | wx.YES_NO, self) == wx.NO:
            return None
        return latest
    # -------------------------------------------------------------------#

    def youtubedl_uptodater(self, event):
        """
        Update to latest version from 'Update youtube-dl' bar menu

        """
        check = self.ydl_check_update()
        if not check:
            return

        if self.appdata['app'] == 'appimage':

            if wx.MessageBox(_("To update {} it is necessary to rebuild "
                               "the Videomass AppImage. This procedure "
                               "will be completely automatic and will "
                               "only require you to select the location "
                               "of the AppImage.\n\nDo you want to "
                               "continue?"
                               ).format(self.appdata['downloader']),
                             "Videomass", wx.ICON_QUESTION
                             | wx.YES_NO, self) == wx.NO:
                return

            cur = current_release()[2]
            fname = _("Select the 'Videomass-{}-x86_64.AppImage' "
                      "file to update").format(cur)
            with wx.FileDialog(
                    None, _(fname), defaultDir=os.path.expanduser('~'),
                    wildcard=(f"*Videomass-{cur}-x86_64.AppImage "
                              f"(*Videomass-{cur}-x86_64.AppImage;)"
                              f"|*Videomass-{cur}-x86_64.AppImage;"),
                    style=wx.FD_OPEN
                    | wx.FD_FILE_MUST_EXIST) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                appimage = fileDialog.GetPath()

            upgrade = io_tools.appimage_update(appimage,
                                               'AppImage_Update_Tool.sh'
                                               )
            if upgrade == 'success':
                wx.MessageBox(_("Successful! {0} is up-to-date ({1})"
                                "\n\nRe-start is required."
                                ).format(self.appdata['downloader'],
                                         check[0]),
                              "Videomass", wx.ICON_INFORMATION, self)
                self.on_Kill()

            elif upgrade == 'error':
                msg = _("Failed! For details consult:\n{}"
                        "/AppImage_Updates.log").format(MainFrame.LOGDIR)
                wx.MessageBox(msg, 'ERROR', wx.ICON_ERROR, self)

            else:
                wx.MessageBox(_('Failed! {}').format(upgrade),
                              'ERROR', wx.ICON_ERROR, self)
            return

        wx.MessageBox('Unable to update', 'ERROR', wx.ICON_ERROR, self)
        return
    # ------------------------------------------------------------------#

    def prst_checkversion(self, event):
        """
        compare the installed version of the presets
        with the latest release on the development page.
        """
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass-presets/releases/latest")

        presetsdir = os.path.join(self.appdata['confdir'], 'presets',
                                  'version', 'version.txt')
        presetsrecovery = os.path.join(self.appdata['srcpath'], 'presets',
                                       'version', 'version.txt')

        if not os.path.isfile(presetsdir):
            copydir_recursively(os.path.dirname(presetsrecovery),
                                os.path.dirname(os.path.dirname(presetsdir))
                                )
        with open(presetsdir, "r", encoding='utf8') as vers:
            fread = vers.read().strip()

        newversion = io_tools.get_github_releases(url, "tag_name")

        if newversion[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{newversion[0]} {newversion[1]}",
                          f"{newversion[0]}", wx.ICON_ERROR, self)

        elif float(newversion[0].split('v')[1]) > float(fread):
            wx.MessageBox(_("There is a new version available "
                            "{0}").format(newversion[0], "Videomass",
                                          wx.ICON_INFORMATION, self))
        else:
            wx.MessageBox(_("No new version available"), "Videomass",
                          wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def prst_downloader(self, event):
        """
        Ask the user where to download the new presets;
        check tarball_url, then proceed to download.
        """
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass-presets/releases/latest")

        dialdir = wx.DirDialog(self, _("Choose a download folder"),
                               "", wx.DD_DEFAULT_STYLE)
        if dialdir.ShowModal() == wx.ID_OK:
            path = dialdir.GetPath()
            dialdir.Destroy()
        else:
            return

        tarball = io_tools.get_github_releases(url, "tarball_url")

        if tarball[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{tarbal[0]} {tarbal[1]}",
                          f"{tarbal[0]}", wx.ICON_ERROR, self)
            return

        name = f"Videomass-presets-{tarball[0].split('/v')[-1]}.tar.gz"
        pathname = os.path.join(path, name)
        msg = _('Wait....\nThe archive is being downloaded')
        download = io_tools.get_presets(tarball[0], pathname, msg)

        if download[1]:
            wx.MessageBox(f"{download[1]}", 'ERROR', wx.ICON_ERROR, self)
            return

        wx.MessageBox(_('Successfully downloaded to "{0}"').format(pathname),
                      'Videomass', wx.ICON_INFORMATION, self)
        return
    # -------------------------------------------------------------------#

    def reminder(self, event):
        """
        Call `io_tools.openpath` to open a 'user_memos.txt' file
        with default GUI text editor.
        """
        fname = os.path.join(self.appdata['confdir'], 'user_memos.txt')

        if os.path.exists(fname) and os.path.isfile(fname):
            io_tools.openpath(fname)
        else:
            try:
                with open(fname, "w", encoding='utf8') as text:
                    text.write("")
            except Exception as err:
                wx.MessageBox(_("Unexpected error while creating file:\n\n"
                                "{0}").format(err),
                              'Videomass', wx.ICON_ERROR, self)
            else:
                io_tools.openpath(fname)
    # ------------------------------------------------------------------#
    # --------- Menu View ###

    def Check_conf(self, event):
        """
        Call io_tools.test_conf

        """
        io_tools.test_conf()
    # ------------------------------------------------------------------#

    def Check_formats(self, event):
        """
        io_tools.test_formats

        """
        io_tools.test_formats()
    # ------------------------------------------------------------------#

    def Check_enc(self, event):
        """
        io_tools.test_encoders

        """
        io_tools.test_codecs('-encoders')
    # ------------------------------------------------------------------#

    def Check_dec(self, event):
        """
        io_tools.test_encoders

        """
        io_tools.test_codecs('-decoders')
    # ------------------------------------------------------------------#

    def durinPlayng(self, event):
        """
        FFplay submenu: show dialog with shortcuts keyboard for FFplay

        """
        dlg = while_playing.While_Playing(self.appdata['ostype'])
        dlg.Show()
    # ------------------------------------------------------------------#

    def showTimestamp(self, event):
        """
        FFplay submenu: enable filter for view timestamp with ffplay

        """
        if self.viewtimestamp.IsChecked():
            self.checktimestamp = True
        else:
            self.checktimestamp = False
    # ------------------------------------------------------------------#

    def timestampCustomize(self, event):
        """
        FFplay submenu: customize the timestamp filter

        """
        with set_timestamp.Set_Timestamp(self, self.cmdtimestamp) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                data = dialog.getvalue()
                if not data:
                    return
                self.cmdtimestamp = data
    # ------------------------------------------------------------------#

    def autoexitFFplay(self, event):
        """
        FFplay submenu:
        set boolean value to self.autoexit attribute to allow
        autoexit at the end of playback

        """
        self.autoexit = self.exitplayback.IsChecked() is True
    # ------------------------------------------------------------------#

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from 'Version in Use' bar menu
        """
        if self.appdata['PYLIBYDL'] is None:  # youtube-dl library
            if self.appdata['downloader'] == 'youtube_dl':
                this = youtube_dl.version.__version__
            elif self.appdata['downloader'] == 'yt_dlp':
                this = yt_dlp.version.__version__
            if msgbox:
                wx.MessageBox(_("You are using '{0}' version {1}"
                                ).format(self.appdata['downloader'], this),
                              'Videomass', wx.ICON_INFORMATION, self)
            return this
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self, event):
        """
        check for new version from github.com

        """
        if self.appdata['downloader'] == 'youtube_dl':
            url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
                   "/releases/latest")
        elif self.appdata['downloader'] == 'yt_dlp':
            url = ("https://api.github.com/repos/yt-dlp/yt-dlp/"
                   "releases/latest")

        latest = io_tools.get_github_releases(url, "tag_name")

        if latest[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{latest[0]} {latest[1]}",
                          f"{latest[0]}", wx.ICON_ERROR, self)
            return
        wx.MessageBox(_("{0}: Latest version available: {1}").format(
                      self.appdata['downloader'], latest[0]),
                      "Videomass", wx.ICON_INFORMATION, self)
    # -----------------------------------------------------------------#

    def View_logs(self, event):
        """
        Show miniframe to view log files
        """
        mf = ShowLogs(self,
                      self.appdata['logdir'],
                      self.appdata['ostype']
                      )
        mf.Show()
    # ------------------------------------------------------------------#

    def view_Timeline(self, event):
        """
        View menu: show timeline via menu bar

        """
        if self.viewtimeline.IsChecked():
            self.TimeLine.Show()
        else:
            self.TimeLine.Hide()
        self.Layout()
    # ------------------------------------------------------------------#
    # --------- Menu  Go  ###

    def startPan(self, event):
        """
        jump on start panel
        """
        self.choosetopicRetrieve()
    # ------------------------------------------------------------------#

    def prstPan(self, event):
        """
        jump on Presets Manager panel
        """
        self.topicname = 'Presets Manager'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def avPan(self, event):
        """
        jump on AVconversions panel
        """
        self.topicname = 'Audio/Video Conversions'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def ydlPan(self, event):
        """
        jump on youtube downloader
        """
        if self.ChooseTopic.on_YoutubeDL(self) is True:
            return
        self.topicname = 'Youtube Downloader'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def concPan(self, event):
        """
        jumpe on Concatenate Demuxer
        """
        self.topicname = 'Concatenate Demuxer'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def on_to_slideshow(self, event):
        """
        jumpe on From Image to Video
        """
        self.topicname = 'Image Sequence to Video'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def on_to_images(self, event):
        """
        jumpe on Video to Image
        """
        self.topicname = 'Video to Pictures'
        self.on_Forward(self)
    # ------------------------------------------------------------------#

    def logPan(self, event):
        """
        view last log on console
        """
        self.switch_to_processing('Viewing last log')
    # ------------------------------------------------------------------#

    def openLog(self, event):
        """
        Open the log directory with file manager

        """
        io_tools.openpath(self.appdata['logdir'])
    # ------------------------------------------------------------------#

    def openConf(self, event):
        """
        Open the configuration folder with file manager

        """
        io_tools.openpath(self.appdata['confdir'])
    # -------------------------------------------------------------------#

    def openCache(self, event):
        """
        Open the cache dir with file manager if exists
        """
        if not os.path.exists(self.appdata['cachedir']):
            wx.MessageBox(_("cache folder has not been created yet."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return
        io_tools.openpath(self.appdata['cachedir'])
    # ------------------------------------------------------------------#
    # --------- Menu  Preferences  ###

    def on_FFmpegfsave(self, event):
        """
        This is a menu event but also intercept the button 'save'
        event in the filedrop panel and sets a new file destination
        path for conversions

        """
        dpath = '' if self.outpath_ffmpeg is None else self.outpath_ffmpeg
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "conversions"), dpath,
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.outpath_ffmpeg = f'{getpath}'
            self.fileDnDTarget.on_file_save(self.outpath_ffmpeg)
            self.fileDnDTarget.file_dest = self.outpath_ffmpeg

            dialdir.Destroy()

            self.resetfolders_tmp.Enable(True)
            self.fold_convers_tmp.Enable(True)
    # ------------------------------------------------------------------#

    def on_Ytdlfsave(self, event):
        """
        This is a menu event but also intercept the button 'save'
        event in the textdrop panel and sets a new file destination
        path for downloading

        """
        dpath = '' if self.outpath_ydl is None else self.outpath_ydl
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "downloads"), dpath,
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.outpath_ydl = f'{getpath}'
            self.textDnDTarget.on_file_save(self.outpath_ydl)
            self.textDnDTarget.file_dest = self.outpath_ydl

            dialdir.Destroy()

            self.resetfolders_tmp.Enable(True)
            self.fold_downloads_tmp.Enable(True)
    # ------------------------------------------------------------------#

    def on_Resetfolders_tmp(self, event):
        """
        Restore the default file destination if saving temporary
        files has been set. For file conversions it has no effect
        if `self.same_destin` is True.

        """
        if not self.same_destin:
            self.outpath_ffmpeg = self.appdata['outputfile']
            self.fileDnDTarget.on_file_save(self.appdata['outputfile'])
            self.fileDnDTarget.file_dest = self.appdata['outputfile']
            self.fold_convers_tmp.Enable(False)

        self.outpath_ydl = self.appdata['outputdownload']
        self.textDnDTarget.on_file_save(self.appdata['outputdownload'])
        self.textDnDTarget.file_dest = self.appdata['outputdownload']
        self.fold_downloads_tmp.Enable(False)

        self.resetfolders_tmp.Enable(False)

        wx.MessageBox(_("Default destination folders successfully restored"),
                      "Videomass", wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def Setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Videomass, being need
        to get the return code from getvalue interface.
        """
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                if set_up.getvalue() is True:
                    self.on_Kill()

    # ------------------------------------------------------------------#
    # --------- Menu Help  ###

    def Helpme(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://jeanslack.github.io/Videomass/videomass_use.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Wiki(self, event):
        """Wiki page """
        page = 'https://github.com/jeanslack/Videomass/wiki'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Videomass/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Translations(self, event):
        """Display translation how to on github"""
        page = ('https://jeanslack.github.io/Videomass/Pages/'
                'Localization_Guidelines.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Donation(self, event):
        """Display donation page on github"""
        page = ('https://jeanslack.github.io/Videomass/Contribute.html'
                '#donations')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def DocFFmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
    # -------------------------------------------------------------------#

    def CheckNewReleases(self, event):
        """
        Compare the Videomass version with a given
        new version found on github.
        """
        this = current_release()  # this version
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass/releases/latest")
        version = io_tools.get_github_releases(url, "tag_name")

        if version[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{version[0]} {version[1]}",
                          f"{version[0]}", wx.ICON_ERROR, self)
            return

        version = version[0].split('v.')[1]
        newmajor, newminor, newmicro = version.split('.')
        new_version = int(f'{newmajor}{newminor}{newmicro}')
        major, minor, micro = this[2].split('.')
        this_version = int(f'{major}{minor}{micro}')

        if new_version > this_version:
            msg = _('A new release is available - '
                    'v.{0}\n').format(version)
        elif this_version > new_version:
            msg = _('You are using a development version '
                    'that has not yet been released!\n')
        else:
            msg = _('Congratulation! You are already '
                    'using the latest version.\n')

        dlg = videomass_check_version.CheckNewVersion(self,
                                                      msg,
                                                      version,
                                                      this[2]
                                                      )
        dlg.ShowModal()
    # -------------------------------------------------------------------#

    def Info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self, self.icons['videomass'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def videomass_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.

            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        if self.appdata['toolbarpos'] == 0:  # on top
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL)
            else:
                style = (wx.TB_DEFAULT_STYLE)

        elif self.appdata['toolbarpos'] == 1:  # on bottom
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_BOTTOM)

        elif self.appdata['toolbarpos'] == 2:  # on right
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_RIGHT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_RIGHT)

        elif self.appdata['toolbarpos'] == 3:
            if self.appdata['toolbartext'] is True:  # show text
                style = (wx.TB_TEXT | wx.TB_LEFT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_LEFT)

        self.toolbar = self.CreateToolBar(style=style)

        bmp_size = (int(self.appdata['toolbarsize']),
                    int(self.appdata['toolbarsize']))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up

            bmpback = get_bmp(self.icons['previous'], bmp_size)
            bmpnext = get_bmp(self.icons['next'], bmp_size)

            bmpinfo = get_bmp(self.icons['fileproperties'], bmp_size)
            bmpstat = get_bmp(self.icons['download_properties'], bmp_size)

            bmpsaveprf = get_bmp(self.icons['profile_append'], bmp_size)

            bmpconv = get_bmp(self.icons['startconv'], bmp_size)
            bmpydl = get_bmp(self.icons['startdownload'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)

            bmpinfo = wx.Bitmap(self.icons['fileproperties'],
                                wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icons['download_properties'],
                                wx.BITMAP_TYPE_ANY)

            bmpsaveprf = wx.Bitmap(self.icons['profile_append'],
                                   wx.BITMAP_TYPE_ANY)

            bmpconv = wx.Bitmap(self.icons['startconv'], wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icons['startdownload'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        tip = _("Go to the previous panel")
        back = self.toolbar.AddTool(3, _('Back'),
                                    bmpback,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Go to the next panel")
        forward = self.toolbar.AddTool(4, _('Next'),
                                       bmpnext,
                                       tip, wx.ITEM_NORMAL
                                       )
        # self.toolbar.AddSeparator()
        # self.toolbar.AddStretchableSpace()
        tip = _("Gathers information of multimedia streams")
        self.btn_metaI = self.toolbar.AddTool(5, _('Media Streams'),
                                              bmpinfo,
                                              tip, wx.ITEM_NORMAL
                                              )
        tip = _("Shows download statistics and information")
        self.btn_ydlstatistics = self.toolbar.AddTool(14, _('Statistics'),
                                                      bmpstat,
                                                      tip, wx.ITEM_NORMAL
                                                      )
        # self.toolbar.AddSeparator()
        tip = _("Add a new profile from this panel with the current settings")
        self.btn_saveprf = self.toolbar.AddTool(8, _('Add Profile'),
                                                bmpsaveprf,
                                                tip, wx.ITEM_NORMAL,
                                                )
        # self.toolbar.AddStretchableSpace()
        # self.toolbar.AddSeparator()
        tip = _("Convert using FFmpeg")
        self.run_coding = self.toolbar.AddTool(12, _('Convert'),
                                               bmpconv,
                                               tip, wx.ITEM_NORMAL
                                               )
        tip = _("Download files using youtube-dl")
        self.run_download = self.toolbar.AddTool(13, _('Download'),
                                                 bmpydl,
                                                 tip, wx.ITEM_NORMAL
                                                 )
        # self.toolbar.AddStretchableSpace()
        # finally, create it
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_coding)
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_Back, back)
        self.Bind(wx.EVT_TOOL, self.on_Forward, forward)
        self.Bind(wx.EVT_TOOL, self.Saveprofile, self.btn_saveprf)
        self.Bind(wx.EVT_TOOL, self.ImportInfo, self.btn_metaI)
        self.Bind(wx.EVT_TOOL, self.ImportInfo, self.btn_ydlstatistics)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_Back(self, event):
        """
        Return to the previous panel.
        """
        if self.textDnDTarget.IsShown() or self.fileDnDTarget.IsShown():
            self.choosetopicRetrieve()

        elif self.topicname in ('Audio/Video Conversions',
                                'Presets Manager',
                                'Concatenate Demuxer',
                                'Image Sequence to Video',
                                'Video to Pictures'):
            self.switch_file_import(self, self.topicname)

        elif self.topicname == 'Youtube Downloader':
            self.switch_text_import(self, self.topicname)
    # ------------------------------------------------------------------#

    def on_Forward(self, event):
        """
        redirect on corresponding panel
        """
        if self.topicname in ('Audio/Video Conversions',
                              'Presets Manager',
                              'Concatenate Demuxer',
                              'Image Sequence to Video',
                              'Video to Pictures'):

            if self.topicname == 'Audio/Video Conversions':
                self.switch_av_conversions(self)

            elif self.topicname == 'Concatenate Demuxer':
                self.switch_concat_demuxer(self)

            elif self.topicname == 'Presets Manager':
                self.switch_presets_manager(self)

            elif self.topicname == 'Image Sequence to Video':
                self.switch_slideshow_maker(self)

            elif self.topicname == 'Video to Pictures':
                self.switch_video_to_pictures(self)

        elif self.topicname == 'Youtube Downloader':
            data = self.textDnDTarget.topic_Redirect()

            if data:
                for url in data:  # Check malformed url
                    res = urlparse(url)
                    if not res[1]:  # if empty netloc given from ParseResult
                        wx.MessageBox(_('ERROR: Invalid URL: "{}"').format(
                                      url), "Videomass", wx.ICON_ERROR, self)
                        return
                if len(set(data)) != len(data):  # equal URLS
                    wx.MessageBox(_("ERROR: Some equal URLs found"),
                                  "Videomass", wx.ICON_ERROR, self)
                    return

            self.switch_youtube_downloader(self, data)
    # ------------------------------------------------------------------#

    def switch_file_import(self, event, which):
        """
        Show files import panel.

        """
        self.topicname = which
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ChooseTopic.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.fileDnDTarget.Show()
        if self.outpath_ffmpeg:
            self.fileDnDTarget.text_path_save.SetValue("")
            self.fileDnDTarget.text_path_save.AppendText(self.outpath_ffmpeg)
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(True)
        self.avpan.Enable(False)
        self.prstpan.Enable(False)
        self.ydlpan.Enable(False)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(False)
        self.concpan.Enable(False)
        self.toseq.Enable(False)
        self.slides.Enable(False)
        self.toolbar.Show()
        self.logpan.Enable(False)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, True)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, False)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, False)
        self.toolbar.EnableTool(13, False)
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - Queued Files'))
    # ------------------------------------------------------------------#

    def switch_text_import(self, event, which):
        """
        Show URLs import panel.
        """
        self.topicname = which
        self.fileDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ChooseTopic.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.textDnDTarget.Show()
        if self.outpath_ydl:
            self.textDnDTarget.text_path_save.SetValue("")
            self.textDnDTarget.text_path_save.AppendText(self.outpath_ydl)
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(False)
        self.avpan.Enable(False)
        self.prstpan.Enable(False)
        self.ydlpan.Enable(False)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(False)
        self.concpan.Enable(False)
        self.toseq.Enable(False)
        self.slides.Enable(False)
        self.toolbar.Show()
        self.logpan.Enable(False)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, True)
        self.toolbar.EnableTool(5, False)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, False)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, False)
        self.toolbar.EnableTool(13, False)
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - Queued URLs'))

    # ------------------------------------------------------------------#

    def switch_youtube_downloader(self, event, data):
        """
        Show youtube-dl downloader panel
        """
        if not data:
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.choice.Disable()
            self.ytDownloader.ckbx_pl.Disable()
            self.ytDownloader.cmbx_af.Disable()
            self.ytDownloader.cmbx_aq.Disable()
            self.ytDownloader.rdbvideoformat.Disable()
            self.ytDownloader.cod_text.Hide()
            self.ytDownloader.labtxt.Hide()
            self.ytDownloader.cmbx_vq.Clear()
            self.ytDownloader.fcode.ClearAll()
            self.ytDownloader.btn_play.Disable()

        elif not data == self.data_url:
            if self.data_url:
                msg = (_('URL list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.data_url = data
            self.ytDownloader.choice.Enable()
            self.ytDownloader.ckbx_pl.Enable()
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.on_choicebox(self, statusmsg=False)
            del self.ytDownloader.info[:]
            self.ytDownloader.format_dict.clear()
            self.ytDownloader.ckbx_pl.SetValue(False)
            self.ytDownloader.on_playlist(self)
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - YouTube Downloader'))
        self.outpath_ydl = self.textDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ytDownloader.Show()
        self.toolbar.Show()
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(False)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.ydlpan.Enable(False)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(False)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, False)
        self.toolbar.EnableTool(14, True)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, False)
        self.toolbar.EnableTool(13, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_av_conversions(self, event):
        """
        Show Video converter panel
        """
        self.outpath_ffmpeg = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.VconvPanel.Show()
        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:  # only if file list changes
            if self.file_src:
                msg = (_('File list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files
                             ]
            if not self.duration:
                self.TimeLine.set_values(self.duration)
            elif max(self.duration) < 100:  # if .jpeg
                self.TimeLine.set_values([])
            else:  # max val from list
                self.TimeLine.set_values(max(self.duration))

            self.VconvPanel.normalize_default()
            self.VconvPanel.on_FiltersClear(self)
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - AV Conversions'))
        self.view_Timeline(self)  # set timeline status
        self.toolbar.Show()
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(True)
        self.avpan.Enable(False)
        self.prstpan.Enable(True)
        self.ydlpan.Enable(True)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(13, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_presets_manager(self, event):
        """
        Show presets manager panel

        """
        self.outpath_ffmpeg = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.PrstsPanel.Show()
        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                msg = (_('File list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files
                             ]
            if not self.duration:
                self.TimeLine.set_values(self.duration)
            elif max(self.duration) < 100:  # if .jpeg
                self.TimeLine.set_values([])
            else:  # max val from list
                self.TimeLine.set_values(max(self.duration))

            self.VconvPanel.normalize_default()
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - Presets Manager'))
        self.view_Timeline(self)  # set timeline status
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(False)
        self.ydlpan.Enable(True)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(13, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_concat_demuxer(self, event):
        """
        Show concat demuxer panel

        """
        self.outpath_ffmpeg = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Show()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.TimeLine.Hide()

        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                msg = (_('File list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files
                             ]
            if not self.duration:
                self.TimeLine.set_values(self.duration)
            elif max(self.duration) < 100:  # if .jpeg
                self.TimeLine.set_values([])
            else:  # max val from list
                self.TimeLine.set_values(max(self.duration))

            self.VconvPanel.normalize_default()
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - Concatenate Demuxer'))
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.ydlpan.Enable(True)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(False)
        self.logpan.Enable(True)
        self.concpan.Enable(False)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(13, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_video_to_pictures(self, event):
        """
        Show  Video to Pictures panel

        """
        self.outpath_ffmpeg = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toSlideshow.Hide()
        self.toPictures.Show()

        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                msg = (_('File list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files
                             ]
            if not self.duration:
                self.TimeLine.set_values(self.duration)
            elif max(self.duration) < 100:  # if .jpeg
                self.TimeLine.set_values([])
            else:  # max val from list
                self.TimeLine.set_values(max(self.duration))

            self.VconvPanel.normalize_default()
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - From Movie to Pictures'))
        self.view_Timeline(self)  # set timeline status
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.ydlpan.Enable(True)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(False)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(13, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_slideshow_maker(self, event):
        """
        Show slideshow maker panel

        """
        self.outpath_ffmpeg = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Show()

        filenames = [f['format']['filename'] for f in
                     self.data_files if f['format']['filename']
                     ]
        if not filenames == self.file_src:
            if self.file_src:
                msg = (_('File list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.file_src = filenames
            self.duration = [f['format']['duration'] for f in
                             self.data_files
                             ]
            if not self.duration:
                self.TimeLine.set_values(self.duration)
            elif max(self.duration) < 100:  # if .jpeg
                self.TimeLine.set_values([])
            else:  # max val from list
                self.TimeLine.set_values(max(self.duration))

            self.VconvPanel.normalize_default()
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - Still Image Maker'))
        self.view_Timeline(self)  # set timeline status
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.ydlpan.Enable(True)
        self.startpan.Enable(True)
        self.viewtimeline.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(False)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(6, True)
        self.toolbar.EnableTool(8, False)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(13, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *varargs):
        """
    1) TIME DEFINITION FOR THE PROGRESS BAR
        For a suitable and efficient progress bar, if a specific
        time sequence has been set with the timeline tool, the total
        duration of each media file will be replaced with the set time
        sequence. Otherwise the duration of each media will be the one
        originated from its source duration.

    2) STARTING THE PROCESS
        Here the panel with the progress bar is instantiated which will
        assign a corresponding thread.

        """
        if varargs[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            duration, time_seq = self.duration, self.time_seq

        elif varargs[0] == 'youtube_dl downloading':
            duration, time_seq = None, None

        elif varargs[0] in ('concat_demuxer', 'sequence_to_video'):
            duration, time_seq = varargs[6], ''

        elif self.time_seq != "-ss 00:00:00.000 -t 00:00:00.000":
            ms = get_milliseconds(self.time_seq.split()[3])  # -t duration
            time_seq = self.time_seq
            if [t for t in self.duration if ms > t]:  # if out time range
                wx.MessageBox(_('Cannot continue: The duration in the '
                                'timeline exceeds the duration of some '
                                'queued files.'),
                                'Videomass', wx.ICON_ERROR, self)
                return
            duration = [ms for n in self.duration]
            self.statusbar_msg(_('Processing...'), None)

        else:
            duration, time_seq = self.duration, ''

        self.SetTitle(_('Videomass - Output Monitor'))
        # Hide all others panels:
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        # Show the panel:
        self.ProcessPanel.Show()
        # self.SetTitle('Videomass')
        [self.menuBar.EnableTop(x, False) for x in range(3, 5)]
        if self.appdata['app'] == 'appimage':
            if self.appdata['PYLIBYDL'] is None:
                self.ydlupdate.Enable(False)  # do not update during a process
        self.viewtimeline.Enable(False)
        self.openmedia.Enable(False)
        # Hide the tool bar
        self.toolbar.Hide()
        self.ProcessPanel.topic_thread(self.topicname, varargs,
                                       duration, time_seq)
        self.Layout()
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        By clicking on Convert/Download buttons in the main frame,
        calls the `on_start method` of the corresponding panel shown,
        which calls the 'switch_to_processing' method above.
        """
        if self.ytDownloader.IsShown():
            if not self.data_url:
                self.switch_text_import(self, self.topicname)
                return

            self.ytDownloader.on_start()
            return

        if not self.data_files:
            self.switch_file_import(self, self.topicname)
            return

        if self.VconvPanel.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.VconvPanel.on_start()

        elif self.PrstsPanel.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.PrstsPanel.on_start()

        elif self.ConcatDemuxer.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.ConcatDemuxer.on_start()

        elif self.toPictures.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.toPictures.on_start()

        elif self.toSlideshow.IsShown():
            self.file_src = [f['format']['filename'] for f in
                             self.data_files if f['format']['filename']
                             ]
            self.toSlideshow.on_start()

    # ------------------------------------------------------------------#

    def panelShown(self, panelshown):
        """
        When clicking 'close button' of the long_processing_task panel,
        retrieval at previous panel showing and re-enables the functions
        provided by the menu bar (see `switch_to_processing` method above).
        """
        if panelshown == 'Audio/Video Conversions':
            self.ProcessPanel.Hide()
            self.switch_av_conversions(self)

        elif panelshown == 'Youtube Downloader':
            self.ProcessPanel.Hide()
            self.switch_youtube_downloader(self, self.data_url)

        elif panelshown == 'Presets Manager':
            self.ProcessPanel.Hide()
            self.switch_presets_manager(self)

        elif panelshown == 'Concatenate Demuxer':
            self.ProcessPanel.Hide()
            self.switch_concat_demuxer(self)

        elif panelshown == 'Video to Pictures':
            self.ProcessPanel.Hide()
            self.switch_video_to_pictures(self)

        elif panelshown == 'Image Sequence to Video':
            self.ProcessPanel.Hide()
            self.switch_slideshow_maker(self)

        # Enable all top menu bar:
        [self.menuBar.EnableTop(x, True) for x in range(3, 5)]
        if self.appdata['app'] == 'appimage':
            if self.appdata['PYLIBYDL'] is None:
                self.ydlupdate.Enable(True)  # re-enable it after processing
        # show buttons bar if the user has shown it:
        self.Layout()
