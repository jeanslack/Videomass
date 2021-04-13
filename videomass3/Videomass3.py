#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Name: Videomass3.py
# Porpose: bootstrap for Videomass app.
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Jan.25.2021 *PEP8 compatible*
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
try:
    from wx.svg import SVGimage
except ModuleNotFoundError:
    pass
import os
import sys
from shutil import which, rmtree
from videomass3.vdms_sys.argparser import args
from videomass3.vdms_sys.configurator import Data_Source
from videomass3.vdms_sys import app_const as appC
# add translation macro to builtin similar to what gettext does
import builtins

builtins.__dict__['_'] = wx.GetTranslation


class Videomass(wx.App):
    """
    bootstrap the wxPython system and initialize the underlying gui toolkit
    and others requirements Before starting the Videomass main frame.

    """
    def __init__(self, redirect=True, filename=None):
        """
        redirect=False will send print statements to a console window (in use)
        redirect=True will be sent to a little textbox window.
        filename=None Redirect sys.stdout and sys.stderr to a popup window.
        filename='path/to/file.txt' Redirect sys.stdout and sys.stderr to file
        See main() function below to settings it.
        -------
        attribute definition (used in some class with wx.GetApp()):
        self.DIRconf > location of the configuration directory
        self.FILEconf > location videomass.conf (Windows or Unix?)
        self.WORKdir > (PWD) location of the current program directory
        self.OS > operating system name
        self.pylibYdl > if None youtube-dl is used as library
        self.execYdl > if False is not used a local executable
        self.FFMPEGoutdir > set user path folder for FFmpeg file destination

        """
        self.DIRconf = None
        self.FILEconf = None
        self.WORKdir = None
        self.OS = None
        self.FFMPEG_url = None
        self.FFPLAY_url = None
        self.FFPROBE_url = None
        self.FFMPEG_loglev = None
        self.FFPLAY_loglev = None
        self.pylibYdl = None  # None if load as library else string
        self.execYdl = False  # path to the executable
        self.YDLsite = None  # path to youtube-dl sitepackage/distpackage
        self.YDL_pref = None  # one of these: false, disabled, system, local
        self.FFMPEGoutdir = None
        self.YDLoutdir = None
        self.CLEARcache = None
        self.GETlang = None  # current short name for the locale
        self.SUPP_langs = ['it_IT', 'en_EN', 'ru_RU']  # supported help langs

        wx.App.__init__(self, redirect, filename)  # constructor
        wx.SystemOptions.SetOption("osx.openfiledialog.always-show-types", "1")
    # -------------------------------------------------------------------

    def OnInit(self):
        """
        Bootstrap interface.

        """
        data = Data_Source()  # user-space and UI settings
        setui = data.get_fileconf()  # get required data
        # locale
        lang = ''
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix(setui[5])
        self.updateLanguage(lang)
        self.GETlang = self.locale.GetName()

        if setui[2]:  # copyerr = True; the share folder is damaged
            wx.MessageBox(_('{0}\n\nSorry, cannot continue..'.format(
                setui[2])), 'Videomass', wx.ICON_STOP)
            return False

        pathicons = data.icons_set(setui[4][11])  # get paths icons data

        dirname = os.path.expanduser('~')  # /home/user/
        self.OS = setui[0]
        self.SRCpath = setui[1]  # backup data for recovery
        self.FILEconf = setui[6]
        self.WORKdir = setui[7]
        self.DIRconf = setui[8]
        self.FFMPEG_loglev = setui[4][4]
        self.FFPLAY_loglev = setui[4][3]
        self.FFMPEG_check = setui[4][5]
        self.FFPROBE_check = setui[4][7]
        self.FFPLAY_check = setui[4][9]
        self.FFthreads = setui[4][2]
        self.FFMPEGoutdir = dirname if setui[4][1] == 'none' else setui[4][1]
        self.LOGdir = setui[9]  # dir for logging
        self.CACHEdir = setui[10]  # dir cache for updates
        self.FFMPEGlocaldir = setui[11]  # local path to FFMPEG on Videomass
        self.TBsize = setui[4][12]  # toolbar icons size
        self.TBpos = setui[4][13]  # toolbar position style
        self.TBtext = setui[4][14]  # toolbar show/hide text along side
        self.CLEARcache = setui[4][15]  # set clear cache on exit
        self.YDL_pref = setui[4][16]  # get youtube-dl preferences
        self.TMP = os.path.join(self.CACHEdir, 'tmp')
        self.THEME = setui[4][11]  # specifies which icon theme is used
        self.SAMEdir = setui[4][17]  # file save with same dest. as source
        self.FILEsuffix = setui[4][18]  # add a suffix string to file name
        self.YDLoutdir = dirname if setui[4][19] == 'none' else setui[4][19]
        self.PLAYLISTsubfolder = setui[4][20]  # subfolder check on playlist
        self.DISPLAY_size = wx.GetDisplaySize()  # get monitor resolution

        # ----- youtube-dl
        execname = 'youtube-dl.exe' if self.OS == 'Windows' else 'youtube-dl'

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.execYdl = os.path.join(self.CACHEdir, execname)
            self.pylibYdl = 'no module loaded'

            if self.YDL_pref != 'false':
                self.YDL_pref = (setui[4][16] if setui[4][16] == 'disabled'
                                 else 'local')
        else:

            if self.YDL_pref == 'disabled':
                self.pylibYdl = 'no module loaded'

            elif self.YDL_pref == 'local':
                self.execYdl = os.path.join(self.CACHEdir, execname)
                self.pylibYdl = 'no module loaded'

            elif self.YDL_pref == 'system':
                win, nix = '\\__init__.py', '/__init__.py'
                sp = win if self.OS == 'Windows' else nix
                try:
                    import youtube_dl
                    self.YDLsite = youtube_dl.__file__.split(sp)[0]

                except (ModuleNotFoundError, ImportError) as nomodule:
                    self.pylibYdl = nomodule

        # ----- ffmpeg
        if setui[0] == 'Windows':  # on MS-Windows check for exe
            for link in [setui[4][6], setui[4][8], setui[4][10]]:
                if which(link, mode=os.F_OK | os.X_OK, path=None):
                    binaries = True
                else:
                    binaries = False
                    break
            if not binaries or self.YDL_pref == 'false':
                self.wizard(pathicons[0])
                return True
            else:
                self.FFMPEG_url = setui[4][6]
                self.FFPROBE_url = setui[4][8]
                self.FFPLAY_url = setui[4][10]

        else:
            #  check for unix binaries
            for link in [setui[4][6], setui[4][8], setui[4][10]]:
                if os.path.isfile("%s" % link):
                    binaries = True
                else:
                    binaries = False
                    break
            if not binaries or self.YDL_pref == 'false':
                self.wizard(pathicons[0])
                return True
            else:
                self.FFMPEG_url = setui[4][6]
                self.FFPROBE_url = setui[4][8]
                self.FFPLAY_url = setui[4][10]

            #  check for permissions when linked locally
            for link in [setui[4][6], setui[4][8], setui[4][10]]:
                if which(link, mode=os.F_OK | os.X_OK, path=None):
                    permissions = True
                else:
                    wx.MessageBox(_('Permission denied: {}\n\n'
                                    'Check execution permissions.').format
                                  (link), 'Videomass', wx.ICON_STOP)
                    permissions = False
                    break
            if not permissions:
                return False

        if not os.path.exists(self.TMP):
            try:  # make temporary folde on cache dir
                os.makedirs(self.TMP, mode=0o777)
            except OSError as err:
                wx.MessageBox('%s' % link, 'Videomass', wx.ICON_STOP)
                return False

        from videomass3.vdms_main.main_frame import MainFrame
        main_frame = MainFrame(setui, pathicons)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def wizard(self, wizardicon):
        """
        Show a temporary dialog for setup during first start time
        of the Videomass application.
        """
        from videomass3.vdms_dialogs.wizard_dlg import Wizard
        main_frame = Wizard(wizardicon)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # ------------------------------------------------------------------

    def updateLanguage(self, lang):
        """
        Update the language to the requested one.
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes

        """
        # if an unsupported language is requested default to English
        if lang in appC.supLang:
            selLang = appC.supLang[lang]
        else:
            selLang = wx.LANGUAGE_DEFAULT

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
        else:
            self.locale = None
    # -------------------------------------------------------------------

    def OnExit(self):
        """
        OnExit provides an interface for exiting the application.
        The ideal place to run the last few things before completely
        exiting the application, eg. delete temporary files etc.
        """
        if self.CLEARcache == 'true':
            tmp = os.path.join(self.CACHEdir, 'tmp')
            if os.path.exists(tmp):
                for cache in os.listdir(tmp):
                    f = os.path.join(tmp, cache)
                    if os.path.isfile(f):
                        os.remove(f)
                    elif os.path.isdir:
                        rmtree(f)

        return True
    # -------------------------------------------------------------------


def main():
    """
    With no arguments starts the wx.App mainloop
    otherwise print output to console.
    """
    if not sys.argv[1:]:
        app = Videomass(redirect=False)
        # app.MainLoop()
        fred = app.MainLoop()
    else:
        argv = args()
        sys.exit(0)
