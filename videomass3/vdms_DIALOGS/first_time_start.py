# -*- coding: UTF-8 -*-
#
#########################################################
# Name: first_time_start.py
# Porpose: Automatize settings first time start
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (01) December 28 2018
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
#
import wx
import os
import platform

from shutil import which

dirname = os.path.expanduser('~/') # /home/user/
filename = '%s/.videomass/videomass.conf' % (dirname)
PWD = os.getcwd()
OS = platform.system()

class FirstStart(wx.Dialog):
    """
    Shows a dialog for choosing FFmpeg executables
    """
    def __init__(self, img):
        """
        The self.FFmpeg attribute consists of a list of executable paths. 
        Each list element is composed of the root (dirname) and the name 
        of the executable file (basename).
        """
        self.FFmpeg = []
        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE)
        
        msg = (_(
            u"This wizard will attempt to automatically detect FFmpeg in\n"
            u"your system.\n\n"
            u"In addition, you can manually set a custom path where to\n"
            u"locate FFmpeg.\n\n"
            u"However, you can always change these settings later in the\n"
            u"Setup dialog.\n\n"
            u"- Press the 'Auto-detection' button to start searching now."
            u"\n\n"
            u"- Press the 'Browse' button to browse your folders and locate\n"
            u"  ffmpeg, then 'Confirm' with the button")
               )
        # widget:
        bitmap_drumsT = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(
                                        img,wx.BITMAP_TYPE_ANY))
        lab_welc2 = wx.StaticText(self, wx.ID_ANY, (msg))
        lab_welc1 = wx.StaticText(self, wx.ID_ANY, (
                                        _(u"Welcome to Videomass Wizard!")))
        self.searchBtn = wx.Button(self, wx.ID_ANY, (_(u"Auto-detection")))

        self.confirmBtn = wx.Button(self, wx.ID_ANY, (_(u"Confirm")))

        self.ffmpegBtn = wx.Button(self, wx.ID_ANY, (_(u"Browse..")))
        
        close_btn = wx.Button(self, wx.ID_EXIT, "")
        
        # properties
        self.SetTitle(_(u"Videomass: Wizard"))
        lab_welc1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL,wx.BOLD, 0, ""))
        # layout:
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grd_base = wx.FlexGridSizer(2, 1, 0, 0)
        grd_1 = wx.FlexGridSizer(1, 2, 0, 0)
        grd_ext = wx.FlexGridSizer(4, 1, 0, 0)
        grd_2 = wx.FlexGridSizer(3, 2, 0, 0)
        grd_base.Add(grd_1)
        grd_1.Add(bitmap_drumsT,0,wx.ALL, 10)
        grd_1.Add(grd_ext)
        grd_base.Add(grd_2)
        grd_ext.Add(lab_welc1,0,  wx.ALL, 10)
        grd_ext.Add(lab_welc2,0, wx.ALIGN_CENTER | wx.ALL, 10)
        grd_2.Add(self.searchBtn,0, wx.ALL, 15)

        grd_2.Add((260,0), 0, wx.ALL, 5)
        grd_2.Add(self.ffmpegBtn,0, wx.ALL, 15)

        grd_2.Add((260,0), 0, wx.ALL, 5)
        grd_btn = wx.FlexGridSizer(1, 2, 0, 0)
        
        grd_btn.Add(self.confirmBtn,0, flag=wx.ALL, border=5)
        grd_btn.Add(close_btn,0, flag=wx.ALL, border=5)
        grd_2.Add((260,0), 0, wx.ALL, 15)
        grd_2.Add(grd_btn,0, flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        #properties
        self.searchBtn.SetMinSize((-1, -1))
        self.ffmpegBtn.SetMinSize((-1, -1))
        
        sizer_base.Add(grd_base)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        
        ######################## bindings #####################
        self.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_BUTTON, self.search, self.searchBtn)
        self.Bind(wx.EVT_BUTTON, self.Executables, self.ffmpegBtn)
        self.Bind(wx.EVT_BUTTON, self.on_Custom, self.confirmBtn)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        
    # EVENTS:
    #-------------------------------------------------------------------#
    def on_close(self, event):
        self.Destroy()
    #-------------------------------------------------------------------#
    def Executables(self, event):
        """
        The user find and import FFmpeg executables (ffmpeg, ffprobe, ffplay) 
        on Windows and MacOs..
        """
        data = []
        if OS == 'Windows':
            FFlist = ['ffmpeg.exe','ffprobe.exe','ffplay.exe']
        else:
            FFlist = ['ffmpeg','ffprobe','ffplay']
            
        dirdialog = wx.DirDialog(self, 
                _(u"Videomass: locate the ffmpeg folder"), "", 
                wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
                                )
            
        if dirdialog.ShowModal() == wx.ID_OK:
            path = u"%s" % dirdialog.GetPath()
            dirdialog.Destroy()
    
            for ff in os.listdir(path):
                if ff in FFlist:
                    data.append('%s/%s' % (path,ff)) 
            
            if not data:
                wx.MessageBox(_(u"'{0}' was not found in the specified path:\n"
                                u"'{1}'\n\n"
                                u"Please, choose a valid path."
                                ).format(FFlist[0],path), 
                                "Videomass: warning!",  wx.ICON_WARNING, self
                                )
                return
            
            pathnorm = [os.path.join(norm) for norm in data]# norm for os
            err = False
            for x,y in zip(FFlist,pathnorm):
                if x not in os.path.basename(y):
                    err = True
                    break
            if err:
                wx.MessageBox(_(u"'{0}' was not found in the specified path:\n"
                                u"'{1}'\n"
                                u"Some required executables are missing.\n"
                                u"need {2}"
                                ).format(x,path,FFlist), 
                                "Videomass: warning!",  wx.ICON_WARNING, self
                                )
                return
            
            self.FFmpeg = pathnorm
    #------------------------------------------------------------------#
    def on_Custom(self, event):
        """
        Confirming a custom path, evaluates that the self.FFmpeg list is not 
        empty, then proceeds to send it to the completion function
        """
        
        if not self.FFmpeg:
            wx.MessageBox(_(u"Please, Locate the folder with ffmpeg inside "
                            u"first."),
                            u'Videomass: Warning', wx.ICON_EXCLAMATION, self)
            return

        self.completion(self.FFmpeg)
        
    #-------------------------------------------------------------------#
    def search(self, event):
        """
        Check for dependencies into your system (compatible with Linux, 
        MacOsX, Windows)
        [https://stackoverflow.com/questions/11210104/check-if-a-program-exists-
        from-a-python-script]
        Search the executable in the system, if fail stop the search, 
        otherwise write the executable pathname in the configuration file.
        """
        local = False
        if OS == 'Windows':
            biname = ['ffmpeg.exe','ffprobe.exe','ffplay.exe']
        else:
            biname = ['ffmpeg','ffprobe','ffplay']
            
        for required in biname:
            if which(required):
                print ("Check for: '%s' ..Ok" % required)
                no_which = False
            else:
                print ("Check for: '%s' ..Not Installed" % required)
                if OS == 'Darwin':
                    if os.path.isfile("/usr/local/bin/%s" % required):
                        local = True
                        no_which = False
                        break
                    else:
                        local = False
                        no_which = True
                        break
                elif OS == 'Windows':
                    no_which = True
                    break
        if no_which:
            for x in biname:
                if not os.path.isfile("%s/FFMPEG_BIN/bin/%s" % (PWD, x)):
                    noexists = True
                    break
                else:
                    noexists = False
            if noexists:
                wx.MessageBox(_("'%s' is not installed on the system.\n"
                          "Please, install it or set a new custom path.") 
                          % required, 'Videomass: Warning', 
                          wx.ICON_EXCLAMATION, self)
                return
            else:
                if wx.MessageBox(_("The Videomass system folder already "
                        "includes the binary executables of FFmpeg, "
                        "FFprobe and FFplay.\n\nDo you want to use them?"), 
                        _('Videomass: Please Confirm'),
                        wx.ICON_QUESTION |
                        wx.YES_NO, 
                        None) == wx.YES:
                    ffmpeg = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[0])
                    ffprobe = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[1])
                    ffplay = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[2])
                    self.FFmpeg = [ffmpeg, ffprobe, ffplay]
                else:
                    return
        else:
            if local:
                ffmpeg = "/usr/local/bin/ffmpeg"
                ffprobe = "/usr/local/bin/ffprobe"
                ffplay = "/usr/local/bin/ffplay"
                self.FFmpeg = [ffmpeg, ffprobe, ffplay]
            else:
                ffmpeg = which(biname[0])
                ffprobe = which(biname[1])
                ffplay = which(biname[2])
                self.FFmpeg = [ffmpeg, ffprobe, ffplay]
        
        self.completion(self.FFmpeg)
    #-------------------------------------------------------------------#
    
    def completion(self, FFmpeg):
        """
        Writes changes to the configuration file
        """
        ffmpeg = FFmpeg[0]
        ffprobe = FFmpeg[1]
        ffplay = FFmpeg[2]
        rowsNum = []#rows number list
        dic = {} # used for debug
        with open (filename, 'r') as f:
            full_list = f.readlines()
        for a,b in enumerate(full_list):
            if not b.startswith('#'):
                if not b == '\n':
                    rowsNum.append(a)

        full_list[rowsNum[8]] = '%s\n' % ffmpeg
        full_list[rowsNum[10]] = '%s\n' % ffprobe
        full_list[rowsNum[12]] = '%s\n' % ffplay
        
        with open (filename, 'w') as fileconf:
            for i in full_list:
                fileconf.write('%s' % i)
            
        wx.MessageBox(_("\nWizard completed successfully.\n"
                       "Restart Videomass now.\n\nThank You!"), 
                       _("That's all folks!"))   
        self.Destroy()
        
