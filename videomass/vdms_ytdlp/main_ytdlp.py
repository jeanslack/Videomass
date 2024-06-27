# -*- coding: UTF-8 -*-
"""
Name: main_ytdlp.py
Porpose: window main frame for yt_dlp library
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.09.2024
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
import wx
from pubsub import pub
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_ytdlp.ydl_mediainfo import YdlMediaInfo
from videomass.vdms_ytdlp.textdrop import Url_DnD_Panel
from videomass.vdms_ytdlp.youtubedl_ui import Downloader
from videomass.vdms_ytdlp.long_task_ytdlp import LogOut
from videomass.vdms_io import io_tools
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_ytdlp.ydl_preferences import Ytdlp_Options
if wx.GetApp().appset['yt_dlp'] is True:
    import yt_dlp


class MainYtdl(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # set status bar colours in html rappresentation:
    ORANGE = '#f28924'
    WHITE = '#fbf4f4'
    # -------------------------------------------------------------#

    def __init__(self, appdata, parent=None):
        """
        If not data_url ytDownloader panel will be disabled
        """
        get = wx.GetApp()
        self.appdata = appdata
        self.icons = get.iconset
        self.data_url = []  # list of urls in text box
        self.changed = True  # previous list is different from new one
        self.infomediadlg = False  # media info dialog

        wx.Frame.__init__(self, parent, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- panel instances:
        self.parent = parent
        self.ytDownloader = Downloader(self)
        self.textDnDTarget = Url_DnD_Panel(self)
        self.ProcessPanel = LogOut(self)
        # hide panels
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        # Layout toolbar buttons:
        mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # Layout external panels:
        mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND)
        mainSizer.Add(self.ytDownloader, 1, wx.EXPAND)
        mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("Videomass - YouTube Downloader")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['videomass'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((1100, 715))
        self.SetSizer(mainSizer)
        self.Fit()
        self.SetSize(tuple(self.appdata['main_ytdl_size']))
        self.Move(tuple(self.appdata['main_ytdl_pos']))
        # menu bar
        self.videomass_menu_bar()
        # tool bar main
        self.videomass_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'), None)
        # disable some toolbar item
        [self.toolbar.EnableTool(x, False) for x in (20, 22, 23, 24)]
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_outputdir)
        self.Bind(wx.EVT_CLOSE, self.on_closefromcaption)

        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_YTDLP")
        pub.subscribe(self.process_terminated, "PROCESS_TERMINATED_YTDLP")

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
        if self.ytDownloader.IsShown():
            self.ytDownloader.Hide()
            self.textDnDTarget.Show()

            self.ydlpan.Enable(False)

            self.SetTitle(_('Videomass'))
            self.statusbar_msg(_('Ready'), None)
            self.Layout()
    # ------------------------------------------------------------------#

    def check_modeless_window(self, msg=None):
        """
        Receives a message from a modeless window close event.
        This method is called using pub/sub protocol subscribing
        "DESTROY_ORPHANED_YTDLP".
        """
        if msg == 'YdlMediaInfo':
            self.infomediadlg.Destroy()
            self.infomediadlg = False
    # ------------------------------------------------------------------#

    def destroy_orphaned_window(self):
        """
        Destroys all orphaned modeless windows,
        ie. on application exit or on editing URLs text.
        """
        if self.infomediadlg:
            self.infomediadlg.Destroy()
            self.infomediadlg = False

    # ---------------------- Event handler (callback) ------------------#

    def on_statistics(self, event):
        """
        Redirect input files at stream_info for media information
        """
        if self.infomediadlg:
            self.infomediadlg.Raise()
            return

        info = []
        if self.data_url:
            info = self.ytDownloader.on_show_statistics()
            if not info:
                return

        self.infomediadlg = YdlMediaInfo(info)
        self.infomediadlg.Show()
    # ------------------------------------------------------------------#

    def on_closefromcaption(self, event):
        """
        Event from EVT_CLOSE binder, offer the user
        the possibility to choose how to close this window.
        """
        if not self.data_url:
            self.on_exit(None, warn=False)
            return
        dlg = wx.MessageDialog(self, _('Do you want to close the active view '
                                       'keeping the data in memory and any '
                                       'background processes?'),
                               _('Please confirm'), wx.ICON_QUESTION
                               | wx.CANCEL | wx.YES_NO)
        res = dlg.ShowModal()
        if res == wx.ID_YES:
            self.on_close(None)
        elif res == wx.ID_NO:
            self.on_exit(None, warn=False)
        else:
            return
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        This event only hide the YouTube Downloader child frame.
        """
        self.Hide()
    # ------------------------------------------------------------------#

    def on_exit(self, event, warn=True):
        """
        This event destroy the YouTube Downloader child frame.
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type is not None:
                wx.MessageBox(_("There are still active windows with running "
                                "processes, make sure you finish your work "
                                "before exit."),
                              _('Videomass - Warning!'), wx.ICON_WARNING, self)
                return

        if self.data_url and self.appdata['warnexiting'] and warn:
            if wx.MessageBox(_('Are you sure you want to exit this window?\n'
                               'All data will be lost'),
                             _('Quit YouTube Downloader?'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return

        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        sett['main_ytdl_size'] = list(self.GetSize())
        sett['main_ytdl_pos'] = list(self.GetPosition())
        sett['subtitles_options'] = self.ytDownloader.opt["SUBS"]
        fcodecolwidth = [self.ytDownloader.panel_cod.fcode.GetColumnWidth(0),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(1),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(2),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(3),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(4),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(5),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(6),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(7),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(8),
                         ]
        sett['fcode_column_width'] = fcodecolwidth
        confmanager.write_options(**sett)
        self.destroy_orphaned_window()
        self.Destroy()
    # ------------------------------------------------------------------#

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
        dscrp = _("Open destination folder of downloads\tCtrl+D")
        fold_downloads = fileButton.Append(wx.ID_ANY, dscrp)
        fileButton.AppendSeparator()
        closeItem = fileButton.Append(wx.ID_CLOSE, _("Close view\tCtrl+W"),
                                      _("Close the active view keeping the "
                                        "data in memory and any background "
                                        "processes"))
        exitItem = fileButton.Append(wx.ID_EXIT,
                                     _("Quit YouTube Downloader\tCtrl+Q"),
                                     _("Exit the window by deleting all data "
                                       "in memory"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ Edit menu
        editButton = wx.Menu()
        dscrp = (_("Paste\tCtrl+V"),
                 _("Paste the copied URLs to clipboard"))
        self.paste = editButton.Append(wx.ID_PASTE, dscrp[0], dscrp[1])
        dscrp = (_("Remove selected URL\tDEL"),
                 _("Remove the selected URL from the list"))
        self.delete = editButton.Append(wx.ID_REMOVE, dscrp[0], dscrp[1])
        dscrp = (_("Clear list\tShift+DEL"),
                 _("Clear the URL list"))
        self.clearall = editButton.Append(wx.ID_CLEAR, dscrp[0], dscrp[1])
        editButton.AppendSeparator()
        self.setupItem = editButton.Append(wx.ID_PREFERENCES,
                                           _("Options\tCtrl+P"),
                                           _("YouTube Downloader options"))
        self.menuBar.Append(editButton, _("Edit"))

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("Work notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(toolsButton, _("Tools"))

        # ------------------ View menu
        viewButton = wx.Menu()
        dscrp = (_("Version of yt-dlp"),
                 _("Shows the version in use"))
        self.ydlused = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Latest version of yt-dlp"),
                 _("Check the latest version available on github.com"))
        self.ydllatest = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(viewButton, _("View"))
        # -------
        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.on_close, closeItem)
        self.Bind(wx.EVT_MENU, self.on_exit, exitItem)
        # ----EDIT----
        self.Bind(wx.EVT_MENU, self.textDnDTarget.on_paste, self.paste)
        self.Bind(wx.EVT_MENU, self.textDnDTarget.on_del_url_selected,
                  self.delete)
        self.Bind(wx.EVT_MENU, self.textDnDTarget.delete_all, self.clearall)
        self.Bind(wx.EVT_MENU, self.on_options, self.setupItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)

    # --------Menu Bar Event handler (callbacks)

    def openMydownload(self, event):
        """
        Open the download dir with file manager

        """
        io_tools.openpath(self.appdata['ydlp-outputdir'])
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

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from
        'Version in Use' bar menu
        """
        if wx.GetApp().appset['yt_dlp'] is True:
            this = yt_dlp.version.__version__
            if msgbox:
                wx.MessageBox(_("You are using \"yt-dlp\" "
                                "version {0}").format(this),
                              'Videomass', wx.ICON_INFORMATION, self)
                return this
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self, event):
        """
        check for new version from github.com
        """
        url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        latest = io_tools.get_github_releases(url, "tag_name")
        if latest[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{latest[0]} {latest[1]}",
                          f"{latest[0]}", wx.ICON_ERROR, self)
            return
        wx.MessageBox(_("\"yt-dlp\": Latest version "
                        "available: {0}").format(latest[0]),
                      "Videomass", wx.ICON_INFORMATION, self)
    # -----------------------------------------------------------------#

    def on_outputdir(self, event):
        """
        Button event to set a new destination directory.
        """
        dialdir = wx.DirDialog(self, _("Choose Destination"),
                               self.appdata['ydlp-outputdir'],
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.textDnDTarget.on_file_save(getpath)
            self.appdata['ydlp-outputdir'] = getpath

            confmanager = ConfigManager(self.appdata['fileconfpath'])
            sett = confmanager.read_options()
            sett['ydlp-outputdir'] = self.appdata['ydlp-outputdir']
            confmanager.write_options(**sett)
            dialdir.Destroy()
    # ------------------------------------------------------------------#

    def on_options(self, event):
        """
        Setting dialog event.
        """
        with Ytdlp_Options(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                self.textDnDTarget.on_file_save(self.appdata['ydlp-outputdir'])
    # ------------------------------------------------------------------#

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def toolbar_pos(self):
        """
        Return the toolbar style
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
        style = self.toolbar_pos()
        self.toolbar = self.CreateToolBar(style=style)
        bmp_size = (int(self.appdata['toolbarsize']),
                    int(self.appdata['toolbarsize']))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpback = get_bmp(self.icons['previous'], bmp_size)
            bmpnext = get_bmp(self.icons['next'], bmp_size)
            bmpstat = get_bmp(self.icons['statistics'], bmp_size)
            bmpydl = get_bmp(self.icons['download'], bmp_size)
            bmpstop = get_bmp(self.icons['stop'], bmp_size)
            bmpopt = get_bmp(self.icons['options'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icons['statistics'], wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icons['download'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmpopt = wx.Bitmap(self.icons['options'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        tip = _("Go to the previous panel")
        back = self.toolbar.AddTool(20, _('Back'),
                                    bmpback,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Go to the next panel")
        forward = self.toolbar.AddTool(21, _('Next'),
                                       bmpnext,
                                       tip, wx.ITEM_NORMAL,
                                       )
        tip = _("Shows statistics and information")
        self.btn_ydlstatistics = self.toolbar.AddTool(22, _('Statistics'),
                                                      bmpstat,
                                                      tip, wx.ITEM_NORMAL,
                                                      )
        tip = _("YouTube Downloader options")
        options = self.toolbar.AddTool(26, _('Options'),
                                       bmpopt, tip, wx.ITEM_NORMAL)
        tip = _("Start downloading")
        self.run_download = self.toolbar.AddTool(23, _('Download'),
                                                 bmpydl, tip, wx.ITEM_NORMAL,
                                                 )
        tip = _("Stops current process")
        stop = self.toolbar.AddTool(24, _('Stop'), bmpstop,
                                    tip, wx.ITEM_NORMAL,
                                    )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_back, back)
        self.Bind(wx.EVT_TOOL, self.on_forward, forward)
        self.Bind(wx.EVT_TOOL, self.on_statistics, self.btn_ydlstatistics)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop)
        self.Bind(wx.EVT_TOOL, self.on_options, options)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_back(self, event):
        """
        Return to the previous panel.
        """
        if self.ProcessPanel.IsShown():
            self.panelShown()
            return

        if self.ytDownloader.IsShown():
            self.switch_text_import(self)
            return
    # ------------------------------------------------------------------#

    def on_forward(self, event):
        """
        redirect to corresponding next panel
        """
        if self.ytDownloader.IsShown():
            self.switch_to_processing('Viewing last log')
            return
        self.switch_youtube_downloader(self)
        self.changed = False
    # ------------------------------------------------------------------#

    def switch_text_import(self, event):
        """
        Show URLs import panel.
        """
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        (self.delete.Enable(True),
         self.paste.Enable(True),
         self.clearall.Enable(True)
         )
        self.toolbar.EnableTool(21, True)
        [self.toolbar.EnableTool(x, False) for x in (20, 22, 23, 24)]
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - List of URLs'))
    # ------------------------------------------------------------------#

    def switch_youtube_downloader(self, event):
        """
        Show youtube-dl downloader panel
        """
        self.ytDownloader.clear_data_list(self.changed)
        self.SetTitle(_('Videomass - YouTube Downloader'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Show()
        (self.delete.Enable(False),
         self.paste.Enable(False),
         self.clearall.Enable(False)
         )
        [self.toolbar.EnableTool(x, True) for x in (20, 21, 22, 23)]
        self.toolbar.EnableTool(24, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *args):
        """
        Preparing to processing
        """
        if args[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            [self.toolbar.EnableTool(x, False) for x in (21, 24)]
            [self.toolbar.EnableTool(x, True) for x in (20, 22, 23)]

        elif args[0] == 'YouTube Downloader':
            (self.delete.Enable(False),
             self.paste.Enable(False),
             self.clearall.Enable(False),
             self.setupItem.Enable(False)
             )
            [self.toolbar.EnableTool(x, False) for x in (20, 21, 23, 26)]
            [self.toolbar.EnableTool(x, True) for x in (22, 24)]

        self.SetTitle(_('Videomass - Downloader Message Monitoring'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.ProcessPanel.Show()
        self.Layout()
        self.ProcessPanel.topic_thread(args, self.data_url)
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        By clicking on Download buttons, calls the
        `ytDownloader.on_start()` method, which calls the
        'switch_to_processing' method above.
        """
        if self.ytDownloader.IsShown() or self.ProcessPanel.IsShown():
            if not self.data_url:
                self.switch_text_import(self)
                return
            self.ytDownloader.on_start()
            return
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
        self.toolbar.EnableTool(20, True)
        self.toolbar.EnableTool(24, False)
        self.toolbar.EnableTool(26, True)
        self.toolbar.EnableTool(23, True)
        self.setupItem.Enable(True)

        if self.appdata['shutdown']:
            self.parent.auto_shutdown()
        elif self.appdata['auto_exit']:
            self.parent.auto_exit()
    # ------------------------------------------------------------------#

    def panelShown(self):
        """
        Clicking 'Back button' from the `long_processing_task` panel,
        retrieval at previous panel (see `switch_to_processing`
        method above).
        """
        self.ProcessPanel.Hide()
        self.switch_youtube_downloader(self)
        self.Layout()
