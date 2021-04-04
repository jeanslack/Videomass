# -*- coding: UTF-8 -*-
# Name: wizard_dlg.py
# Porpose: wizard setup dialog
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
from videomass3.vdms_utils.utils import detect_binaries


def write_changes(fileconf, ffmpeg, ffplay, ffprobe, youtubedl, binfound):
    """
    Writes changes to the configuration file

    """
    rowsNum = []  # rows number list
    dic = {}  # used for debug
    with open(fileconf, 'r', encoding='utf8') as f:
        full_list = f.readlines()
    for a, b in enumerate(full_list):
        if not b.startswith('#'):
            if not b == '\n':
                rowsNum.append(a)

    if binfound == 'system':
        full_list[rowsNum[5]] = 'false\n'
        full_list[rowsNum[6]] = '%s\n' % ffmpeg
        full_list[rowsNum[7]] = 'false\n'
        full_list[rowsNum[8]] = '%s\n' % ffprobe
        full_list[rowsNum[9]] = 'false\n'
        full_list[rowsNum[10]] = '%s\n' % ffplay
        full_list[rowsNum[16]] = '%s\n' % youtubedl
    else:
        full_list[rowsNum[5]] = 'true\n'
        full_list[rowsNum[6]] = '%s\n' % ffmpeg
        full_list[rowsNum[7]] = 'true\n'
        full_list[rowsNum[8]] = '%s\n' % ffprobe
        full_list[rowsNum[9]] = 'true\n'
        full_list[rowsNum[10]] = '%s\n' % ffplay
        full_list[rowsNum[16]] = '%s\n' % youtubedl

    with open(fileconf, 'w', encoding='utf8') as fileconf:
        for i in full_list:
            fileconf.write('%s' % i)

    return None


class PageOne(wx.Panel):
    """
    This is a first panel displayed on Wizard dialog box

    """
    get = wx.GetApp()
    OS = get.OS
    MSG2 = (_("Please take a moment to set up the application"))
    MSG3 = (_('Click the "Next" button to get started'))

    def __init__(self, parent, icon):
        """
        """
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
        lab3 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG3,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)

        if PageOne.OS == 'Darwin':
            lab1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(13, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab2.SetFont(wx.Font(11, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 80), 0)
        sizer_base.Add(bitmap_vdms, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab1, 0, wx.CENTER)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 30), 0)
        sizer_base.Add(lab3, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 80), 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()


