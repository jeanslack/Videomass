# -*- coding: UTF-8 -*-
# Name: main_frame.py
# Porpose: top window main frame
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Apr.04.2021 *PEP8 compatible*
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
from videomass3.vdms_utils.get_bmpfromsvg import get_bmp
import webbrowser
from urllib.parse import urlparse
import os
import sys
from videomass3.vdms_dialogs import settings
from videomass3.vdms_dialogs import set_timestamp
from videomass3.vdms_dialogs import infoprg
from videomass3.vdms_frames import while_playing
from videomass3.vdms_frames import ffmpeg_search
from videomass3.vdms_frames.mediainfo import Mediainfo
from videomass3.vdms_frames.showlogs import ShowLogs
from videomass3.vdms_panels import timeline
from videomass3.vdms_panels import choose_topic
from videomass3.vdms_panels import filedrop
from videomass3.vdms_panels import textdrop
from videomass3.vdms_panels import youtubedl_ui
from videomass3.vdms_panels import av_conversions
from videomass3.vdms_panels import concatenate
from videomass3.vdms_panels.long_processing_task import Logging_Console
from videomass3.vdms_panels import presets_manager
from videomass3.vdms_io import IO_tools
from videomass3.vdms_sys.msg_info import current_release
from videomass3.vdms_utils.utils import get_milliseconds
from videomass3.vdms_utils.utils import copydir_recursively
if 'youtube_dl' in sys.modules:
    import youtube_dl


