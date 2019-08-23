# -*- coding: UTF-8 -*-
#
#########################################################
# Name: first_time_start.py
# Porpose: Automatize settings first time start
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2013-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GNU GENERAL PUBLIC LICENSE (see COPYING)

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

# Rev (00) Sett 15 2018
#########################################################
#
import wx
import os
import platform

from videomass2.vdms_SYS.whichcraft import which

dirname = os.path.expanduser('~/') # /home/user/
filename = '%s/.videomass/videomass.conf' % (dirname)
PWD = os.getcwd()
OS = platform.system()

class FirstStart(wx.Dialog):
    """
    Shows a dialog for choosing FFmpeg executables
    """
    def __init__(self, img):
        """constructor"""
        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE)
        
        msg1 = (_(
            u"This wizard will attempt to automatically detect FFmpeg in\n"
            u"your system.\n\n"
            u"In addition, it allows you to manually set a custom path\n"
            u"to locate FFmpeg and its associated executables.\n\n"
            u"Also, Remember that you can always change these settings\n"
            u"later, through the Setup dialog.\n\n"
            u"- Press 'Auto-detection' to start the system search now."
            u"\n\n"
            u"- Press 'Browse..' to indicate yourself where FFmpeg is located.\n")
               )
        # widget:
        bitmap_drumsT = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(
                                        img,wx.BITMAP_TYPE_ANY))
        lab_welc1 = wx.StaticText(self, wx.ID_ANY, (
                                        _(u"Welcome to Videomass Wizard!")))
        lab_welc2 = wx.StaticText(self, wx.ID_ANY, (msg1))
        
        self.detectBtn = wx.Button(self, wx.ID_ANY, (_(u"Auto-detection")))

        self.browseBtn = wx.Button(self, wx.ID_ANY, (_(u"Browse..")))
        
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
        grd_2.Add(self.detectBtn,0, wx.ALL, 15)

        grd_2.Add((260,0), 0, wx.ALL, 5)
        grd_2.Add(self.browseBtn,0, wx.ALL, 15)

        grd_2.Add((260,0), 0, wx.ALL, 5)
        grd_btn = wx.FlexGridSizer(1, 2, 0, 0)
        
        grd_btn.Add(close_btn,0, flag=wx.ALL, border=5)
        grd_2.Add((260,0), 0, wx.ALL, 15)
        grd_2.Add(grd_btn,0, flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        #properties
        self.detectBtn.SetMinSize((200, -1))
        self.browseBtn.SetMinSize((200, -1))
        
        sizer_base.Add(grd_base)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        
        ######################## bindings #####################
        self.Bind(wx.EVT_BUTTON, self.On_close)
        self.Bind(wx.EVT_BUTTON, self.Detect, self.detectBtn)
        self.Bind(wx.EVT_BUTTON, self.Browse, self.browseBtn)
        self.Bind(wx.EVT_CLOSE, self.On_close) # controlla la chiusura (x)
        
    # EVENTS:
    #-------------------------------------------------------------------#
    def On_close(self, event):
        self.Destroy()
    #-------------------------------------------------------------------#
    def Browse(self, event):
        """
        The user find and import FFmpeg executables folder with
        ffmpeg, ffprobe, ffplay inside on Posix or ffmpeg.exe, ffprobe.exe, 
        ffplay.exe inside on Windows NT.
        """
        
        if OS == 'Windows':
            listFF = {'ffmpeg.exe':"",'ffprobe.exe':"",'ffplay.exe':""}
        else:
            listFF = {'ffmpeg':"",'ffprobe':"",'ffplay':""}
            
        dirdialog = wx.DirDialog(self, 
                _(u"Videomass: locate the ffmpeg folder"), "", 
                wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
                                )
            
        if dirdialog.ShowModal() == wx.ID_OK:
            path = u"%s" % dirdialog.GetPath()
            dirdialog.Destroy()
            
            filelist = []
            for ff in os.listdir(path):
                if ff in listFF.keys():
                    listFF[ff] = os.path.join("%s" % path, "%s" % ff)
                    
            error = False
            for key,val in listFF.items():
                if not val:
                    error = True
                    break
            
            if error:
                wx.MessageBox(_(u"File not found: '{0}'\n"
                                u"'{1}' does not exist!\n\n"
                                u"Need {2}\n\n"
                                u"Please, choose a valid path.").format(
                                        os.path.join("%s" % path, "%s" % key),
                                        key,
                                        [k for k in listFF.keys()]), 
                                "Videomass: warning!",  wx.ICON_WARNING, self
                                )
                return
            
            self.completion([v for v in listFF.values()])

    #-------------------------------------------------------------------#
    def Detect(self, event):
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
                          "Please, install it or set a custom path "
                          "using the 'Browse..' button.") 
                          % required, 'Videomass: Warning', 
                          wx.ICON_EXCLAMATION, self)
                return
            else:
                if wx.MessageBox(_(u"Videomass already seems to include "
                                   u"FFmpeg and the executables associated "
                                   u"with it.\n\n"
                                   u"Are you sure you want to use them?"), 
                        _(u'Videomass: Please Confirm'),
                        wx.ICON_QUESTION |
                        wx.YES_NO, 
                        None) == wx.YES:
                    ffmpeg = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[0])
                    ffprobe = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[1])
                    ffplay = "%s/FFMPEG_BIN/bin/%s" % (PWD, biname[2])
                else:
                    return
        else:
            if local:
                ffmpeg = "/usr/local/bin/ffmpeg"
                ffprobe = "/usr/local/bin/ffprobe"
                ffplay = "/usr/local/bin/ffplay"
            else:
                ffmpeg = which(biname[0])
                ffprobe = which(biname[1])
                ffplay = which(biname[2])
        
        self.completion([ffmpeg,ffprobe,ffplay])
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
            
        wx.MessageBox(_(u"\nWizard completed successfully.\n"
                       "Restart Videomass now.\n\nThank You!"), 
                       _(u"That's all folks!"))   
        self.Destroy()
        
