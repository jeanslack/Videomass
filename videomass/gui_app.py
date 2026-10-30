# -*- coding: UTF-8 -*-
"""
Name: gui_app.py
Porpose: bootstrap for Videomass app.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.29.2026
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
import builtins
import os
import sys
from shutil import rmtree, which

import wx

from videomass.vdms_sys import app_const as appC
from videomass.vdms_sys.argparser import arguments
from videomass.vdms_sys.configurator import DataSource
from videomass.vdms_utils.utils import del_filecontents

# from videomass.vdms_sys.external_package import importer_init_file

# add translation macro to builtin similar to what gettext does
builtins.__dict__['_'] = wx.GetTranslation


class Videomass(wx.App):
    """
    bootstrap the wxPython GUI toolkit before
    starting the main_frame.

    """

    def __init__(self, redirect=True, filename=None, **kwargs):
        """
        - redirect=False will send print statements to a console
          window (in use)
        - redirect=True will be sent to a little textbox window.
        - filename=None Redirect sys.stdout and sys.stderr
          to a popup window.
        - filename='path/to/file.txt' Redirect sys.stdout
          and sys.stderr to file

        Also see main() function.

        """
        self.locale = None
        self.appset = {'DISPLAY_SIZE': None,
                       'IS_DARK_THEME': None,
                       'GETLANG': None,
                       # short name for the locale
                       'SUPP_LANGs': ['it_IT', 'en_US', 'ru_RU'],
                       # supported langs for online help (user guide)
                       }
        self.data = DataSource(kwargs)  # instance data
        self.appset.update(self.data.get_configuration())  # data system
        self.iconset = None

        wx.App.__init__(self, redirect, filename)  # constructor
        wx.SystemOptions.SetOption("osx.openfiledialog.always-show-types", "1")
    # -------------------------------------------------------------------

    def OnInit(self):
        """Bootstrap interface."""

        if self.appset.get('ERROR'):
            wx.MessageBox(f"FATAL: {self.appset['ERROR']}\n\nSorry, unable "
                          f"to continue...", 'Videomass - ERROR', wx.ICON_STOP)
            return False

        self.appset['DISPLAY_SIZE'] = wx.GetDisplaySize()  # get monitor res
        if hasattr(wx.SystemSettings, 'GetAppearance'):
            appear = wx.SystemSettings.GetAppearance()
            if hasattr(appear, 'IsSystemDark') and appear.IsSystemDark():
                self.SetAppearance(Videomass.Appearance.Dark)
            self.appset['IS_DARK_THEME'] = appear.IsDark()

        self.iconset = self.data.icons_set(self.appset['icontheme'])

        # locale
        wx.Locale.AddCatalogLookupPathPrefix(self.appset['localepath'])
        self.update_language(self.appset['locale_name'])

        if self.check_ffmpeg():
            self.wizard(self.iconset['videomass'])
            return True

        from videomass.vdms_main.main_frame import MainFrame
        main_frame = MainFrame(self.appset)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def check_ffmpeg(self):
        """
        Check the FFmpeg's executables (ffmpeg, ffprobe, ffplay).
        Returns True if one of the executables is missing or if
        one of the executables doesn't have execute permission.
        Returns None otherwise.
        """
        for link in [self.appset['ffmpeg_cmd'],
                     self.appset['ffprobe_cmd'],
                     self.appset['ffplay_cmd']
                     ]:
            if not which(link, mode=os.F_OK | os.X_OK, path=None):
                return True
        return None
    # -------------------------------------------------------------------

    def wizard(self, wizardicon):
        """
        Shows dialog to setup the application on initial start-up.
        """
        from videomass.vdms_dialogs.wizard_dlg import Wizard
        main_frame = Wizard(wizardicon)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # ------------------------------------------------------------------

    def update_language(self, lang=None):
        """
        Update the language to the requested one.
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes
        https://docs.wxpython.org/wx.Language.enumeration.html#wx-language

        """
        # if an unsupported language is requested, default to English
        selectlang = appC.supLang.get(lang, wx.LANGUAGE_ENGLISH)

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selectlang[0])

        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
            self.appset['GETLANG'] = self.locale.GetName()
        else:
            self.locale = None
            self.appset['GETLANG'] = "en_US"
    # -------------------------------------------------------------------

    def OnExit(self):
        """
        OnExit provides an interface for exiting the application.
        The ideal place to run the last few things before completely
        exiting the application, eg. delete temporary files etc.
        """
        if self.appset['clearcache']:
            tmp = os.path.join(self.appset['cachedir'], 'tmp')
            if os.path.exists(tmp):
                failed_cachef = None
                for cache in os.listdir(tmp):
                    fcache = os.path.join(tmp, cache)
                    try:
                        if os.path.isfile(fcache) or os.path.islink(fcache):
                            os.remove(fcache)
                        elif os.path.isdir(fcache):
                            rmtree(fcache)
                    except OSError:
                        failed_cachef = True

                if failed_cachef:
                    wx.MessageBox(_("Could not erase some cache files."),
                                  'Videomass', wx.ICON_WARNING)

        if self.appset['clearlogfiles']:
            logdir = self.appset['logdir']
            if os.path.exists(logdir):
                flist = os.listdir(logdir)
                if flist:
                    failed_logf = []
                    for logname in flist:
                        logfile = os.path.join(logdir, logname)
                        try:
                            del_filecontents(logfile)
                        except OSError as err:
                            failed_logf.append(f"{logname} ({err})")

                    if failed_logf:
                        errors_str = "\n".join(failed_logf)
                        wx.MessageBox(_("Could not clear some log files."
                                      "\n\n{0}").format(errors_str),
                                      'Videomass', wx.ICON_WARNING)

        if self.appset['auto-restart-app']:
            try:
                auto_restart(self.appset['app'], self.appset['make_portable'])
                return True
            except OSError as err:  # executable not found or failed
                wx.MessageBox(_("Failed to auto-restart the application:\n\n"
                                "{0}").format(err),
                              'Videomass', wx.ICON_WARNING)
        return True
    # -------------------------------------------------------------------


def auto_restart(apptype, portmode):
    """
    This function spawns the same executable again, automatically
    restarting this application if required.
    """
    # Avoid restart in interactive mode (python shell)
    if not sys.argv or sys.argv[0].startswith('-'):
        sys.exit()

    if apptype == 'pyinstaller':
        cmd_list = [sys.executable]  # (videomass.exe)
    else:  # source
        cmd_list = [sys.executable, sys.argv[0]]

    if portmode:
        cmd_list.extend(['--make-portable', str(portmode)])

    for arg in sys.argv[1:]:
        if (arg not in cmd_list and arg != portmode and arg
           != '--make-portable'):
            cmd_list.append(arg)
    try:
        # do not use EXEC_SYNC here, use EXEC_ASYNC instead !
        wx.Execute(' '.join(f'"{arg}"' for arg in cmd_list),
                   flags=wx.EXEC_ASYNC)

    except OSError as err:
        # Raise the OSError exception so that OnExit can catch it
        raise OSError(f"Unable to initiate the restart process: {err}")


def main():
    """
    With the default command line arguments starts
    wx.App mainloop with default keyword arguments.
    """
    if not sys.argv[1:]:
        kwargs = {'make_portable': None}
    else:
        kwargs = arguments()

    app = Videomass(redirect=False, **kwargs)
    app.MainLoop()
