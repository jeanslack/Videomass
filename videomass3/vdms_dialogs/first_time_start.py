# -*- coding: UTF-8 -*-
# Name: first_time_start.py
# Porpose: First-time settings guide (MSwindows and MacOs only)
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.07.2020 *PEP8 compatible*
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
import os
from shutil import which


class FirstStart(wx.Dialog):
    """
    Shows a dialog wizard to locate FFmpeg executables
    """
    MSG1 = (_("This wizard will attempt to automatically detect FFmpeg on\n"
              "your system.\n\n"
              "In addition, it allows you to manually set a custom path\n"
              "to locate FFmpeg and its associated executables.\n\n"
              "Also, Remember that you can always change these settings\n"
              "later, through the Setup dialog.\n\n"
              "- Click on 'Auto-detection' to start the search now."
              "\n\n"
              "- Click on 'Browse..' to indicate the folder where to locate "
              "FFmpeg.\n"))

    def __init__(self, img):
        """
        Set attribute with GetApp (see Videomass.py __init__)
        """
        get = wx.GetApp()
        self.getfileconf = get.FILEconf
        self.workdir = get.WORKdir
        self.oS = get.OS
        self.ffmpeglocaldir = get.FFMPEGlocaldir

        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""

        # widget:
        bitmap_vdms = wx.StaticBitmap(self,
                                      wx.ID_ANY,
                                      wx.Bitmap(img, wx.BITMAP_TYPE_ANY)
                                      )
        lab_welc1 = wx.StaticText(self, wx.ID_ANY, (
                                        _("Welcome to Videomass Wizard!")))
        lab_welc2 = wx.StaticText(self, wx.ID_ANY, (_(FirstStart.MSG1)))
        self.detectBtn = wx.Button(self, wx.ID_ANY, (_("Auto-detection")))
        self.browseBtn = wx.Button(self, wx.ID_ANY, (_("Browse..")))
        close_btn = wx.Button(self, wx.ID_EXIT, "")
        # properties
        self.SetTitle(_("Videomass: Wizard"))
        lab_welc1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        # layout:
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grd_base = wx.FlexGridSizer(2, 1, 0, 0)
        grd_1 = wx.FlexGridSizer(1, 2, 0, 0)
        grd_ext = wx.FlexGridSizer(4, 1, 0, 0)
        grd_2 = wx.FlexGridSizer(3, 2, 0, 0)
        grd_base.Add(grd_1)
        grd_1.Add(bitmap_vdms, 0, wx.ALL, 10)
        grd_1.Add(grd_ext)
        grd_base.Add(grd_2)
        grd_ext.Add(lab_welc1, 0, wx.ALL, 10)
        grd_ext.Add(lab_welc2, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        grd_2.Add(self.detectBtn, 0, wx.ALL, 15)

        grd_2.Add((260, 0), 0, wx.ALL, 5)
        grd_2.Add(self.browseBtn, 0, wx.ALL, 15)

        grd_2.Add((260, 0), 0, wx.ALL, 5)
        grd_btn = wx.FlexGridSizer(1, 2, 0, 0)

        grd_btn.Add(close_btn, 0, flag=wx.ALL, border=5)
        grd_2.Add((260, 0), 0, wx.ALL, 15)
        grd_2.Add(grd_btn, 0,
                  flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        # properties
        self.detectBtn.SetMinSize((200, -1))
        self.browseBtn.SetMinSize((200, -1))
        sizer_base.Add(grd_base)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # bindings
        self.Bind(wx.EVT_BUTTON, self.On_close)
        self.Bind(wx.EVT_BUTTON, self.Detect, self.detectBtn)
        self.Bind(wx.EVT_BUTTON, self.Browse, self.browseBtn)
        self.Bind(wx.EVT_CLOSE, self.On_close)  # controlla la chiusura (x)

    # EVENTS:
    def On_close(self, event):
        self.Destroy()
    # -------------------------------------------------------------------#

    def Browse(self, event):
        """
        The user find and import FFmpeg executables folder with
        ffmpeg, ffprobe, ffplay inside on Posix or ffmpeg.exe, ffprobe.exe,
        ffplay.exe inside on Windows NT.

        """
        if self.oS == 'Windows':
            executables = {'ffmpeg.exe': "",
                           'ffprobe.exe': "",
                           'ffplay.exe': ""}
        else:
            executables = {'ffmpeg': "",
                           'ffprobe': "",
                           'ffplay': ""}

        dirdialog = wx.DirDialog(self, _("Locate the folder with ffmpeg, "
                                         "ffprobe and ffplay"), "",
                                 wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
                                 )
        if dirdialog.ShowModal() == wx.ID_OK:
            path = "%s" % dirdialog.GetPath()
            dirdialog.Destroy()

            filelist = []
            for ff in os.listdir(path):
                if ff in executables.keys():
                    executables[ff] = os.path.join("%s" % path, "%s" % ff)

            error = False
            for key, val in executables.items():
                if not val:
                    error = True
                    break
            if error:
                wx.MessageBox(
                        _("'{}'\nFile not found: '{}'\n"
                          "{}  > are required.\n\n"
                          "Please, choose a valid path.").format(
                          path, key, [k for k in executables.keys()]),
                        "Videomass: error!", wx.ICON_ERROR, self)
                return

            self.completion([v for v in executables.values()])
    # -------------------------------------------------------------------#

    def Detect(self, event):
        """
        Check for dependencies into your system (compatible with Linux,
        MacOsX, Windows)
        <https://stackoverflow.com/questions/11210104/check-if
        -a-program-exists-from-a-python-script>
        Search the executable in the system, if fail stop the search,
        otherwise write the executable pathname in the configuration file.
        """
        local = False
        if self.oS == 'Windows':
            executables = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        else:
            executables = ['ffmpeg', 'ffprobe', 'ffplay']

        for required in executables:
            if which(required):
                installed = True
            else:
                if self.oS == 'Windows':
                    installed = False
                    break
                elif self.oS == 'Darwin':
                    if os.path.isfile("/usr/local/bin/%s" % required):
                        local = True
                        installed = True
                        break
                    else:
                        local = False
                        installed = False
                        break
                else:  # Linux, FreeBSD, etc.
                    installed = False
                    break

        if not installed:
            for x in executables:
                if not os.path.isfile("%s/bin/%s" % (self.ffmpeglocaldir, x)):
                    bin_on_src_dir = False
                    break
                else:
                    bin_on_src_dir = True
            if not bin_on_src_dir:
                wx.MessageBox(_("'{}' is not installed on the system. "
                                "Please, install it or set a custom path "
                                "using the 'Browse..' "
                                "button.").format(required),
                              'Videomass: Warning', wx.ICON_EXCLAMATION, self)
                return
            else:
                if wx.MessageBox(_("Videomass already seems to include "
                                   "FFmpeg.\n\n"
                                   "Do you want to use that?"),
                                 _('Videomass: Please Confirm'),
                                 wx.ICON_QUESTION |
                                 wx.YES_NO,
                                 None) == wx.YES:

                    ffmpeg = "%s/bin/%s" % (self.ffmpeglocaldir,
                                            executables[0])
                    ffprobe = "%s/bin/%s" % (self.ffmpeglocaldir,
                                             executables[1])
                    ffplay = "%s/bin/%s" % (self.ffmpeglocaldir,
                                            executables[2])
                else:
                    return
        else:  # only for MacOs
            if local:
                ffmpeg = "/usr/local/bin/ffmpeg"
                ffprobe = "/usr/local/bin/ffprobe"
                ffplay = "/usr/local/bin/ffplay"
            else:
                ffmpeg = which(executables[0])
                ffprobe = which(executables[1])
                ffplay = which(executables[2])

        self.completion([ffmpeg, ffprobe, ffplay])
    # -------------------------------------------------------------------#

    def completion(self, FFmpeg):
        """
        Writes changes to the configuration file
        """
        ffmpeg = FFmpeg[0]
        ffprobe = FFmpeg[1]
        ffplay = FFmpeg[2]
        rowsNum = []  # rows number list
        dic = {}  # used for debug
        with open(self.getfileconf, 'r') as f:
            full_list = f.readlines()
        for a, b in enumerate(full_list):
            if not b.startswith('#'):
                if not b == '\n':
                    rowsNum.append(a)

        full_list[rowsNum[6]] = '%s\n' % ffmpeg
        full_list[rowsNum[8]] = '%s\n' % ffprobe
        full_list[rowsNum[10]] = '%s\n' % ffplay

        with open(self.getfileconf, 'w') as fileconf:
            for i in full_list:
                fileconf.write('%s' % i)

        wx.MessageBox(_("\nWizard completed successfully.\n"
                        "Restart Videomass now.\n\nThank You!"),
                      _("Done!"))
        self.Destroy()
