# -*- coding: UTF-8 -*-

#########################################################
# Name: main_frame.py
# Porpose: top window main frame
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec 28 2018, Sept 10 2019
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
import wx.lib.agw.gradientbutton as GB
import webbrowser
from videomass3.vdms_DIALOGS import dialog_tools
from videomass3.vdms_DIALOGS import settings
from videomass3.vdms_DIALOGS import infoprg
from videomass3.vdms_DIALOGS import while_playing
from videomass3.vdms_DIALOGS import ffmpeg_search
from videomass3.vdms_DIALOGS.mediainfo import Mediainfo
from videomass3.vdms_PANELS import choose_topic
from videomass3.vdms_PANELS import filedrop
from videomass3.vdms_PANELS import textdrop
from videomass3.vdms_PANELS import downloader
from videomass3.vdms_PANELS import video_conv
from videomass3.vdms_PANELS import audio_conv
from videomass3.vdms_PANELS.long_processing_task import Logging_Console
from videomass3.vdms_IO import IO_tools



# set widget colours in some case with html rappresentetion:
azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
green = '#268826'

########################################################################
class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    All panels are instantiated in the init constructor, except 
    ProcessPanel which is instantiated in an appropriate instance 
    method. (see switch_Process method doc strings below)
    """
    def __init__(self, setui, ffmpeg_link,
                 ffprobe_link, ffplay_link, 
                 pathicons):
        """
        NOTE: 'SRCpath' is a current work directory of Videomass 
               program. How it can be localized depend if Videomass is 
               run as portable program or installated program.
        """
        self.videomass_icon = pathicons[0]
        self.icon_runconversion = pathicons[2]

        barC = setui[4][12].split(',') 
        barColor = wx.Colour(int(barC[0]),int(barC[1]),int(barC[2])) 
        # toolbar panel colour
        bBtnC = setui[4][13].split(',')
        self.bBtnC = wx.Colour(int(bBtnC[0]),int(bBtnC[1]),int(bBtnC[2]))
        # toolbar buttons colour
        
        fBtnC = setui[4][14].split(',')
        self.fBtnC = wx.Colour(int(fBtnC[0]),int(fBtnC[1]),int(fBtnC[2]))
        # Buttons Font Colour 
        
        #self.helping = setui[5]# path contestual help for helping:
        self.OS = setui[0]# ID of the operative system:
        SRCpath = setui[1]# share dir (are where the origin files?):
        self.PATHconf = setui[6]
        self.WORKdir = setui[7]
        self.DIRconf = setui[8]
        
        #---------------------------#
        self.threads = setui[4][2]#ffmpeg option, set the cpu threads
        self.ffplay_loglevel = setui[4][3]
        self.ffmpeg_loglevel = setui[4][4]
        self.loglevel_batch = ''#setui[4][7]# marks as batch process
        self.ffmpeg_check = setui[4][5]
        self.ffprobe_check = setui[4][7]
        self.ffplay_check = setui[4][9]
        self.ffmpeg_link = ffmpeg_link
        self.ffprobe_link = ffprobe_link
        self.ffplay_link = ffplay_link
        self.iconset = setui[4][11]
        #-------------------------------# 
        self.data = None# list of items in list control
        self.file_destin = None # path name for file saved destination
        self.time_seq = ''# ffmpeg format time specifier with flag -ss, -t
        self.time_read = {'start seek':['',''],'time':['','']}
        self.duration = [] # empty if not file imported
        self.topicname = None # panel name shown

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        #----------- panel toolbar buttons
        self.btnpanel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        
        infoIbmp = wx.Bitmap(pathicons[4], wx.BITMAP_TYPE_ANY)
        previewbmp = wx.Bitmap(pathicons[5], wx.BITMAP_TYPE_ANY)
        cutbmp = wx.Bitmap(pathicons[6], wx.BITMAP_TYPE_ANY)
        saveprfbmp = wx.Bitmap(pathicons[9], wx.BITMAP_TYPE_ANY)

        self.btn_metaI = GB.GradientButton(self.btnpanel,
                                           size=(-1,25),
                                           bitmap=infoIbmp, 
                                           label=_("Streams Information"))
        self.btn_metaI.SetBaseColours(startcolour=wx.Colour(158,201,232), 
                                      foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_metaI.SetBottomEndColour(self.bBtnC)
        self.btn_metaI.SetBottomStartColour(self.bBtnC)
        self.btn_metaI.SetTopStartColour(self.bBtnC)
        self.btn_metaI.SetTopEndColour(self.bBtnC)
        
        self.btn_playO = GB.GradientButton(self.btnpanel,
                                           size=(-1,25),
                                           bitmap=previewbmp, 
                                           label=_("Preview"))
        self.btn_playO.SetBaseColours(startcolour=wx.Colour(158,201,232), 
                                      foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_playO.SetBottomEndColour(self.bBtnC)
        self.btn_playO.SetBottomStartColour(self.bBtnC)
        self.btn_playO.SetTopStartColour(self.bBtnC)
        self.btn_playO.SetTopEndColour(self.bBtnC)
        
        self.btn_duration = GB.GradientButton(self.btnpanel,
                                              size=(-1,25),
                                              bitmap=cutbmp, 
                                              label=_("Duration"))
        self.btn_duration.SetBaseColours(startcolour=wx.Colour(158,201,232), 
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_duration.SetBottomEndColour(self.bBtnC)
        self.btn_duration.SetBottomStartColour(self.bBtnC)
        self.btn_duration.SetTopStartColour(self.bBtnC)
        self.btn_duration.SetTopEndColour(self.bBtnC)
        
        self.btn_saveprf = GB.GradientButton(self.btnpanel,
                                              size=(-1,25),
                                              bitmap=saveprfbmp, 
                                              label=_("Create Vinc Preset"))
        self.btn_saveprf.SetBaseColours(startcolour=wx.Colour(158,201,232), 
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_saveprf.SetBottomEndColour(self.bBtnC)
        self.btn_saveprf.SetBottomStartColour(self.bBtnC)
        self.btn_saveprf.SetTopStartColour(self.bBtnC)
        self.btn_saveprf.SetTopEndColour(self.bBtnC)

        self.btnpanel.SetBackgroundColour(barColor)
        #self.btnpanel.SetBackgroundColour(wx.Colour(205, 235, 222))
        #---------- others panel instances:
        self.ChooseTopic = choose_topic.Choose_Topic(self, 
                                                     self.OS,
                                                     pathicons[1],
                                                     pathicons[3],
                                                     pathicons[23],
                                                     pathicons[24],
                                                     pathicons[20],
                                                     pathicons[21],
                                                     pathicons[22],
                                                     pathicons[25],
                                                     )
        self.ChooseTopic.SetBackgroundColour(barColor)
        self.ytDownloader = downloader.Downloader(self, self.OS)
        self.VconvPanel = video_conv.Video_Conv(self, 
                                                self.ffmpeg_link,
                                                self.ffplay_link,
                                                self.ffprobe_link,
                                                self.threads, 
                                                self.ffmpeg_loglevel,
                                                self.ffplay_loglevel,
                                                self.OS,
                                                pathicons[7],# icon playfilters
                                                pathicons[8],# icon resetfilters
                                                pathicons[10],# icon resize
                                                pathicons[11],# icon crop
                                                pathicons[12],# icon rotate
                                                pathicons[13],# icon deinterlace
                                                pathicons[14],# icon ic_denoiser
                                                pathicons[15],# icon analyzes
                                                pathicons[16],# icon settings
                                                pathicons[18],# icon peaklevel
                                                pathicons[19],# icon audiotrack
                                                self.bBtnC,
                                                self.fBtnC,
                                                )
        self.AconvPanel = audio_conv.Audio_Conv(self, 
                                                self.ffmpeg_link, 
                                                self.threads,
                                                self.ffmpeg_loglevel, 
                                                self.ffprobe_link,
                                                self.OS,
                                                pathicons[15],# icon analyzes
                                                pathicons[16],# icon settings
                                                pathicons[18],# icon peaklevel
                                                self.bBtnC,
                                                self.fBtnC,
                                                )

        self.fileDnDTarget = filedrop.FileDnD(self, 
                                              self.ffprobe_link, 
                                              pathicons[26]) # panel
        self.textDnDTarget = textdrop.TextDnD(self, pathicons[26]) # panel
        
        self.ProcessPanel = Logging_Console(self)
        
        self.fileDnDTarget.Hide()
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.VconvPanel.Hide()
        self.AconvPanel.Hide()
        self.ProcessPanel.Hide()
        # Layout toolbar buttons:
        self.mainSizer = wx.BoxSizer(wx.VERTICAL) # sizer base global
        grid_pan = wx.FlexGridSizer(1, 7, 0, 0)
        grid_pan.Add(self.btn_metaI, 0, wx.CENTER|wx.ALL, 5)
        grid_pan.Add(self.btn_playO, 0, wx.CENTER|wx.ALL, 5)
        grid_pan.Add(self.btn_duration, 0, wx.CENTER|wx.ALL, 5)
        grid_pan.Add(self.btn_saveprf, 0, wx.CENTER|wx.ALL, 5)
        self.btnpanel.SetSizer(grid_pan) # set panel
        self.mainSizer.Add(self.btnpanel, 0, wx.EXPAND, 0)
        # Layout externals panels:
        self.mainSizer.Add(self.ChooseTopic, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.fileDnDTarget, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.ytDownloader, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.VconvPanel, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.AconvPanel, 1, wx.EXPAND|wx.ALL, 0)
        self.mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND|wx.ALL, 0)
        
        #----------------------Set Properties----------------------#
        self.SetTitle("Videomass")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.videomass_icon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        if self.OS == 'Darwin':
            self.SetSize((970, 500))
        elif self.OS == 'Windows':
            self.SetSize((900, 530))
        else:
            self.SetSize((1000, 600))
        #self.Centre()
        #self.CentreOnScreen() # se lo usi, usa CentreOnScreen anziche Centre
        self.SetSizer(self.mainSizer)
        #self.Layout()
        
        # Tooltips:
        self.btn_duration.SetToolTip(_('Set a global timeline to apply to '
                                       'any media file with duration.'
                                           ))
        self.btn_metaI.SetToolTip(_("Show information about the metadata "
                                        "of the selected imported file." 
                                        ))
        self.btn_playO.SetToolTip(_("Choose a file to playback in the "
                                    "destination folder"
                                        ))
        self.btn_saveprf.SetToolTip(_("Save the settings as a preset for Vinc"
                                        ))
        # menu bar
        self.videomass_menu_bar()
        ## tool bar main
        self.videomass_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        
        # hide toolbar and buttons bar
        self.toolbar.Hide()
        self.btnpanel.Hide()
        self.Layout()
        
        #---------------------- Binding (EVT) ----------------------#
        self.fileDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.onCustomSave)
        self.textDnDTarget.btn_save.Bind(wx.EVT_BUTTON, self.onCustomSave)
        self.Bind(wx.EVT_BUTTON, self.Cut_range, self.btn_duration)
        self.Bind(wx.EVT_BUTTON, self.Saveprofile, self.btn_saveprf)
        self.Bind(wx.EVT_BUTTON, self.ImportInfo, self.btn_metaI)
        self.Bind(wx.EVT_BUTTON, self.ExportPlay, self.btn_playO)
        #self.Bind(wx.EVT_SHOW, self.panelShown)
        #self.fileDnDTargetPanel.fileListCtrl.Bind(wx.EVT_LIST_INSERT_ITEM, self.new_isertion)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        
    #-------------------Status bar settings--------------------#
    def statusbar_msg(self, msg, color):
        """
        set the status-bar with messages and color types
        """
        if color == None:
            self.sb.SetBackgroundColour(wx.NullColour)
        else:
            self.sb.SetBackgroundColour(color)
        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    #
    #------------------------------------------------------------------#
    def choosetopicRetrieve(self):
        """
        Retrieve to choose topic panel and reset data object
        """
        self.topicname = None
        self.data = None
        self.fileDnDTarget.deleteAll(self), self.fileDnDTarget.Hide()
        self.textDnDTarget.deleteAll(self), self.textDnDTarget.Hide()
        if self.ytDownloader.IsShown():
            self.ytDownloader.fcode.DeleteAllItems()
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.on_Choice(self)
            self.ytDownloader.Hide()
            
        elif self.VconvPanel.IsShown():
            self.VconvPanel.normalize_default()
            self.VconvPanel.Hide()
            
        elif self.AconvPanel.IsShown():
            self.AconvPanel.normalization_default()
            self.AconvPanel.Hide()
            
        self.ChooseTopic.Show(), self.toolbar.Hide(), self.btnpanel.Hide()
        self.statusbar_msg(_(''), None)
        self.Layout()
    #------------------------------------------------------------------#
    def topic_Redirect(self, data):
        """
        """
        self.data = data
        if self.topicname == 'Video Conversions':
            self.switch_video_conv(self)
            
        elif self.topicname == 'Audio Conversions':
            self.switch_audio_conv(self)
        
        elif self.topicname == 'Youtube Downloader':
            self.youtube_Downloader(self)

    #---------------------- Event handler (callback) ------------------#
    # This series of events are interceptions of the filedrop panel
    #-------------------------------- Options ----------------------------#
    def Cut_range(self, event):
        """
        Call dialog to Set a global time sequence on all imported
        media. Here set self.time_seq and self.time_read attributes
        """
        data = ''

        dial = dialog_tools.Cut_Range(self, self.time_seq)
        retcode = dial.ShowModal()
        if retcode == wx.ID_OK:
            data = dial.GetValue()
            if data == '-ss 00:00:00 -t 00:00:00':
                data = ''
                self.time_read['start seek'] = ['','']
                self.time_read['time'] = ['','']
                self.btn_duration.SetBottomEndColour(self.bBtnC)
            else:
                self.btn_duration.SetBottomEndColour(wx.Colour(255, 255, 0))
                # set a more readable time
                ss = data.split()[1] # the -ss flag
                h,m,s = ss.split(':')
                start = (int(h)*60+ int(m)*60+ int(s))
                t = data.split()[3] # the -t flag
                h,m,s = t.split(':')
                time = (int(h)*60+ int(m)*60+ int(s))
                self.time_read['start seek'] = [ss,start]
                self.time_read['time'] = [t,time]
                
            self.time_seq = data
        else:
            dial.Destroy()
            return
    #------------------------------ Menu  Streams -----------------------#
    def ImportPlay(self, filepath):
        """
        Redirect input file clicked at stream_play for playback feature.
        This feature is available by context menu in drag n drop panel only.
        """
        IO_tools.stream_play(filepath, 
                             self.time_seq, 
                            '', # parameters
                            )
    #------------------------------------------------------------------#
    def ImportInfo(self, event):
        """
        Redirect input file clicked at stream_info for metadata display
        """
        
        dialog = Mediainfo(self.data, self.OS,)
        dialog.Show()
    #------------------------------------------------------------------#
    
    def ExportPlay(self, event):
        """
        Playback with FFplay
        
        """
        with wx.FileDialog(self, "Videomass: Open a file to playback", 
                           defaultDir=self.file_destin,
                           #wildcard="Audio source (%s)|%s" % (f, f),
                           style=wx.FD_OPEN | 
                           wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     
            pathname = fileDialog.GetPath()

        IO_tools.stream_play(pathname,
                             '', # time_seq is useless for the exported file
                             '', # no others parameters are needed
                             )
    #------------------------------------------------------------------#
    def Saveprofile(self, event):
        """
        Store new profile with same current settings of the panel shown 
        (Video Conversion & Audio Conversion)..
        Every modification on the panel shown will be reported when saving 
        a new profile.
        """
        if self.VconvPanel.IsShown():
            self.VconvPanel.Addprof()
        elif self.AconvPanel.IsShown():
            self.AconvPanel.Addprof()
        else:
            print ('Videomass: Error, no panels shown')
            
    #------------------------------------------------------------------#
    #def onCheckBox(self, event):
        #"""
        #Intercept the Checkbox event in the filedrop panel
        #and set same file sources destination path
        #"""
        #if self.fileDnDTarget.IsShown():
            #self.fileDnDTarget.same_filedest()
            #self.file_destin = self.fileDnDTarget.file_dest
            
        #elif self.textDnDTarget.IsShown():
            #self.textDnDTarget.same_filedest()
            #self.file_destin = self.textDnDTarget.file_dest
    #------------------------------------------------------------------#
    def onCustomSave(self, event):
        """
        Intercept the button 'save' event in the filedrop panel
        and set file custom destination path
        """
        if self.fileDnDTarget.IsShown():
            self.fileDnDTarget.on_custom_save()
            self.file_destin = self.fileDnDTarget.file_dest
            
        elif self.textDnDTarget.IsShown():
            self.textDnDTarget.on_custom_save()
            self.file_destin = self.textDnDTarget.file_dest
    #------------------------------------------------------------------#
    def on_close(self, event):
        """
        switch to panels or destroy the videomass app.
        
        """
        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)
            
        elif not self.topicname:
            if wx.MessageBox(_('Are you sure you want to exit?'), 
                    _('Exit'), wx.ICON_QUESTION | wx.YES_NO, 
                    self) == wx.YES:
                self.Destroy()
        else:
            self.choosetopicRetrieve()
    
    #### -------------   BUILD THE MENU BAR  ----------------###
    def videomass_menu_bar(self):
        """
        Make a menu bar. Per usare la disabilitazione di un menu item devi
        prima settare l'attributo self sull'item interessato - poi lo gestisci
        con self.item.Enable(False) per disabilitare o (True) per abilitare.
        Se vuoi disabilitare l'intero top di items fai per esempio:
        self.menuBar.EnableTop(6, False) per disabilitare la voce Help.
        """
        self.menuBar = wx.MenuBar()
        
        ####----------------------- file
        fileButton = wx.Menu()
        
        self.file_save = fileButton.Append(wx.ID_SAVE, _("Choose a Destination " 
                                                        "folder.."), 
                        _("Choice a folder where save processed files"))

        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit"), _("Close Videomass"))
        self.menuBar.Append(fileButton,"&File")
        
        ####------------------ tools button
        toolsButton = wx.Menu()
        
        playing = toolsButton.Append( wx.ID_ANY, _("While playing"), 
        _("Show dialog box with keyboard shortcuts useful during playback"))
        toolsButton.AppendSeparator()
        checkconf = toolsButton.Append( wx.ID_ANY, _("FFmpeg specifications"), 
                            _("Shows the configuration features of FFmpeg"))
        toolsButton.AppendSeparator()
        ckformats = toolsButton.Append( wx.ID_ANY, _("FFmpeg file formats"),
                                _("Shows file formats available on FFmpeg"))
        toolsButton.AppendSeparator()
        ckcoders = toolsButton.Append( wx.ID_ANY, _("FFmpeg encoders"),
                                _("Shows available encoders on FFmpeg"))
        ckdecoders = toolsButton.Append( wx.ID_ANY, _("FFmpeg decoders"),
                                _("Shows available decoders on FFmpeg"))
        toolsButton.AppendSeparator()
        searchtopic = toolsButton.Append( wx.ID_ANY, _("FFmpeg search topics"),
                        _("Show a dialog box to help you find FFmpeg topics"))
        toolsButton.AppendSeparator()
        openlogdir = toolsButton.Append( wx.ID_ANY, _("Log directory"),
                            _("Opens the Videomass log directory if it exists"))
        openconfdir = toolsButton.Append( wx.ID_ANY,
                                         _("Configuration directory"),
                            _("Opens the Videomass configuration directory"))
        self.menuBar.Append(toolsButton,_("&Tools"))
        
        ####------------------ setup button
        setupButton = wx.Menu()
        setupItem = setupButton.Append(wx.ID_PREFERENCES, _("Setup"), 
                                       _("General Settings"))
        
        self.menuBar.Append(setupButton,_("&Preferences"))
        
        ####------------------ help buton
        helpButton = wx.Menu()
        helpItem = helpButton.Append( wx.ID_HELP, _("User Guide"), "")
        wikiItem = helpButton.Append( wx.ID_ANY, _("Wiki"), "")
        issueItem = helpButton.Append( wx.ID_ANY, _("Issue tracker"), "")
        helpButton.AppendSeparator()
        DonationItem = helpButton.Append( wx.ID_ANY, _("Donation"), "")
        helpButton.AppendSeparator()
        docFFmpeg = helpButton.Append(wx.ID_ANY, _("FFmpeg documentation"), "")
        helpButton.AppendSeparator()
        checkItem = helpButton.Append(wx.ID_ANY, _("Check new releases"), "")
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Videomass"), "")
        self.menuBar.Append(helpButton, _("&Help"))

        self.SetMenuBar(self.menuBar)
        
        #-----------------------Binding menu bar-------------------------#
        #----FILE----
        self.Bind(wx.EVT_MENU, self.File_Save, self.file_save)
        self.Bind(wx.EVT_MENU, self.Quiet, exitItem)
        #----TOOLS----
        self.Bind(wx.EVT_MENU, self.durinPlayng, playing)
        self.Bind(wx.EVT_MENU, self.Check_conf, checkconf)
        self.Bind(wx.EVT_MENU, self.Check_formats, ckformats)
        self.Bind(wx.EVT_MENU, self.Check_enc, ckcoders)
        self.Bind(wx.EVT_MENU, self.Check_dec, ckdecoders)
        self.Bind(wx.EVT_MENU, self.Search_topic, searchtopic)
        self.Bind(wx.EVT_MENU, self.Openlog, openlogdir)
        self.Bind(wx.EVT_MENU, self.Openconf, openconfdir)
        
        #----SETUP----
        self.Bind(wx.EVT_MENU, self.Setup, setupItem)
        #----HELP----
        self.Bind(wx.EVT_MENU, self.Helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.Wiki, wikiItem)
        self.Bind(wx.EVT_MENU, self.Issues, issueItem)
        self.Bind(wx.EVT_MENU, self.Donation, DonationItem)
        self.Bind(wx.EVT_MENU, self.DocFFmpeg, docFFmpeg)
        self.Bind(wx.EVT_MENU, self.CheckNewReleases, checkItem)
        self.Bind(wx.EVT_MENU, self.Info, infoItem)
        
    #-------------------Menu Bar Event handler (callback)----------------------#
    
    #-------------------------- Menu  File -----------------------------#
    def File_Save(self, event):
        """
        Open choice dialog output
        """
        self.fileDnDTarget.on_custom_save()
    #--------------------------------------------------#

    def Quiet(self, event):
        """
        destroy the videomass.
        """
        self.on_close(self)
                
    #------------------------ Menu  Preferences -------------------------#

    def Setup(self, event):
        """
        Call the module setup for setting preferences
        """
        #self.parent.Setup(self)
        setup_dlg = settings.Setup(self, self.threads, self.ffplay_loglevel, 
                                   self.ffmpeg_loglevel, self.ffmpeg_link, 
                                   self.ffmpeg_check, self.ffprobe_link, 
                                   self.ffprobe_check, self.ffplay_link, 
                                   self.ffplay_check, self.OS, 
                                   self.iconset, self.PATHconf,
                                   self.WORKdir
                                     )
        setup_dlg.ShowModal()
    
    #--------------------------- Menu Tools ---------------------------#
    def durinPlayng(self, event):
        """
        show dialog with shortcuts keyboard for FFplay
        """
        dlg = while_playing.While_Playing(self.OS)
        dlg.Show()
        
    #------------------------------------------------------------------#
    def Check_conf(self, event):
        """
        Call IO_tools.test_conf
        
        """
        IO_tools.test_conf(self.ffmpeg_link, self.ffprobe_link, 
                                 self.ffplay_link
                                 )
    #------------------------------------------------------------------#
    def Check_formats(self, event):
        """
        IO_tools.test_formats
        
        """
        IO_tools.test_formats(self.ffmpeg_link)
    #------------------------------------------------------------------#
    def Check_enc(self, event):
        """
        IO_tools.test_encoders
        
        """
        IO_tools.test_codecs(self.ffmpeg_link, '-encoders')
    #------------------------------------------------------------------#
    def Check_dec(self, event):
        """
        IO_tools.test_encoders
        
        """
        IO_tools.test_codecs(self.ffmpeg_link, '-decoders')
    #------------------------------------------------------------------#
    def Search_topic(self, event):
        """
        Show a dialog box to help you find FFmpeg topics
        
        """
        dlg = ffmpeg_search.FFmpeg_Search(self.ffmpeg_link, self.OS)
        dlg.Show()
    #------------------------------------------------------------------#
    def Openlog(self, event):
        """
        Open the log diretctory with file manager
        
        """
        IO_tools.openpath('openlog')
    #------------------------------------------------------------------#
    def Openconf(self, event):
        """
        Open the configuration folder with file manager
        
        """
        IO_tools.openpath('dirconf')
        
    #---------------------------- Menu Edit ----------------------------#
    def Helpme(self, event):
        """Online User guide"""
        page = 'https://jeanslack.github.io/Videomass/videomass_use.html'
        webbrowser.open(page)

    #------------------------------------------------------------------#
    def Wiki(self, event):
        """Wiki page """
        page = 'https://github.com/jeanslack/Videomass/wiki'
        webbrowser.open(page)
        
    #------------------------------------------------------------------#
    def Issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Videomass/issues'
        webbrowser.open(page)
        
    #------------------------------------------------------------------#
    def Donation(self, event):
        """Display Issues page on github"""
        page = 'https://jeanslack.github.io/Videomass/donation.html'
        webbrowser.open(page)
        
    #------------------------------------------------------------------#
    def DocFFmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
        
    #-------------------------------------------------------------------#
    def CheckNewReleases(self, event):
        """
        Check for new version releases of Videomass, useful for 
        users with Videomass installer on Windows and MacOs.
        """
        from videomass3.vdms_SYS.msg_info import current_release
        """
        FIXME : There are was some error regarding 
        [SSL: CERTIFICATE_VERIFY_FAILED]
        see:
        <https://stackoverflow.com/questions/27835619/urllib-and-ssl-
        certificate-verify-failed-error>
        <https://stackoverflow.com/questions/35569042/ssl-certificate-
        verify-failed-with-python3>
        """
        import ssl
        import urllib.request
        
        cr = current_release()
        
        #ssl._create_default_https_context = ssl._create_unverified_context

        try:
            context = ssl._create_unverified_context()
            f = urllib.request.urlopen('https://pypi.org/project/videomass/',
                                       context=context
                                       )
            #f = urllib.request.urlopen(
                            #'https://test.pypi.org/project/videomass/',
                            #context=context
                                       #)
            myfile = f.read().decode('UTF-8')
            page = myfile.strip().split()
            indx = ''
            for v in page:
                if 'class="package-header__name">' in v:
                    indx = page.index(v)

        except IOError as error:
            wx.MessageBox("%s" % error, "Videomass: ERROR", 
                          wx.ICON_ERROR, None
                          )
            return
        
        except urllib.error.HTTPError as error:
            wx.MessageBox("%s" % error, "Videomass: ERROR", 
                          wx.ICON_ERROR
                          )
            return
            
        if indx: 
            new_major, new_minor, new_micro =  page[indx+2].split('.')
            new_version = int('%s%s%s' %(new_major, new_minor, new_micro))
            this_major, this_minor, this_micro = cr[2].split('.')
            this_version = int('%s%s%s' %(this_major, this_minor, this_micro))
            
            if new_version > this_version:
                wx.MessageBox(_('A new version (v{0}) of Videomass is available'
                                '\nfrom <https://pypi.org/project/videomass/>') 
                            .format(page[indx+2]), "Videomass: Check new version", 
                                wx.ICON_INFORMATION, None
                                )
            else:
                wx.MessageBox(_('You are already using the latest version '
                                '(v{0}) of Videomass').format(cr[2]), 
                                "Videomass: Check new version", 
                                wx.ICON_INFORMATION, None
                                )
        else:
            wx.MessageBox(_('An error was found in the search for '
                            'the web page.\nSorry for this inconvenience.'),
                            "Videomass: Warning", wx.ICON_EXCLAMATION, None
                          )
            return
    
    #-------------------------------------------------------------------#
    def Info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self, self.videomass_icon)
        
    ####-----------------  BUILD THE TOOL BAR  --------------------###
    def videomass_tool_bar(self):
        """
        Makes and attaches the view toolsBtn bar
        """
        #--------- Properties
        self.toolbar = self.CreateToolBar(style=(wx.TB_HORZ_LAYOUT|
                                                 wx.TB_FLAT|
                                                 wx.TB_TEXT))
        self.toolbar.SetToolBitmapSize((32,32))
        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        # ------- Run process button
        self.toolbar.AddStretchableSpace()
        run_coding = self.toolbar.AddTool(wx.ID_OK, _('Start'), 
                                    wx.Bitmap(self.icon_runconversion)
                                          )
        #self.toolbar.AddStretchableSpace()
        self.toolbar.EnableTool(wx.ID_OK, False)
        #self.toolbar.AddSeparator()
        # finally, create it
        self.toolbar.Realize()
        
        #----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.Run_Coding, run_coding)

    #--------------- Tool Bar Callback (event handler) -----------------#
    def File_import(self, event, which):
        """
        Show files import panel.
        """
        self.topicname = which
        self.textDnDTarget.Hide(), self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.AconvPanel.Hide()
        self.ChooseTopic.Hide(), self.fileDnDTarget.Show()
        if self.file_destin:
            self.fileDnDTarget.text_path_save.SetValue("")
            self.fileDnDTarget.text_path_save.AppendText(self.file_destin)
        self.Layout()
        self.statusbar_msg(_('Add Files'), None)
        
    #------------------------------------------------------------------#
    def Text_import(self, event, which):
        """
        Show URLs import panel.
        """
        self.topicname = which
        self.fileDnDTarget.Hide(),self.ytDownloader.Hide()
        self.VconvPanel.Hide(), self.AconvPanel.Hide()
        self.ChooseTopic.Hide(), self.textDnDTarget.Show()
        if self.file_destin:
            self.textDnDTarget.text_path_save.SetValue("")
            self.textDnDTarget.text_path_save.AppendText(self.file_destin)
        self.Layout()
        self.statusbar_msg(_('Add URLs'), None)

    #------------------------------------------------------------------#
    def youtube_Downloader(self, event):
        """
        Show youtube-dl downloader
        """
        self.file_destin = self.textDnDTarget.file_dest
        
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.VconvPanel.Hide(), self.AconvPanel.Hide()
        self.ytDownloader.Show()#, self.SetSize((700, 800))
        self.statusbar_msg(_('Youtube Downloader'), None)
        self.toolbar.Show(), self.btnpanel.Show(), self.btn_playO.Show()
        self.btn_saveprf.Hide(),self.btn_duration.Hide(),self.btn_metaI.Hide()
        self.toolbar.EnableTool(wx.ID_OK, True)
        self.Layout()

    #------------------------------------------------------------------#
    def switch_video_conv(self, event):
        """
        Show Video converter panel
        """
        self.file_destin = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.AconvPanel.Hide()
        self.VconvPanel.Show(), 
        self.statusbar_msg(_('Video Conversions'), None)
        flist = [f['format']['filename'] for f in 
                 self.data if f['format']['filename']
                 ]
        self.duration = [f['format']['duration'] for f in 
                         self.data if f['format']['duration']
                         ]
        self.VconvPanel.file_src = flist
        self.toolbar.Show(), self.btnpanel.Show()
        self.btn_saveprf.Show(), self.btn_duration.Show(),
        self.btn_metaI.Show(), self.btn_playO.Show()
        self.toolbar.EnableTool(wx.ID_OK, True)
        self.Layout()
        
    #------------------------------------------------------------------#
    def switch_audio_conv(self, event):
        """
        Show Audio converter panel
        """
        self.file_destin = self.fileDnDTarget.file_dest
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.AconvPanel.Show()
        self.statusbar_msg(_('Audio Conversions'), None)
        flist = [f['format']['filename'] for f in 
                 self.data if f['format']['filename']
                 ]
        self.duration = [f['format']['duration'] for f in 
                         self.data if f['format']['duration']
                         ]
        self.AconvPanel.file_src = flist
        self.toolbar.Show(), self.btnpanel.Show()
        self.btn_saveprf.Show(), self.btn_duration.Show()
        self.btn_metaI.Show(), self.btn_playO.Show()
        self.toolbar.EnableTool(wx.ID_OK, True)
        self.Layout()
            
    #------------------------------------------------------------------#
    def switch_Process(self, *varargs):
        """
    1) TIME DEFINITION FOR THE PROGRESS BAR
        For a suitable and efficient progress bar, if a specific 
        time sequence has been set with the duration tool, the total 
        duration of each media file will be replaced with the set time 
        sequence. Otherwise the duration of each media will be the one 
        originated from its real duration.
        
    2) STARTING THE PROCESS
        Here the panel with the progress bar is instantiated which will 
        assign a corresponding thread.
        
        """
        if self.time_seq:
            newDuration = []
            for n in self.duration:
                newDuration.append(self.time_read['time'][1])
            duration = newDuration
        else:
            duration = self.duration

        self.btnpanel.Hide()# hide buttons bar if the user has shown it:
        #Hide all others panels:
        self.fileDnDTarget.Hide(), self.textDnDTarget.Hide(),
        self.ytDownloader.Hide(), self.VconvPanel.Hide(),
        self.AconvPanel.Hide(), 
        #Show the panel:
        self.ProcessPanel.Show()
        self.SetTitle(_('Processing Status - Videomass'))
        [self.menuBar.EnableTop(x, False) for x in range(0,3)]
        #Hide the tool bar
        self.toolbar.Hide()
        self.ProcessPanel.topic_thread(self.topicname, varargs, duration)
        self.Layout()
    #------------------------------------------------------------------#
    def Run_Coding(self, event):
        """
        By clicking the Start encoding button on the main frame, calls 
        the on_ok method of the corresponding panel shown, which calls 
        the 'switch_Process' method above.
        """
        if self.ytDownloader.IsShown():
            self.ytDownloader.on_Start()
        elif self.VconvPanel.IsShown():
            self.VconvPanel.on_ok()
        elif self.AconvPanel.IsShown():
            self.AconvPanel.on_ok()
            
    #------------------------------------------------------------------#
    def panelShown(self, panelshown):
        """
        When clicking 'close button' of the processing panel
        (see switch_Process method above), Retrieval at previous 
        panel showing and re-enables the functions provided by 
        the menu bar.
        """
        if panelshown == 'Video Conversions':
            self.ProcessPanel.Hide()
            self.switch_video_conv(self)
            self.btnpanel.Show()
        elif panelshown == 'Audio Conversions':
            self.ProcessPanel.Hide()
            self.switch_audio_conv(self)
            self.btnpanel.Show()
        elif panelshown == 'Youtube Downloader':
            self.ProcessPanel.Hide()
            self.youtube_Downloader(self)
        # Enable all top menu bar:
        [self.menuBar.EnableTop(x, True) for x in range(0,3)]
        self.SetTitle("Videomass")# set the appropriate title
        # show buttons bar if the user has shown it:
        self.Layout()
        