class PageTwo(wx.Panel):
    """
    Shows panel wizard to locate FFmpeg executables
    and set the Wizard attributes on parent.

    """
    get = wx.GetApp()
    OS = get.OS
    FFMPEG_LOCALDIR = get.FFMPEGlocaldir

    MSG0 = (_('Videomass is an application based on FFmpeg\n'))

    MSG1 = (_('If FFmpeg is not on your computer, this application '
              'will be unusable'))

    MSG2 = (_('If you have already installed FFmpeg on your operating\n'
              'system, click the "Auto-detection" button.'))

    MSG3 = (_('If you want to use a version of FFmpeg located on your\n'
              'filesystem but not installed on your operating system,\n'
              'click the "Locate" button.'))

    def __init__(self, parent):
        """
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        self.parent = parent

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizerText = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG1,
                              style=wx.ALIGN_CENTRE_HORIZONTAL)
        lab2 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG2)
        lab3 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG3)
        self.detectBtn = wx.Button(self, wx.ID_ANY, _("Auto-detection"),
                                   size=(250, -1))
        self.locateBtn = wx.Button(self, wx.ID_ANY, _("Locate"),
                                   size=(250, -1))
        self.labFFpath = wx.StaticText(self, wx.ID_ANY, "",
                                       style=wx.ST_ELLIPSIZE_END |
                                       wx.ALIGN_CENTRE_HORIZONTAL
                                       )
        if PageTwo.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            self.labFFpath.SetFont(wx.Font(13, wx.MODERN,
                                           wx.NORMAL, wx.BOLD, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
            lab1.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
            self.labFFpath.SetFont(wx.Font(10, wx.MODERN,
                                           wx.NORMAL, wx.BOLD, 0, ""))
        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        #sizer_base.Add((0, 5), 0)
        sizer_base.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(sizerText, 0, wx.CENTER)
        sizerText.Add(lab2, 0, wx.EXPAND)
        sizerText.Add((0, 15), 0)
        sizerText.Add(lab3, 0, wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(self.detectBtn, 0, wx.CENTER)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(self.locateBtn, 0, wx.CENTER)
        sizer_base.Add((0, 25), 0)
        sizer_base.Add(self.labFFpath, 0, wx.CENTER | wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # bindings
        self.Bind(wx.EVT_BUTTON, self.detectbin, self.detectBtn)
        self.Bind(wx.EVT_BUTTON, self.Locate, self.locateBtn)
    # -------------------------------------------------------------------#

    def Locate(self, event):
        """
        The user browse manually to find ffmpeg, ffprobe,
        ffplay executables

        """
        self.parent.btnNext.Enable()
        self.locateBtn.Disable(), self.detectBtn.Enable()
        self.labFFpath.SetLabel(_('Click the "Next" button'))
        self.Layout()
    # -------------------------------------------------------------------#

    def detectbin(self, event):
        """
        The user push the auto-detect button to automatically
        detect ffmpeg, ffprobe and ffplay on the O.S.

        """
        if PageTwo.OS == 'Windows':
            executable = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        else:
            executable = ['ffmpeg', 'ffprobe', 'ffplay']

        exit = None
        path = []
        for x in executable:
            status = detect_binaries(PageTwo.OS, x, PageTwo.FFMPEG_LOCALDIR)

            if status[0] == 'not installed':
                wx.MessageBox(_("'{}' is not installed on your computer. "
                                "Install it or indicate another location "
                                "by clicking the 'Locate' button.").format(x),
                              'Videomass: Warning', wx.ICON_EXCLAMATION, self)
                return

            elif status[0] == 'provided':
                exit = status[0]
                path.append(status[1])

            elif not status[0]:
                path.append(status[1])

        if exit == 'provided':
            if wx.MessageBox(_("Videomass already seems to include "
                               "FFmpeg.\n\nDo you want to use that?"),
                             _('Videomass: Please Confirm'),
                             wx.ICON_QUESTION | wx.YES_NO,  None) == wx.NO:
                return

        self.parent.ffmpeg = path[0]
        self.parent.ffprobe = path[1]
        self.parent.ffplay = path[2]
        self.parent.btnNext.Enable()
        self.detectBtn.Disable(), self.locateBtn.Enable()
        self.labFFpath.SetLabel('...Found: "%s"' % path[0])
        self.Layout()


class PageThree(wx.Panel):
    """
    Shows panel to locate manually ffmpeg, ffprobe,
    and ffplay executables and set attributes on parent.

    """
    get = wx.GetApp()
    OS = get.OS
    FFMPEG_LOCALDIR = get.FFMPEGlocaldir

    MSG0 = (_('Locating FFmpeg executables\n'))

    MSG1 = (_('"ffmpeg", "ffprobe" and "ffplay" are required. Complete all\n'
              'the text boxes below by clicking on the respective buttons.'))

    def __init__(self, parent):
        """
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor"""

        self.parent = parent

        if PageTwo.OS == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizerText = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG1)
        #  ffmpeg
        gridffmpeg = wx.BoxSizer(wx.HORIZONTAL)
        self.ffmpegTxt = wx.TextCtrl(self, wx.ID_ANY, "",
                                     style=wx.TE_READONLY)
        gridffmpeg.Add(self.ffmpegTxt, 1, wx.ALL, 5)

        self.ffmpegBtn = wx.Button(self, wx.ID_ANY, "ffmpeg")
        gridffmpeg.Add(self.ffmpegBtn, 0, wx.RIGHT | wx.CENTER, 5)
        #  ffprobe
        gridffprobe = wx.BoxSizer(wx.HORIZONTAL)
        self.ffprobeTxt = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_READONLY)
        gridffprobe.Add(self.ffprobeTxt, 1, wx.ALL, 5)

        self.ffprobeBtn = wx.Button(self, wx.ID_ANY, "ffprobe")
        gridffprobe.Add(self.ffprobeBtn, 0, wx.RIGHT | wx.CENTER, 5)
        #  ffplay
        gridffplay = wx.BoxSizer(wx.HORIZONTAL)
        self.ffplayTxt = wx.TextCtrl(self, wx.ID_ANY, "",
                                     style=wx.TE_READONLY)
        gridffplay.Add(self.ffplayTxt, 1, wx.ALL, 5)

        self.ffplayBtn = wx.Button(self, wx.ID_ANY, "ffplay")
        gridffplay.Add(self.ffplayBtn, 0, wx.RIGHT | wx.CENTER, 5)

        if PageThree.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        sizer_base.Add(sizerText, 0, wx.CENTER)
        sizerText.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(gridffmpeg, 0, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(gridffprobe, 0, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add((0, 5), 0)
        sizer_base.Add(gridffplay, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # bindings
        self.Bind(wx.EVT_BUTTON, self.on_ffmpeg, self.ffmpegBtn)
        self.Bind(wx.EVT_BUTTON, self.on_ffprobe, self.ffprobeBtn)
        self.Bind(wx.EVT_BUTTON, self.on_ffplay, self.ffplayBtn)

    def on_ffmpeg(self, event):
        """
        Open filedialog to locate ffmpeg executable
        """
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffmpeg), "", "",
                           "ffmpeg binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffmpeg, self.ffmpeg),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffmpeg:
                    self.ffmpegTxt.Clear()
                    self.ffmpegTxt.write(dlgfile.GetPath())
                    self.parent.ffmpeg = dlgfile.GetPath()

    def on_ffprobe(self, event):
        """
        Open filedialog to locate ffprobe executable
        """
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffprobe), "", "",
                           "ffprobe binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffprobe, self.ffprobe),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffprobe:
                    self.ffprobeTxt.Clear()
                    self.ffprobeTxt.write(dlgfile.GetPath())
                    self.parent.ffprobe = dlgfile.GetPath()

    def on_ffplay(self, event):
        """
        Open filedialog to locate ffplay executable
        """
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffplay), "", "",
                           "ffplay binarys (*%s)|*%s| All files "
                           "(*.*)|*.*" % (self.ffplay, self.ffplay),
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffplay:
                    self.ffplayTxt.Clear()
                    self.ffplayTxt.write(dlgfile.GetPath())
                    self.parent.ffplay = dlgfile.GetPath()


class PageFour(wx.Panel):
    """
    The PageFour panel asks the user if they want to enable
    youtube-dl. This panel determines whether the PageFive
    panel is displayed or not.

    """
    get = wx.GetApp()
    OS = get.OS

    MSG0 = _('Videomass has a simple graphical\ninterface for youtube-dl\n')

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
        sizerText = wx.BoxSizer(wx.VERTICAL)

        lab0 = wx.StaticText(self, wx.ID_ANY, PageFour.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageFour.MSG1)
        descr = _(" Do you want to enable this feature?")
        self.ckbx_yn = wx.CheckBox(self, wx.ID_ANY, (descr))

        if PageFour.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        # layout
        sizer_base.Add((0, 50), 0)
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)

        sizer_base.Add(sizerText, 0, wx.CENTER)
        sizerText.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        sizerText.Add((0, 50), 0)
        sizerText.Add(self.ckbx_yn, 0, wx.CENTER | wx.ALL, 10)
        sizerText.Add((0, 50), 0)

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


class PageFive(wx.Panel):
    """
    Shows a wizard panel to set downloader preferences aka youtube-dl.
    The display of this panel depends on the PageFour panel settings;
    if the PageFour panel checkbox is True then this panel is shown.

    """
    get = wx.GetApp()
    OS = get.OS
    CACHEDIR = get.CACHEdir

    MSG0 = _('Choose how you want to use youtube-dl\n')

    MSG1 = _('Videomass can use youtube-dl internally as a Python\n'
             'module (recommended) or as an executable file. The\n'
             'executable file can be downloaded and updated from\n'
             'Videomass itself and will be placed on:')

    MSG2 = _('Notice: This version of Videomass can\n'
             'only use youtube-dl as local executable')
    #  if AppImage
    if ('/tmp/.mount_' in sys.executable or os.path.exists(
        os.path.dirname(os.path.dirname(os.path.dirname(
         sys.argv[0]))) + '/AppRun')):

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
        sizerText = wx.BoxSizer(wx.VERTICAL)
        self.rdbDownloader = wx.RadioBox(self, wx.ID_ANY,
                                         (_("Downloader preferences")),
                                         choices=PageFive.dldlist,
                                         majorDimension=1,
                                         style=wx.RA_SPECIFY_COLS
                                         )
        sizer_base.Add((0, 50), 0)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageFive.MSG0,
                             style=wx.ST_ELLIPSIZE_END |
                             wx.ALIGN_CENTRE_HORIZONTAL
                             )
        sizer_base.Add(lab0, 0, wx.CENTER | wx.EXPAND)
        sizer_base.Add((0, 40), 0)
        lab1 = wx.StaticText(self, wx.ID_ANY, PageFive.MSG1)
        sizer_base.Add(sizerText, 0, wx.CENTER)

        sizerText.Add(lab1, 0, wx.CENTER | wx.EXPAND)
        labpath = wx.StaticText(self, wx.ID_ANY, PageFive.CACHEDIR,
                                style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer_base.Add((0, 15), 0)
        sizer_base.Add(labpath, 0, wx.CENTER | wx.EXPAND, 5)
        sizer_base.Add((0, 15), 0)
        sizer_base.Add(self.rdbDownloader, 0, wx.CENTER | wx.ALL, 10)
        sizer_base.Add((0, 15), 0)
        #  if pyinstaller packages
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            lab2 = wx.StaticText(self, wx.ID_ANY, PageFive.MSG2,
                                 style=wx.ALIGN_CENTRE_HORIZONTAL)
            lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            sizer_base.Add(lab2, 0, wx.CENTER | wx.EXPAND)
            self.rdbDownloader.SetSelection(1)
            self.rdbDownloader.Disable()

        if PageFive.OS == 'Darwin':
            lab0.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))

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
    MSG0 = _("Wizard completed successfully!\n")
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
            lab3.SetFont(wx.Font(14, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        else:
            lab0.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            lab1.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL, 0, ""))
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
    for configuring Videomass during the startup.

    """
    get = wx.GetApp()
    getfileconf = get.FILEconf
    YDLPREF = get.YDL_pref
    OS = get.OS

    def __init__(self, icon_videomass):
        """
        Note that the attributes of ffmpeg are set in the "PageTwo"
        and "PageThree" panels. The other values are obtained with
        the `wizard_Finish` method and not on the panels

        """
        self.ffmpeg = None
        self.ffprobe = None
        self.ffplay = None

        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER)
        mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        self.pageOne = PageOne(self, icon_videomass)  # start...
        self.pageTwo = PageTwo(self)  # choose ffmpeg modality
        self.pageThree = PageThree(self)  # browse for ffmpeg binaries
        self.pageFour = PageFour(self)  # choose youtube-dl modality
        self.pageFive = PageFive(self)  # choose youtube-dl binaries
        self.pageFinish = PageFinish(self)  # ...end
        #  hide panels
        self.pageTwo.Hide(), self.pageThree.Hide(), self.pageFour.Hide()
        self.pageFive.Hide(), self.pageFinish.Hide()
        #  adds panels to sizer
        mainSizer.Add(self.pageOne, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageTwo, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageThree, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageFour, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageFive, 1, wx.ALL | wx.EXPAND, 5)
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
        self.Fit()
        self.Layout()

        #  bindings
        self.Bind(wx.EVT_BUTTON, self.On_close)
        self.Bind(wx.EVT_BUTTON, self.on_Back, self.btnBack)
        self.Bind(wx.EVT_BUTTON, self.on_Next, self.btnNext)
        self.Bind(wx.EVT_CLOSE, self.On_close)  # controlla la chiusura (x)

    # events:
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

            if (self.pageTwo.locateBtn.IsEnabled() and
                    self.pageTwo.detectBtn.IsEnabled()):
                self.btnNext.Disable()

        elif self.pageTwo.IsShown():

            if not self.pageTwo.locateBtn.IsEnabled():
                self.pageTwo.Hide(), self.pageThree.Show()
            else:
                self.pageTwo.Hide(), self.pageFour.Show()

        elif self.pageThree.IsShown():
            if (self.pageThree.ffmpegTxt.GetValue() and
                    self.pageThree.ffprobeTxt.GetValue() and
                    self.pageThree.ffplayTxt.GetValue()):
                self.pageThree.Hide(), self.pageFour.Show()
            else:
                wx.MessageBox(_("Some text boxes are still incomplete"),
                              ("Videomass"), wx.ICON_INFORMATION, self)

        elif self.pageFour.IsShown():
            self.pageOne.Hide(), self.pageTwo.Hide(), self.pageFour.Hide()

            if self.pageFour.ckbx_yn.IsChecked():
                self.pageFive.Show()
            else:
                self.pageFinish.Show()
                self.btnNext.SetLabel(_('Finish'))

        elif self.pageFive.IsShown():
            self.pageFive.Hide(), self.pageFinish.Show()
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
            self.pageThree.Hide()
            self.pageTwo.Show()

        elif self.pageFour.IsShown():
            if self.pageTwo.locateBtn.IsEnabled():
                self.pageFour.Hide(), self.pageTwo.Show()
            else:
                self.pageFour.Hide(), self.pageThree.Show()

        elif self.pageFive.IsShown():
            self.pageFive.Hide(), self.pageFour.Show()

        elif self.pageFinish.IsShown():
            self.btnNext.SetLabel(_('Next >'))
            self.pageFinish.Hide()
            if self.pageFour.ckbx_yn.IsChecked():
                self.pageFive.Show()
            else:
                self.pageFour.Show()

        self.Layout()
    # -------------------------------------------------------------------#

    def wizard_Finish(self):
        """
        Get all settings and call `write_changes` to applies changes.
        If `rdbDownloader` is disabled means that use Videomass with
        pyinstaller (pyinstaller does not allow to update easily
        youtube-dl package, only uses youtube-dl executable).

        """
        if self.pageFour.ckbx_yn.IsChecked():

            if not self.pageFive.rdbDownloader.IsEnabled():
                youtubedl = 'local'  # usually pyinstaller packages

            elif self.pageFive.rdbDownloader.GetSelection() == 0:
                youtubedl = 'system'

            elif self.pageFive.rdbDownloader.GetSelection() == 1:
                youtubedl = 'local'
        else:
            youtubedl = 'disabled'

        if not self.pageTwo.locateBtn.IsEnabled():
            binfound = 'local'
        elif not self.pageTwo.detectBtn.IsEnabled():
            binfound = 'system'

        wchange = write_changes(Wizard.getfileconf,
                                self.ffmpeg,
                                self.ffplay,
                                self.ffprobe,
                                youtubedl,
                                binfound
                                )
        if not wchange:
            self.Hide()
            wx.MessageBox(_("Re-start is required"),
                          _("Done!"), wx.ICON_INFORMATION, self)
            self.Destroy()
        else:
            wx.MessageBox('%s' % wchange, 'ERROR', wx.ICON_ERROR, self)
