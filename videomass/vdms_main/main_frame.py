# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.13.2023
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
from pubsub import pub
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs import preferences
from videomass.vdms_dialogs import set_timestamp
from videomass.vdms_dialogs import about
from videomass.vdms_dialogs import videomass_check_version
from videomass.vdms_frames.while_playing import WhilePlaying
from videomass.vdms_frames.ffmpeg_conf import FFmpegConf
from videomass.vdms_frames.ffmpeg_codecs import FFmpegCodecs
from videomass.vdms_frames.ffmpeg_formats import FFmpegFormats
from videomass.vdms_dialogs.mediainfo import MediaStreams
from videomass.vdms_dialogs.showlogs import ShowLogs
from videomass.vdms_dialogs.ffmpeg_help import FFmpegHelp
from videomass.vdms_panels import timeline
from videomass.vdms_panels import choose_topic
from videomass.vdms_panels import filedrop
from videomass.vdms_panels import av_conversions
from videomass.vdms_panels import concatenate
from videomass.vdms_panels import video_to_sequence
from videomass.vdms_panels import sequence_to_video
from videomass.vdms_panels.long_processing_task import LogOut
from videomass.vdms_panels import presets_manager
from videomass.vdms_io import io_tools
from videomass.vdms_sys.msg_info import current_release
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_sys.argparser import info_this_platform
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.utils import copydir_recursively


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
        self.outputpath = self.appdata['outputfile']  # path destination
        self.outputnames = []  # output file basenames (even renames)
        self.file_src = []  # input full file names list
        self.changed = []  # previous list is different from new one
        self.same_destin = self.appdata['outputfile_samedir']  # True/False
        self.suffix = self.appdata['filesuffix']  # suffix to output names
        self.filedropselected = None  # int(index) or None filedrop selected
        self.time_seq = "-ss 00:00:00.000 -t 00:00:00.000"  # FFmpeg time seq.
        self.duration = []  # empty if not file imported
        self.topicname = None  # shown panel name
        self.checktimestamp = True  # show timestamp during playback
        self.autoexit = False  # set autoexit during ffplay playback
        self.movetotrash = self.appdata['move_file_to_trash']
        self.emptylist = self.appdata['move_file_to_trash']
        self.mediastreams = False
        self.showlogs = False
        self.helptopic = False
        self.whileplay = False
        self.ffmpegconf = False
        self.ffmpegcodecs = False
        self.ffmpegdecoders = False
        self.ffmpegformats = False
        self.audivolnormalize = False
        # set fontconfig for timestamp
        if self.appdata['ostype'] == 'Darwin':
            tsfont = '/Library/Fonts/Arial.ttf'
        elif self.appdata['ostype'] == 'Windows':
            tsfont = 'C\\:/Windows/Fonts/Arial.ttf'
        else:
            tsfont = 'Arial'
        # set command line for timestamp
        ptshms = r"%{pts\:hms}"
        self.cmdtimestamp = (
            f"drawtext=fontfile='{tsfont}':text='{ptshms}':fontcolor=White:"
            f"shadowcolor=Black:shadowx=1:shadowy=1:fontsize=32:"
            f"box=1:boxcolor=DeepPink:x=(w-tw)/2:y=h-(2*lh)")

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- panel instances:
        self.TimeLine = timeline.Timeline(self, self.icons['clear'])
        self.ChooseTopic = choose_topic.Choose_Topic(self,
                                                     self.appdata['ostype'],
                                                     )
        self.VconvPanel = av_conversions.AV_Conv(self,
                                                 self.appdata,
                                                 self.icons,
                                                 )
        self.fileDnDTarget = filedrop.FileDnD(self,
                                              self.icons['playback'],
                                              self.outputpath,
                                              self.outputnames,
                                              self.data_files,
                                              self.file_src,
                                              self.duration,
                                              )
        self.ProcessPanel = LogOut(self)
        self.PrstsPanel = presets_manager.PrstPan(self,
                                                  self.appdata,
                                                  self.icons,
                                                  )
        self.ConcatDemuxer = concatenate.Conc_Demuxer(self,)
        self.toPictures = video_to_sequence.VideoToSequence(self, self.icons)
        self.toSlideshow = sequence_to_video.SequenceToVideo(self, self.icons)
        # hide panels
        self.TimeLine.Hide()
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.ProcessPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        # Layout toolbar buttons:
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global

        # Layout external panels:
        self.mainSizer.Add(self.TimeLine, 0, wx.EXPAND)
        self.mainSizer.Add(self.ChooseTopic, 1, wx.EXPAND)
        self.mainSizer.Add(self.fileDnDTarget, 1, wx.EXPAND)
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
        self.SetMinSize((850, 560))
        self.SetSizer(self.mainSizer)
        self.Fit()
        self.SetSize(tuple(self.appdata['window_size']))
        self.Move(tuple(self.appdata['window_position']))
        # menu bar
        self.videomass_menu_bar()
        # tool bar main
        self.videomass_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'), None)
        # hide toolbar & disable some file menu items
        self.toolbar.Hide()
        self.menu_items()
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_destpath_setup)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_WINDOWS")
        pub.subscribe(self.process_terminated, "PROCESS TERMINATED")

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, bcolor, fcolor=None):
        """
        Set the status-bar message and color.
        Note that These methods don't always work on every platform.
        Usage:
            - self.statusbar_msg(_('...Finished'))  # no color
            - self.statusbar_msg(_('...Finished'),
                                 bcolor=color,
                                 fcolor=color)  # with colors

        bcolor: background color, fcolor: foreground color
        """
        if self.appdata['ostype'] == 'Linux':
            if not bcolor:
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
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type:
                return
            self.ProcessPanel.Hide()

        self.topicname = None
        self.fileDnDTarget.Hide()
        self.TimeLine.Hide()

        if self.VconvPanel.IsShown():
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
        self.startpan.Enable(False)
        self.logpan.Enable(False)
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
        if self.ChooseTopic.IsShown():
            self.avpan.Enable(False)
            self.prstpan.Enable(False)
            self.concpan.Enable(False)
            self.toseq.Enable(False)
            self.slides.Enable(False)
            self.startpan.Enable(False)
            self.logpan.Enable(False)
    # ------------------------------------------------------------------#

    def check_modeless_window(self, msg=None):
        """
        Receives a message from a modeless window close event
        """
        if msg == 'MediaStreams':
            self.mediastreams.Destroy()
            self.mediastreams = False
        elif msg == 'ShowLogs':
            self.showlogs.Destroy()
            self.showlogs = False
        elif msg == 'HelpTopic':
            self.helptopic.Destroy()
            self.helptopic = False
        elif msg == 'WhilePlaying':
            self.whileplay.Destroy()
            self.whileplay = False
        elif msg == 'FFmpegConf':
            self.ffmpegconf.Destroy()
            self.ffmpegconf = False
        elif msg == 'FFmpegCodecs':
            self.ffmpegcodecs.Destroy()
            self.ffmpegcodecs = False
        elif msg == 'FFmpegDecoders':
            self.ffmpegdecoders.Destroy()
            self.ffmpegdecoders = False
        elif msg == 'FFmpegFormats':
            self.ffmpegformats.Destroy()
            self.ffmpegformats = False
        elif msg == 'AudioVolNormal':
            self.audivolnormalize.Destroy()
            self.audivolnormalize = False

    # ---------------------- Event handler (callback) ------------------#

    def media_streams(self, event):
        """
        Show the Media Stream Analyzer in modeless way (non-modal)
        """
        if self.mediastreams:
            self.mediastreams.Raise()
            return
        self.mediastreams = MediaStreams(self.data_files,
                                         self.appdata['ostype'])
        self.mediastreams.Show()
    # ------------------------------------------------------------------#

    def destroy_orphaned_window(self):
        """
        Destroys all orphaned modeless windows, ie. on
        application exit or on opening or deleting files.
        """
        if self.mediastreams:
            self.mediastreams.Destroy()
            self.mediastreams = False
        if self.showlogs:
            self.showlogs.Destroy()
            self.showlogs = False
        if self.helptopic:
            self.helptopic.Destroy()
            self.helptopic = False
        if self.whileplay:
            self.whileplay.Destroy()
            self.whileplay = False
        if self.ffmpegconf:
            self.ffmpegconf.Destroy()
            self.ffmpegconf = False
        if self.ffmpegcodecs:
            self.ffmpegcodecs.Destroy()
            self.ffmpegcodecs = False
        if self.ffmpegdecoders:
            self.ffmpegdecoders.Destroy()
            self.ffmpegdecoders = False
        if self.ffmpegformats:
            self.ffmpegformats.Destroy()
            self.ffmpegformats = False
        if self.audivolnormalize:
            self.audivolnormalize.Destroy()
            self.audivolnormalize = False
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        switch to panels or destroy the videomass app.
        """
        def _setsize():
            """
            Write last window size and position
            for next start if changed
            """
            confmanager = ConfigManager(self.appdata['fileconfpath'])
            sett = confmanager.read_options()
            sett['window_size'] = list(self.GetSize())
            sett['window_position'] = list(self.GetPosition())
            confmanager.write_options(**sett)

        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)
        else:
            if self.appdata['warnexiting']:
                if wx.MessageBox(_('Are you sure you want to exit?'),
                                 _('Exit'), wx.ICON_QUESTION | wx.YES_NO,
                                 self) == wx.NO:
                    return
            _setsize()
            self.destroy_orphaned_window()
            self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        Try to kill application during a process thread
        that does not want to terminate with the abort button

        """
        self.destroy_orphaned_window()
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
        fileButton.AppendSeparator()
        dscrp = (_("Conversions folder\tCtrl+C"),
                 _("Open the default file conversions folder"))
        fold_convers = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Open temporary conversions"),
                 _("Open the temporary file conversions folder"))
        self.fold_convers_tmp = fileButton.Append(wx.ID_ANY, dscrp[0],
                                                  dscrp[1])
        self.fold_convers_tmp.Enable(False)
        fileButton.AppendSeparator()
        dscrp = (_("Rename the selected file\tCtrl+R"),
                 _("Rename the file selected in the Queued Files panel"))
        self.rename = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.rename.Enable(False)
        dscrp = (_("Batch renaming\tCtrl+B"),
                 _("Rename all files listed in the Queued Files panel"))
        self.rename_batch = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.rename_batch.Enable(False)
        fileButton.AppendSeparator()
        dscrp = (_("Trash folder"),
                 _("Open the Videomass Trash folder if it exists"))
        fold_trash = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Empty Trash"),
                 _("Delete all files in the Videomass Trash folder"))
        empty_trash = fileButton.Append(wx.ID_DELETE, dscrp[0], dscrp[1])
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
        dscrp = (_("Find FFmpeg topics and options"),
                 _("A useful tool to search for FFmpeg help topics and "
                   "options"))
        searchtopic = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
        prstpage = '<https://github.com/jeanslack/Videomass-presets>'
        dscrp = (_("Check for preset updates"),
                 _("Check for new presets release from {0}").format(prstpage))
        self.prstcheck = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Download preset archive"),
                 _("Download the entire collection of the latest "
                   "presets available from the home page"))
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
        viewButton.AppendSeparator()
        dscrp = (_("Show Logs\tCtrl+L"),
                 _("Viewing log messages"))
        viewlogs = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(viewButton, _("View"))

        # ------------------ Go menu
        goButton = wx.Menu()
        self.startpan = goButton.Append(wx.ID_ANY,
                                        _("Home panel\tCtrl+Shift+H"),
                                        _("Go to the 'Home' panel"))
        goButton.AppendSeparator()
        self.prstpan = goButton.Append(wx.ID_ANY,
                                       _("Presets Manager\tCtrl+Shift+P"),
                                       _("Go to the 'Presets Manager' panel"))
        self.avpan = goButton.Append(wx.ID_ANY,
                                     _("A/V Conversions\tCtrl+Shift+V"),
                                     _("Go to the 'A/V Conversions' panel"))
        self.concpan = goButton.Append(wx.ID_ANY,
                                       _("Concatenate Demuxer\tCtrl+Shift+D"),
                                       _("Go to the 'Concatenate Demuxer' "
                                         "panel"))
        self.slides = goButton.Append(wx.ID_ANY,
                                      _("Still Image Maker\tCtrl+Shift+I"),
                                      _("Go to the 'Still Image Maker' panel"))
        self.toseq = goButton.Append(wx.ID_ANY,
                                     _("From Movie to Pictures\tCtrl+Shift+S"),
                                     _("Go to the 'From Movie to Pictures' "
                                       "panel"))
        goButton.AppendSeparator()
        dscrp = (_("Output Monitor\tCtrl+Shift+O"),
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
        path_dest = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        if self.same_destin:
            path_dest.Enable(False)
        setupButton.AppendSeparator()
        dscrp = (_("Restore the default destination folder"),
                 _("Restore the default folder for file conversions"))
        self.resetfolders_tmp = setupButton.Append(wx.ID_ANY, dscrp[0],
                                                   dscrp[1])
        self.resetfolders_tmp.Enable(False)
        setupButton.AppendSeparator()
        dscrp = (_("Display timestamps during playback"),
                 _("Displays timestamp when playing media with FFplay"))
        self.viewtimestamp = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                                kind=wx.ITEM_CHECK)
        dscrp = (_("Auto-exit after playback"),
                 _("If checked, the FFplay window will auto-close "
                   "when playback is complete"))
        self.exitplayback = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                               kind=wx.ITEM_CHECK)
        dscrp = (_("FFplay timestamp settings"),
                 _("Change the size and color of the timestamp "
                   "during playback"))
        tscustomize = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        setupButton.AppendSeparator()
        setupItem = setupButton.Append(wx.ID_PREFERENCES,
                                       _("Preferences\tCtrl+P"),
                                       _("Application preferences"))
        self.menuBar.Append(setupButton, _("Settings"))
        self.menuBar.Check(self.exitplayback.GetId(), self.autoexit)
        self.menuBar.Check(self.viewtimestamp.GetId(), True)

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
        dscrp = (_("System version"),
                 _("Get version about your operating system, version of "
                   "Python and wxPython."))
        sysinfo = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Videomass"), "")
        self.menuBar.Append(helpButton, _("Help"))

        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.open_media_files, self.openmedia)
        self.Bind(wx.EVT_MENU, self.openMyconversions, fold_convers)
        self.Bind(wx.EVT_MENU, self.openMyconversions_tmp,
                  self.fold_convers_tmp)
        self.Bind(wx.EVT_MENU, self.on_file_renaming, self.rename)
        self.Bind(wx.EVT_MENU, self.on_batch_renaming, self.rename_batch)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        self.Bind(wx.EVT_MENU, self.open_trash_folder, fold_trash)
        self.Bind(wx.EVT_MENU, self.empty_trash_folder, empty_trash)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.Search_topic, searchtopic)
        self.Bind(wx.EVT_MENU, self.prst_downloader, self.prstdownload)
        self.Bind(wx.EVT_MENU, self.prst_checkversion, self.prstcheck)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_codecs, ckcoders)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_decoders, ckdecoders)
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.showTimestamp, self.viewtimestamp)
        self.Bind(wx.EVT_MENU, self.timestampCustomize, tscustomize)
        self.Bind(wx.EVT_MENU, self.autoexitFFplay, self.exitplayback)
        self.Bind(wx.EVT_MENU, self.View_logs, viewlogs)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPan, self.startpan)
        self.Bind(wx.EVT_MENU, self.prstPan, self.prstpan)
        self.Bind(wx.EVT_MENU, self.avPan, self.avpan)
        self.Bind(wx.EVT_MENU, self.concPan, self.concpan)
        self.Bind(wx.EVT_MENU, self.on_to_slideshow, self.slides)
        self.Bind(wx.EVT_MENU, self.on_to_images, self.toseq)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        self.Bind(wx.EVT_MENU, self.openLog, openlogdir)
        self.Bind(wx.EVT_MENU, self.openConf, openconfdir)
        self.Bind(wx.EVT_MENU, self.openCache, opencachedir)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.on_destpath_setup, path_dest)
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
        self.Bind(wx.EVT_MENU, self.system_vers, sysinfo)
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
                           "", "", wildcard,
                           style=wx.FD_OPEN
                           | wx.FD_MULTIPLE
                           | wx.FD_FILE_MUST_EXIST
                           | wx.FD_PREVIEW) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return
            paths = filedlg.GetPaths()
            for path in paths:
                self.fileDnDTarget.flCtrl.dropUpdate(path)
    # -------------------------------------------------------------------#

    def openMyconversions(self, event):
        """
        Open the conversions folder with file manager
        """
        io_tools.openpath(self.appdata['outputfile'])
    # -------------------------------------------------------------------#

    def openMyconversions_tmp(self, event):
        """
        Open the temporary conversions folder with file manager
        """
        io_tools.openpath(self.outputpath)
    # -------------------------------------------------------------------#

    def on_file_renaming(self, event):
        """
        One file renaming
        """
        self.fileDnDTarget.renaming_file()
    # -------------------------------------------------------------------#

    def on_batch_renaming(self, event):
        """
        Batch file renaming
        """
        self.fileDnDTarget.renaming_batch_files()
    # -------------------------------------------------------------------#

    def open_trash_folder(self, event):
        """
        Open Videomass trash folder if it exists
        """
        path = self.appdata['trash_dir']
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
        path = self.appdata['trash_dir']
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
        if self.helptopic:
            self.helptopic.Raise()
            return
        self.helptopic = FFmpegHelp(self, self.appdata['ostype'])
        self.helptopic.Show()
    # -------------------------------------------------------------------#

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
            return

        latest = sum((int(x) for x in newversion[0][1:].split('.')))
        current = sum((int(x) for x in fread.split('.')))
        if latest > current:
            wx.MessageBox(_("Installed release v{0}. A new presets release "
                            "is available {1}").format(fread, newversion[0]),
                          "Videomass", wx.ICON_INFORMATION, self)
        else:
            wx.MessageBox(_("Installed release v{0}. No new updates "
                            "found.").format(fread),
                          "Videomass", wx.ICON_INFORMATION, self)
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

    def get_ffmpeg_conf(self, event):
        """
        Show miniframe to check the ffmpeg configuration state.
        """
        if self.ffmpegconf:
            self.ffmpegconf.Raise()
            return

        out = io_tools.test_conf()
        if 'Not found' in out[0]:
            wx.MessageBox(f"\n{out[1]}", "Videomass",
                          wx.ICON_ERROR, self)
            return
        self.ffmpegconf = FFmpegConf(out,
                                     self.appdata['ffmpeg_cmd'],
                                     self.appdata['ffprobe_cmd'],
                                     self.appdata['ffplay_cmd'],
                                     self.appdata['ostype'],
                                     )
        self.ffmpegconf.Show()
    # ------------------------------------------------------------------#

    def get_ffmpeg_formats(self, event):
        """
        Show miniframe to check the ffmpeg supported formats.
        """
        if self.ffmpegformats:
            self.ffmpegformats.Raise()
            return

        out = io_tools.test_formats()
        if 'Not found' in out:
            wx.MessageBox(f"\n{out['Not found']}", "Videomass",
                          wx.ICON_ERROR, self)
            return
        self.ffmpegformats = FFmpegFormats(out, self.appdata['ostype'])
        self.ffmpegformats.Show()
    # ------------------------------------------------------------------#

    def get_ffmpeg_codecs(self, event):
        """
        Show miniframe to check the ffmpeg supported codecs.
        Shares the same window as `get_ffmpeg_decoders`
        """
        if self.ffmpegcodecs:
            self.ffmpegcodecs.Raise()
            return

        out = io_tools.test_codecs('-encoders')
        if 'Not found' in out:
            wx.MessageBox(f"\n{out['Not found']}", "Videomass",
                          wx.ICON_ERROR, self)
            return
        self.ffmpegcodecs = FFmpegCodecs(out,
                                         self.appdata['ostype'],
                                         '-encoders')
        self.ffmpegcodecs.Show()
    # ------------------------------------------------------------------#

    def get_ffmpeg_decoders(self, event):
        """
        Show miniframe to check the ffmpeg supported decoders.
        Shares the same window as `get_ffmpeg_codecs`
        """
        if self.ffmpegdecoders:
            self.ffmpegdecoders.Raise()
            return

        out = io_tools.test_codecs('-decoders')
        if 'Not found' in out:
            wx.MessageBox(f"\n{out['Not found']}", "Videomass",
                          wx.ICON_ERROR, self)
            return
        self.ffmpegdecoders = FFmpegCodecs(out,
                                           self.appdata['ostype'],
                                           '-decoders')
        self.ffmpegdecoders.Show()
    # ------------------------------------------------------------------#

    def durinPlayng(self, event):
        """
        FFplay submenu:
        show dialog with shortcuts keyboard for FFplay
        """
        if self.whileplay:
            self.whileplay.Raise()
            return
        self.whileplay = WhilePlaying(self.appdata['ostype'])
        self.whileplay.Show()
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
        self.autoexit = self.exitplayback.IsChecked()
    # ------------------------------------------------------------------#

    def View_logs(self, event):
        """
        Show to view log files dialog
        """
        if self.showlogs:
            self.showlogs.Raise()
            return
        self.showlogs = ShowLogs(self,
                                 self.appdata['logdir'],
                                 self.appdata['ostype'],
                                 )
        self.showlogs.Show()
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

    def on_destpath_setup(self, event):
        """
        This is a menu event but also intercept the button 'save'
        event in the filedrop panel and sets a new file destination
        path for conversions
        """
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "conversions"), self.outputpath,
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.outputpath = getpath
            self.fileDnDTarget.on_file_save(self.outputpath)
            dialdir.Destroy()

            self.resetfolders_tmp.Enable(True)
            self.fold_convers_tmp.Enable(True)
    # ------------------------------------------------------------------#

    def on_Resetfolders_tmp(self, event):
        """
        Restore the default file destination if saving temporary
        files has been set. For file conversions it has no effect
        if `self.same_destin` is True.
        """
        if not self.same_destin:
            self.outputpath = self.appdata['outputfile']
            self.fileDnDTarget.on_file_save(self.appdata['outputfile'])
            self.fold_convers_tmp.Enable(False)
            self.resetfolders_tmp.Enable(False)
            wx.MessageBox(_("Default destination folders "
                            "successfully restored"), "Videomass",
                          wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def Setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Videomass, being need
        to get the return code from getvalue interface.
        """
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                if set_up.getvalue():
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

        version = version[0].split('v')[1]
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
                                                      this[2],
                                                      )
        dlg.ShowModal()
    # -------------------------------------------------------------------#

    def system_vers(self, event):
        """
        Get system version
        """
        wx.MessageBox(info_this_platform(), "Videomass",
                      wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def Info(self, event):
        """
        Display the program informations and developpers
        """
        about.aboutdlg(self, self.icons['videomass'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def videomass_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.
            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        if self.appdata['toolbarpos'] == 0:  # on top
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL
            else:
                style = wx.TB_DEFAULT_STYLE

        elif self.appdata['toolbarpos'] == 1:  # on bottom
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_BOTTOM

        elif self.appdata['toolbarpos'] == 2:  # on right
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_RIGHT
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_RIGHT

        elif self.appdata['toolbarpos'] == 3:
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_LEFT
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_LEFT

        self.toolbar = self.CreateToolBar(style=style)

        bmp_size = (int(self.appdata['toolbarsize']),
                    int(self.appdata['toolbarsize']))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpback = get_bmp(self.icons['previous'], bmp_size)
            bmpnext = get_bmp(self.icons['next'], bmp_size)
            bmpinfo = get_bmp(self.icons['fileproperties'], bmp_size)
            bmpconv = get_bmp(self.icons['startconv'], bmp_size)
            bmpstop = get_bmp(self.icons['stop'], bmp_size)
            bmphome = get_bmp(self.icons['home'], bmp_size)
            bmplog = get_bmp(self.icons['logpan'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpinfo = wx.Bitmap(self.icons['fileproperties'],
                                wx.BITMAP_TYPE_ANY)
            bmpconv = wx.Bitmap(self.icons['startconv'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmphome = wx.Bitmap(self.icons['home'], wx.BITMAP_TYPE_ANY)
            bmplog = wx.Bitmap(self.icons['logpan'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
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
        tip = _("Go to the 'Home' panel")
        home = self.toolbar.AddTool(16, _('Home'),
                                    bmphome,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Keeps track of the output for debugging errors")
        logpan = self.toolbar.AddTool(18, _('Output Monitor'),
                                      bmplog,
                                      tip, wx.ITEM_NORMAL
                                      )
        # self.toolbar.AddSeparator()
        # self.toolbar.AddStretchableSpace()
        tip = _("Get informative data about imported media streams")
        self.btn_steams = self.toolbar.AddTool(5, _('Media Details'),
                                               bmpinfo,
                                               tip, wx.ITEM_NORMAL
                                               )
        tip = _("Start rendering")
        self.run_coding = self.toolbar.AddTool(12, _('Start'),
                                               bmpconv,
                                               tip, wx.ITEM_NORMAL
                                               )

        tip = _("Stops current process")
        stop_coding = self.toolbar.AddTool(14, _('Abort'),
                                           bmpstop,
                                           tip, wx.ITEM_NORMAL
                                           )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.startPan, home)
        self.Bind(wx.EVT_TOOL, self.logPan, logpan)
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_coding)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop_coding)
        self.Bind(wx.EVT_TOOL, self.on_Back, back)
        self.Bind(wx.EVT_TOOL, self.on_Forward, forward)
        self.Bind(wx.EVT_TOOL, self.media_streams, self.btn_steams)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_Back(self, event):
        """
        Return to the previous panel.
        """
        if self.ProcessPanel.IsShown():
            self.panelShown(self.ProcessPanel.previus)
            return

        if self.fileDnDTarget.IsShown():
            self.choosetopicRetrieve()

        elif self.topicname in ('Audio/Video Conversions',
                                'Presets Manager',
                                'Concatenate Demuxer',
                                'Image Sequence to Video',
                                'Video to Pictures'):
            self.switch_file_import(self, self.topicname)
    # ------------------------------------------------------------------#

    def on_Forward(self, event):
        """
        redirect on corresponding panel
        """
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
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
    # ------------------------------------------------------------------#

    def on_changes_file_list(self):
        """
        Check changes made to files list in the drag-and-drop panel.
        """
        if not self.changed:
            pub.sendMessage("MAX_FILE_DURATION", msg='Changes')
            self.changed = self.file_src.copy()
            self.statusbar_msg(_('Ready'), None)

        elif self.changed == self.file_src:
            self.statusbar_msg(_('Ready'), None)
        else:
            pub.sendMessage("RESET_ON_CHANGED_LIST", msg='Changes')
            pub.sendMessage("MAX_FILE_DURATION", msg='Changes')
            self.changed = self.file_src.copy()
            msg = (_('File list changed, please check the settings again.'),
                   MainFrame.ORANGE, MainFrame.WHITE)
            self.statusbar_msg(msg[0], msg[1], msg[2])
    # ------------------------------------------------------------------#

    def switch_file_import(self, event, which):
        """
        Show files import panel.
        """
        self.topicname = which
        self.VconvPanel.Hide()
        self.ChooseTopic.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.fileDnDTarget.Show()
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(True)
        self.avpan.Enable(False)
        self.prstpan.Enable(False)
        self.startpan.Enable(True)
        self.concpan.Enable(False)
        self.toseq.Enable(False)
        self.slides.Enable(False)
        self.toolbar.Show()
        self.logpan.Enable(False)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, True)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, False)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, False)
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - Queued Files'))
    # ------------------------------------------------------------------#

    def switch_av_conversions(self, event):
        """
        Show Video converter panel
        """
        self.fileDnDTarget.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.VconvPanel.Show()
        self.on_changes_file_list()  # file list changed
        self.SetTitle(_('Videomass - AV Conversions'))
        self.TimeLine.Show()
        self.toolbar.Show()
        self.menu_items()  # disable some menu items
        self.openmedia.Enable(True)
        self.avpan.Enable(False)
        self.prstpan.Enable(True)
        self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_presets_manager(self, event):
        """
        Show presets manager panel
        """
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.PrstsPanel.Show()
        self.on_changes_file_list()  # file list changed
        self.SetTitle(_('Videomass - Presets Manager'))
        self.TimeLine.Show()
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(False)
        self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, True)
        self.Layout()
        self.PrstsPanel.update_preset_state()
    # ------------------------------------------------------------------#

    def switch_concat_demuxer(self, event):
        """
        Show concat demuxer panel
        """
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Show()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.TimeLine.Hide()
        self.on_changes_file_list()  # file list changed
        self.SetTitle(_('Videomass - Concatenate Demuxer'))
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(False)
        self.toseq.Enable(True)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_video_to_pictures(self, event):
        """
        Show  Video to Pictures panel
        """
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toSlideshow.Hide()
        self.toPictures.Show()
        self.on_changes_file_list()  # file list changed
        self.SetTitle(_('Videomass - From Movie to Pictures'))
        self.TimeLine.Show()
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(False)
        self.slides.Enable(True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_slideshow_maker(self, event):
        """
        Show slideshow maker panel
        """
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Show()
        self.on_changes_file_list()  # file list changed
        self.SetTitle(_('Videomass - Still Image Maker'))
        self.TimeLine.Show()
        self.toolbar.Show()
        self.openmedia.Enable(True)
        self.avpan.Enable(True)
        self.prstpan.Enable(True)
        self.startpan.Enable(True)
        self.logpan.Enable(True)
        self.concpan.Enable(True)
        self.toseq.Enable(True)
        self.slides.Enable(False)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(12, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(18, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *args):
        """
        Call the `ProcessPanel.topic_thread` instance method
        (Monitor Output) assigning the corresponding thread.
        """
        if args[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            dur, seq = self.duration, self.time_seq
        elif args[0] in ('concat_demuxer', 'sequence_to_video'):
            dur, seq = args[6], ''
        elif self.time_seq != "-ss 00:00:00.000 -t 00:00:00.000":
            ms = get_milliseconds(self.time_seq.split()[3])  # -t duration
            seq = self.time_seq
            if [t for t in self.duration if ms > t]:  # if out time range
                wx.MessageBox(_('Cannot continue: The duration in the '
                                'timeline exceeds the duration of some '
                                'queued files.'),
                              'Videomass', wx.ICON_ERROR, self)
                return
            dur = [ms for n in self.duration]
            self.statusbar_msg(_('Processing...'), None)
        else:
            dur, seq = self.duration, ''

        self.SetTitle(_('Videomass - Output Monitor'))
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.TimeLine.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ProcessPanel.Show()
        if not args[0] == 'Viewing last log':
            [self.menuBar.EnableTop(x, False) for x in range(3, 5)]
            self.openmedia.Enable(False)
            # self.toolbar Hide/Show items
            self.toolbar.EnableTool(3, False)
            self.toolbar.EnableTool(4, False)
            self.toolbar.EnableTool(5, True)
            self.toolbar.EnableTool(14, True)  # stop
            self.toolbar.EnableTool(16, False)  # home
        self.toolbar.EnableTool(12, False)  # rendering
        self.toolbar.EnableTool(18, False)

        self.ProcessPanel.topic_thread(self.topicname, dur, seq, *args)
        self.Layout()
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        Clicking on Convert buttons, calls the `on_start method`
        of the corresponding class panel shown, which calls the
        'switch_to_processing' method above.
        """
        if not self.data_files:
            if self.ProcessPanel.IsShown():
                self.ProcessPanel.Hide()
            self.switch_file_import(self, self.topicname)
            return

        if self.VconvPanel.IsShown():
            self.VconvPanel.on_start()
        elif self.PrstsPanel.IsShown():
            self.PrstsPanel.on_start()
        elif self.ConcatDemuxer.IsShown():
            self.ConcatDemuxer.on_start()
        elif self.toPictures.IsShown():
            self.toPictures.on_start()
        elif self.toSlideshow.IsShown():
            self.toSlideshow.on_start()
    # ------------------------------------------------------------------#

    def click_stop(self, event):
        """
        Stop/Abort the current process
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type:
                self.ProcessPanel.on_stop()
    # ------------------------------------------------------------------#

    def process_terminated(self, msg):
        """
        Process report terminated. This method is called using
        pub/sub protocol. see `long_processing_task.end_proc()`)
        """
        # Enable all top menu bar:
        [self.menuBar.EnableTop(x, True) for x in range(3, 5)]
        # enable toolbar items
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(4, False)
        self.toolbar.EnableTool(5, True)
        self.toolbar.EnableTool(14, False)
        self.toolbar.EnableTool(16, True)
        if self.emptylist:
            self.fileDnDTarget.delete_all(self)
    # ------------------------------------------------------------------#

    def panelShown(self, panelshown=None):
        """
        Closing the `long_processing_task` panel,
        retrieval at previous panel shown.
        (see `switch_to_processing` method above).
        """
        self.ProcessPanel.Hide()
        if panelshown == 'Audio/Video Conversions':
            self.switch_av_conversions(self)
        elif panelshown == 'Presets Manager':
            self.switch_presets_manager(self)
        elif panelshown == 'Concatenate Demuxer':
            self.switch_concat_demuxer(self)
        elif panelshown == 'Video to Pictures':
            self.switch_video_to_pictures(self)
        elif panelshown == 'Image Sequence to Video':
            self.switch_slideshow_maker(self)
        self.Layout()