class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # get videomass wx.App attribute
    get = wx.GetApp()
    PYLIB_YDL = get.pylibYdl  # youtube_dl library with None is in use
    EXEC_YDL = get.execYdl  # youtube-dl executable with False do not exist
    OS = get.OS  # ID of the operative system:
    DIR_CONF = get.DIRconf  # default configuration directory
    FILE_CONF = get.FILEconf  # pathname of the file configuration
    WORK_DIR = get.WORKdir  # pathname of the current work directory
    SRC_PATH = get.SRCpath  # pathname to the application directory
    LOGDIR = get.LOGdir  # log directory pathname
    CACHEDIR = get.CACHEdir  # cache directory pathname
    FFMPEG_DEFAULTDEST = get.FFMPEGoutdir  # default file dest from conf.
    YDL_DEFAULTDEST = get.YDLoutdir  # default download dest from conf.
    TBSIZE = get.TBsize  # toolbar icons size
    TBPOS = get.TBpos  # toolbar position
    TBTEXT = get.TBtext  # toolbar show/hide text (str(true) or str(false))
    # colour rappresentetion in rgb
    AZURE_NEON = 158, 201, 232
    YELLOW_LMN = 255, 255, 0
    BLUE = 0, 7, 12
    # set widget colours with html rappresentetion:
    ORANGE = '#f28924'
    YELLOW = '#a29500'
    LIMEGREEN = '#87A615'
    DARK_BROWN = '#262222'
    WHITE = '#fbf4f4'
    BLACK = '#060505'
    # AZURE = '#d9ffff'  # rgb form (wx.Colour(217,255,255))
    # RED = '#ea312d'
    # GREENOLIVE = '#6aaf23'
    # GREEN = '#268826'
    # -------------------------------------------------------------#

    def __init__(self, setui, pathicons):
        """
        NOTE: 'SRCpath' is a current work directory of Videomass
               program. How it can be localized depend if Videomass is
               run as portable program or installated program.

        """
        SRCpath = setui[1]  # share dir (are where the source files?):
        # ---------------------------#
        self.iconset = setui[4][11]
        self.videomass_icon = pathicons[0]
        self.icon_runconv = pathicons[2]
        self.icon_ydl = pathicons[24]
        self.icon_mainback = pathicons[22]
        self.icon_mainforward = pathicons[23]
        self.icon_info = pathicons[3]
        self.icon_saveprf = pathicons[8]
        self.icon_viewstatistics = pathicons[25]
        # self.viewlog = pathicons[26]

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
        if MainFrame.OS == 'Darwin':
            tsfont = '/Library/Fonts/Arial.ttf'
        elif MainFrame.OS == 'Windows':
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
                                                     MainFrame.OS,
                                                     pathicons[1],
                                                     pathicons[17],
                                                     pathicons[18],
                                                     pathicons[5],
                                                     )
        self.ytDownloader = youtubedl_ui.Downloader(self, pathicons[6])
        self.VconvPanel = av_conversions.AV_Conv(self,
                                                 MainFrame.OS,
                                                 pathicons[6],  # playfilt
                                                 pathicons[7],  # resetfilt
                                                 pathicons[9],  # resize
                                                 pathicons[10],  # crop
                                                 pathicons[11],  # rotate
                                                 pathicons[12],  # deinter
                                                 pathicons[13],  # ic_denoi
                                                 pathicons[14],  # analyzes
                                                 pathicons[15],  # settings
                                                 pathicons[16],  # peaklevel
                                                 pathicons[17],  # audiotr
                                                 pathicons[26],  # stabilizer
                                                 )
        self.fileDnDTarget = filedrop.FileDnD(self, pathicons[4])
        self.textDnDTarget = textdrop.TextDnD(self)
        self.ProcessPanel = Logging_Console(self)
        self.PrstsPanel = presets_manager.PrstPan(self,
                                                  SRCpath,
                                                  MainFrame.DIR_CONF,
                                                  MainFrame.WORK_DIR,
                                                  MainFrame.OS,
                                                  pathicons[19],  # newprf
                                                  pathicons[20],  # delprf
                                                  pathicons[21],  # editprf
                                                  )
        self.ConcatDemuxer = concatenate.Conc_Demuxer(self,)
        # hide panels
        self.TimeLine.Hide()
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.ProcessPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
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

        # ----------------------Set Properties----------------------#
        self.SetTitle("Videomass")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.videomass_icon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        if MainFrame.OS == 'Darwin':
            self.SetMinSize((980, 570))
        elif MainFrame.OS == 'Windows':
            self.SetMinSize((920, 640))
        else:
            self.SetMinSize((900, 600))
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
        self.textDnDTarget.Hide(), self.fileDnDTarget.Hide()
        self.TimeLine.Hide()
        if self.ytDownloader.IsShown():
            self.ytDownloader.Hide()

        elif self.VconvPanel.IsShown():
            self.VconvPanel.Hide()

        elif self.PrstsPanel.IsShown():
            self.PrstsPanel.Hide()

        elif self.ConcatDemuxer.IsShown():
            self.ConcatDemuxer.Hide()

        self.ChooseTopic.Show()
        self.toolbar.Hide(), self.avpan.Enable(False)
        self.prstpan.Enable(False), self.concpan.Enable(False)
        self.ydlpan.Enable(False), self.startpan.Enable(False)
        self.logpan.Enable(False), self.viewtimeline.Enable(False)
        self.SetTitle(_('Videomass'))
        self.statusbar_msg(_('Ready'), None)
        self.Layout()
    # ------------------------------------------------------------------#

    def menu_items(self):
        """
        enable or disable some menu items in according by showing panels
        """
        if self.ChooseTopic.IsShown() is True:
            self.avpan.Enable(False), self.prstpan.Enable(False),
            self.concpan.Enable(False), self.ydlpan.Enable(False),
            self.startpan.Enable(False), self.viewtimeline.Enable(False),
            self.logpan.Enable(False)
        if MainFrame.PYLIB_YDL is not None:  # no used as module
            if MainFrame.EXEC_YDL:
                if os.path.isfile(MainFrame.EXEC_YDL):
                    return
            self.ydlused.Enable(False)
            self.ydlupdate.Enable(False)
        # else:
            # self.ydlupdate.Enable(False)
    # ------------------------------------------------------------------#

    def reset_Timeline(self):
        """
        By adding or deleting files on file drop panel, cause reset
        the timeline data (only if `self.time_seq` attribute is true)
        """
        if self.time_seq != "-ss 00:00:00.000 -t 00:00:00.000":
            self.TimeLine.resetValues()

    # ---------------------- Event handler (callback) ------------------#

    def ImportInfo(self, event):
        """
        Redirect input files at stream_info for media information
        """
        if self.topicname == 'Youtube Downloader':
            self.ytDownloader.on_show_statistics()

        elif not self.data_files:
            wx.MessageBox(_('Drag at least one file'),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        else:
            miniframe = Mediainfo(self.data_files, MainFrame.OS)
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
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)

        # elif self.topicname:
        else:
            if wx.MessageBox(_('Are you sure you want to exit?'), _('Exit'),
                             wx.ICON_QUESTION | wx.YES_NO,
                             self) == wx.YES:
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
        dscrp = (_("Conversions folder\tCtrl+C"),
                 _("Open the default file conversions folder"))
        fold_convers = fileButton.Append(wx.ID_OPEN, dscrp[0], dscrp[1])
        dscrp = (_("Downloads folder\tCtrl+D"),
                 _("Open the default downloads folder"))
        fold_downloads = fileButton.Append(wx.ID_BOTTOM, dscrp[0], dscrp[1])
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
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit"),
                                     _("Close Videomass"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("FFmpeg help topics"),
                 _("A useful tool to search for FFmpeg help topics and "
                   "options"))
        searchtopic = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
        dscrp = (_("Update youtube-dl"),
                 _("Update to latest youtube-dl version"))
        self.ydlupdate = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
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
        ckcoders = ffmpegButton.Append(wx.ID_ANY, _("Encoders"), _("Shows "
                                       "available encoders for FFmpeg"))
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
        # show youtube-dl
        viewButton.AppendSeparator()
        ydlButton = wx.Menu()  # ydl sub menu
        dscrp = (_("Version in Use"),
                 _("Shows the version in use"))
        self.ydlused = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Show the latest version..."),
                 _("Shows the latest version available on github.com"))
        self.ydllatest = ydlButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        viewButton.AppendSubMenu(ydlButton, _("Youtube-dl"))
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
                                        _("jump to the start panel"))
        goButton.AppendSeparator()
        self.prstpan = goButton.Append(wx.ID_ANY,
                                       _("Presets manager\tShift+P"),
                                       _("jump to the Presets Manager panel"))
        self.avpan = goButton.Append(wx.ID_ANY, _("A/V conversions\tShift+V"),
                                     _("jump to the Audio/Video Conversion "
                                       "panel"))
        self.concpan = goButton.Append(wx.ID_ANY,
                                       _("Concatenate Demuxer\tShift+D"),
                                       _("jump to the Concatenate Demuxer "
                                         "panel"))
        goButton.AppendSeparator()
        dscrp = (_("YouTube downloader\tShift+Y"),
                 _("jump to the YouTube Downloader panel"))
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
        dscrp = (_("Setting timestamp"),
                 _("Change the size and color of the timestamp "
                   "during playback"))
        tscustomize = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Auto-exit after playback"),
                 _("If checked, the FFplay window will auto-close at the "
                   "end of playback"))
        self.exitplayback = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                               kind=wx.ITEM_CHECK)

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
        self.Bind(wx.EVT_MENU, self.openMyconversions, fold_convers)
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.openMyconversions_tmp,
                  self.fold_convers_tmp)
        self.Bind(wx.EVT_MENU, self.openMydownloads_tmp,
                  self.fold_downloads_tmp)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.Search_topic, searchtopic)
        self.Bind(wx.EVT_MENU, self.youtubedl_uptodater, self.ydlupdate)
        self.Bind(wx.EVT_MENU, self.prst_downloader, self.prstdownload)
        self.Bind(wx.EVT_MENU, self.prst_checkversion, self.prstcheck)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.Check_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.Check_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.Check_enc, ckcoders)
        self.Bind(wx.EVT_MENU, self.Check_dec, ckdecoders)
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.showTimestamp, self.viewtimestamp)
        self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        self.Bind(wx.EVT_MENU, self.View_logs, viewlogs)
        self.Bind(wx.EVT_MENU, self.view_Timeline, self.viewtimeline)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPan, self.startpan)
        self.Bind(wx.EVT_MENU, self.prstPan, self.prstpan)
        self.Bind(wx.EVT_MENU, self.avPan, self.avpan)
        self.Bind(wx.EVT_MENU, self.concPan, self.concpan)
        self.Bind(wx.EVT_MENU, self.ydlPan, self.ydlpan)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        self.Bind(wx.EVT_MENU, self.openLog, openlogdir)
        self.Bind(wx.EVT_MENU, self.openConf, openconfdir)
        self.Bind(wx.EVT_MENU, self.openCache, opencachedir)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.on_FFmpegfsave, setconvers_tmp)
        self.Bind(wx.EVT_MENU, self.on_Ytdlfsave, setdownload_tmp)
        self.Bind(wx.EVT_MENU, self.on_Resetfolders_tmp, self.resetfolders_tmp)
        self.Bind(wx.EVT_MENU, self.timestampCustomize, tscustomize)
        self.Bind(wx.EVT_MENU, self.autoexitFFplay, self.exitplayback)

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
    def openMydownload(self, event):
        """
        Open the download folder with file manager

        """
        IO_tools.openpath(MainFrame.YDL_DEFAULTDEST)
    # -------------------------------------------------------------------#

    def openMyconversions(self, event):
        """
        Open the conversions folder with file manager

        """
        IO_tools.openpath(MainFrame.FFMPEG_DEFAULTDEST)
    # -------------------------------------------------------------------#

    def openMydownloads_tmp(self, event):
        """
        Open the temporary download folder with file manager

        """
        IO_tools.openpath(self.outpath_ydl)
    # -------------------------------------------------------------------#

    def openMyconversions_tmp(self, event):
        """
        Open the temporary conversions folder with file manager

        """
        IO_tools.openpath(self.outpath_ffmpeg)
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
        dlg = ffmpeg_search.FFmpeg_Search(MainFrame.OS)
        dlg.Show()
    # -------------------------------------------------------------------#

    def youtubedl_uptodater(self, event):
        """
        Update to latest version from 'Update youtube-dl' bar menu

        """
        def _check():
            """
            check latest and installed versions of youtube-dl
            and return latest or None if error
            """
            url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
                   "/releases/latest")
            latest = IO_tools.get_github_releases(url, "tag_name")

            if latest[0] in ['request error:', 'response error:']:
                wx.MessageBox("%s %s" % (latest[0], latest[1]),
                              "%s" % latest[0], wx.ICON_ERROR, self)
                return None

            this = self.ydl_used(self, False)
            if latest[0].strip() == this:
                wx.MessageBox(_('youtube-dl is already '
                                'up-to-date {}').format(this),
                              "Videomass", wx.ICON_INFORMATION, self)
                return None
            elif wx.MessageBox(_(
                    'youtube-dl version {0} is available and will replace the '
                    'old version {1}\n\nDo you want to update '
                    'now?').format(latest[0].strip(), this),
                   "Videomass", wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return None
            return latest
        # ----------------------------------------------------------

        if (MainFrame.EXEC_YDL is not False and
                os.path.isfile(MainFrame.EXEC_YDL)):
            ck = _check()
            if not ck:
                return
            else:
                upgrade = IO_tools.youtubedl_upgrade(ck[0],
                                                     MainFrame.EXEC_YDL,
                                                     upgrade=True)

            if upgrade[1]:  # failed
                wx.MessageBox("%s" % (upgrade[1]), "Videomass",
                              wx.ICON_ERROR, self)
                return

            wx.MessageBox(_('Successful! youtube-dl is up-to-date'),
                          'Videomass', wx.ICON_INFORMATION, self)
            return

        elif ('/tmp/.mount_' in sys.executable or os.path.exists(
              os.path.dirname(os.path.dirname(os.path.dirname(
               sys.argv[0]))) + '/AppRun')):

            ck = _check()
            if not ck:
                return
            else:
                if wx.MessageBox(_(
                            'To update youtube_dl it is necessary to '
                            'rebuild the Videomass AppImage. This procedure '
                            'will be completely automatic and will only '
                            'require you to select the location of the '
                            'AppImage.'
                            '\n\nDo you want to continue?'),
                        "Videomass", wx.ICON_QUESTION |
                        wx.YES_NO, self) == wx.NO:
                    return
                cr = current_release()[2]
                fname = _("Select the 'Videomass-{}-x86_64.AppImage' "
                          "file to update").format(cr)
                with wx.FileDialog(
                        None, _(fname), defaultDir=os.path.expanduser('~'),
                        wildcard=("*Videomass-{0}-x86_64.AppImage (*Videomass-"
                                  "{0}-x86_64.AppImage;)|*Videomass-{0}-"
                                  "x86_64.AppImage;".format(cr)),
                        style=wx.FD_OPEN |
                        wx.FD_FILE_MUST_EXIST) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return
                    appimage = fileDialog.GetPath()

                upgrade = IO_tools.appimage_update_youtube_dl(appimage)

                if upgrade == 'success':
                    if wx.MessageBox(_(
                            'Successful! youtube-dl is up-to-date ({0})\n\n'
                            'Re-start is required. Do you want to close '
                            'Videomass now?').format(ck[0]),
                            "Videomass", wx.ICON_QUESTION |
                            wx.YES_NO, self) == wx.NO:
                        return

                    self.on_Kill()

                elif upgrade == 'error':
                    msg = _('Failed! For details consult:\n'
                            '{}/youtube_dl-update-on-AppImage.log').format(
                                MainFrame.LOGDIR)
                    wx.MessageBox(msg, 'ERROR', wx.ICON_ERROR, self)

                else:
                    wx.MessageBox(_('Failed! {}').format(upgrade),
                                  'ERROR', wx.ICON_ERROR, self)
                return

        elif MainFrame.PYLIB_YDL is None:  # system installed
            wx.MessageBox(
                    _('It looks like you installed youtube-dl with a '
                      'package manager. Please use that to update.'),
                    'Videomass', wx.ICON_INFORMATION, self)
            return
    # ------------------------------------------------------------------#

    def prst_checkversion(self, event):
        """
        compare the installed version of the presets
        with the latest release on the development page.
        """
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass-presets/releases/latest")

        presetsdir = os.path.join(MainFrame.DIR_CONF, 'presets',
                                  'version', 'version.txt')
        presetsrecovery = os.path.join(MainFrame.SRC_PATH, 'presets',
                                       'version', 'version.txt')

        if not os.path.isfile(presetsdir):
            pcopy = copydir_recursively(
                                os.path.dirname(presetsrecovery),
                                os.path.dirname(os.path.dirname(presetsdir)))

        with open(presetsdir, "r", encoding='utf8') as vers:
            fread = vers.read().strip()

        newversion = IO_tools.get_github_releases(url, "tag_name")

        if newversion[0] in ['request error:', 'response error:']:
            wx.MessageBox("%s %s" % (newversion[0], newversion[1]),
                          "%s" % newversion[0], wx.ICON_ERROR, self)

        elif float(newversion[0].split('v')[1]) > float(fread):
            wx.MessageBox(_("There is a new version available "
                          "{0}").format(newversion[0], "Videomass",
                                        wx.ICON_INFORMATION, self))
        else:
            wx.MessageBox(_("No new version available"), "Videomass",
                          wx.ICON_INFORMATION, self)
        return
    # ------------------------------------------------------------------#

    def prst_downloader(self, event):
        """
        Ask the user where to download the new presets;
        check tarball_url, then proceed to download.
        """
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass-presets/releases/latest")

        dialdir = wx.DirDialog(self, _("Choose a download folder"))
        if dialdir.ShowModal() == wx.ID_OK:
            path = dialdir.GetPath()
            dialdir.Destroy()
        else:
            return

        tarball = IO_tools.get_github_releases(url, "tarball_url")

        if tarball[0] in ['request error:', 'response error:']:
            wx.MessageBox("%s %s" % (tarbal[0], tarbal[1]),
                          "%s" % tarbal[0], wx.ICON_ERROR, self)
            return

        name = 'Videomass-presets-%s.tar.gz' % tarball[0].split('/v')[-1]
        pathname = os.path.join(path, name)
        msg = _('\nWait....\nThe archive is being downloaded\n')
        download = IO_tools.get_presets(tarball[0], pathname, msg)

        if download[1]:
            wx.MessageBox("%s" % download[1], 'ERROR', wx.ICON_ERROR, self)
            return
        else:
            wx.MessageBox(_('Successfully downloaded to '
                            '"{0}"').format(pathname), 'Videomass',
                          wx.ICON_INFORMATION, self)
            return
    # ------------------------------------------------------------------#
    # --------- Menu View ###

    def Check_conf(self, event):
        """
        Call IO_tools.test_conf

        """
        IO_tools.test_conf()
    # ------------------------------------------------------------------#

    def Check_formats(self, event):
        """
        IO_tools.test_formats

        """
        IO_tools.test_formats()
    # ------------------------------------------------------------------#

    def Check_enc(self, event):
        """
        IO_tools.test_encoders

        """
        IO_tools.test_codecs('-encoders')
    # ------------------------------------------------------------------#

    def Check_dec(self, event):
        """
        IO_tools.test_encoders

        """
        IO_tools.test_codecs('-decoders')
    # ------------------------------------------------------------------#

    def durinPlayng(self, event):
        """
        FFplay submenu: show dialog with shortcuts keyboard for FFplay

        """
        dlg = while_playing.While_Playing(MainFrame.OS)
        dlg.Show()
    # ------------------------------------------------------------------#

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from 'Version in Use' bar menu
        """
        waitmsg = _('\nWait....\nCheck installed version\n')
        if MainFrame.PYLIB_YDL is None:  # youtube-dl library
            this = youtube_dl.version.__version__
            if msgbox:
                wx.MessageBox(_('You are using youtube-dl '
                                'version {}').format(this),
                              'Videomass', wx.ICON_INFORMATION, self)
            return this
        else:
            if os.path.exists(MainFrame.EXEC_YDL):
                this = IO_tools.youtubedl_update([MainFrame.EXEC_YDL,
                                                  '--version'],
                                                 waitmsg)
                if this[1]:  # failed
                    wx.MessageBox("%s" % this[0], "Videomass",
                                  wx.ICON_ERROR, self)
                    return None

                if msgbox:
                    wx.MessageBox(_('You are using youtube-dl '
                                    'version {}').format(this[0]),
                                  'Videomass', wx.ICON_INFORMATION, self)
                    return this[0]

                return this[0].strip()
        if msgbox:
            wx.MessageBox(_('ERROR: {0}\n\nyoutube-dl has not been '
                            'installed yet.').format(MainFrame.PYLIB_YDL),
                          'Videomass', wx.ICON_ERROR, self)
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self, event):
        """
        check new version from github.com

        """
        url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
               "/releases/latest")
        latest = IO_tools.get_github_releases(url, "tag_name")

        if latest[0] in ['request error:', 'response error:']:
            wx.MessageBox("%s %s" % (latest[0], latest[1]),
                          "%s" % latest[0], wx.ICON_ERROR, self)
            return

        else:
            wx.MessageBox(_('Latest version available: {0}').format(latest[0]),
                          "Videomass", wx.ICON_INFORMATION, self)
    # -----------------------------------------------------------------#

    def showTimestamp(self, event):
        """
        FFplay submenu: enable filter for view timestamp with ffplay

        """
        if self.viewtimestamp.IsChecked():
            self.checktimestamp = True
        else:
            self.checktimestamp = False
    # ------------------------------------------------------------------#

    def View_logs(self, event):
        """
        Show miniframe to view log files
        """
        if not os.path.exists(MainFrame.LOGDIR):
            wx.MessageBox(_("There are no logs to show."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        else:
            mf = ShowLogs(self, MainFrame.LOGDIR, MainFrame.OS)
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
        if not self.data_files:
            self.statusbar_msg(_('No files added yet'), MainFrame.YELLOW)
        else:
            self.topicname = 'Presets Manager'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def avPan(self, event):
        """
        jump on AVconversions panel
        """
        if not self.data_files:
            self.statusbar_msg(_('No files added yet'), MainFrame.YELLOW)
        else:
            self.topicname = 'Audio/Video Conversions'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def ydlPan(self, event):
        """
        jumpe on youtube downloader
        """
        if not self.data_url:
            self.statusbar_msg(_('No URLs added yet'), MainFrame.YELLOW)
        else:
            self.topicname = 'Youtube Downloader'
            self.on_Forward(self)
    # ------------------------------------------------------------------#

    def concPan(self, event):
        """
        jumpe on Concatenate Demuxer
        """
        if not self.data_files:
            self.statusbar_msg(_('No files added yet'), MainFrame.YELLOW)
        else:
            self.topicname = 'Concatenate Demuxer'
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
        if not os.path.exists(MainFrame.LOGDIR):
            wx.MessageBox(_("There are no logs to show."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return
        IO_tools.openpath(MainFrame.LOGDIR)
    # ------------------------------------------------------------------#

    def openConf(self, event):
        """
        Open the configuration folder with file manager

        """
        IO_tools.openpath(MainFrame.DIR_CONF)
    # -------------------------------------------------------------------#

    def openCache(self, event):
        """
        Open the cache dir with file manager if exists
        """
        if not os.path.exists(MainFrame.CACHEDIR):
            wx.MessageBox(_("cache folder has not been created yet."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return
        IO_tools.openpath(MainFrame.CACHEDIR)
    # ------------------------------------------------------------------#
    # --------- Menu  Preferences  ###

    def on_FFmpegfsave(self, event):
        """
        This is a menu event but also intercept the button 'save'
        event in the filedrop panel and sets a new file destination
        path for conversions

        """
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "conversions"))
        if dialdir.ShowModal() == wx.ID_OK:
            self.outpath_ffmpeg = '%s' % (dialdir.GetPath())
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
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "downloads"))
        if dialdir.ShowModal() == wx.ID_OK:
            self.outpath_ydl = '%s' % (dialdir.GetPath())
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
            self.outpath_ffmpeg = MainFrame.FFMPEG_DEFAULTDEST
            self.fileDnDTarget.on_file_save(MainFrame.FFMPEG_DEFAULTDEST)
            self.fileDnDTarget.file_dest = MainFrame.FFMPEG_DEFAULTDEST
            self.fold_convers_tmp.Enable(False)

        self.outpath_ydl = MainFrame.YDL_DEFAULTDEST
        self.textDnDTarget.on_file_save(MainFrame.YDL_DEFAULTDEST)
        self.textDnDTarget.file_dest = MainFrame.YDL_DEFAULTDEST
        self.fold_downloads_tmp.Enable(False)

        self.resetfolders_tmp.Enable(False)

        wx.MessageBox(_("Default destination folders successfully restored"),
                      "Videomass", wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def timestampCustomize(self, event):
        """
        customize the timestamp filter

        """
        dialog = set_timestamp.Set_Timestamp(self, self.cmdtimestamp)
        retcode = dialog.ShowModal()
        if retcode == wx.ID_OK:
            data = dialog.GetValue()
            if not data:
                return
            else:
                self.cmdtimestamp = data
        else:
            dialog.Destroy()
            return
    # ------------------------------------------------------------------#

    def autoexitFFplay(self, event):
        """
        set boolean value to self.autoexit attribute to allow
        autoexit at the end of playback

        """
        self.autoexit = True if self.exitplayback.IsChecked() else False
    # ------------------------------------------------------------------#

    def Setup(self, event):
        """
        Call the module setup for setting preferences
        """
        # self.parent.Setup(self)
        setup_dlg = settings.Setup(self, self.iconset)
        setup_dlg.ShowModal()
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
        page = ('https://github.com/jeanslack/Videomass/blob/'
                'master/docs/localization_guidelines.md')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def Donation(self, event):
        """Display donation page on github"""
        page = 'https://jeanslack.github.io/Videomass/donation.html'
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
        version = IO_tools.get_github_releases(url, "tag_name")

        if version[0] in ['request error:', 'response error:']:
            wx.MessageBox("%s %s" % (version[0], version[1]),
                          "%s" % version[0], wx.ICON_ERROR, self)
            return

        else:
            version = version[0].split('v')[1]
            newmajor, newminor, newmicro = version.split('.')
            new_version = int('%s%s%s' % (newmajor, newminor, newmicro))
            major, minor, micro = this[2].split('.')
            this_version = int('%s%s%s' % (major, minor, micro))

            if new_version > this_version:
                wx.MessageBox(_(
                    '\n\nNew releases fix bugs and offer new features'
                    '\n\nThis is Videomass version {0}\n\n'
                    '<https://pypi.org/project/videomass/>\n\n'
                    'The latest version {1} is available\n').format(this[2],
                                                                    check[0]),
                    _("Checking for newer version"),
                    wx.ICON_INFORMATION | wx.CENTRE, self)
            else:
                wx.MessageBox(_(
                        '\n\nNew releases fix bugs and offer new features'
                        '\n\nThis is Videomass version {0}\n\n'
                        '<https://pypi.org/project/videomass/>\n\n'
                        'You are using the latest version\n').format(this[2]),
                        _("Checking for newer version"),
                        wx.ICON_INFORMATION | wx.CENTRE, self)
    # -------------------------------------------------------------------#

    def Info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self, self.videomass_icon)

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def videomass_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.

            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        if MainFrame.TBPOS == '0':  # on top
            if MainFrame.TBTEXT == 'show':  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL)
            else:
                style = (wx.TB_DEFAULT_STYLE)

        elif MainFrame.TBPOS == '1':  # on bottom
            if MainFrame.TBTEXT == 'show':  # show text
                style = (wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_BOTTOM)

        elif MainFrame.TBPOS == '2':  # on right
            if MainFrame.TBTEXT == 'show':  # show text
                style = (wx.TB_TEXT | wx.TB_RIGHT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_RIGHT)

        elif MainFrame.TBPOS == '3':
            if MainFrame.TBTEXT == 'show':  # show text
                style = (wx.TB_TEXT | wx.TB_LEFT)
            else:
                style = (wx.TB_DEFAULT_STYLE | wx.TB_LEFT)

        self.toolbar = self.CreateToolBar(style=style)

        bmp_size = (int(MainFrame.TBSIZE), int(MainFrame.TBSIZE))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up

            bmpback = get_bmp(self.icon_mainback, bmp_size)
            bmpnext = get_bmp(self.icon_mainforward, bmp_size)

            bmpinfo = get_bmp(self.icon_info, bmp_size)
            bmpstat = get_bmp(self.icon_viewstatistics, bmp_size)

            bmpsaveprf = get_bmp(self.icon_saveprf, bmp_size)

            bmpconv = get_bmp(self.icon_runconv, bmp_size)
            bmpydl = get_bmp(self.icon_ydl, bmp_size)

        else:
            bmpback = wx.Bitmap(self.icon_mainback, wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icon_mainforward, wx.BITMAP_TYPE_ANY)

            bmpinfo = wx.Bitmap(self.icon_info, wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icon_viewstatistics, wx.BITMAP_TYPE_ANY)

            bmpsaveprf = wx.Bitmap(self.icon_saveprf, wx.BITMAP_TYPE_ANY)

            bmpconv = wx.Bitmap(self.icon_runconv, wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icon_ydl, wx.BITMAP_TYPE_ANY)
        '''
        self.toolbar.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))
        '''
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
        self.btn_ydlstatistics = self.toolbar.AddTool(
                                    14, _('Statistics'),
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
                                'Concatenate Demuxer'):
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
                              'Concatenate Demuxer',):
            if not self.data_files:
                wx.MessageBox(_('Drag at least one file'), "Videomass",
                              wx.ICON_INFORMATION, self)
                return

            if self.topicname == 'Audio/Video Conversions':
                self.switch_av_conversions(self)

            elif self.topicname == 'Concatenate Demuxer':
                self.switch_concat_demuxer(self)

            else:
                self.switch_presets_manager(self)

        elif self.topicname == 'Youtube Downloader':
            data = self.textDnDTarget.topic_Redirect()
            if not data:
                wx.MessageBox(_('Append at least one URL'), "Videomass",
                              wx.ICON_INFORMATION, self)
                return

            for url in data:  # Check malformed url
                o = urlparse(url)
                if not o[1]:  # if empty netloc given from ParseResult
                    wx.MessageBox(_('Invalid URL: "{}"').format(url),
                                  "Videomass", wx.ICON_ERROR, self)
                    return

            self.switch_youtube_downloader(self, data)
    # ------------------------------------------------------------------#

    def switch_file_import(self, event, which):
        """
        Show files import panel.

        """
        self.topicname = which
        self.textDnDTarget.Hide(), self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.ChooseTopic.Hide()
        self.PrstsPanel.Hide(), self.TimeLine.Hide()
        self.ConcatDemuxer.Hide(), self.fileDnDTarget.Show()
        if self.outpath_ffmpeg:
            self.fileDnDTarget.text_path_save.SetValue("")
            self.fileDnDTarget.text_path_save.AppendText(self.outpath_ffmpeg)
        self.menu_items()  # disable some menu items
        self.avpan.Enable(False), self.prstpan.Enable(False),
        self.ydlpan.Enable(False), self.startpan.Enable(True)
        self.viewtimeline.Enable(False), self.concpan.Enable(False)
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
        self.fileDnDTarget.Hide(), self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.ChooseTopic.Hide()
        self.PrstsPanel.Hide(), self.TimeLine.Hide()
        self.ConcatDemuxer.Hide(), self.textDnDTarget.Show()
        if self.outpath_ydl:
            self.textDnDTarget.text_path_save.SetValue("")
            self.textDnDTarget.text_path_save.AppendText(self.outpath_ydl)
        self.menu_items()  # disable some menu items
        self.avpan.Enable(False), self.prstpan.Enable(False),
        self.ydlpan.Enable(False), self.startpan.Enable(True)
        self.viewtimeline.Enable(False), self.concpan.Enable(False)
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
        if not data == self.data_url:
            if self.data_url:
                msg = (_('URL list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.data_url = data
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.on_Choice(self)
            del self.ytDownloader.info[:]
            self.ytDownloader.format_dict.clear()
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Videomass - YouTube Downloader'))
        self.outpath_ydl = self.textDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide()
        self.VconvPanel.Hide(), self.PrstsPanel.Hide()
        self.TimeLine.Hide(), self.ConcatDemuxer.Hide()
        self.ytDownloader.Show()
        self.toolbar.Show()
        self.menu_items()  # disable some menu items
        self.avpan.Enable(True), self.prstpan.Enable(True)
        self.ydlpan.Enable(False), self.startpan.Enable(True)
        self.viewtimeline.Enable(False), self.logpan.Enable(True)
        self.concpan.Enable(True)
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
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide()
        self.ytDownloader.Hide(), self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide(), self.VconvPanel.Show()
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
        self.avpan.Enable(False), self.prstpan.Enable(True)
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.viewtimeline.Enable(True), self.logpan.Enable(True)
        self.concpan.Enable(True)
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
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.ConcatDemuxer.Hide(), self.PrstsPanel.Show()
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
        self.avpan.Enable(True), self.prstpan.Enable(False),
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.viewtimeline.Enable(True), self.logpan.Enable(True)
        self.concpan.Enable(True)
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
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.PrstsPanel.Hide(), self.ConcatDemuxer.Show()
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
        self.avpan.Enable(True), self.prstpan.Enable(True),
        self.ydlpan.Enable(True), self.startpan.Enable(True)
        self.viewtimeline.Enable(False), self.logpan.Enable(True)
        self.concpan.Enable(False)
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
            duration = self.duration
            time_seq = self.time_seq

        elif self.time_seq != "-ss 00:00:00.000 -t 00:00:00.000":
            ms = get_milliseconds(self.time_seq.split()[3])  # -t duration
            time_seq = self.time_seq
            if [t for t in self.duration if ms > t]:  # if out time range
                wx.MessageBox(_('Cannot continue: The duration in the '
                                'timeline exceeds the duration of some queued '
                                'files.'), 'Videomass', wx.ICON_ERROR, self)
                return
            duration = [ms for n in self.duration]
            self.statusbar_msg(_('Processing...'), None)

        else:
            duration = self.duration
            time_seq = ''
            self.statusbar_msg(_('Processing...'), None)

        self.SetTitle(_('Videomass - Output Monitor'))
        # Hide all others panels:
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.PrstsPanel.Hide(), self.TimeLine.Hide(),
        self.ConcatDemuxer.Hide()
        # Show the panel:
        self.ProcessPanel.Show()
        # self.SetTitle('Videomass')
        [self.menuBar.EnableTop(x, False) for x in range(0, 5)]
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
            self.ytDownloader.on_start()

        elif self.VconvPanel.IsShown():
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

        # Enable all top menu bar:
        [self.menuBar.EnableTop(x, True) for x in range(0, 5)]
        # show buttons bar if the user has shown it:
        self.Layout()
