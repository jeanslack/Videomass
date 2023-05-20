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
from videomass.vdms_dialogs.while_playing import WhilePlaying
from videomass.vdms_dialogs.ffmpeg_conf import FFmpegConf
from videomass.vdms_dialogs.ffmpeg_codecs import FFmpegCodecs
from videomass.vdms_dialogs.ffmpeg_formats import FFmpegFormats
from videomass.vdms_ytdlp.main_ytdlp import MainYtdl
from videomass.vdms_dialogs.mediainfo import MediaStreams
from videomass.vdms_dialogs.showlogs import ShowLogs
from videomass.vdms_dialogs.ffmpeg_help import FFmpegHelp
from videomass.vdms_miniframes import timeline
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
    This is the main frame top window for panels
    implementation and/or other children frames.
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
    # -------------------------------------------------------------#

    def __init__(self):
        """
        Note, self.topic name attr must be None on Start panel,
        see `startPanel` event handler, it is the panel that
        should be shown at startup.
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.icons = get.iconset
        # -------------------------------#
        self.data_files = []  # list of items in list control
        self.outputpath = self.appdata['outputfile']  # path destination
        self.outputnames = []  # output file basenames (even renames)
        self.file_src = []  # input full file names list
        self.same_destin = self.appdata['outputfile_samedir']  # True/False
        self.suffix = self.appdata['filesuffix']  # suffix to output names
        self.filedropselected = None  # int(index) or None filedrop selected
        self.time_seq = ""  # FFmpeg time seq.
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
        self.ytdlframe = False
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

        # panel instances:
        self.ChooseTopic = choose_topic.Choose_Topic(self,
                                                     self.appdata['ostype'],
                                                     )
        self.VconvPanel = av_conversions.AV_Conv(self,
                                                 self.appdata,
                                                 self.icons,
                                                 )
        self.fileDnDTarget = filedrop.FileDnD(self,
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
        # miniframes
        self.TimeLine = timeline.Float_TL(parent=wx.GetTopLevelParent(self))
        self.TimeLine.Hide()
        # hide all panels
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.ProcessPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        # global sizer base
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        # Layout external panels:
        self.mainSizer.Add(self.ChooseTopic, 1, wx.EXPAND)
        self.mainSizer.Add(self.fileDnDTarget, 1, wx.EXPAND)
        self.mainSizer.Add(self.VconvPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.PrstsPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.ConcatDemuxer, 1, wx.EXPAND)
        self.mainSizer.Add(self.toPictures, 1, wx.EXPAND)
        self.mainSizer.Add(self.toSlideshow, 1, wx.EXPAND)

        # Set frame properties
        self.SetTitle("Videomass")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['videomass'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((850, 560))
        self.SetSizer(self.mainSizer)
        self.Fit()
        self.SetSize(tuple(self.appdata['main_window_size']))
        self.Move(tuple(self.appdata['main_window_pos']))
        # create menu bar
        self.videomass_menu_bar()
        # cretae tool bar
        self.videomass_tool_bar()
        # create status bar
        self.sb = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'), None)
        # disabling toolbar/menu items
        [self.toolbar.EnableTool(x, False) for x in (3, 4, 5, 6, 7, 8, 9, 35)]
        self.menu_items(enable=False)
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

    def menu_items(self, enable=True):
        """
        enable or disable some menu items in
        according by showing panels
        """
        if enable:
            self.avpan.Enable(True)
            self.prstpan.Enable(True)
            self.concpan.Enable(True)
            self.toseq.Enable(True)
            self.slides.Enable(True)
            self.startpan.Enable(True)
            self.logpan.Enable(True)
        else:
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
        Receives a message from a modeless window close event.
        This method is called using pub/sub protocol subscribing
        "DESTROY_ORPHANED_WINDOWS".
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
        Where possible, it destroys the application and
        its children programmatically, saving the size
        and position of the window.
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type is not None:
                wx.MessageBox(_('There are still processes running. if you '
                                'want to stop them, use the "Abort" button.'),
                              _('Videomass'), wx.ICON_WARNING, self)
                return

        if self.appdata['warnexiting']:
            if wx.MessageBox(_('Are you sure you want to exit '
                               'the application?'),
                             _('Exit'), wx.ICON_QUESTION | wx.CANCEL
                             | wx.YES_NO, self) != wx.YES:
                return

        if self.ytdlframe:
            if self.ytdlframe.ProcessPanel.thread_type:
                wx.MessageBox(_("There are still active windows with running "
                                "processes, make sure you finish your work "
                                "before closing them."),
                              "Videomass", wx.ICON_WARNING, self)
                return
            self.ytdlframe.on_exit(self, warn=False)

        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        sett['main_window_size'] = list(self.GetSize())
        sett['main_window_pos'] = list(self.GetPosition())
        confmanager.write_options(**sett)
        self.destroy_orphaned_window()
        self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        This method tries to destroy the application and its
        children more directly than the `on_close` method above.
        Note that this method may also be called from the `Setup()`
        method.
        """
        if self.ytdlframe:
            if self.ytdlframe.ProcessPanel.thread_type:
                wx.MessageBox(_("There are still active windows with running "
                                "processes, make sure you finish your work "
                                "before closing them."),
                              "Videomass", wx.ICON_WARNING, self)
                return
            self.ytdlframe.destroy_orphaned_window()
        self.destroy_orphaned_window()
        self.Destroy()

    # -------------   BUILD THE MENU BAR  ----------------###

    def videomass_menu_bar(self):
        """
        Make the menu bar.
        For disabling or enabling the menu items in methods or
        event handlers in a class of type Frame, you first set
        a `self` attribute on an item.

        Disabling/Enabling a single item a time:

            `self.item.Enable(False)`

        to disable it or `True` to enable it.

        If you want to disable a single top item:

            `self.menuBar.EnableTop(0, False)`  # dis. the first item

        To disable the entire top of items, use range func:
            `[self.menuBar.EnableTop(x, False) for x in range(0, to n)`

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
        dscrp = (_("Open Trash folder"),
                 _("Open the Videomass Trash folder if it exists"))
        dir_trash = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Empty Trash folder"),
                 _("Delete all files in the Videomass Trash folder"))
        empty_trash = fileButton.Append(wx.ID_DELETE, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Work Notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Completely exit the application"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ Edit menu
        editButton = wx.Menu()
        dscrp = (_("Remove selected file\tDEL"),
                 _("Remove the selected files from the list"))
        self.delfile = editButton.Append(wx.ID_REMOVE, dscrp[0], dscrp[1])
        self.menuBar.Append(editButton, _("Edit"))
        self.delfile.Enable(False)

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("Find FFmpeg topics and options"),
                 _("A useful tool to search for FFmpeg help topics and "
                   "options"))
        searchtopic = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
        prstpage = '<https://github.com/jeanslack/Videomass-presets>'
        dscrp = (_("Check for preset updates"),
                 _("Check for new presets updates from {0}").format(prstpage))
        self.prstcheck = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Get the latest presets"),
                 _("Get the latest presets from {0}").format(prstpage))
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

        viewButton.AppendSeparator()
        dscrp = (_("Show timeline\tCtrl+T"),
                 _("Show timeline editor"))
        self.viewtimeline = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                              kind=wx.ITEM_CHECK)
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
        self.winytdlp = goButton.Append(wx.ID_ANY,
                                        _("YouTube Downloader\tCtrl+Shift+Y"),
                                        _("Open 'YouTube Downloader' window"))
        goButton.AppendSeparator()
        dscrp = (_("Output Monitor\tCtrl+Shift+O"),
                 _("Keeps track of the output for debugging errors"))
        self.logpan = goButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
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
        self.Bind(wx.EVT_MENU, self.open_trash_folder, dir_trash)
        self.Bind(wx.EVT_MENU, self.empty_trash_folder, empty_trash)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        # ----EDIT----
        self.Bind(wx.EVT_MENU, self.fileDnDTarget.on_delete_selected,
                  self.delfile)
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
        self.Bind(wx.EVT_MENU, self.view_Timeline, self.viewtimeline)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPanel, self.startpan)
        self.Bind(wx.EVT_MENU, self.switch_presets_manager, self.prstpan)
        self.Bind(wx.EVT_MENU, self.switch_av_conversions, self.avpan)
        self.Bind(wx.EVT_MENU, self.switch_concat_demuxer, self.concpan)
        self.Bind(wx.EVT_MENU, self.switch_slideshow_maker, self.slides)
        self.Bind(wx.EVT_MENU, self.switch_video_to_pictures, self.toseq)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        self.Bind(wx.EVT_MENU, self.youtubedl, self.winytdlp)
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

            self.switch_file_import(self)
            paths = filedlg.GetPaths()
            for path in paths:
                self.fileDnDTarget.flCtrl.dropUpdate(path)
            self.fileDnDTarget.flCtrl.rejected_files()
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
        path = self.appdata['user_trashdir']
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
        path = self.appdata['user_trashdir']
        if os.path.exists(path):
            files = os.listdir(path)
            if len(files) > 0:
                if wx.MessageBox(_("Are you sure to empty trash folder?"),
                                 "Videomass", wx.ICON_QUESTION | wx.CANCEL
                                 | wx.YES_NO, self) != wx.YES:
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
        download = io_tools.get_presets(tarball[0],
                                        pathname,
                                        msg,
                                        parent=self.GetParent(),
                                        )

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
            with open(fname, "w", encoding='utf8') as text:
                text.write("")
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

    def view_Timeline(self, event):
        """
        View menu: show timeline via menu bar
        """
        if self.viewtimeline.IsChecked():
            self.TimeLine.Show()
        else:
            self.TimeLine.Hide()
    # ------------------------------------------------------------------#
    # --------- Menu  Go  ###

    def logPan(self, event):
        """
        view last log on console
        """
        self.switch_to_processing('Viewing last log')
    # ------------------------------------------------------------------#
    # --------- Menu  Preferences  ###

    def on_destpath_setup(self, event):
        """
        This is a menu event and a filedrop button event.
        It sets a new file destination path for conversions
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

    def Setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Videomass, being need
        to get the return code from getvalue interface.
        """
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                if self.ProcessPanel.IsShown():
                    if self.ProcessPanel.thread_type is not None:
                        wx.MessageBox(_("Changes will take effect once the "
                                        "program has been restarted."),
                                      _('Videomass'), wx.ICON_WARNING, self)
                        return
                if wx.MessageBox(_("Changes will take effect once the program "
                                   "has been restarted.\n\n"
                                   "Do you want to exit the application now?"),
                                 _('Exit'), wx.ICON_QUESTION | wx.CANCEL
                                 | wx.YES_NO, self) == wx.YES:
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

    def get_toolbar_pos(self):
        """
        Get toolbar position properties according to
        the user preferences.
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

        return style
    # ------------------------------------------------------------------#

    def videomass_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.
            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)

        """
        style = self.get_toolbar_pos()
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
            bmpclear = get_bmp(self.icons['cleanup'], bmp_size)
            bmpplay = get_bmp(self.icons['play'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpinfo = wx.Bitmap(self.icons['fileproperties'],
                                wx.BITMAP_TYPE_ANY)
            bmpconv = wx.Bitmap(self.icons['startconv'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmphome = wx.Bitmap(self.icons['home'], wx.BITMAP_TYPE_ANY)
            bmpclear = wx.Bitmap(self.icons['cleanup'], wx.BITMAP_TYPE_ANY)
            bmpplay = wx.Bitmap(self.icons['play'], wx.BITMAP_TYPE_ANY)

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
        home = self.toolbar.AddTool(5, _('Home'),
                                    bmphome,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Play the selected file in the list")
        play = self.toolbar.AddTool(35, _('Play'),
                                    bmpplay,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Get informative data about imported media streams")
        self.btn_streams = self.toolbar.AddTool(6, _('Properties'),
                                                bmpinfo,
                                                tip, wx.ITEM_NORMAL
                                                )
        tip = _("Start rendering")
        self.run_coding = self.toolbar.AddTool(7, _('Run'),
                                               bmpconv,
                                               tip, wx.ITEM_NORMAL
                                               )
        tip = _("Stops current process")
        stop_coding = self.toolbar.AddTool(8, _('Abort'),
                                           bmpstop,
                                           tip, wx.ITEM_NORMAL
                                           )
        tip = _("Delete all files from the list")
        clear = self.toolbar.AddTool(9, _('Clear'),
                                     bmpclear,
                                     tip, wx.ITEM_NORMAL
                                     )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.startPanel, home)
        self.Bind(wx.EVT_TOOL, self.fileDnDTarget.delete_all, clear)
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_coding)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop_coding)
        self.Bind(wx.EVT_TOOL, self.on_Back, back)
        self.Bind(wx.EVT_TOOL, self.on_Forward, forward)
        self.Bind(wx.EVT_TOOL, self.media_streams, self.btn_streams)
        self.Bind(wx.EVT_TOOL, self.fileDnDTarget.on_play_select, play)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_Back(self, event):
        """
        Click Back toolbar button event
        """
        if self.ProcessPanel.IsShown():
            self.panelShown(self.ProcessPanel.previus)
            return

        if self.fileDnDTarget.IsShown():
            self.startPanel(self)
        else:
            self.switch_file_import(self)
    # ------------------------------------------------------------------#

    def on_Forward(self, event):
        """
        Click Next toolbar button event
        """
        if self.fileDnDTarget.IsShown():
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
        else:
            self.switch_to_processing('Viewing last log')
    # ------------------------------------------------------------------#

    def startPanel(self, event):
        """
        Shared event from the menu bar and the "Home" toolbar
        button to switch at the Home panel.
        Note, this event could be called indirectly from the
        "Back" toolbar button.
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type:
                return
            self.ProcessPanel.Hide()

        self.topicname = None
        self.fileDnDTarget.Hide()

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

        [self.toolbar.EnableTool(x, False) for x in (3, 4, 5, 6, 7, 8, 9, 35)]
        self.ChooseTopic.Show()
        self.openmedia.Enable(False)
        self.menu_items(enable=False)
        self.delfile.Enable(False)
        self.SetTitle(_('Videomass'))
        self.statusbar_msg(_('Ready'), None)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_file_import(self, event):
        """
        Shared event by manubar and toolbar
        to switch on Drag&Drop panel.
        """
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.VconvPanel.Hide()
        self.ChooseTopic.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.fileDnDTarget.Show()
        pub.sendMessage("SET_DRAG_AND_DROP_TOPIC", topic=self.topicname)
        self.menu_items(enable=False)  # disable menu items
        self.delfile.Enable(True)
        self.openmedia.Enable(True)
        if self.file_src:
            [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 9, 35)]
            [self.toolbar.EnableTool(x, False) for x in (7, 8)]
        else:
            [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 35)]
            [self.toolbar.EnableTool(x, False) for x in (7, 8, 9)]
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - Queued Files'))
    # ------------------------------------------------------------------#

    def switch_av_conversions(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show Video converter panel
        """
        self.topicname = 'Audio/Video Conversions'
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.VconvPanel.Show()
        self.SetTitle(_('Videomass - AV Conversions'))
        self.menu_items(enable=True)  # enable all menu items
        self.delfile.Enable(False)
        self.openmedia.Enable(True)
        self.avpan.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 9)]
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_presets_manager(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show presets manager panel
        """
        self.topicname = 'Presets Manager'
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.PrstsPanel.Show()
        self.SetTitle(_('Videomass - Presets Manager'))
        self.menu_items(enable=True)  # enable all menu items
        self.delfile.Enable(False)
        self.openmedia.Enable(True)
        self.prstpan.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 9)]
        self.Layout()
        self.PrstsPanel.update_preset_state()
    # ------------------------------------------------------------------#

    def switch_concat_demuxer(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `ConcatDemuxer` panel
        """
        self.topicname = 'Concatenate Demuxer'
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ConcatDemuxer.Show()
        self.SetTitle(_('Videomass - Concatenate Demuxer'))
        self.menu_items(enable=True)  # enable all menu items
        self.delfile.Enable(False)
        self.openmedia.Enable(True)
        self.concpan.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 9)]
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_video_to_pictures(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `toPictures` panel
        """
        self.topicname = 'Video to Pictures'
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toSlideshow.Hide()
        self.toPictures.Show()
        self.SetTitle(_('Videomass - From Movie to Pictures'))
        self.menu_items(enable=True)  # enable all menu items
        self.delfile.Enable(False)
        self.openmedia.Enable(True)
        self.toseq.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 9)]
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_slideshow_maker(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `toSlideshow` panel
        """
        self.topicname = 'Image Sequence to Video'
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Show()
        self.SetTitle(_('Videomass - Still Image Maker'))
        self.menu_items(enable=True)  # enable all menu items
        self.delfile.Enable(False)
        self.openmedia.Enable(True)
        self.slides.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 9)]
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *args):
        """
        This method is called by start methods of any
        topic. It call `ProcessPanel.topic_thread`
        method assigning the corresponding thread.
        """
        if args[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            dur, seq = self.duration, self.time_seq
        elif args[0] in ('concat_demuxer', 'sequence_to_video'):
            dur, seq = args[6], ''
        elif self.time_seq:
            ms = get_milliseconds(self.time_seq.split()[3])  # -t duration
            seq = self.time_seq
            dur = [ms for n in self.duration]
            self.statusbar_msg(_('Processing...'), None)
        else:
            dur, seq = self.duration, ''

        self.SetTitle(_('Videomass - FFmpeg message monitor'))
        self.fileDnDTarget.Hide()
        self.VconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ProcessPanel.Show()
        if not args[0] == 'Viewing last log':
            self.delfile.Enable(False)
            self.menu_items(enable=False)  # disable menu items
            self.openmedia.Enable(False)
            [self.toolbar.EnableTool(x, True) for x in (6, 8)]
            [self.toolbar.EnableTool(x, False) for x in (3, 5)]
        self.logpan.Enable(False)
        [self.toolbar.EnableTool(x, False) for x in (4, 7, 9)]

        self.ProcessPanel.topic_thread(self.topicname, dur, seq, *args)
        self.Layout()
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        Click Start toolbar event, calls the `on_start` method
        of the corresponding class panel shown, which calls the
        'switch_to_processing' method above.
        """
        if not self.data_files:
            self.switch_file_import(self)
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
        Click stop toolbar event, set to abort True the current process
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
        self.menu_items(enable=True)  # enable all menu items
        self.openmedia.Enable(False)
        [self.toolbar.EnableTool(x, True) for x in (3, 5)]
        self.toolbar.EnableTool(8, False)

        if self.emptylist:
            self.fileDnDTarget.delete_all(self)
    # ------------------------------------------------------------------#

    def panelShown(self, panelshown=None):
        """
        Closing the `long_processing_task` panel, retrieval at previous
        panel shown (see `switch_to_processing` method above).
        """
        self.logpan.Enable(True)  # menu item
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
    # ------------------------------------------------------------------#

    def youtubedl(self, event):
        """
        Start a separate, self-contained frame
        for yt-dlp GUI functionality.
        """
        if self.ytdlframe:
            if not self.ytdlframe.IsShown():
                self.ytdlframe.Show()
            self.ytdlframe.Raise()
            return
        self.ytdlframe = MainYtdl(parent=wx.GetTopLevelParent(self))
        self.ytdlframe.Show()
