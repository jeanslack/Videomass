# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.20.2025
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
from videomass.vdms_utils.queue_utils import load_json_file_queue
from videomass.vdms_utils.queue_utils import write_json_file_queue
from videomass.vdms_utils.queue_utils import extend_data_queue
from videomass.vdms_dialogs import preferences
from videomass.vdms_dialogs import set_timestamp
from videomass.vdms_dialogs import about_dialog
from videomass.vdms_dialogs import videomass_check_version
from videomass.vdms_dialogs.while_playing import WhilePlaying
from videomass.vdms_dialogs.ffmpeg_conf import FFmpegConf
from videomass.vdms_dialogs.ffmpeg_codecs import FFmpegCodecs
from videomass.vdms_dialogs.ffmpeg_formats import FFmpegFormats
from videomass.vdms_dialogs.queuedlg import QueueManager
from videomass.vdms_dialogs.mediainfo import MediaStreams
from videomass.vdms_dialogs.showlogs import ShowLogs
from videomass.vdms_dialogs.ffmpeg_help import FFmpegHelp
from videomass.vdms_dialogs.widget_utils import CountDownDlg
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
from videomass.vdms_sys.about_app import VERSION
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_sys.argparser import info_this_platform
from videomass.vdms_utils.utils import copydir_recursively
from videomass.vdms_threads.shutdown import shutdown_system


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

    def __init__(self, appdata):
        """
        Note, self.topic name attr must be None on Start panel,
        see `startPanel` event handler, it is the panel that
        should be shown at startup.
        """
        get = wx.GetApp()
        self.appdata = appdata
        self.icons = get.iconset
        # -------------------------------#
        self.data_files = []  # list of items in list control
        self.outputnames = []  # output file basenames (even renames)
        self.file_src = []  # input full file names list
        self.filedropselected = None  # int(index) or None filedrop selected
        self.time_seq = ""  # FFmpeg time seq.
        self.duration = []  # empty if not file imported
        self.topicname = None  # shown panel name
        self.checktimestamp = True  # show timestamp during playback
        self.autoexit = True  # set autoexit during ffplay playback
        self.movetotrash = self.appdata['move_file_to_trash']  # boolean
        self.emptylist = self.appdata['move_file_to_trash']  # boolean
        self.queuelist = None  # list data to process queue
        self.removequeue = True  # Remove items queue when finished
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
        fontsize = "fontsize=h/10:x=(w-text_w)/2:y=(h-text_h*2)"  # autosize
        # set command line for timestamp
        ptshms = r"%{pts\:hms}"
        self.cmdtimestamp = (
            f"drawtext=fontfile='{tsfont}':text='{ptshms}':fontcolor=White:"
            f"shadowcolor=Black:shadowx=1:shadowy=1:{fontsize}:"
            f"box=1:boxcolor=DeepPink:x=(w-tw)/2:y=h-(2*lh)")

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # panel instances:
        self.ChooseTopic = choose_topic.Choose_Topic(self)
        self.AVconvPanel = av_conversions.AV_Conv(self)
        self.fileDnDTarget = filedrop.FileDnD(self,
                                              self.outputnames,
                                              self.data_files,
                                              self.file_src,
                                              self.duration,
                                              )
        self.ProcessPanel = LogOut(self)
        self.PrstsPanel = presets_manager.PrstPan(self)
        self.ConcatDemuxer = concatenate.Conc_Demuxer(self)
        self.toPictures = video_to_sequence.VideoToSequence(self)
        self.toSlideshow = sequence_to_video.SequenceToVideo(self)
        # miniframes
        self.TimeLine = timeline.Float_TL(parent=wx.GetTopLevelParent(self))
        self.TimeLine.Hide()
        # hide all panels
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
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
        self.mainSizer.Add(self.AVconvPanel, 1, wx.EXPAND)
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
        self.SetMinSize((1070, 685))  # ideal minsize (1140, 800)
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
        [self.toolbar.EnableTool(x, False) for x in (3, 4, 5, 6, 7, 8,
                                                     35, 36, 37)]
        self.menu_go_items((0, 1, 1, 1, 1, 1, 1))  # Go menu items
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_destpath_setup)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_WINDOWS")
        pub.subscribe(self.process_terminated, "PROCESS TERMINATED")
        pub.subscribe(self.end_queue_processing, "QUEUE PROCESS SUCCESSFULLY")

        # this block need to initilizes queue.backup on startup
        fque = os.path.join(self.appdata["confdir"], 'queue.backup')
        if os.path.exists(fque):
            if wx.MessageBox(_('Not all items in the queue were completed.\n\n'
                               'Would you like to keep them in the queue?'),
                             _('Please confirm'), wx.ICON_QUESTION | wx.CANCEL
                             | wx.YES_NO, self) == wx.YES:

                queue = load_json_file_queue(fque)
                if queue:
                    self.queuelist = queue
                    self.queue_tool_counter()
            else:
                os.remove(fque)

    # ------------------------------------------------------------------#

    def queue_tool_counter(self):
        """
        Set a counter aside Queue text when adding items
        to queue list
        """
        counter = len(self.queuelist)
        if self.queuelist:
            self.pqueue.SetLabel(_("Queue ({0})").format(counter))
            # need to call Realize() to re-draw the toolbar
            self.toolbar.Realize()
            self.toolbar.EnableTool(37, True)
        else:
            self.pqueue.SetLabel(_("Queue"))
            self.toolbar.Realize()
    # ------------------------------------------------------------------#

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

    def menu_go_items(self, enablelist: list = None):
        """
        Enables `Go` menu bar items based on showing panels.
        The `enablelist` default arg is a boolean list containing
        enable items (1) or disable items (0).
        """
        if not enablelist:
            return

        items = [self.startpan, self.prstpan, self.avpan, self.concpan,
                 self.slides, self.toseq, self.logpan,]

        [x.Enable(y) for x, y in zip(items, enablelist)]
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

    def write_option_before_exit(self):
        """
        Write user settings to the configuration file
        before exit the application.
        """
        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        sett['main_window_size'] = list(self.GetSize())
        sett['main_window_pos'] = list(self.GetPosition())
        prstcolwidth = [self.PrstsPanel.lctrl.GetColumnWidth(0),
                        self.PrstsPanel.lctrl.GetColumnWidth(1),
                        self.PrstsPanel.lctrl.GetColumnWidth(2),
                        self.PrstsPanel.lctrl.GetColumnWidth(3),
                        ]
        sett['prstmng_column_width'] = prstcolwidth
        filedropcolwidth = [self.fileDnDTarget.flCtrl.GetColumnWidth(0),
                            self.fileDnDTarget.flCtrl.GetColumnWidth(1),
                            self.fileDnDTarget.flCtrl.GetColumnWidth(2),
                            self.fileDnDTarget.flCtrl.GetColumnWidth(3),
                            self.fileDnDTarget.flCtrl.GetColumnWidth(4),
                            self.fileDnDTarget.flCtrl.GetColumnWidth(5),
                            ]
        sett['filedrop_column_width'] = filedropcolwidth
        confmanager.write_options(**sett)
    # ------------------------------------------------------------------#

    def checks_running_processes(self):
        """
        Check currently running processes
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type is not None:
                return True

        return False
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Application exit request given by the user.
        """
        if self.checks_running_processes():
            wx.MessageBox(_("There are still active windows with running "
                            "processes, make sure you finish your work "
                            "before exit."),
                          _('Videomass - Warning!'), wx.ICON_WARNING, self)
            return

        if self.appdata['warnexiting']:
            if wx.MessageBox(_('Are you sure you want to exit '
                               'the application?'),
                             _('Exit'), wx.ICON_QUESTION | wx.CANCEL
                             | wx.YES_NO, self) != wx.YES:
                return
        self.write_option_before_exit()
        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        This method is called after from the `main_setup_dlg()` method.
        """
        if self.checks_running_processes():
            wx.MessageBox(_("There are still active windows with running "
                            "processes, make sure you finish your work "
                            "before exit."),
                          _('Videomass - Warning!'), wx.ICON_WARNING, self)
            self.appdata['auto-restart-app'] = False
            return
        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

    def destroy_application(self):
        """
        Permanent exit from the application.
        Do not use this method directly.
        """
        self.Destroy()
    # ------------------------------------------------------------------#

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
        dscrp = _("Import files\tCtrl+O")
        self.openmedia = fileButton.Append(wx.ID_OPEN, dscrp)
        self.openmedia.Enable(False)
        dscrp = _("Open destination folder of encodings\tCtrl+D")
        opendest = fileButton.Append(wx.ID_ANY, dscrp)
        fileButton.AppendSeparator()
        dscrp = (_("Load queue file"),
                 _("Load a previously exported queue file"))
        self.loadqueue = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Open trash"),
                 _("Open the Videomass trash folder"))
        dir_trash = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Empty trash"),
                 _("Delete all files in the Videomass trash folder"))
        empty_trash = fileButton.Append(wx.ID_DELETE, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Completely exit the application"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ Edit menu
        editButton = wx.Menu()
        dscrp = (_("Rename selected file\tCtrl+R"),
                 _("Rename the destination of the selected file"))
        self.rename = editButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.rename.Enable(False)
        dscrp = (_("Batch rename files\tCtrl+B"),
                 _("Numerically renames the destination of "
                   "all items in the list"))
        self.rename_batch = editButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.rename_batch.Enable(False)
        editButton.AppendSeparator()
        dscrp = (_("Remove selected entry\tDEL"),
                 _("Remove the selected file from the list"))
        self.delfile = editButton.Append(wx.ID_REMOVE, dscrp[0], dscrp[1])
        self.delfile.Enable(False)
        dscrp = (_("Clear list\tShift+DEL"),
                 _("Clear the file list"))
        self.clearall = editButton.Append(wx.ID_CLEAR, dscrp[0], dscrp[1])
        self.clearall.Enable(False)
        editButton.AppendSeparator()
        self.setupItem = editButton.Append(wx.ID_PREFERENCES,
                                           _("Preferences\tCtrl+P"),
                                           _("Application preferences"))
        self.menuBar.Append(editButton, _("Edit"))

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("Find FFmpeg topics"),
                 _("A useful tool to search for FFmpeg help topics and "
                   "options"))
        searchtopic = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
        prstpage = '<https://github.com/jeanslack/Videomass-presets>'
        dscrp = (_("Check for preset updates"),
                 _("Check for new presets updates from {0}").format(prstpage))
        self.prstcheck = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Get latest presets"),
                 _("Get the latest presets from {0}").format(prstpage))
        self.prstdownload = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        toolsButton.AppendSeparator()
        dscrp = (_("Work notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
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
                 _("Muxers and demuxers available on your version of FFmpeg"))
        ckformats = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffmpegButton.AppendSeparator()
        dscrp = (_("Encoders"),
                 _("Encoders available on your version of FFmpeg"))
        ckcoders = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Decoders"),
                 _("Decoders available on your version of FFmpeg"))
        ckdecoders = ffmpegButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffplayButton = wx.Menu()  # ffplay sub menu
        viewButton.AppendSubMenu(ffplayButton, "FFplay")
        dscrp = (_("Enable timestamps on playback"),
                 _("Displays timestamp when playing media with FFplay"))
        self.viewtimestamp = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                                 kind=wx.ITEM_CHECK)
        dscrp = (_("Auto-exit after playback"),
                 _("If checked, the FFplay window will auto-close "
                   "when playback is complete"))
        self.exitplayback = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                                kind=wx.ITEM_CHECK)
        dscrp = (_("Timestamp settings"), _("Customize the timestamp style"))
        tscustomize = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        ffplayButton.AppendSeparator()
        dscrp = (_("While playing..."),
                 _("Show useful shortcut keys when playing or previewing "
                   "using FFplay"))
        playing = ffplayButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        viewButton.AppendSeparator()
        dscrp = (_("Show timeline editor\tCtrl+T"),
                 _("Set duration or trim slices of time to remove unwanted "
                   "parts from your files"))
        self.viewtimeline = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1],
                                              kind=wx.ITEM_CHECK)
        self.menuBar.Append(viewButton, _("View"))
        self.menuBar.Check(self.exitplayback.GetId(), self.autoexit)
        self.menuBar.Check(self.viewtimestamp.GetId(), True)

        # ------------------ Go menu
        goButton = wx.Menu()
        self.startpan = goButton.Append(wx.ID_ANY,
                                        _("Home panel\tCtrl+Shift+H"),
                                        _("Go to the «Home» panel"))
        goButton.AppendSeparator()
        self.prstpan = goButton.Append(wx.ID_ANY,
                                       _("Presets Manager\tCtrl+Shift+P"),
                                       _("Go to the «Presets Manager» panel"))
        self.avpan = goButton.Append(wx.ID_ANY,
                                     _("A/V Conversions\tCtrl+Shift+V"),
                                     _("Go to the «A/V Conversions» panel"))
        self.concpan = goButton.Append(wx.ID_ANY,
                                       _("Concatenate Demuxer\tCtrl+Shift+D"),
                                       _("Go to the «Concatenate Demuxer» "
                                         "panel"))
        self.slides = goButton.Append(wx.ID_ANY,
                                      _("Still Image Maker\tCtrl+Shift+I"),
                                      _("Go to the «Still Image Maker» panel"))
        self.toseq = goButton.Append(wx.ID_ANY,
                                     _("From Movie to Pictures\tCtrl+Shift+S"),
                                     _("Go to the «From Movie to Pictures» "
                                       "panel"))
        goButton.AppendSeparator()
        dscrp = (_("Output monitor\tCtrl+Shift+O"),
                 _("Keeps track of the output for debugging errors"))
        self.logpan = goButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(goButton, _("Go"))

        # ------------------ help menu
        helpButton = wx.Menu()
        helpItem = helpButton.Append(wx.ID_HELP, _("User guide"),
                                     ("https://jeanslack.github.io/"
                                      "Videomass/videomass_use.html"))
        helpButton.AppendSeparator()
        dscrp = (_("System version"),
                 _("Get version about your operating system, version of "
                   "Python and wxPython."))
        sysinfo = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        dscrp = (_("Show log files\tCtrl+L"),
                 _("Viewing log messages"))
        viewlogs = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        issueItem = helpButton.Append(wx.ID_ANY, _("Issue tracker"),
                                      "https://github.com/jeanslack/"
                                      "Videomass/issues")
        contribution = helpButton.Append(wx.ID_ANY,
                                         _('Contribute to the project'),
                                         ('https://jeanslack.github.io/'
                                          'Videomass/Contribute.html'))
        spons = helpButton.Append(wx.ID_ANY, _("Sponsor this project"),
                                  _("Become a developer supporter"))
        donat = helpButton.Append(wx.ID_ANY, _("Donate"),
                                  _("Donate to the app developer"))
        helpButton.AppendSeparator()
        projButton = wx.Menu()  # projects sub menu
        helpButton.AppendSubMenu(projButton,
                                 _("Other projects by the developer"))
        dscrp = ("Vidtuber",
                 ("A simple multi-platform GUI for yt-dlp"))
        proj1 = projButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = ("FFcuesplitter",
                 ("FFmpeg based audio splitter for CDDA images associated "
                  "with .cue files"))
        proj2 = projButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = ("FFaudiocue",
                 ("GUI based on FFcuesplitter library written in "
                  "wxPython-Phoenix"))
        proj3 = projButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = ("Videomass-Presets",
                 "A collection of additional presets for Videomass")
        proj4 = projButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Videomass"), "")
        dscrp = (_("Check for newer version"),
                 _("Check for the latest Videomass version"))
        chklatest = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(helpButton, _("Help"))
        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.open_media_files, self.openmedia)
        self.Bind(wx.EVT_MENU, self.open_dest_encodings, opendest)
        self.Bind(wx.EVT_MENU, self.on_load_queue, self.loadqueue)
        self.Bind(wx.EVT_MENU, self.open_trash_folder, dir_trash)
        self.Bind(wx.EVT_MENU, self.empty_trash_folder, empty_trash)
        self.Bind(wx.EVT_MENU, self.quiet_app, exitItem)
        # ----EDIT----
        self.Bind(wx.EVT_MENU, self.on_file_renaming, self.rename)
        self.Bind(wx.EVT_MENU, self.on_batch_renaming, self.rename_batch)
        self.Bind(wx.EVT_MENU, self.fileDnDTarget.on_delete_selected,
                  self.delfile)
        self.Bind(wx.EVT_MENU, self.fileDnDTarget.delete_all, self.clearall)
        self.Bind(wx.EVT_MENU, self.main_setup_dlg, self.setupItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.find_topics, searchtopic)
        self.Bind(wx.EVT_MENU, self.prst_downloader, self.prstdownload)
        self.Bind(wx.EVT_MENU, self.prst_checkversion, self.prstcheck)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_codecs, ckcoders)
        self.Bind(wx.EVT_MENU, self.get_ffmpeg_decoders, ckdecoders)
        self.Bind(wx.EVT_MENU, self.showTimestamp, self.viewtimestamp)
        self.Bind(wx.EVT_MENU, self.timestampCustomize, tscustomize)
        self.Bind(wx.EVT_MENU, self.autoexitFFplay, self.exitplayback)
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.view_Timeline, self.viewtimeline)
        # ---- GO -----
        self.Bind(wx.EVT_MENU, self.startPanel, self.startpan)
        self.Bind(wx.EVT_MENU, self.switch_presets_manager, self.prstpan)
        self.Bind(wx.EVT_MENU, self.switch_av_conversions, self.avpan)
        self.Bind(wx.EVT_MENU, self.switch_concat_demuxer, self.concpan)
        self.Bind(wx.EVT_MENU, self.switch_slideshow_maker, self.slides)
        self.Bind(wx.EVT_MENU, self.switch_video_to_pictures, self.toseq)
        self.Bind(wx.EVT_MENU, self.logPan, self.logpan)
        # ----HELP----
        self.Bind(wx.EVT_MENU, self.helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.system_vers, sysinfo)
        self.Bind(wx.EVT_MENU, self.view_logs, viewlogs)
        self.Bind(wx.EVT_MENU, self.issues, issueItem)
        self.Bind(wx.EVT_MENU, self.contribute, contribution)
        self.Bind(wx.EVT_MENU, self.sponsor_this_project, spons)
        self.Bind(wx.EVT_MENU, self.donate_to_dev, donat)
        self.Bind(wx.EVT_MENU,
                  lambda event: self.dev_projects(event, 'Vidtuber'), proj1)
        self.Bind(wx.EVT_MENU,
                  lambda event: self.dev_projects(event,
                                                  'FFcuesplitter'), proj2)
        self.Bind(wx.EVT_MENU,
                  lambda event: self.dev_projects(event, 'FFaudiocue'), proj3)
        self.Bind(wx.EVT_MENU,
                  lambda event: self.dev_projects(event,
                                                  'Videomass-Presets'), proj4)
        self.Bind(wx.EVT_MENU, self.about_videomass, infoItem)
        self.Bind(wx.EVT_MENU, self.check_new_releases, chklatest)
    # --------Menu Bar Event handler (callback)

    # --------- Menu  Files

    def open_media_files(self, event):
        """
        Open the file dialog to choose media files.
        The order of selected files only supported by GTK
        """
        wild = ("All files |*.*|*.mkv|*.mkv|*.avi|*.avi|*.webm|*.webm"
                "|*.ogv|*.ogv|*.mp4|*.mp4|*.flv|*.flv|*.wav|*.wav"
                "|*.mp3|*.mp3|*.ogg|*.ogg|*.flac|*.flac|*.opus|*.opus"
                "|*.jpg|*.jpg|*.png|*.png|*.bmp|*.bmp")

        with wx.FileDialog(self, _("Import files"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard=wild,
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

    def open_dest_encodings(self, event):
        """
        Open the conversions dir with file manager
        """
        if self.appdata['outputdir_asinput']:
            wx.MessageBox(_('No default folder has been set for the '
                            'destination of the encodings. The current '
                            'setting is "Same destination paths as source '
                            'files".'),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        io_tools.openpath(self.appdata['outputdir'])
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
        Open Videomass trash dir if it exists
        """
        trashdir = self.appdata['trashdir_loc']
        if os.path.exists(trashdir):
            io_tools.openpath(trashdir)
        else:
            wx.MessageBox(_("'{}':\nNo such file "
                            "or directory").format(trashdir),
                          "Videomass", wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def empty_trash_folder(self, event):
        """
        Delete permanently all files inside trash folder
        """
        trashdir = self.appdata['trashdir_loc']
        if os.path.exists(trashdir):
            files = os.listdir(trashdir)
            if len(files) > 0:
                if wx.MessageBox(_("Are you sure to empty trash folder?"),
                                 _("Please confirm"), wx.ICON_QUESTION
                                 | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                    return

                for fname in files:
                    os.remove(os.path.join(trashdir, fname))
            else:
                wx.MessageBox(_("'{}':\nThere are no files "
                                "to delete.").format(trashdir),
                              "Videomass", wx.ICON_INFORMATION, self)
        else:
            wx.MessageBox(_("'{}':\nNo such file "
                            "or directory").format(trashdir),
                          "Videomass", wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def quiet_app(self, event):
        """
        destroy the videomass.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#
    # --------- Menu Tools  ###

    def find_topics(self, event):
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
        presetsrecovery = os.path.join(self.appdata['srcdata'], 'presets',
                                       'version', 'version.txt')
        if not os.path.isfile(presetsdir):
            copydir_recursively(os.path.dirname(presetsrecovery),
                                os.path.dirname(os.path.dirname(presetsdir))
                                )
        with open(presetsdir, "r", encoding='utf-8') as vers:
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

        dialdir = wx.DirDialog(self, _("Choose Destination"),
                               "", wx.DD_DEFAULT_STYLE)
        if dialdir.ShowModal() == wx.ID_OK:
            path = dialdir.GetPath()
            dialdir.Destroy()
        else:
            return

        tarball = io_tools.get_github_releases(url, "tarball_url")

        if tarball[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{tarball[0]} {tarball[1]}",
                          f"{tarball[0]}", wx.ICON_ERROR, self)
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
            wx.MessageBox(f"{download[1]}", _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
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
            with open(fname, "w", encoding='utf-8') as text:
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
            wx.MessageBox(f"\n{out[1]}", _('Videomass - Error!'),
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
            wx.MessageBox(f"\n{out['Not found']}", _('Videomass - Error!'),
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
            wx.MessageBox(f"\n{out['Not found']}", _('Videomass - Error!'),
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
            wx.MessageBox(f"\n{out['Not found']}", _('Videomass - Error!'),
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

    def view_logs(self, event, flog=None):
        """
        Show to view log files dialog
        flog: filename to select on showlog if any.
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
        self.switch_to_processing('View')
    # ------------------------------------------------------------------#
    # --------- Menu  Preferences  ###

    def on_destpath_setup(self, event):
        """
        This is a menu event and a filedrop button event.
        It sets a new file destination path for conversions
        """
        dialdir = wx.DirDialog(self, _("Choose Destination"),
                               self.appdata['outputdir'], wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.appdata['outputdir_asinput'] = False
            self.appdata['filesuffix'] = ""
            self.appdata['outputdir'] = getpath
            self.fileDnDTarget.on_file_save(getpath)

            confmanager = ConfigManager(self.appdata['fileconfpath'])
            sett = confmanager.read_options()
            sett['outputdir'] = self.appdata['outputdir']
            sett['outputdir_asinput'] = self.appdata['outputdir_asinput']
            sett['filesuffix'] = self.appdata['filesuffix']
            confmanager.write_options(**sett)

            dialdir.Destroy()
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

    def main_setup_dlg(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Videomass, being need
        to get the return code from getvalue interface.
        """
        msg = _("Some changes require restarting the application.")
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                changes = set_up.getvalue()
                self.fileDnDTarget.on_file_save(self.appdata['outputdir'])
                if [x for x in changes if x is False]:
                    if wx.MessageBox(_("{0}\n\nDo you want to restart "
                                       "the application now?").format(msg),
                                     _('Restart Videomass?'), wx.ICON_QUESTION
                                     | wx.CANCEL | wx.YES_NO, self) == wx.YES:
                        self.appdata['auto-restart-app'] = True
                        self.on_Kill()
    # ------------------------------------------------------------------#
    # --------- Menu Help  ###

    def helpme(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://jeanslack.github.io/Videomass/Docs.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Videomass/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def contribute(self, event):
        """Display contribute web page"""
        page = 'https://jeanslack.github.io/Videomass/Contribute.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def sponsor_this_project(self, event):
        """Go to sponsor page"""
        page = 'https://github.com/sponsors/jeanslack'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def donate_to_dev(self, event):
        """Go to donation page"""
        page = 'https://www.paypal.me/GPernigotto'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def dev_projects(self, event, topic):
        """Go to project pages"""
        if topic == 'Vidtuber':
            page = 'https://github.com/jeanslack/Vidtuber'
        elif topic == 'FFcuesplitter':
            page = 'https://github.com/jeanslack/FFcuesplitter'
        elif topic == 'Videomass-Presets':
            page = 'https://github.com/jeanslack/Videomass-presets'
        elif topic == 'FFaudiocue':
            page = 'https://github.com/jeanslack/FFaudiocue'
        else:
            page = None

        if page:
            webbrowser.open(page)
    # ------------------------------------------------------------------#

    def check_new_releases(self, event):
        """
        Compare the Videomass version with a given
        new version found on github.
        """
        url = ("https://api.github.com/repos/jeanslack/"
               "Videomass/releases/latest")
        version = io_tools.get_github_releases(url, "tag_name")

        if version[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{version[0]} {version[1]}",
                          f"{version[0]}", wx.ICON_ERROR, self)
            return

        version = version[0].split('v')[1]
        major, minor, micro = version.split('.')
        released_version = int(f'{major}{minor}{micro}')
        major, minor, micro = VERSION.split('.')
        this_version = int(f'{major}{minor}{micro}')

        if released_version > this_version:
            msg = _('A new release is available - '
                    'v.{0}\n').format(version)
        elif this_version > released_version:
            msg = _('You are using a development version '
                    'that has not yet been released!\n')
        else:
            msg = _('Congratulation! You are already '
                    'using the latest version.\n')

        dlg = videomass_check_version.CheckNewVersion(self,
                                                      msg,
                                                      version,
                                                      VERSION,
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

    def about_videomass(self, event):
        """
        Display the program informations and developpers
        """
        about_dialog.show_about_dlg(self, self.icons['videomass'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def get_toolbar_pos(self):
        """
        Get toolbar position properties according to
        the user preferences.
        """
        if self.appdata['toolbarpos'] == 0:  # on top
            return wx.TB_TEXT

        if self.appdata['toolbarpos'] == 1:  # on bottom
            return wx.TB_TEXT | wx.TB_BOTTOM

        if self.appdata['toolbarpos'] == 2:  # on right
            return wx.TB_TEXT | wx.TB_RIGHT

        if self.appdata['toolbarpos'] == 3:
            return wx.TB_TEXT | wx.TB_LEFT

        return None
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
            bmpplay = get_bmp(self.icons['play'], bmp_size)
            bmpprocqueue = get_bmp(self.icons['proc-queue'], bmp_size)
            bmpaddqueue = get_bmp(self.icons['add-queue'], bmp_size)
        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpinfo = wx.Bitmap(self.icons['fileproperties'],
                                wx.BITMAP_TYPE_ANY)
            bmpconv = wx.Bitmap(self.icons['startconv'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmphome = wx.Bitmap(self.icons['home'], wx.BITMAP_TYPE_ANY)
            bmpplay = wx.Bitmap(self.icons['play'], wx.BITMAP_TYPE_ANY)
            bmpprocqueue = wx.Bitmap(self.icons['proc-queue'],
                                     wx.BITMAP_TYPE_ANY)
            bmpaddqueue = wx.Bitmap(self.icons['add-queue'],
                                    wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))
        tip = _("Previous panel")
        back = self.toolbar.AddTool(3, _('Back'), bmpback,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Next panel")
        forward = self.toolbar.AddTool(4, _('Next'), bmpnext,
                                       tip, wx.ITEM_NORMAL
                                       )
        tip = _("Home panel")
        home = self.toolbar.AddTool(5, _('Home'), bmphome,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Play the selected imput file")
        play = self.toolbar.AddTool(35, _('Play'), bmpplay,
                                    tip, wx.ITEM_NORMAL
                                    )
        tip = _("Get informative data about imported media streams")
        self.btn_streams = self.toolbar.AddTool(6, _('Properties'), bmpinfo,
                                                tip, wx.ITEM_NORMAL
                                                )
        tip = _("Start batch processing")
        self.run_coding = self.toolbar.AddTool(7, _('Run'), bmpconv,
                                               tip, wx.ITEM_NORMAL
                                               )
        tip = _("Stops current process")
        stop_coding = self.toolbar.AddTool(8, _('Stop'), bmpstop,
                                           tip, wx.ITEM_NORMAL
                                           )
        tip = _("Add an item to Queue")
        addqueue = self.toolbar.AddTool(36, _('Add to Queue'), bmpaddqueue,
                                        tip, wx.ITEM_NORMAL
                                        )
        tip = _("Show queue")
        self.pqueue = self.toolbar.AddTool(37, _('Queue'), bmpprocqueue,
                                           tip, wx.ITEM_NORMAL
                                           )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.startPanel, home)
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_coding)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop_coding)
        self.Bind(wx.EVT_TOOL, self.on_Back, back)
        self.Bind(wx.EVT_TOOL, self.on_Forward, forward)
        self.Bind(wx.EVT_TOOL, self.media_streams, self.btn_streams)
        self.Bind(wx.EVT_TOOL, self.fileDnDTarget.on_play_select, play)
        self.Bind(wx.EVT_TOOL, self.on_add_to_queue, addqueue)
        self.Bind(wx.EVT_TOOL, self.on_process_queue, self.pqueue)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_Back(self, event):
        """
        Click Back toolbar button event
        """
        if self.ProcessPanel.IsShown():
            self.panelShown(self.ProcessPanel.previous)
            return

        if self.fileDnDTarget.IsShown():
            self.startPanel(None)
        else:
            self.switch_file_import(None)
    # ------------------------------------------------------------------#

    def on_Forward(self, event):
        """
        Click Next toolbar button event
        """
        if self.fileDnDTarget.IsShown():
            if self.topicname == 'Audio/Video Conversions':
                self.switch_av_conversions(None)
            elif self.topicname == 'Concatenate Demuxer':
                self.switch_concat_demuxer(None)
            elif self.topicname == 'Presets Manager':
                self.switch_presets_manager(None)
            elif self.topicname == 'Image Sequence to Video':
                self.switch_slideshow_maker(None)
            elif self.topicname == 'Video to Pictures':
                self.switch_video_to_pictures(None)
        else:
            self.switch_to_processing('View')
    # ------------------------------------------------------------------#

    def startPanel(self, event):
        """
        Shared event from the menu bar and the "Home" toolbar
        button to switch at the Home panel.
        Note, this event could be called indirectly from the
        "Back" toolbar button.
        """
        self.topicname = None
        self.ProcessPanel.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        [self.toolbar.EnableTool(x, False) for x in (3, 4, 5, 6, 7, 8, 35, 36)]
        self.ChooseTopic.Show()
        self.openmedia.Enable(False)
        self.menu_go_items((0, 1, 1, 1, 1, 1, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.SetTitle(_('Videomass'))
        self.statusbar_msg(_('Ready'), None)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_file_import(self, event):
        """
        Shared event by menubar and toolbar
        to switch on Drag&Drop panel.
        """
        self.ProcessPanel.Hide()
        self.AVconvPanel.Hide()
        self.ChooseTopic.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.fileDnDTarget.Show()
        pub.sendMessage("SET_DRAG_AND_DROP_TOPIC", topic=self.topicname)
        self.menu_go_items((1, 1, 1, 1, 1, 1, 1))  # Go menu items
        if self.filedropselected:
            self.delfile.Enable(True)
            self.rename.Enable(True)
        if len(self.outputnames) > 1:
            self.clearall.Enable(True)
            self.rename_batch.Enable(True)
        self.openmedia.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 35)]
        [self.toolbar.EnableTool(x, False) for x in (7, 8, 36)]
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - File List'))
    # ------------------------------------------------------------------#

    def switch_av_conversions(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show Video converter panel
        """
        self.topicname = 'Audio/Video Conversions'
        self.ProcessPanel.Hide()
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.AVconvPanel.Show()
        self.SetTitle(_('Videomass - AV Conversions'))
        self.menu_go_items((1, 1, 0, 1, 1, 1, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.openmedia.Enable(True)
        self.loadqueue.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35, 36)]
        self.toolbar.EnableTool(8, False)
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_presets_manager(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show presets manager panel
        """
        self.topicname = 'Presets Manager'
        self.ProcessPanel.Hide()
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.PrstsPanel.Show()
        self.SetTitle(_('Videomass - Presets Manager'))
        self.menu_go_items((1, 0, 1, 1, 1, 1, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.openmedia.Enable(True)
        self.loadqueue.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35, 36)]
        self.toolbar.EnableTool(8, False)
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.Layout()
        self.PrstsPanel.update_preset_state()
    # ------------------------------------------------------------------#

    def switch_concat_demuxer(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `ConcatDemuxer` panel
        """
        self.topicname = 'Concatenate Demuxer'
        self.ProcessPanel.Hide()
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ConcatDemuxer.Show()
        self.SetTitle(_('Videomass - Concatenate Demuxer'))
        self.menu_go_items((1, 1, 1, 0, 1, 1, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.openmedia.Enable(True)
        self.loadqueue.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 36)]
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_video_to_pictures(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `toPictures` panel
        """
        self.topicname = 'Video to Pictures'
        self.ProcessPanel.Hide()
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toSlideshow.Hide()
        self.toPictures.Show()
        self.SetTitle(_('Videomass - From Movie to Pictures'))
        self.menu_go_items((1, 1, 1, 1, 1, 0, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.openmedia.Enable(True)
        self.loadqueue.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 36)]
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_slideshow_maker(self, event):
        """
        Called by self.ChooseTopic object on start.
        Menu bar event to show `toSlideshow` panel
        """
        self.topicname = 'Image Sequence to Video'
        self.ProcessPanel.Hide()
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Show()
        self.SetTitle(_('Videomass - Still Image Maker'))
        self.menu_go_items((1, 1, 1, 1, 0, 1, 1))  # Go menu items
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        self.openmedia.Enable(True)
        self.loadqueue.Enable(True)
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 5, 6, 7, 35)]
        [self.toolbar.EnableTool(x, False) for x in (8, 36)]
        if self.queuelist:
            self.toolbar.EnableTool(37, True)
        self.Layout()
    # ------------------------------------------------------------------#

    def on_load_queue(self, event):
        """
        Load a previously saved json queue file
        """
        queue = load_json_file_queue()
        if not queue:
            return

        if not self.queuelist:
            self.queuelist = []
            self.queuelist.extend(queue)
        else:
            update = extend_data_queue(self, self.queuelist, queue)
            if not update:
                return

        write_json_file_queue(self.queuelist)
        self.queue_tool_counter()
    # ------------------------------------------------------------------#

    def on_process_queue(self, event):
        """
        process queue data if any
        """
        with QueueManager(self,
                          self.queuelist,
                          self.movetotrash,
                          self.emptylist,
                          self.removequeue,
                          ) as queman:
            if queman.ShowModal() == wx.ID_OK:
                data = queman.getvalue()
                self.queuelist = data[0]
                self.movetotrash = data[1]
                self.emptylist = data[2]
                self.removequeue = data[3]
                if not self.queuelist:
                    self.toolbar.EnableTool(37, False)
                    return None
                self.switch_to_processing('Queue Processing',
                                          'Queue Processing.log',
                                          datalist=self.queuelist
                                          )
            else:
                if not self.queuelist:
                    self.toolbar.EnableTool(37, False)
        return None
    # ------------------------------------------------------------------#

    def end_queue_processing(self, msg):
        """
        QUEUE PROCESS SUCCESSFULLY. This method is called using
        pub/sub protocol. see `long_processing_task.end_proc()`)
        """
        if self.removequeue and msg == 'Done':
            queuef = os.path.join(self.appdata["confdir"], 'queue.backup')
            os.remove(queuef)  # remove queue.backup
            self.queuelist.clear()
            self.toolbar.EnableTool(37, False)
            self.queue_tool_counter()
        else:
            self.toolbar.EnableTool(37, True)
    # ------------------------------------------------------------------#

    def on_add_to_queue(self, event):
        """
        Append data of selected file to queue
        """
        if not self.data_files or not self.filedropselected:
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return

        kwargs = None
        if self.AVconvPanel.IsShown():
            kwargs = self.AVconvPanel.queue_mode()
        elif self.PrstsPanel.IsShown():
            kwargs = self.PrstsPanel.queue_mode()

        if not kwargs:
            return
        if not self.queuelist:
            self.queuelist = []
            self.queuelist.append(kwargs)
            self.toolbar.EnableTool(37, True)
        else:
            dup = None
            for idx, item in enumerate(self.queuelist):
                if item["destination"] == kwargs["destination"]:
                    dup = idx
            if dup is not None:
                if wx.MessageBox(_('An item with the same destination file '
                                   'already exists.\n\nDo you want to replace '
                                   'it by adding the new item to the queue?'),
                                 _('Please confirm'), wx.ICON_QUESTION
                                 | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                    return
                self.queuelist[dup] = kwargs

            else:
                self.queuelist.append(kwargs)

        write_json_file_queue(self.queuelist)
        self.queue_tool_counter()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *args, datalist=None):
        """
        This method is called by start methods of any
        topic. It call `ProcessPanel.topic_thread`
        method assigning the corresponding thread.
        """
        self.SetTitle(_('Videomass - FFmpeg Message Monitoring'))
        self.ChooseTopic.Hide()
        self.fileDnDTarget.Hide()
        self.AVconvPanel.Hide()
        self.PrstsPanel.Hide()
        self.ConcatDemuxer.Hide()
        self.toPictures.Hide()
        self.toSlideshow.Hide()
        self.ProcessPanel.Show()
        self.delfile.Enable(False)
        self.clearall.Enable(False)
        self.rename.Enable(False)
        self.rename_batch.Enable(False)
        if not args[0] == 'View':
            self.menu_go_items((0, 0, 0, 0, 0, 0, 0))  # Go menu items
            self.openmedia.Enable(False)
            self.loadqueue.Enable(False)
            self.setupItem.Enable(False)
            [self.toolbar.EnableTool(x, True) for x in (6, 8)]
            [self.toolbar.EnableTool(x, False) for x in (3, 4, 5, 36, 37, 7)]
        else:
            self.menu_go_items((1, 1, 1, 1, 1, 1, 0))  # Go menu items
            [self.toolbar.EnableTool(x, False) for x in (4, 8, 36)]
            [self.toolbar.EnableTool(x, True) for x in (3, 5, 6, 7, 35)]
        self.ProcessPanel.topic_thread(args, datalist, self.topicname)
        self.Layout()
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        Click Start toolbar event, calls the `on_start` method
        of the corresponding class panel shown, which calls the
        'switch_to_processing' method above.
        """
        if not self.topicname:
            self.startPanel(None)
            return

        if not self.data_files:
            self.switch_file_import(None)
            return

        if self.AVconvPanel.IsShown():
            self.AVconvPanel.batch_mode()
        elif self.PrstsPanel.IsShown():
            self.PrstsPanel.batch_mode()
        elif self.ConcatDemuxer.IsShown():
            self.ConcatDemuxer.on_start()
        elif self.toPictures.IsShown():
            self.toPictures.on_start()
        elif self.toSlideshow.IsShown():
            self.toSlideshow.on_start()
        elif self.ProcessPanel.IsShown():
            self.panelShown(self.topicname)
            #  self.click_start(None)  # need recursion here
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
        self.menu_go_items((1, 1, 1, 1, 1, 1, 0))  # Go menu items
        self.openmedia.Enable(False)
        self.loadqueue.Enable(False)
        self.setupItem.Enable(True)

        [self.toolbar.EnableTool(x, True) for x in (3, 5, 7)]
        self.toolbar.EnableTool(8, False)

        if self.emptylist:
            self.fileDnDTarget.delete_all(self)

        if self.filedropselected is not None:
            self.rename.Enable(True)
        if self.file_src:
            self.rename_batch.Enable(True)

        if self.appdata['shutdown']:
            self.auto_shutdown()
        elif self.appdata['auto_exit']:
            self.auto_exit()
    # ------------------------------------------------------------------#

    def panelShown(self, panelshown=None):
        """
        Clicking Back arrow on tool bar it Closes the
        `long_processing_task` panel and retrieval at previous
        panel shown (see `switch_to_processing` method above).
        """
        if panelshown == 'Audio/Video Conversions':
            self.switch_av_conversions(None)
        elif panelshown == 'Presets Manager':
            self.switch_presets_manager(None)
        elif panelshown == 'Concatenate Demuxer':
            self.switch_concat_demuxer(None)
        elif panelshown == 'Video to Pictures':
            self.switch_video_to_pictures(None)
        elif panelshown == 'Image Sequence to Video':
            self.switch_slideshow_maker(None)

        if not panelshown:
            self.startPanel(None)

        self.Layout()
    # ------------------------------------------------------------------#

    def auto_shutdown(self):
        """
        Turn off the system when processing is finished
        """
        if self.checks_running_processes():
            return

        self.write_option_before_exit()

        msgdlg = _('The system will turn off in {0} seconds')
        title = _('Videomass - Shutdown!')
        dlg = CountDownDlg(self, timeout=59, message=msgdlg, caption=title)
        res = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if res:
            succ = shutdown_system(self.appdata['sudo_password'])
            if not succ:
                msg = (_("Error while shutting down. Please see "
                         "file log for details."))
                wx.LogError(msg)
    # ------------------------------------------------------------------#

    def auto_exit(self):
        """
        Auto-exit the application when processing is finished
        """
        if self.checks_running_processes():
            return

        msgdlg = _('Exiting the application in {0} seconds')
        title = _('Videomass - Exiting!')
        dlg = CountDownDlg(self, timeout=10, message=msgdlg, caption=title)
        res = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if res:
            self.write_option_before_exit()
            self.destroy_orphaned_window()
            self.destroy_application()
