# -*- coding: UTF-8 -*-
# Name: wizard_dlg.py
# Porpose: wizard settings dialog
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Jan.09.2020 *PEP8 compatible*
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
import sys
from shutil import which


def write_changes(fileconf, ffmpeg, ffplay, ffprobe, youtubedl):
    """
    Writes changes to the configuration file

    """
    rowsNum = []  # rows number list
    dic = {}  # used for debug
    with open(fileconf, 'r') as f:
        full_list = f.readlines()
    for a, b in enumerate(full_list):
        if not b.startswith('#'):
            if not b == '\n':
                rowsNum.append(a)

    full_list[rowsNum[6]] = '%s\n' % ffmpeg
    full_list[rowsNum[8]] = '%s\n' % ffprobe
    full_list[rowsNum[10]] = '%s\n' % ffplay
    full_list[rowsNum[16]] = '%s\n' % youtubedl

    with open(fileconf, 'w') as fileconf:
        for i in full_list:
            fileconf.write('%s' % i)

    return None


class PageOne(wx.Panel):
    """
    This is a first panel displayed on Wizard dialog box

    """
    get = wx.GetApp()
    OS = get.OS
    MSG2 = _("Please take a moments to set up the application")
    MSG3 = (_('Click the "Next" button to get started'))

    def __init__(self, parent, icon):
        """
        """
        get = wx.GetApp()
        self.getfileconf = get.FILEconf
        self.workdir = get.WORKdir
        self.oS = get.OS
        self.ffmpeglocaldir = get.FFMPEGlocaldir

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.Bitmap(icon, wx.BITMAP_TYPE_ANY)
        img = bitmap.ConvertToImage()
        img = img.Scale(64, 64, wx.IMAGE_QUALITY_NORMAL)
        img = img.ConvertToBitmap()
        bitmap_vdms = wx.StaticBitmap(self, wx.ID_ANY, img)
        lab1 = wx.StaticText(self, wx.ID_ANY,
                             _("Welcome to Videomass Wizard!"))
        lab2 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG2,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab3 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG3)

        if PageOne.OS == 'Darwin':
            lab1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(13, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        else:
            lab1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(11, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 80), 0)
        sizer_base.Add(bitmap_vdms, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab1, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab2, 0, wx.CENTER)
        #sizer_base.Add((0, 30), 0)
        #sizer_base.Add(lab4, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab3, 0, wx.CENTER)
        sizer_base.Add((0, 80), 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()


class PageTwo(wx.Panel):
    """
    Shows a dialog wizard to locate FFmpeg executables
    and set the Wizard attributes aka parent.

    """
    get = wx.GetApp()
    OS = get.OS
    ffmpeglocaldir = get.FFMPEGlocaldir

    MSG00 = (_('Videomass is an application based on FFmpeg'))

    MSG0 = (_('If FFmpeg is not on your computer, this application '
               'is unusable'))

    MSG1 = (_('If you have already installed FFmpeg on your operating '
              'system, click\nthe "Auto-detection" button.'))

    MSG2 = (_('If you want to use a version of FFmpeg located on your '
              'filesystem but\nnot installed on your operating system, '
              'click the "Browse.." button.'))

    def __init__(self, parent):
        """

        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        self.parent = parent

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG00,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab01 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG0,
                              style=wx.ALIGN_CENTRE_HORIZONTAL)
        lab1 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG1,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        lab2 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG2,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.detectBtn = wx.Button(self, wx.ID_ANY, _("Auto-detection"),
                                   size=(250, -1))
        self.browseBtn = wx.Button(self, wx.ID_ANY, _("Browse.."),
                                   size=(250, -1))
        self.labFFpath = wx.StaticText(self, wx.ID_ANY, "",
                                       style=wx.ST_ELLIPSIZE_END |
                                       wx.ALIGN_CENTRE_HORIZONTAL
                                       )
        if PageTwo.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab01.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            lab2.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            self.labFFpath.SetFont(wx.Font(13, wx.MODERN,
                                           wx.NORMAL, wx.BOLD, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab01.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            lab2.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            self.labFFpath.SetFont(wx.Font(10, wx.MODERN,
                                           wx.NORMAL, wx.BOLD, 0, ""))
        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(lab01, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 15), 0)
        sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(self.detectBtn, 0, wx.CENTER)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(self.browseBtn, 0, wx.CENTER)
        sizer_base.Add((0, 25), 0)
        sizer_base.Add(self.labFFpath, 0, wx.CENTER | wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # bindings
        self.Bind(wx.EVT_BUTTON, self.Detect, self.detectBtn)
        self.Bind(wx.EVT_BUTTON, self.Browse, self.browseBtn)
    # -------------------------------------------------------------------#

    def Browse(self, event):
        """
        The user find and import FFmpeg executables folder with
        ffmpeg, ffprobe, ffplay.

        """
        if PageTwo.OS == 'Windows':
            executables = {'ffmpeg.exe': "",
                           'ffprobe.exe': "",
                           'ffplay.exe': ""}
        else:
            executables = {'ffmpeg': "",
                           'ffprobe': "",
                           'ffplay': ""}

        dirdialog = wx.DirDialog(self, _("Select the folder with the ffmpeg, "
                                         "ffrpobe and ffplay files"),
                                 "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
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

            self.parent.ffmpeg = list(executables.items())[0][1]
            self.parent.ffprobe = list(executables.items())[1][1]
            self.parent.ffplay = list(executables.items())[2][1]
            self.parent.btnNext.Enable()
            self.browseBtn.Disable(), self.detectBtn.Enable()
            self.labFFpath.SetLabel('%s' % path)
            self.Layout()
    # -------------------------------------------------------------------#

    def Detect(self, event):
        """
        <https://stackoverflow.com/questions/11210104/check-if
        -a-program-exists-from-a-python-script>

        The search order is as following:
            Search for FFmpeg executables on the system
                if not found
                    Search on the videomass source directory
            If both failed
                show warning.
            else
                set Wizard attributes
        """
        local = False
        if PageTwo.OS == 'Windows':
            executables = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        else:
            executables = ['ffmpeg', 'ffprobe', 'ffplay']

        for required in executables:
            if which(required):
                installed = True
            else:
                if PageTwo.OS == 'Windows':
                    installed = False
                    break
                elif PageTwo.OS == 'Darwin':
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
                if not os.path.isfile("%s/bin/%s" % (PageTwo.ffmpeglocaldir,
                                                     x)):
                    bin_on_src_dir = False
                    break
                else:
                    bin_on_src_dir = True
            if not bin_on_src_dir:
                wx.MessageBox(_("'{}' is not installed on your computer. "
                                "Install it or set a custom location using "
                                "the 'Browse..' button.").format(required),
                              'Videomass: Warning', wx.ICON_EXCLAMATION, self)
                return
            else:
                if wx.MessageBox(_("Videomass already seems to include "
                                   "FFmpeg.\n\nDo you want to use that?"),
                                 _('Videomass: Please Confirm'),
                                 wx.ICON_QUESTION |
                                 wx.YES_NO,
                                 None) == wx.YES:

                    ffmpeg = "%s/bin/%s" % (PageTwo.ffmpeglocaldir,
                                            executables[0])
                    ffprobe = "%s/bin/%s" % (PageTwo.ffmpeglocaldir,
                                             executables[1])
                    ffplay = "%s/bin/%s" % (PageTwo.ffmpeglocaldir,
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

        self.parent.ffmpeg = ffmpeg
        self.parent.ffprobe = ffprobe
        self.parent.ffplay = ffplay
        self.parent.btnNext.Enable()
        self.detectBtn.Disable(), self.browseBtn.Enable()
        self.labFFpath.SetLabel('%s' % os.path.dirname(ffmpeg))
        self.Layout()


class PageThree(wx.Panel):
    """
    The PageThree panel asks the user if they want to enable
    youtube-dl or not. This panel determines whether the PageFour
    panel is displayed or not.

    """
    get = wx.GetApp()
    OS = get.OS

    MSG0 = _('Videomass has a simple graphical interface for youtube-dl')

    MSG1 = _('This feature allows you to download video and audio from\n'
             'many sites, including YouTube.com and even Facebook.')

    def __init__(self, parent):
        """
        NOTE: note the pass statement on `choose_Youtubedl`
        the values of this panel are get by Wizard.wizard_Finish method
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        self.parent = parent
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG1)
        descr = _(" Do you want to enable this feature?")
        self.ckbx_yn = wx.CheckBox(self, wx.ID_ANY, (descr))

        if PageThree.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab1, 0, wx.CENTER)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(self.ckbx_yn, 0, wx.CENTER | wx.ALL, 10)
        sizer_base.Add((0, 50), 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_CHECKBOX, self.choose_Youtubedl, self.ckbx_yn)

    def choose_Youtubedl(self, event):
        """
        the values are get on Wizard.wizard_Finish method
        """
        pass
        '''
        if self.ckbx_yn.IsChecked() is False:
            self.parent.youtubedl = 'disabled'
        else:
            self.parent.youtubedl = None
        '''


