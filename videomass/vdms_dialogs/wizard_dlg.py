# -*- coding: UTF-8 -*-
"""
Name: wizard_dlg.py
Porpose: wizard setup dialog for Videomass
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.10.2025
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
import wx
from videomass.vdms_utils.utils import detect_binaries
from videomass.vdms_sys.settings_manager import ConfigManager


def write_changes(ffmpeg, ffplay, ffprobe, binfound):
    """
    Writes changes to the configuration file

    """
    get = wx.GetApp()
    appdata = get.appset
    conf = ConfigManager(appdata['fileconfpath'])
    dataread = conf.read_options()
    if not dataread['trashdir_loc'].strip():
        # prevent Nonetype error saving settings from preferences
        dataread['trashdir_loc'] = appdata['trashdir_default']
    dataread['ffmpeg_cmd'] = ffmpeg
    dataread['ffprobe_cmd'] = ffprobe
    dataread['ffplay_cmd'] = ffplay
    local = not binfound == 'system'
    dataread['ffmpeg_islocal'] = local
    dataread['ffprobe_islocal'] = local
    dataread['ffplay_islocal'] = local

    conf.write_options(**dataread)


class PageOne(wx.Panel):
    """
    This is the first panel displayed on Wizard dialog box

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    MSG2 = _("Please take a moment to set up the application")
    MSG3 = _('Click the "Next" button to get started')

    def __init__(self, parent, icon):
        """
        A simple welcome message is displayed
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.Bitmap(icon, wx.BITMAP_TYPE_ANY)
        img = bitmap.ConvertToImage()
        img = img.Scale(64, 64, wx.IMAGE_QUALITY_NORMAL)
        img = img.ConvertToBitmap()
        bitmap_vdms = wx.StaticBitmap(self, wx.ID_ANY, img)
        lab1 = wx.StaticText(self, wx.ID_ANY,
                             _("Welcome to the Videomass Wizard!"))
        lab2 = wx.StaticText(self, wx.ID_ANY, PageOne.MSG2,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
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
    The PageTwo panel help the user to set the FFmpeg executables.
    This class offers the user two options for determining these
    pathnames:
        - Auto-detect the executables in environment variables.
        - Manually set the user's preferred executables.
    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    GETPATH = get.appset['getpath']
    FFMPEG_LOCALDIR = get.appset['FFMPEG_DIR']

    MSG0 = _('Videomass is an application based on FFmpeg\n')

    MSG1 = (_('If FFmpeg is not on your computer, this application '
              'will be unusable'))

    MSG2 = (_('If you have already installed FFmpeg on your operating '
              'system,\nclick the "Auto-detection" button.'))

    MSG3 = (_('If you want to use a version of FFmpeg located on your '
              'filesystem\nbut not installed on your operating system,\n'
              'click the "Locate" button.'))

    def __init__(self, parent):
        """
        The purpose of this class is to get the FFmpeg
        executables in environment variables as and set
        them to the values of `parent.ffmpeg/ffprobe/ffplay`
        attributes (see Wizard class).
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        self.parent = parent

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizerText = wx.BoxSizer(wx.VERTICAL)
        lab0 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG0,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG1,
                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        lab2 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG2,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
                             )
        lab3 = wx.StaticText(self, wx.ID_ANY, PageTwo.MSG3,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
                             )
        self.detectBtn = wx.Button(self, wx.ID_ANY, _("Auto-detection"),
                                   size=(250, -1))
        self.locateBtn = wx.Button(self, wx.ID_ANY, _("Locate"),
                                   size=(250, -1))
        self.labFFpath = wx.StaticText(self, wx.ID_ANY, "",
                                       style=wx.ST_ELLIPSIZE_END
                                       | wx.ALIGN_CENTRE_HORIZONTAL,
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
        # sizer_base.Add((0, 5), 0)
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
        The user browse manually to find FFmpeg executables

        """
        self.parent.btnNext.Enable()
        self.locateBtn.Disable()
        self.detectBtn.Enable()
        self.labFFpath.SetLabel(_('Click the "Next" button'))
        self.Layout()
    # -------------------------------------------------------------------#

    def detectbin(self, event):
        """
        The user push the auto-detect button to automatically
        detect FFmpeg based on the OS environment variables.

        """
        if PageTwo.OS == 'Windows':
            executable = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        else:
            executable = ['ffmpeg', 'ffprobe', 'ffplay']

        exiting = None
        path = []
        for exe in executable:
            status = detect_binaries(exe, PageTwo.FFMPEG_LOCALDIR)

            if status[0] == 'not installed':
                wx.MessageBox(_("'{}' is not installed on your computer. "
                                "Install it or indicate another location by "
                                "clicking the 'Locate' button.").format(exe),
                              'Videomass: Warning', wx.ICON_EXCLAMATION, self)
                return

            if status[0] == 'provided':
                exiting = status[0]
                path.append(status[1])

            elif not status[0]:
                path.append(status[1])

        if exiting == 'provided':
            if wx.MessageBox(_("Videomass already seems to include "
                               "FFmpeg.\n\nDo you want to use that?"),
                             _('Please confirm'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return

        self.parent.ffmpeg = PageTwo.GETPATH(path[0])
        self.parent.ffprobe = PageTwo.GETPATH(path[1])
        self.parent.ffplay = PageTwo.GETPATH(path[2])
        self.parent.btnNext.Enable()
        self.detectBtn.Disable()
        self.locateBtn.Enable()
        self.labFFpath.SetLabel(f'...Found: "{PageTwo.GETPATH(path[0])}"')
        self.Layout()


class PageThree(wx.Panel):
    """
    Shows panel to locate manually ffmpeg, ffprobe, and
    ffplay executables to setting attributes on parent class.

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    GETPATH = get.appset['getpath']

    MSG0 = _('Locating FFmpeg executables\n')

    MSG1 = (_('"ffmpeg", "ffprobe" and "ffplay" are required. Complete all\n'
              'the text boxes below by clicking on the respective buttons.'))

    def __init__(self, parent):
        """
        The purpose of this class is to get the FFmpeg
        executables manually as and set them to the values
        of `parent.ffmpeg/ffprobe/ffplay` attributes (see Wizard class).
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

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
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
                             )
        lab1 = wx.StaticText(self, wx.ID_ANY, PageThree.MSG1,
                             style=wx.ST_ELLIPSIZE_END
                             | wx.ALIGN_CENTRE_HORIZONTAL,
                             )
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
    # -------------------------------------------------------------------#

    def on_ffmpeg(self, event):
        """
        Open filedialog to locate ffmpeg executable
        """
        with wx.FileDialog(self, _("{} location").format(self.ffmpeg),
                           "", "", "ffmpeg binary "
                           f"(*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffmpeg:
                    self.ffmpegTxt.Clear()
                    ffmpegpath = PageThree.GETPATH(dlgfile.GetPath())
                    self.ffmpegTxt.write(ffmpegpath)
                    self.parent.ffmpeg = ffmpegpath
                    self.check_text_fields()
    # -------------------------------------------------------------------#

    def on_ffprobe(self, event):
        """
        Open filedialog to locate ffprobe executable
        """
        with wx.FileDialog(self, _("{} location").format(self.ffprobe),
                           "", "", "ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffprobe:
                    self.ffprobeTxt.Clear()
                    ffprobepath = PageThree.GETPATH(dlgfile.GetPath())
                    self.ffprobeTxt.write(ffprobepath)
                    self.parent.ffprobe = ffprobepath
                    self.check_text_fields()
    # -------------------------------------------------------------------#

    def on_ffplay(self, event):
        """
        Open filedialog to locate ffplay executable
        """
        with wx.FileDialog(self, _("{} location").format(self.ffplay),
                           "", "", "ffplay binary "
                           f"(*{self.ffplay})|*{self.ffplay}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgfile:

            if dlgfile.ShowModal() == wx.ID_OK:
                if os.path.basename(dlgfile.GetPath()) == self.ffplay:
                    self.ffplayTxt.Clear()
                    ffplaypath = PageThree.GETPATH(dlgfile.GetPath())
                    self.ffplayTxt.write(ffplaypath)
                    self.parent.ffplay = ffplaypath
                    self.check_text_fields()
    # -------------------------------------------------------------------#

    def check_text_fields(self):
        """
        Text boxes must not be empty to enable the
        `parent.Next` button.
        """
        if (self.ffprobeTxt.GetValue() and self.ffmpegTxt.GetValue()
                and self.ffplayTxt.GetValue()):
            self.parent.btnNext.Enable()
        else:
            self.parent.btnNext.Disable()


class PageFinish(wx.Panel):
    """
    This is the last panel displayed on Wizard dialog box

    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    MSG0 = _("Wizard completed successfully!\n")
    MSG1 = (_("Remember that you can always change these settings "
              "later, through the Preferences dialog."))
    MSG3 = _("Thank You!")
    MSG2 = _('To exit click the "Finish" button')

    def __init__(self, parent):
        """
        A thank you message is displayed.
        """
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

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
    This Wizard dialog is a container for all panels instantiated
    on the constructor method of this class. It provides a
    multi-panel dialog box (dynamic wizard) for configuring Videomass
    during the startup.

    """
    def __init__(self, icon_videomass):
        """
        The attributes of ffmpeg, ffprobe, ffplay are set
        in the "PageTwo" and/or "PageThree" classes.

        """
        self.ffmpeg = None
        self.ffprobe = None
        self.ffplay = None

        wx.Dialog.__init__(self, None, -1,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER,
                           )
        mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        self.pageOne = PageOne(self, icon_videomass)  # start...
        self.pageTwo = PageTwo(self)  # choose ffmpeg modality
        self.pageThree = PageThree(self)  # browse for ffmpeg binaries
        self.pageFinish = PageFinish(self)  # ...end
        #  hide panels
        self.pageTwo.Hide()
        self.pageThree.Hide()
        self.pageFinish.Hide()
        #  adds panels to sizer
        mainSizer.Add(self.pageOne, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageTwo, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.pageThree, 1, wx.ALL | wx.EXPAND, 5)
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
        Shows next panel when the 'Next' button is clicked.

        """
        if self.btnNext.GetLabel() == _('Finish'):
            self.wizard_Finish()

        if self.pageOne.IsShown():
            self.pageOne.Hide()
            self.pageTwo.Show()
            self.btnBack.Enable()
            if (self.pageTwo.locateBtn.IsEnabled()
                    and self.pageTwo.detectBtn.IsEnabled()):
                self.btnNext.Disable()

        elif self.pageTwo.IsShown():

            if self.pageTwo.detectBtn.IsEnabled():
                self.pageTwo.Hide()
                self.pageThree.Show()
                if (not self.pageThree.ffmpegTxt.GetValue()
                        and not self.pageThree.ffprobeTxt.GetValue()
                        and not self.pageThree.ffplayTxt.GetValue()):
                    self.btnNext.Disable()
            else:
                self.pageTwo.Hide()
                self.pageFinish.Show()
                self.btnNext.SetLabel(_('Finish'))

        elif self.pageThree.IsShown():
            self.pageThree.Hide()
            self.pageFinish.Show()
            self.btnNext.SetLabel(_('Finish'))

        self.Layout()
    # -------------------------------------------------------------------#

    def on_Back(self, event):
        """
        Shows previous panel when the 'Previous' button is clicked.

        """
        if self.pageTwo.IsShown():
            self.pageTwo.Hide()
            self.pageOne.Show()
            self.btnBack.Disable()
            self.btnNext.Enable()

        elif self.pageThree.IsShown():
            self.pageThree.Hide()
            self.pageTwo.Show()
            self.btnNext.Enable()

        elif self.pageFinish.IsShown():
            self.btnNext.SetLabel(_('Next >'))
            self.pageFinish.Hide()
            if self.pageTwo.locateBtn.IsEnabled():
                self.pageTwo.Show()
            else:
                self.pageThree.Show()

        self.Layout()
    # -------------------------------------------------------------------#

    def wizard_Finish(self):
        """
        This method is called by `on_Next` method of this class,
        e.g. when the user has reached the last step of the wizard

        """
        if not self.pageTwo.locateBtn.IsEnabled():
            binfound = 'local'
        else:  # if not self.pageTwo.detectBtn.IsEnabled():
            binfound = 'system'

        write_changes(self.ffmpeg,
                      self.ffplay,
                      self.ffprobe,
                      binfound
                      )
        get = wx.GetApp()
        appdata = get.appset
        appdata['auto-restart-app'] = True
        self.Destroy()
