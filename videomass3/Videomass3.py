#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#########################################################
# Name: Videomass3.py
# Porpose: bootstrap for Videomass app.
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import shutil
from videomass3.vdms_sys.ctrl_run import system_check
from videomass3.vdms_sys.appearance import Appearance
# add translation macro to builtin similar to what gettext does
import builtins
builtins.__dict__['_'] = wx.GetTranslation
from videomass3.vdms_sys import app_const as appC


class Videomass(wx.App):
    """
    Check for the essentials Before starting the Videomass main frame

    """
    def __init__(self, redirect=True, filename=None):
        """
        The following attributes will be used in some class
        with wx.GetApp()
        -------
        attribute definition:
        self.DIRconf > location of the configuration directory
        self.FILEconf > location videomass.conf (Windows or Unix?)
        self.WORKdir > (PWD) location of the current program directory
        self.OS > operating system name
        self.pylibYdl > if None youtube-dl is used as library
        self.execYdl > if False is not used a local executable
        self.USERfilesave > set user path folder for file destination

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
        self.pylibYdl = None
        self.execYdl = False
        self.USERfilesave = None
        # print ("App __init__")
        wx.App.__init__(self, redirect, filename)  # constructor
    # -------------------------------------------------------------------

    def OnInit(self):
        """
        This is bootstrap interface. ``setui`` get data
        of the file configuration and set the environment.

        """
        setui = system_check()  # user-space and interface settings
        # locale
        lang = ''
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix(setui[5])
        self.updateLanguage(lang)

        if setui[2]:  # copyerr = True; the share folder is damaged
            wx.MessageBox(_('{0}\n\nSorry, cannot continue..'.format(
                setui[2])), 'Videomass: Fatal Error', wx.ICON_STOP)
            return False

        icons = Appearance(setui[3], setui[4][13])  # set appearance
        pathicons = icons.icons_set()  # get paths icons
        self.OS = setui[0]
        self.FILEconf = setui[6]
        self.WORKdir = setui[7]
        self.DIRconf = setui[8]
        self.FFMPEG_loglev = setui[4][4]
        self.FFPLAY_loglev = setui[4][3]
        self.FFMPEG_check = setui[4][5]
        self.FFPROBE_check = setui[4][7]
        self.FFPLAY_check = setui[4][9]
        self.MPV_check = setui[4][11]
        self.MPV_url = setui[4][12]
        self.FFthreads = setui[4][2]
        self.USERfilesave = None if setui[4][1] == 'none' else setui[4][1]
        self.LOGdir = setui[9]  # dir for logging
        self.CACHEdir = setui[10]  # dir cache for updates

        # ----- youtube-dl
        if self.OS == 'Windows':
            try:
                from youtube_dl import YoutubeDL
                self.execYdl = False
            except (ModuleNotFoundError, ImportError) as nomodule:
                self.pylibYdl = nomodule
                self.execYdl = os.path.join(self.CACHEdir, 'youtube-dl.exe')
        else:
            try:
                from youtube_dl import YoutubeDL
                self.execYdl = False
            except (ModuleNotFoundError, ImportError) as nomodule:
                src = os.path.join(self.CACHEdir, 'youtube-dl')
                sys.path.append(src)
                try:
                    from youtube_dl import YoutubeDL
                    self.execYdl = False
                except (ModuleNotFoundError, ImportError) as nomodule:
                    self.pylibYdl = (nomodule)
                    self.execYdl = src
        # ----- ffmpeg
        if setui[0] == 'Darwin':  # on MacOs
            for link in [setui[4][6], setui[4][8], setui[4][10]]:
                if os.path.isfile("%s" % link):
                    binaries = False
                else:
                    binaries = True
                    break
            if binaries:
                self.firstrun(pathicons[16])
                return True
            else:
                self.FFMPEG_url = setui[4][6]
                self.FFPROBE_url = setui[4][8]
                self.FFPLAY_url = setui[4][10]

        elif setui[0] == 'Windows':  # on MS-Windows
            for link in [setui[4][6], setui[4][8], setui[4][10]]:
                if os.path.isfile("%s" % link):
                    binaries = False
                else:
                    binaries = True
                    break
            if binaries:
                self.firstrun(pathicons[16])
                return True
            else:
                self.FFMPEG_url = setui[4][6]
                self.FFPROBE_url = setui[4][8]
                self.FFPLAY_url = setui[4][10]

        else:  # on Linux
            self.FFMPEG_url = setui[4][6]
            self.FFPROBE_url = setui[4][8]
            self.FFPLAY_url = setui[4][10]
            # --- used for debug only ---#
            # self.firstrun(pathicons[16])
            # return True

        from videomass3.vdms_main.main_frame import MainFrame
        main_frame = MainFrame(setui, pathicons)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def firstrun(self, icon):
        """
        Start a temporary dialog: this is showing during first time
        start of the Videomass application on MacOS and Windows.
        """
        from videomass3.vdms_dialogs.first_time_start import FirstStart
        main_frame = FirstStart(icon)
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
            # print ('set a custom language: %s' % selLang)
        else:
            selLang = wx.LANGUAGE_DEFAULT
            # print ("Set language default\n%s" % appC.supLang)
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
        OnExit provides an interface for exiting the application
        """
        # print ("OnExit")
        return True
    # -------------------------------------------------------------------


def main():
    """
    Starts the wx.App mainloop
    """
    app = Videomass(False)
    # app.MainLoop()
    fred = app.MainLoop()
    # print ("after MainLoop", fred)