class PageFour(wx.Panel):
    """
    Shows a wizard panel to set downloader preferences aka youtube-dl.
    The display of this panel depends on the PageThree panel settings;
    if the PageThree panel checkbox is True then this panel is shown.

    """
    get = wx.GetApp()
    OS = get.OS
    CACHEDIR = get.CACHEdir

    MSG0 = _('Choose how you want to use youtube-dl')

    MSG1 = _('Videomass can use youtube-dl internally as a Python module '
             '(recommended)\nor as an executable file. The executable '
             'file can be downloaded and updated\nby Videomass and will be '
             'placed locally on:')

    MSG2 = _('Notice: This version of Videomass can only use youtube-dl\n'
             'as local executable')
    #  if AppImage
    if '/tmp/.mount_' in sys.executable or \
       os.path.exists(os.getcwd() + '/AppRun'):

        dldlist = [
                _('Use the one included in the AppImage (recommended)'),
                _('Use a local copy of youtube-dl')]
    else:
        dldlist = [
                _('Use the one installed in your O.S. (recommended)'),
                _('Use a local copy of youtube-dl updatable by Videomass')]

    def __init__(self, parent):
        """
        The display of information messages may vary depending
        on the type of installer or type of embedding (usually
        on AppImage and pyinstaller packages)

        NOTE: note the pass statement on `choose_Youtubedl`
        the values of this panel are get by Wizard.wizard_Finish method

        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        self.parent = parent
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.rdbDownloader = wx.RadioBox(self, wx.ID_ANY,
                                         (_("Downloader preferences")),
                                         choices=PageFour.dldlist,
                                         majorDimension=1,
                                         style=wx.RA_SPECIFY_COLS
                                         )
        sizer_base.Add((0, 50), 0)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageFour.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        lab1 = wx.StaticText(self, wx.ID_ANY, PageFour.MSG1)
        sizer_base.Add(lab1, 0, wx.CENTER)
        labpath = wx.StaticText(self, wx.ID_ANY, PageFour.CACHEDIR)
        sizer_base.Add(labpath, 0, wx.CENTER | wx.ALL, 5)
        sizer_base.Add((0, 15), 0)
        sizer_base.Add(self.rdbDownloader, 0, wx.CENTER | wx.ALL, 10)
        sizer_base.Add((0, 15), 0)
        #  if pyinstaller packages
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            lab2 = wx.StaticText(self, wx.ID_ANY, PageFour.MSG2)
            sizer_base.Add(lab2, 0, wx.CENTER)
            lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            self.rdbDownloader.SetSelection(1)
            self.rdbDownloader.Disable()

        if PageFour.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_RADIOBOX, self.choose_Youtubedl, self.rdbDownloader)

    def choose_Youtubedl(self, event):
        """
        the values are get on Wizard.wizard_Finish method
        """
        pass
        '''
        if self.rdbDownloader.GetSelection() == 0:
            self.parent.youtubedl = 'system'
        elif self.rdbDownloader.GetSelection() == 1:
            self.parent.youtubedl = 'local'
        '''


class PageFinish(wx.Panel):
    """
    This is last panel to show during wizard session

    """
    get = wx.GetApp()
    OS = get.OS
    MSG0 = _("Wizard completed successfully!")
    MSG1 = (_("Remember that you can always change these settings "
              "later, through the Setup dialog."))
    MSG3 = _("Thank You!")
    MSG2 = (_('To exit click the "Finish" button'))

    def __init__(self, parent):
        """
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG0,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG1,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab2 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG2,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab3 = wx.StaticText(self, wx.ID_ANY, PageFinish.MSG3,
                             style=wx.ALIGN_CENTRE_HORIZONTAL
                             )
        if PageFinish.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab1.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab2.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab1.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            lab2.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
            lab3.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 120), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab3, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()


