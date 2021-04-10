# -*- coding: UTF-8 -*-
# Name: configurator.py
# Porpose: Set Videomass configuration and appearance on startup
# Compatibility: Python3
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Apr.04.2021 *PEP8 compatible*
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
import os
import sys
import shutil
from videomass3.vdms_utils.utils import copydir_recursively
from videomass3.vdms_utils.utils import copy_restore
import platform


class Data_Source(object):
    """
    Data_Source class determines the Videomass's configuration
    according to the Operating System and define the environment
    paths based on the program execution and/or where it's
    installed.
    """
    USER_NAME = os.path.expanduser('~')
    OS = platform.system()

    # Establish the conventional paths based on OS
    if OS == 'Windows':
        DIRPATH = "\\AppData\\Roaming\\videomass\\videomass.conf"
        FILE_CONF = os.path.join(USER_NAME + DIRPATH)
        DIR_CONF = os.path.join(USER_NAME + "\\AppData\\Roaming\\videomass")
        LOG_DIR = os.path.join(DIR_CONF, 'log')  # logs
        CACHE_DIR = os.path.join(DIR_CONF, 'cache')  # updates executable

    elif OS == "Darwin":
        DIRPATH = "Library/Application Support/videomass/videomass.conf"
        FILE_CONF = os.path.join(USER_NAME, DIRPATH)
        DIR_CONF = os.path.join(USER_NAME, os.path.dirname(DIRPATH))
        LOG_DIR = os.path.join(USER_NAME, "Library/Logs/videomass")
        CACHE_DIR = os.path.join(USER_NAME, "Library/Caches/videomass")

    else:  # Linux, FreeBsd, etc.
        DIRPATH = ".config/videomass/videomass.conf"
        FILE_CONF = os.path.join(USER_NAME, DIRPATH)
        DIR_CONF = os.path.join(USER_NAME, ".config/videomass")
        LOG_DIR = os.path.join(USER_NAME, ".local/share/videomass/log")
        CACHE_DIR = os.path.join(USER_NAME, ".cache/videomass")
    # -------------------------------------------------------------------

    def __init__(self):
        """
        Given the paths defined by `data_location` (a configuration
        folder for recovery > `self.SRCpath`, a set of icons >
        `self.icodir` and a folder for the locale > `self.localepath`),
        it performs the initialization described in Data_Source.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            print('getattr frozen, hasattr _MEIPASS')
            frozen, meipass = True, True
            path = getattr(sys, '_MEIPASS',  os.path.abspath(__file__))
            data_location = path
        else:
            frozen, meipass = False, False
            path = os.path.realpath(os.path.abspath(__file__))
            data_location = os.path.dirname(os.path.dirname(path))

        self.WORKdir = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        self.localepath = os.path.join(data_location, 'locale')
        self.SRCpath = os.path.join(data_location, 'share')
        self.icodir = os.path.join(data_location, 'art', 'icons')
        self.FFmpeglocaldir = os.path.join(data_location, 'FFMPEG')
        launcher = os.path.isfile('%s/launcher' % self.WORKdir)

        if frozen and meipass or launcher:
            print('frozen=%s meipass=%s launcher=%s' % (frozen, meipass,
                                                        launcher))
            self.videomass_icon = "%s/videomass.png" % self.icodir

        else:
            if Data_Source.OS == 'Windows':  # Installed with pip command
                print('Win32 executable=%s' % sys.executable)
                # HACK check this
                dirname = os.path.dirname(sys.executable)
                pythonpath = os.path.join(dirname, 'Script', 'videomass')
                # self.icodir = dirname + '\\share\\videomass\\icons'
                self.videomass_icon = self.icodir + "\\videomass.png"

            elif ('/tmp/.mount_' in sys.executable or os.path.exists(
                  os.path.dirname(os.path.dirname(os.path.dirname(
                   sys.argv[0]))) + '/AppRun')):
                # embedded on python appimage
                print('Embedded on python appimage')
                userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
                pixmaps = '/share/pixmaps/videomass.png'
                self.videomass_icon = os.path.join(userbase + pixmaps)

            elif 'usr/bin/videomass' in sys.argv[0]:
                print('Embedded on python appimage externally')
                userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
                pixmaps = '/share/pixmaps/videomass.png'
                self.videomass_icon = os.path.join(userbase + pixmaps)

            else:
                binarypath = shutil.which('videomass')

                if binarypath == '/usr/local/bin/videomass':
                    print('executable=%s' % binarypath)
                    # pip as super user, usually Linux, MacOs, Unix
                    share = '/usr/local/share/pixmaps'
                    self.videomass_icon = share + '/videomass.png'

                elif binarypath == '/usr/bin/videomass':
                    print('executable=%s' % binarypath)
                    # installed via apt, rpm, etc, usually Linux
                    share = '/usr/share/pixmaps'
                    self.videomass_icon = share + "/videomass.png"

                else:
                    print('executable=%s' % binarypath)
                    # pip as normal user, usually Linux, MacOs, Unix
                    userbase = os.path.dirname(os.path.dirname(binarypath))
                    pixmaps = '/share/pixmaps/videomass.png'
                    self.videomass_icon = os.path.join(userbase + pixmaps)
    # ---------------------------------------------------------------------

    def parsing_fileconf(self):
        """
        Make parsing of the configuration file and return
        object list with the current program settings data.
        """
        with open(Data_Source.FILE_CONF, 'r', encoding='utf8') as f:
            fconf = f.readlines()
        lst = [line.strip() for line in fconf if not line.startswith('#')]
        dataconf = [x for x in lst if x]  # list without empties values
        if not dataconf:
            return
        return dataconf
    # --------------------------------------------------------------------

    def get_fileconf(self):
        """
        Get videomass configuration data from videomass.conf .

        This method performs the following main steps:

            1) Checks user videomass configuration dir; if not exists try to
               restore from self.SRCpath
            2) Read the videomass.conf file; if not exists try to restore
               from self.SRCpath
            3) Checks presets folder; if not exists try to restore from
               self.SRCpath

        Note that when `copyerr` is not False, it causes a fatal error on
        videomass bootstrap.
        """
        copyerr = False
        existfileconf = True  # True > found, False > not found

        if os.path.exists(Data_Source.DIR_CONF):  # if ~/.conf/videomass dir
            if os.path.isfile(Data_Source.FILE_CONF):
                userconf = self.parsing_fileconf()  # fileconf data
                if not userconf:
                    existfileconf = False
                if float(userconf[0]) != 3.0:
                    existfileconf = False
            else:
                existfileconf = False

            if not existfileconf:  # try to restore only videomass.conf
                fcopy = copy_restore('%s/videomass.conf' % self.SRCpath,
                                     Data_Source.FILE_CONF)
                if fcopy:
                    copyerr, userconf = fcopy, None
                else:
                    userconf = self.parsing_fileconf()  # read again file conf

            if not os.path.exists(os.path.join(Data_Source.DIR_CONF,
                                               "presets")):
                # try to restoring presets directory on videomass dir
                drest = copydir_recursively(os.path.join(self.SRCpath,
                                                         "presets"),
                                            Data_Source.DIR_CONF)
                if drest:
                    copyerr, userconf = drest, None

        else:  # try to restore entire configuration directory
            dconf = copydir_recursively(self.SRCpath,
                                        os.path.dirname(Data_Source.DIR_CONF),
                                        "videomass")
            userconf = self.parsing_fileconf()  # read again file conf
            if dconf:
                copyerr, userconf = dconf, None

        return (Data_Source.OS,
                self.SRCpath,
                copyerr,
                None,  # unused
                userconf,
                self.localepath,
                Data_Source.FILE_CONF,
                self.WORKdir,
                Data_Source.DIR_CONF,
                Data_Source.LOG_DIR,
                Data_Source.CACHE_DIR,
                self.FFmpeglocaldir,
                )
    # --------------------------------------------------------------------

    def icons_set(self, iconset):
        """
        Assignment paths at the used icons in according to
        configuration file.

        """
        if 'wx.svg' in sys.modules:
            ext = 'svg'
        else:
            ext = 'png'
        #  Videomass icons for light themes
        if iconset == 'Videomass-Light':
            x48 = '%s/Sign_Icons/48x48_light' % self.icodir
            x16 = '%s/Videomass-Light/16x16' % self.icodir
            x22 = '%s/Videomass-Light/24x24' % self.icodir
        #  Videomass icons for dark themes
        elif iconset == 'Videomass-Dark':
            x48 = '%s/Sign_Icons/48x48_dark' % self.icodir
            x16 = '%s/Videomass-Dark/16x16' % self.icodir
            x22 = '%s/Videomass-Dark/24x24' % self.icodir
        #  Videomass icons for all themes
        elif iconset == 'Videomass-Colours':
            x48 = '%s/Sign_Icons/48x48' % self.icodir
            x16 = '%s/Videomass-Colours/16x16' % self.icodir
            x22 = '%s/Videomass-Colours/24x24' % self.icodir
        # Breeze for light themes
        elif iconset == 'Breeze':  # default
            x48 = '%s/Sign_Icons/48x48_light' % self.icodir
            x16 = '%s/Breeze/16x16' % self.icodir
            x22 = '%s/Breeze/22x22' % self.icodir
        # breeze for dark themes
        elif iconset == 'Breeze-Dark':
            x48 = '%s/Sign_Icons/48x48_dark' % self.icodir
            x16 = '%s/Breeze-Dark/16x16' % self.icodir
            x22 = '%s/Breeze-Dark/22x22' % self.icodir
        # breeze custom icons colorized for all themes
        elif iconset == 'Breeze-Blues':
            x48 = '%s/Sign_Icons/48x48' % self.icodir
            x16 = '%s/Breeze-Blues/16x16' % self.icodir
            x22 = '%s/Breeze-Blues/22x22' % self.icodir

        # choose topic icons 48x48:
        icon_switchvideomass = '%s/icon_videoconversions.%s' % (x48, ext)
        icon_youtube = '%s/icon_youtube.%s' % (x48, ext)
        icon_prst_mng = '%s/icon_prst_mng.%s' % (x48, ext)
        icon_concat = '%s/icon_concat.%s' % (x48, ext)
        # toolbar icons 22x22:
        icon_process = '%s/convert.%s' % (x22, ext)
        icon_toolback = '%s/go-previous.%s' % (x22, ext)
        icon_toolforward = '%s/go-next.%s' % (x22, ext)
        icon_ydl = '%s/download.%s' % (x22, ext)
        icn_infosource = '%s/properties.%s' % (x22, ext)
        icn_saveprf = '%s/profile-append.%s' % (x22, ext)
        icn_viewstatistics = '%s/statistics.%s' % (x22, ext)
        # button icons 16x16:
        icn_playback = '%s/playback.%s' % (x16, ext)
        icn_preview = '%s/preview.%s' % (x16, ext)
        icn_resetfilters = '%s/edit-clear.%s' % (x16, ext)
        ic_resize = '%s/transform-scale.%s' % (x16, ext)
        ic_crop = '%s/transform-crop.%s' % (x16, ext)
        ic_rotate = '%s/transform-rotate.%s' % (x16, ext)
        ic_deinterlace = '%s/deinterlace.%s' % (x16, ext)
        ic_denoiser = '%s/denoise.%s' % (x16, ext)
        ic_analyzes = '%s/statistics.%s' % (x16, ext)
        ic_settings = '%s/configure.%s' % (x16, ext)
        ic_peaklevel = '%s/player-volume.%s' % (x16, ext)
        icn_newprf = '%s/newprf.%s' % (x16, ext)
        icn_delprf = '%s/delprf.%s' % (x16, ext)
        icn_editprf = '%s/editprf.%s' % (x16, ext)
        icn_vidstab = '%s/stabilizer.%s' % (x16, ext)

        return [os.path.join(norm) for norm in [self.videomass_icon,  # 0
                                                icon_switchvideomass,  # 1
                                                icon_process,  # 2
                                                icn_infosource,  # 3
                                                icn_playback,  # 4
                                                icon_concat,  # 5
                                                icn_preview,  # 6
                                                icn_resetfilters,   # 7
                                                icn_saveprf,  # 8
                                                ic_resize,  # 9
                                                ic_crop,  # 10
                                                ic_rotate,  # 11
                                                ic_deinterlace,  # 12
                                                ic_denoiser,  # 13
                                                ic_analyzes,  # 14
                                                ic_settings,  # 15
                                                ic_peaklevel,  # 16
                                                icon_youtube,  # 17
                                                icon_prst_mng,  # 18
                                                icn_newprf,  # 19
                                                icn_delprf,  # 20
                                                icn_editprf,  # 21
                                                icon_toolback,  # 22
                                                icon_toolforward,  # 23
                                                icon_ydl,  # 24
                                                icn_viewstatistics,  # 25
                                                icn_vidstab,  # 26
                                                ]]
