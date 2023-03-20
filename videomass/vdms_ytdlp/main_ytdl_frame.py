# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
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
from urllib.parse import urlparse
import webbrowser
import wx
from pubsub import pub
import yt_dlp
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_ytdlp.ydl_mediainfo import YdlMediaInfo
from videomass.vdms_ytdlp.textdrop import TextDnD
from videomass.vdms_ytdlp.youtubedl_ui import Downloader
from videomass.vdms_ytdlp.long_processing_task import LogOut
from videomass.vdms_io import io_tools
from videomass.vdms_sys.settings_manager import ConfigManager


class MainYtdl(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # set status bar colours in html rappresentation:
    ORANGE = '#f28924'
    WHITE = '#fbf4f4'
    # -------------------------------------------------------------#

    def __init__(self, parent=None):
        """
        If not data_url ytDownloader panel will be disabled
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.icons = get.iconset

        # -------------------------------#
        self.data_url = []  # list of urls in text box
        self.changed = True  # previous list is different from new one
        self.filedldir = self.appdata['dirdownload']  # file dest dir
        self.infomediadlg = False  # media info dialog

        wx.Frame.__init__(self, parent, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- panel instances:
        self.ytDownloader = Downloader(self)
        self.textDnDTarget = TextDnD(self)
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
        self.SetMinSize((850, 560))
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
        [self.toolbar.EnableTool(x, False) for x in (3, 13, 14, 18)]
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_outputdir)
        self.Bind(wx.EVT_CLOSE, self.on_close)

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

        self.infomediadlg = YdlMediaInfo(info, self.appdata['ostype'])
        self.infomediadlg.Show()
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
            sett['main_ytdl_size'] = list(self.GetSize())
            sett['main_ytdl_pos'] = list(self.GetPosition())
            confmanager.write_options(**sett)

        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)
        else:
            #if self.appdata['warnexiting']:
                #if wx.MessageBox(_('Are you sure you want to exit?'),
                                 #_('Exit'), wx.ICON_QUESTION | wx.YES_NO,
                                 #self) == wx.NO:
                    #return
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
        dscrp = (_("Downloads folder\tCtrl+D"),
                 _("Open the default downloads folder"))
        fold_downloads = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Open temporary downloads"),
                 _("Open the temporary downloads folder"))
        self.fold_downloads_tmp = fileButton.Append(wx.ID_ANY, dscrp[0],
                                                    dscrp[1])
        self.fold_downloads_tmp.Enable(False)
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Close Videomass"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ View menu
        viewButton = wx.Menu()
        dscrp = (_("Version in Use"),
                 _("Shows the version in use"))
        self.ydlused = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Show the latest version..."),
                 _("Shows the latest version available on github.com"))
        self.ydllatest = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(viewButton, _("View"))

        # ------------------ setup menu
        setupButton = wx.Menu()

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
        self.menuBar.Append(setupButton, _("Settings"))

        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.openMydownloads_tmp,
                  self.fold_downloads_tmp)
        self.Bind(wx.EVT_MENU, self.quiet, exitItem)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.on_outputdir, setdownload_tmp)
        self.Bind(wx.EVT_MENU, self.on_resetfolders_tmp, self.resetfolders_tmp)

    # --------Menu Bar Event handler (callback)
    # --------- Menu  Files

    def openMydownload(self, event):
        """
        Open the download folder with file manager

        """
        io_tools.openpath(self.appdata['dirdownload'])
    # -------------------------------------------------------------------#

    def openMydownloads_tmp(self, event):
        """
        Open the temporary download folder with file manager

        """
        io_tools.openpath(self.filedldir)
    # -------------------------------------------------------------------#

    def quiet(self, event):
        """
        destroy the videomass.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#
    # --------- Menu View ###

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from
        'Version in Use' bar menu
        """
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

    # --------- Menu  Preferences  ###

    def on_outputdir(self, event):
        """
        Event for button and menu to set a
        temporary destination path of files.
        """
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "downloads"), self.filedldir,
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.textDnDTarget.on_file_save(getpath)

            dialdir.Destroy()

            self.resetfolders_tmp.Enable(True)
            self.fold_downloads_tmp.Enable(True)
    # ------------------------------------------------------------------#

    def on_resetfolders_tmp(self, event):
        """
        Restore the default file destination if
        saving temporary files has been set.
        """
        self.textDnDTarget.on_file_save(self.appdata['dirdownload'])
        self.fold_downloads_tmp.Enable(False)
        self.resetfolders_tmp.Enable(False)
        wx.MessageBox(_("Default destination folders successfully restored"),
                      "Videomass", wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    # --------- Menu Help  ###
    # -----------------  BUILD THE TOOL BAR  --------------------###

    def toolbar_pos(self):
        """
        Return the toolbar style
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
            bmpclear = get_bmp(self.icons['cleanup'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icons['statistics'], wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icons['download'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmpclear = wx.Bitmap(self.icons['cleanup'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        tip = _("Go to the previous panel")
        back = self.toolbar.AddTool(3, _('Back'),
                                    bmpback,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Go to the next panel")
        forward = self.toolbar.AddTool(4, _('Next'),
                                       bmpnext,
                                       tip, wx.ITEM_NORMAL,
                                       )
        tip = _("Shows statistics and information")
        self.btn_ydlstatistics = self.toolbar.AddTool(14, _('Statistics'),
                                                      bmpstat,
                                                      tip, wx.ITEM_NORMAL,
                                                      )
        tip = _("Start downloading")
        self.run_download = self.toolbar.AddTool(13, _('Download'),
                                                 bmpydl,
                                                 tip, wx.ITEM_NORMAL,
                                                 )
        tip = _("Stops current process")
        stop = self.toolbar.AddTool(18, _('Stop'), bmpstop,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Clear the URL list")
        clear = self.toolbar.AddTool(20, _('Clear'), bmpclear,
                                     tip, wx.ITEM_NORMAL,
                                     )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_back, back)
        self.Bind(wx.EVT_TOOL, self.on_forward, forward)
        self.Bind(wx.EVT_TOOL, self.on_statistics, self.btn_ydlstatistics)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop)
        self.Bind(wx.EVT_TOOL, self.textDnDTarget.delete_all, clear)

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

        lines = self.textDnDTarget.textctrl_urls.GetValue().split()
        if lines:
            for url in lines:  # Check malformed url
                res = urlparse(url)
                if not res[1]:  # if empty netloc given from ParseResult
                    wx.MessageBox(_('ERROR: Invalid URL: "{}"').format(
                                  url), "Videomass", wx.ICON_ERROR, self)
                    return
            if len(set(lines)) != len(lines):  # equal URLS
                wx.MessageBox(_("ERROR: Some equal URLs found"),
                              "Videomass", wx.ICON_ERROR, self)
                return

            if not lines == self.data_url:
                self.changed = True
                self.destroy_orphaned_window()
                self.data_url = lines.copy()
        else:
            del self.data_url[:]
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
        [self.toolbar.EnableTool(x, True) for x in (4, 20)]
        [self.toolbar.EnableTool(x, False) for x in (3, 13, 14, 18)]
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Videomass - Queued URLs'))
    # ------------------------------------------------------------------#

    def switch_youtube_downloader(self, event):
        """
        Show youtube-dl downloader panel
        """
        self.ytDownloader.clear_data_list(self.changed)
        self.SetTitle(_('Videomass - YouTube Downloader'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Show()
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 14, 13)]
        [self.toolbar.EnableTool(x, False) for x in (18, 20)]

        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *varargs):
        """
        Preparing to processing
        """
        if varargs[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            [self.toolbar.EnableTool(x, False) for x in (4, 18, 20)]
            [self.toolbar.EnableTool(x, True) for x in (3, 14)]

        elif varargs[0] == 'youtube_dl downloading':
            self.menuBar.EnableTop(2, False)
            [self.toolbar.EnableTool(x, False) for x in (3, 4, 13, 20)]
            self.toolbar.EnableTool(18, True)

        self.SetTitle(_('Videomass - Output Monitor'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.ProcessPanel.Show()
        self.ProcessPanel.topic_thread(varargs)
        self.Layout()
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
        self.menuBar.EnableTop(2, True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(18, False)
    # ------------------------------------------------------------------#

    def panelShown(self):
        """
        When clicking 'stop button' of the long_processing_task panel,
        retrieval at previous panel showing and re-enables the functions
        provided by the menu bar (see `switch_to_processing` method above).
        """
        self.ProcessPanel.Hide()
        self.switch_youtube_downloader(self)

        # Enable all top menu bar:
        self.menuBar.EnableTop(2, True)
        # show buttons bar if the user has shown it:
        self.Layout()