class Wizard(wx.Dialog):
    """
    Provides a multi-panel dialog box (dynamic wizard)
    for configuring Videomass during the first start of
    the application.

    """
    get = wx.GetApp()
    getfileconf = get.FILEconf
    YDLPREF = get.YDL_pref

    def __init__(self, icon_videomass):
        """
        Note that the attributes of ffmpeg are set in the
        "PageTwo" panel. The other values are obtained with the
        `wizard_Finish` method and not on the panels

        """
        self.ffmpeg = None
        self.ffprobe = None
        self.ffplay = None

        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER)
        mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        self.pageOne = PageOne(self, icon_videomass)
        self.pageTwo = PageTwo(self)
        self.pageThree = PageThree(self)
        self.pageFour = PageFour(self)
        self.pageFinish = PageFinish(self)
        self.pageTwo.Hide(), self.pageThree.Hide()
        self.pageFour.Hide(), self.pageFinish.Hide()
        mainSizer.Add(self.pageOne, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageTwo, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageThree, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageFour, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageFinish, 1, wx.ALL | wx.EXPAND, 5)
        # bottom side layout
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        gridBtn.Add(btn_cancel, 0)
        gridchoices = wx.GridSizer(1, 2, 0, 5)
        self.btnBack = wx.Button(self, wx.ID_ANY, _("< Previous"))
        self.btnBack.Disable()
        gridchoices.Add(self.btnBack, 0, wx.EXPAND)
        self.btnNext = wx.Button(self, wx.ID_ANY, _("Next >"))
        gridchoices.Add(self.btnNext, 0, wx.EXPAND)
        gridBtn.Add(gridchoices, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        mainSizer.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)
        #  properties
        self.SetTitle(_("Videomass Wizard"))
        self.SetMinSize((700, 500))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(icon_videomass, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Layout()

        #  bindings
        self.Bind(wx.EVT_BUTTON, self.On_close)
        self.Bind(wx.EVT_BUTTON, self.on_Back, self.btnBack)
        self.Bind(wx.EVT_BUTTON, self.on_Next, self.btnNext)
        self.Bind(wx.EVT_CLOSE, self.On_close)  # controlla la chiusura (x)

    # EVENTS:
    def On_close(self, event):
        """
        Destroy app
        """
        self.Destroy()
    # -------------------------------------------------------------------#

    def on_Next(self, event):
        """
        Set the panels to show when the 'Next'
        button is clicked

        """
        if self.btnNext.GetLabel() == _('Finish'):
            self.wizard_Finish()

        if self.pageOne.IsShown():
            self.pageOne.Hide(), self.pageTwo.Show(), self.btnBack.Enable()

            if self.pageTwo.browseBtn.IsEnabled() and \
               self.pageTwo.detectBtn.IsEnabled():
                self.btnNext.Disable()

        elif self.pageTwo.IsShown():
            self.pageTwo.Hide(), self.pageThree.Show()

        elif self.pageThree.IsShown():
            self.pageOne.Hide(), self.pageTwo.Hide(), self.pageThree.Hide()

            if self.pageThree.ckbx_yn.IsChecked():
                self.pageFour.Show()
            else:
                self.pageFinish.Show()
                self.btnNext.SetLabel(_('Finish'))

        elif self.pageFour.IsShown():
            self.pageFour.Hide(), self.pageFinish.Show()
            self.btnNext.SetLabel(_('Finish'))

        self.Layout()
    # -------------------------------------------------------------------#

    def on_Back(self, event):
        """
        Set the panels to show when the 'Previous'
        button is clicked

        """
        if self.pageTwo.IsShown():
            self.pageTwo.Hide()
            self.pageOne.Show()
            self.btnBack.Disable()
            self.btnNext.Enable()

        elif self.pageThree.IsShown():
            self.pageThree.Hide(), self.pageTwo.Show()

        elif self.pageFour.IsShown():
            self.pageFour.Hide(), self.pageThree.Show()

        elif self.pageFinish.IsShown():
            self.btnNext.SetLabel(_('Next >'))
            self.pageFinish.Hide()
            if self.pageThree.ckbx_yn.IsChecked():
                self.pageFour.Show()
            else:
                self.pageThree.Show()

        self.Layout()
    # -------------------------------------------------------------------#

    def wizard_Finish(self):
        """
        Get all settings and call write_changes to applies changes.
        If `rdbDownloader` is disabled means that use Videomass with
        pyinstaller (pyinstaller does not allow to update easily
        youtube-dl package, only uses youtube-dl executable).

        """
        if self.pageThree.ckbx_yn.IsChecked():

            if not self.pageFour.rdbDownloader.IsEnabled():
                youtubedl = 'local'  # usually pyinstaller packages

            elif self.pageFour.rdbDownloader.GetSelection() == 0:
                youtubedl = 'system'

            elif self.pageFour.rdbDownloader.GetSelection() == 1:
                youtubedl = 'local'
        else:
            youtubedl = 'disabled'

        wchange = write_changes(Wizard.getfileconf,
                                self.ffmpeg,
                                self.ffplay,
                                self.ffprobe,
                                youtubedl
                                )
        if not wchange:
            self.Hide()
            wx.MessageBox(_("Re-start is required"),
                          _("Done!"), wx.ICON_INFORMATION, self)
            self.Destroy()
        else:
            wx.MessageBox('%s' % wchange, 'ERROR', wx.ICON_ERROR, self)
