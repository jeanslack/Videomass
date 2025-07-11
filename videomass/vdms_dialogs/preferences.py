# -*- coding: UTF-8 -*-
"""
Name: preferences.py
Porpose: videomass setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.05.2025
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
from videomass.vdms_utils.utils import detect_binaries
from videomass.vdms_io import io_tools
from videomass.vdms_sys.settings_manager import ConfigManager
from videomass.vdms_sys.app_const import supLang


class SetUp(wx.Dialog):
    """
    Represents settings and configuration
    storing of the program.
    """
    FFPLAY_LOGLEV = [("quiet (Show nothing at all)"),
                     ("fatal (Only show fatal errors)"),
                     ("error (Show all errors)"),
                     ("warning (Show all warnings and errors)"),
                     ("info (Show informative messages during processing)")
                     ]
    FFMPEG_LOGLEV = [("error (Show all errors)"),
                     ("warning (Show all warnings and errors)"),
                     ("info (Show informative messages during processing)"),
                     ("verbose (Same as `info`, except more verbose)"),
                     ("debug (Show everything, including debugging info)")
                     ]
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) default settings already loaded.
        self.confmanager: instance to ConfigManager class
        self.settings: (dict) current user settings from file conf.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.settings = self.confmanager.read_options()
        self.retcode = None

        if self.appdata['ostype'] == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
            self.ffplay = 'ffplay.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe'
            self.ffplay = 'ffplay'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER)

        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerFiles = wx.BoxSizer(wx.VERTICAL)
        sizerFiles.Add((0, 10))
        msg = _("Where do you prefer to save your transcodes?")
        labfile = wx.StaticText(tabOne, wx.ID_ANY, msg)
        sizerFiles.Add(labfile, 0, wx.ALL | wx.EXPAND, 5)
        sizerFiles.Add((0, 10))
        sizeFFdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeFFdirdest, 0, wx.EXPAND)
        self.txtctrl_FFpath = wx.TextCtrl(tabOne, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizeFFdirdest.Add(self.txtctrl_FFpath, 1, wx.ALL, 5)
        self.txtctrl_FFpath.AppendText(self.appdata['outputdir'])
        self.btn_fsave = wx.Button(tabOne, wx.ID_ANY, _('Change'))
        sizeFFdirdest.Add(self.btn_fsave, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        descr = _("Same destination paths as source files")
        self.ckbx_same_dest = wx.CheckBox(tabOne, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_same_dest, 0, wx.ALL, 5)
        sizeSamedest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeSamedest, 0, wx.EXPAND)
        descr = _("Assign optional suffix to destination file names:")
        self.lab_suffix = wx.StaticText(tabOne, wx.ID_ANY, (descr))
        sizeSamedest.Add(self.lab_suffix, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        self.text_suffix = wx.TextCtrl(tabOne, wx.ID_ANY, "", size=(90, -1))
        sizeSamedest.Add(self.text_suffix, 1, wx.ALL | wx.CENTER, 5)
        sizerFiles.Add((0, 20))
        msg = _("File removal preferences")
        labrem = wx.StaticText(tabOne, wx.ID_ANY, msg)
        sizerFiles.Add(labrem, 0, wx.ALL | wx.EXPAND, 5)
        sizerFiles.Add((0, 10))
        descr = _("Trash the source files after successful encoding")
        self.ckbx_trash = wx.CheckBox(tabOne, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_trash, 0, wx.ALL, 5)
        sizetrash = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizetrash, 0, wx.EXPAND)
        self.txtctrl_trash = wx.TextCtrl(tabOne, wx.ID_ANY, "",
                                         style=wx.TE_READONLY
                                         )
        sizetrash.Add(self.txtctrl_trash, 1, wx.ALL, 5)
        self.txtctrl_trash.AppendText(self.appdata['trashdir_loc'])
        self.btn_trash = wx.Button(tabOne, wx.ID_ANY, _('Change'))
        sizetrash.Add(self.btn_trash, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        tabOne.SetSizer(sizerFiles)
        notebook.AddPage(tabOne, _("File Preferences"))

        # -----tab 2
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        sizerFFmpeg = wx.BoxSizer(wx.VERTICAL)
        sizerFFmpeg.Add((0, 10))
        labFFexec = wx.StaticText(tabTwo, wx.ID_ANY,
                                  _('Location of executables'))
        sizerFFmpeg.Add(labFFexec, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_('FFmpeg can be built by enabling/disabling its options '
                 'and this depends on your needs.\nFor some use cases it '
                 'is possible to provide a custom build of FFmpeg where you '
                 'can specify\nit in this preferences tab.'))
        labffdescr = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFFmpeg.Add(labffdescr, 0, wx.ALL | wx.EXPAND, 5)
        sizerFFmpeg.Add((0, 20))
        msg = _("Enable a custom location to run FFmpeg")
        self.ckbx_exeFFmpeg = wx.CheckBox(tabTwo, wx.ID_ANY, (msg))
        self.btn_ffmpeg = wx.Button(tabTwo, wx.ID_ANY, _('Change'))
        self.txtctrl_ffmpeg = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizerFFmpeg.Add(self.ckbx_exeFFmpeg, 0, wx.LEFT, 5)
        gridFFmpeg = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFmpeg, 0, wx.EXPAND)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALL, 5)
        gridFFmpeg.Add(self.btn_ffmpeg, 0, wx.RIGHT | wx.CENTER, 5)
        sizerFFmpeg.Add((0, 15))
        msg = _("Enable a custom location to run FFprobe")
        self.ckbx_exeFFprobe = wx.CheckBox(tabTwo, wx.ID_ANY, (msg))
        self.btn_ffprobe = wx.Button(tabTwo, wx.ID_ANY, _('Change'))
        self.txtctrl_ffprobe = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizerFFmpeg.Add(self.ckbx_exeFFprobe, 0, wx.LEFT, 5)
        gridFFprobe = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFprobe, 0, wx.EXPAND)
        gridFFprobe.Add(self.txtctrl_ffprobe, 1, wx.ALL, 5)
        gridFFprobe.Add(self.btn_ffprobe, 0, wx.RIGHT | wx.CENTER, 5)
        sizerFFmpeg.Add((0, 15))
        msg = _("Enable a custom location to run FFplay")
        self.ckbx_exeFFplay = wx.CheckBox(tabTwo, wx.ID_ANY, (msg))
        self.btn_ffplay = wx.Button(tabTwo, wx.ID_ANY, _('Change'))
        self.txtctrl_ffplay = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizerFFmpeg.Add(self.ckbx_exeFFplay, 0, wx.LEFT, 5)
        gridFFplay = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFplay, 0, wx.EXPAND)
        gridFFplay.Add(self.txtctrl_ffplay, 1, wx.ALL, 5)
        gridFFplay.Add(self.btn_ffplay, 0, wx.RIGHT | wx.CENTER, 5)
        tabTwo.SetSizer(sizerFFmpeg)
        notebook.AddPage(tabTwo, _("FFmpeg"))

        # -----tab 3
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerAppearance = wx.BoxSizer(wx.VERTICAL)
        sizerAppearance.Add((0, 10))
        msg = _('Look and Feel (requires application restart)')
        labappe = wx.StaticText(tabThree, wx.ID_ANY, msg)
        sizerAppearance.Add(labappe, 0, wx.ALL | wx.EXPAND, 5)
        sizerAppearance.Add((0, 10))
        sizericon = wx.BoxSizer(wx.HORIZONTAL)
        labTheme = wx.StaticText(tabThree, wx.ID_ANY, _('Icon themes'))
        sizericon.Add(labTheme, 0, wx.LEFT | wx.TOP, 5)
        self.cmbx_icons = wx.ComboBox(tabThree, wx.ID_ANY,
                                      choices=[("Videomass-Light"),
                                               ("Videomass-Dark"),
                                               ("Videomass-Colours"),
                                               ("Ubuntu-Light-Aubergine"),
                                               ("Ubuntu-Dark-Aubergine"),
                                               ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        sizericon.Add(self.cmbx_icons, 0, wx.LEFT, 5)
        sizerAppearance.Add(sizericon, 0, wx.ALL, 5)
        tbchoice = [_('At the top of window (default)'),
                    _('At the bottom of window'),
                    _('At the right of window'),
                    _('At the left of window')]
        self.rdbTBpref = wx.RadioBox(tabThree, wx.ID_ANY,
                                     (_("Place the toolbar")),
                                     choices=tbchoice,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS
                                     )
        sizerAppearance.Add(self.rdbTBpref, 0, wx.ALL | wx.EXPAND, 5)
        gridTBsize = wx.FlexGridSizer(0, 2, 0, 5)
        sizerAppearance.Add(gridTBsize, 0, wx.ALL, 5)
        lab1_appearance = wx.StaticText(tabThree, wx.ID_ANY,
                                        _("Toolbar's icons size:"))
        gridTBsize.Add(lab1_appearance, 0, wx.LEFT | wx.TOP
                       | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmbx_iconsSize = wx.ComboBox(tabThree, wx.ID_ANY,
                                          choices=[("16"), ("24"), ("32"),
                                                   ("64")], size=(120, -1),
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY
                                          )
        gridTBsize.Add(self.cmbx_iconsSize, 0, wx.TOP
                       | wx.ALIGN_CENTER_VERTICAL, 5)
        if 'wx.svg' not in sys.modules:  # only in wx version 4.1 to up
            self.cmbx_iconsSize.Disable()
            lab1_appearance.Disable()
        sizerAppearance.Add((0, 10))
        msg = _('Application Language (requires application restart)')
        lablang = wx.StaticText(tabThree, wx.ID_ANY, msg)
        sizerAppearance.Add(lablang, 0, wx.ALL | wx.EXPAND, 5)
        sizerAppearance.Add((0, 10))
        langs = [lang[1] for lang in supLang.values()]
        self.cmbx_lang = wx.ComboBox(tabThree, wx.ID_ANY,
                                     choices=langs,
                                     size=(-1, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        sizerAppearance.Add(self.cmbx_lang, 0, wx.ALL, 5)
        tabThree.SetSizer(sizerAppearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tabThree, _("Look and Language"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizerexitopt = wx.BoxSizer(wx.VERTICAL)
        sizerexitopt.Add((0, 10))
        msg = _('Upon exiting the application')
        labexitopt = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizerexitopt.Add(labexitopt, 0, wx.ALL | wx.EXPAND, 5)
        sizerexitopt.Add((0, 10))
        self.ckbx_exitconfirm = wx.CheckBox(tabFour, wx.ID_ANY,
                                            _("Always ask me to confirm"))
        sizerexitopt.Add(self.ckbx_exitconfirm, 0, wx.LEFT, 5)
        msg = _("Clean the log files")
        self.ckbx_logclr = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerexitopt.Add(self.ckbx_logclr, 0, wx.LEFT, 5)
        msg = _("Remove cached files")
        self.ckbx_cacheclr = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerexitopt.Add(self.ckbx_cacheclr, 0, wx.LEFT, 5)
        sizerexitopt.Add((0, 20))
        msg = _('On operations completion')
        labendop = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizerexitopt.Add(labendop, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_("These settings will remain active until the application is "
                 "closed, If necessary, remember to reactivate them."))
        labendopdescr = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        sizerexitopt.Add(labendopdescr, 0, wx.ALL, 5)
        sizerexitopt.Add((0, 10))
        msg = _("Exit the application")
        self.ckbx_exitapp = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerexitopt.Add(self.ckbx_exitapp, 0, wx.LEFT, 5)
        msg = _("Shutdown the system")
        self.ckbx_turnoff = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerexitopt.Add(self.ckbx_turnoff, 0, wx.LEFT, 5)
        sizersudo = wx.BoxSizer(wx.HORIZONTAL)
        self.labsudo = wx.StaticText(tabFour, wx.ID_ANY, _('SUDO password:'))
        self.labsudo.Disable()
        sizersudo.Add(self.labsudo, 0, wx.LEFT | wx.TOP, 5)
        self.txtctrl_sudo = wx.TextCtrl(tabFour, wx.ID_ANY, "",
                                        style=wx.TE_PASSWORD, size=(300, -1))
        self.txtctrl_sudo.Disable()
        sizersudo.Add(self.txtctrl_sudo, 0, wx.ALL, 5)
        sizerexitopt.Add(sizersudo, 0, wx.LEFT, 5)
        tabFour.SetSizer(sizerexitopt)
        notebook.AddPage(tabFour, _("Exit and Shutdown"))

        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        sizeradv = wx.BoxSizer(wx.VERTICAL)
        sizeradv.Add((0, 10))
        msg = _("Specify the character encoding format")
        labenctitle = wx.StaticText(tabFive, wx.ID_ANY, msg)
        sizeradv.Add(labenctitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_("Although UTF-8 is the default and most widely used standard "
                 "encoding format, it is not the only encoding format "
                 "available.\nSome file metadata may still contain non-UTF-8 "
                 "character encodings resulting in the error \"'utf-8' codec "
                 "can't decode bytes...\".\nIf you know the encoding format "
                 "the file was written in, you can try specifying it here, "
                 "e.g. ISO 8859-1, ISO 8859-16, etc."))
        labencgen = wx.StaticText(tabFive, wx.ID_ANY, (msg))
        sizeradv.Add(labencgen, 0, wx.ALL, 5)
        sizerenc = wx.BoxSizer(wx.HORIZONTAL)
        labenc = wx.StaticText(tabFive, wx.ID_ANY, _('Character encoding:'))
        sizerenc.Add(labenc, 0, wx.LEFT | wx.TOP, 5)
        self.txtctrl_charenc = wx.TextCtrl(tabFive, wx.ID_ANY,
                                           self.appdata["encoding"].strip(),
                                           size=(150, -1)
                                           )
        sizerenc.Add(self.txtctrl_charenc, 0, wx.ALL, 5)
        sizeradv.Add(sizerenc, 0, wx.LEFT, 5)
        sizeradv.Add((0, 20))
        msg = _("Default application directories")
        labdirtitle = wx.StaticText(tabFive, wx.ID_ANY, msg)
        sizeradv.Add(labdirtitle, 0, wx.ALL | wx.EXPAND, 5)
        labconf = wx.StaticText(tabFive, wx.ID_ANY,
                                _('Configuration directory'))
        self.btn_conf = wx.Button(tabFive, wx.ID_ANY, "...", size=(35, -1),
                                  name='config dir')
        self.txtctrl_conf = wx.TextCtrl(tabFive, wx.ID_ANY,
                                        self.appdata['confdir'],
                                        size=(500, -1),
                                        style=wx.TE_READONLY,
                                        )
        griddefdirs = wx.FlexGridSizer(3, 3, 5, 0)
        griddefdirs.Add(labconf, 0, wx.LEFT | wx.TOP, 5)
        griddefdirs.Add(self.txtctrl_conf, 1, wx.RIGHT
                        | wx.TOP | wx.LEFT | wx.EXPAND, 5)
        griddefdirs.Add(self.btn_conf, 0, wx.RIGHT | wx.TOP, 5)
        labcache = wx.StaticText(tabFive, wx.ID_ANY, _('Cache directory'))
        self.btn_cache = wx.Button(tabFive, wx.ID_ANY, "...", size=(35, -1),
                                   name='cache dir')
        self.txtctrl_cache = wx.TextCtrl(tabFive, wx.ID_ANY,
                                         self.appdata['cachedir'],
                                         size=(500, -1),
                                         style=wx.TE_READONLY,
                                         )
        griddefdirs.Add(labcache, 0, wx.LEFT | wx.TOP, 5)
        griddefdirs.Add(self.txtctrl_cache, 1, wx.RIGHT
                        | wx.TOP | wx.LEFT | wx.EXPAND, 5)
        griddefdirs.Add(self.btn_cache, 0, wx.RIGHT | wx.TOP, 5)
        lablog = wx.StaticText(tabFive, wx.ID_ANY, _('Log directory'))
        self.btn_log = wx.Button(tabFive, wx.ID_ANY, "...", size=(35, -1),
                                 name='log dir')
        self.txtctrl_log = wx.TextCtrl(tabFive, wx.ID_ANY,
                                       self.appdata['logdir'],
                                       size=(500, -1),
                                       style=wx.TE_READONLY,
                                       )
        griddefdirs.Add(lablog, 0, wx.LEFT | wx.TOP, 5)
        griddefdirs.Add(self.txtctrl_log, 1, wx.RIGHT
                        | wx.TOP | wx.LEFT | wx.EXPAND, 5)
        griddefdirs.Add(self.btn_log, 0, wx.RIGHT | wx.TOP, 5)
        sizeradv.Add(griddefdirs, 0, wx.LEFT | wx.EXPAND, 5)
        tabFive.SetSizer(sizeradv)
        notebook.AddPage(tabFive, _("Advanced"))

        # -----tab 6
        tabSix = wx.Panel(notebook, wx.ID_ANY)
        sizerLog = wx.BoxSizer(wx.VERTICAL)
        sizerLog.Add((0, 10))
        msglog = _("The following settings affect output messages and "
                   "the log messages during transcoding processes.\n"
                   "Be careful, by changing these settings some functions "
                   "of the application may not work correctly,\n"
                   "change only if you know what you are doing.\n")
        labLog = wx.StaticText(tabSix, wx.ID_ANY, (msglog))
        sizerLog.Add(labLog, 0, wx.ALL, 5)
        msg = _("Set logging level flags used by FFmpeg")
        self.rdbFFmpeg = wx.RadioBox(tabSix, wx.ID_ANY, (msg),
                                     choices=SetUp.FFMPEG_LOGLEV,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS,
                                     )
        sizerLog.Add(self.rdbFFmpeg, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("Set logging level flags used by FFplay")
        self.rdbFFplay = wx.RadioBox(tabSix, wx.ID_ANY, (msg),
                                     choices=SetUp.FFPLAY_LOGLEV,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS,
                                     )
        sizerLog.Add(self.rdbFFplay, 0, wx.ALL | wx.EXPAND, 5)
        tabSix.SetSizer(sizerLog)
        notebook.AddPage(tabSix, _("FFmpeg logging levels"))

        # ----- confirm buttons section
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_cancel, 0, wx.ALIGN_CENTER_VERTICAL)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        grdexit.Add(btn_ok, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizer_base.Add(grdBtn, 0, wx.EXPAND)

        # ----- Properties
        if self.appdata['ostype'] == 'Darwin':
            lablang.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdirtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labexitopt.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labendop.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labendopdescr.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labfile.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labffdescr.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labappe.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labrem.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labenctitle.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
            labencgen.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lablang.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdirtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labexitopt.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labendop.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labendopdescr.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labfile.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labffdescr.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labappe.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labLog.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labrem.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labenctitle.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            labencgen.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        tip = (_("By assigning an additional suffix you could avoid "
                 "overwriting files"))
        self.text_suffix.SetToolTip(tip)
        tip = (_("Type sudo password here, only for Unix-like operating "
                 "systems, not for MS Windows"))
        self.txtctrl_sudo.SetToolTip(tip)
        self.SetTitle(_("Preferences"))

        # ------ set sizer
        self.SetMinSize((750, 550))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_set_lang, self.cmbx_lang)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_conf)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_log)
        self.Bind(wx.EVT_BUTTON, self.opendir, self.btn_cache)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffplay, self.rdbFFplay)
        self.Bind(wx.EVT_RADIOBOX, self.logging_ffmpeg, self.rdbFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.on_outputdir, self.btn_fsave)
        self.Bind(wx.EVT_CHECKBOX, self.same_dir_dest, self.ckbx_same_dest)
        self.Bind(wx.EVT_TEXT, self.set_Suffix, self.text_suffix)
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_BUTTON, self.on_browse_trash, self.btn_trash)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.ckbx_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.ckbx_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_ffprobe)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFplay, self.ckbx_exeFFplay)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffplay, self.btn_ffplay)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)
        self.Bind(wx.EVT_RADIOBOX, self.on_toolbarPos, self.rdbTBpref)
        self.Bind(wx.EVT_COMBOBOX, self.on_toolbarSize, self.cmbx_iconsSize)
        self.Bind(wx.EVT_CHECKBOX, self.on_exit_after, self.ckbx_exitapp)
        self.Bind(wx.EVT_CHECKBOX, self.on_shutdown_after, self.ckbx_turnoff)
        self.Bind(wx.EVT_CHECKBOX, self.exit_warn, self.ckbx_exitconfirm)
        self.Bind(wx.EVT_CHECKBOX, self.clear_Cache, self.ckbx_cacheclr)
        self.Bind(wx.EVT_CHECKBOX, self.clear_logs, self.ckbx_logclr)
        self.Bind(wx.EVT_TEXT, self.on_char_encoding, self.txtctrl_charenc)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#

        self.general_current_settings()
        self.ffmpeg_current_settings()

    def general_current_settings(self):
        """
        Performs the current settings for preferences dialog
        """
        if self.appdata['locale_name'] in supLang:
            lang = supLang[self.appdata['locale_name']][1]
        else:
            lang = supLang["en_US"][1]
        self.cmbx_lang.SetValue(lang)

        self.cmbx_icons.SetValue(self.appdata['icontheme'])
        self.cmbx_iconsSize.SetValue(str(self.appdata['toolbarsize']))
        self.rdbTBpref.SetSelection(self.appdata['toolbarpos'])
        self.ckbx_cacheclr.SetValue(self.appdata['clearcache'])
        self.ckbx_exitconfirm.SetValue(self.appdata['warnexiting'])
        self.ckbx_logclr.SetValue(self.appdata['clearlogfiles'])
        self.ckbx_trash.SetValue(self.settings['move_file_to_trash'])

        self.ckbx_exitapp.SetValue(self.appdata["auto_exit"])
        self.ckbx_turnoff.SetValue(self.appdata["shutdown"])
        self.txtctrl_sudo.SetValue(self.appdata.get("sudo_password", ''))
        if self.ckbx_turnoff.GetValue():
            if self.appdata['ostype'] != 'Windows':
                self.labsudo.Enable(), self.txtctrl_sudo.Enable()

        if not self.settings['move_file_to_trash']:
            self.txtctrl_trash.Disable()
            self.btn_trash.Disable()

        if not self.appdata['outputdir_asinput']:
            self.lab_suffix.Disable()
            self.text_suffix.Disable()
            self.ckbx_same_dest.SetValue(False)
        else:
            self.lab_suffix.Enable()
            self.text_suffix.Enable()
            self.ckbx_same_dest.SetValue(True)
            self.btn_fsave.Disable()
            self.txtctrl_FFpath.Disable()
            if not self.appdata['filesuffix'] == "":
                self.text_suffix.AppendText(self.appdata['filesuffix'])
    # --------------------------------------------------------------------#

    def ffmpeg_current_settings(self):
        """
        Performs the current settings for the FFmpeg tab in
        the preferences dialog
        """
        for strs in range(self.rdbFFplay.GetCount()):
            if (self.appdata['ffplay_loglev'].split()[1] in
               self.rdbFFplay.GetString(strs).split()[0]):
                self.rdbFFplay.SetSelection(strs)

        for strs in range(self.rdbFFmpeg.GetCount()):
            if (self.appdata['ffmpeg_loglev'].split()[1] in
               self.rdbFFmpeg.GetString(strs).split()[0]):
                self.rdbFFmpeg.SetSelection(strs)

        if not self.appdata['ffmpeg_islocal']:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.ckbx_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.ckbx_exeFFmpeg.SetValue(True)

        if not self.appdata['ffprobe_islocal']:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.ckbx_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.ckbx_exeFFprobe.SetValue(True)

        if not self.appdata['ffplay_islocal']:
            self.btn_ffplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.ckbx_exeFFplay.SetValue(False)
        else:
            self.txtctrl_ffplay.AppendText(self.appdata['ffplay_cmd'])
            self.ckbx_exeFFplay.SetValue(True)
    # --------------------------------------------------------------------#

    def opendir(self, event):
        """
        Open the configuration folder with file manager
        """
        name = event.GetEventObject().GetName()
        if name == 'config dir':
            io_tools.openpath(self.appdata['confdir'])
        elif name == 'log dir':
            io_tools.openpath(self.appdata['logdir'])
        elif name == 'cache dir':
            io_tools.openpath(self.appdata['cachedir'])
    # -------------------------------------------------------------------#

    def on_set_lang(self, event):
        """set application language"""
        lang = 'Default'
        for key, val in supLang.items():
            if val[1] == self.cmbx_lang.GetValue():
                lang = key
        self.settings['locale_name'] = lang
    # --------------------------------------------------------------------#

    def on_outputdir(self, event):
        """set up a custom user path for file exporting"""
        dlg = wx.DirDialog(self, _("Choose Destination"),
                           self.appdata['outputdir'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_FFpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_FFpath.AppendText(getpath)
            self.settings['outputdir'] = getpath
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def same_dir_dest(self, event):
        """Save the FFmpeg output files in the same source folder"""
        if self.ckbx_same_dest.IsChecked():
            self.lab_suffix.Enable()
            self.text_suffix.Enable()
            self.btn_fsave.Disable()
            self.txtctrl_FFpath.Disable()
            self.settings['outputdir_asinput'] = True
        else:
            self.text_suffix.Clear()
            self.lab_suffix.Disable()
            self.text_suffix.Disable()
            self.btn_fsave.Enable()
            self.txtctrl_FFpath.Enable()
            self.settings['outputdir_asinput'] = False
            self.settings['filesuffix'] = ""
    # --------------------------------------------------------------------#

    def set_Suffix(self, event):
        """Set a custom suffix to append at the output file names"""
        msg = _('Enter only alphanumeric characters. You can also use the '
                'hyphen ("-") and the underscore ("_"). Spaces are '
                'not allowed.')
        suffix = self.text_suffix.GetValue()

        if self.text_suffix.GetBackgroundColour() == (152, 131, 19, 255):
            # html: ('#988313') == rgb: (152, 131, 19, 255) =
            self.text_suffix.SetBackgroundColour(wx.NullColour)
            self.text_suffix.Clear()

        if not suffix == '':
            for c in suffix:
                if c not in ('_', '-'):
                    if not c.isalnum():  # is not alphanumeric
                        self.text_suffix.SetBackgroundColour('#988313')
                        wx.MessageBox(msg, _('Videomass - Warning!'),
                                      wx.ICON_WARNING)
                        self.settings['filesuffix'] = ""
                        return

            self.settings['filesuffix'] = suffix
        else:
            self.settings['filesuffix'] = ""
    # --------------------------------------------------------------------#

    def on_file_to_trash(self, event):
        """
        enable/disable "Move file to trash" after successful encoding
        """
        if self.ckbx_trash.IsChecked():
            self.settings['move_file_to_trash'] = True
            self.settings['trashdir_loc'] = self.appdata['trashdir_default']
            self.txtctrl_trash.Enable()
            self.btn_trash.Enable()
            if not os.path.exists(self.appdata['trashdir_default']):
                os.mkdir(self.appdata['trashdir_default'], mode=0o777)
        else:
            self.txtctrl_trash.Clear()
            self.txtctrl_trash.AppendText(self.appdata['trashdir_default'])
            self.txtctrl_trash.Disable()
            self.btn_trash.Disable()
            self.settings['move_file_to_trash'] = False
            self.settings['trashdir_loc'] = self.appdata['trashdir_default']
    # --------------------------------------------------------------------#

    def on_browse_trash(self, event):
        """
        Browse to set a trash folder.
        """
        dlg = wx.DirDialog(self, _("Choose Destination"),
                           self.appdata['trashdir_loc'],
                           wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_trash.Clear()
            newtrash = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_trash.AppendText(newtrash)
            self.settings['trashdir_loc'] = newtrash
            if not os.path.exists(newtrash):
                os.makedirs(newtrash, mode=0o777)
            dlg.Destroy()
    # --------------------------------------------------------------------#

    def logging_ffplay(self, event):
        """
        specifies loglevel type for ffplay.
        """
        strn = self.rdbFFplay.GetStringSelection().split()[0]
        self.settings['ffplay_loglev'] = f'-loglevel {strn}'
    # --------------------------------------------------------------------#

    def logging_ffmpeg(self, event):
        """
        specifies loglevel type for ffmpeg
        """
        strn = self.rdbFFmpeg.GetStringSelection().split()[0]
        self.settings['ffmpeg_loglev'] = f'-loglevel {strn}'
    # --------------------------------------------------------------------#

    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg local binary"""
        if self.ckbx_exeFFmpeg.IsChecked():
            self.btn_ffmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.settings['ffmpeg_islocal'] = True
        else:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.settings['ffmpeg_islocal'] = False

            status = detect_binaries(self.ffmpeg, self.appdata['FFMPEG_DIR'])
            if status[0] == 'not installed':
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write('Not found')
                self.settings['ffmpeg_cmd'] = ''
            else:
                self.txtctrl_ffmpeg.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffmpeg.write(getpath)
                self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        with wx.FileDialog(self, _("{} location").format(self.ffmpeg),
                           "", "", "ffmpeg binary "
                           f"(*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffmpeg:
                    self.txtctrl_ffmpeg.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffmpeg.write(getpath)
                    self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exeFFprobe(self, event):
        """Enable or disable ffprobe local binary"""
        if self.ckbx_exeFFprobe.IsChecked():
            self.btn_ffprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.settings['ffprobe_islocal'] = True

        else:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.settings['ffprobe_islocal'] = False

            status = detect_binaries(self.ffprobe, self.appdata['FFMPEG_DIR'])
            if status[0] == 'not installed':
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write('Not found')
                self.settings['ffprobe_cmd'] = ''
            else:
                self.txtctrl_ffprobe.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffprobe.write(getpath)
                self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        with wx.FileDialog(self, _("{} location").format(self.ffprobe),
                           "", "", "ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffprobe:
                    self.txtctrl_ffprobe.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffprobe.write(getpath)
                    self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exeFFplay(self, event):
        """Enable or disable ffplay local binary"""
        if self.ckbx_exeFFplay.IsChecked():
            self.btn_ffplay.Enable()
            self.txtctrl_ffplay.Enable()
            self.settings['ffplay_islocal'] = True

        else:
            self.btn_ffplay.Disable()
            self.txtctrl_ffplay.Disable()
            self.settings['ffplay_islocal'] = False

            status = detect_binaries(self.ffplay, self.appdata['FFMPEG_DIR'])
            if status[0] == 'not installed':
                self.txtctrl_ffplay.Clear()
                self.txtctrl_ffplay.write('Not found')
                self.settings['ffplay_cmd'] = ''
            else:
                self.txtctrl_ffplay.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffplay.write(getpath)
                self.settings['ffplay_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffplay(self, event):
        """Indicates a new ffplay path-name"""
        with wx.FileDialog(self, _("{} location").format(self.ffplay),
                           "", "", "ffplay binary "
                           f"(*{self.ffplay})|*{self.ffplay}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffplay:
                    self.txtctrl_ffplay.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffplay.write(getpath)
                    self.settings['ffplay_cmd'] = getpath
    # ---------------------------------------------------------------------#

    def on_Iconthemes(self, event):
        """
        Set themes of icons
        """
        self.settings['icontheme'] = self.cmbx_icons.GetStringSelection()
    # --------------------------------------------------------------------#

    def on_toolbarSize(self, event):
        """
        Set the size of the toolbar buttons and the size of its icons
        """
        size = self.cmbx_iconsSize.GetStringSelection()
        self.settings['toolbarsize'] = size
    # --------------------------------------------------------------------#

    def on_toolbarPos(self, event):
        """
        Set toolbar position on main frame
        """
        self.settings['toolbarpos'] = self.rdbTBpref.GetSelection()
    # --------------------------------------------------------------------#

    def on_exit_after(self, event):
        """
        Exit the app At the end of the operations
        """
        if self.ckbx_exitapp.GetValue():
            if self.ckbx_turnoff.IsChecked():
                self.ckbx_turnoff.SetValue(False)
                self.on_shutdown_after(None)
    # --------------------------------------------------------------------#

    def on_shutdown_after(self, event):
        """
        At the end of the processes operations
        """
        if self.ckbx_turnoff.GetValue():
            if self.ckbx_exitapp.IsChecked():
                self.ckbx_exitapp.SetValue(False)
            if self.appdata['ostype'] != 'Windows':
                self.txtctrl_sudo.Enable(), self.labsudo.Enable()
        else:
            self.txtctrl_sudo.SetValue(""), self.txtctrl_sudo.Disable()
            self.labsudo.Disable()
    # --------------------------------------------------------------------#

    def exit_warn(self, event):
        """
        Enable or disable the warning message before
        exiting the program
        """
        self.settings['warnexiting'] = self.ckbx_exitconfirm.GetValue()
    # --------------------------------------------------------------------#

    def clear_Cache(self, event):
        """
        if checked, set to clear cached data on exit
        """
        self.settings['clearcache'] = self.ckbx_cacheclr.GetValue()
    # --------------------------------------------------------------------#

    def clear_logs(self, event):
        """
        if checked, set to clear all log files on exit
        """
        self.settings['clearlogfiles'] = self.ckbx_logclr.GetValue()
    # --------------------------------------------------------------------#

    def on_char_encoding(self, event):
        """
        TextCtrl event to set character encoding
        """
        self.settings['encoding'] = self.txtctrl_charenc.GetValue().strip()
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Startup_and_Setup_en.pdf')

        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Writes the new changes to configuration file
        aka `settings.json` and updates `appdata` dict.
        """
        if not self.settings['trashdir_loc'].strip():
            self.settings['trashdir_loc'] = self.appdata['trashdir_default']
        self.retcode = (
            self.settings['locale_name'] == self.appdata['locale_name'],
            self.settings['icontheme'] == self.appdata['icontheme'],
            self.settings['toolbarsize'] == self.appdata['toolbarsize'],
            self.settings['toolbarpos'] == self.appdata['toolbarpos'])
        self.confmanager.write_options(**self.settings)
        self.appdata.update(self.settings)
        # do not store this data in the configuration file
        self.appdata["auto_exit"] = self.ckbx_exitapp.GetValue()
        self.appdata["shutdown"] = self.ckbx_turnoff.GetValue()
        self.appdata['sudo_password'] = self.txtctrl_sudo.GetValue()
        event.Skip()

    # --------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        return self.retcode
