# -*- coding: UTF-8 -*-
"""
Name: configurator.py
Porpose: Set Videomass configuration and appearance on startup
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.13.2021
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import shutil
import platform
from videomass3.vdms_utils.utils import copydir_recursively
from videomass3.vdms_utils.utils import copy_restore


def parsing_fileconf(fileconf):
    """
    Make parsing of the configuration file and return
    object list with the current program settings data.
    """
    with open(fileconf, 'r', encoding='utf8') as fget:
        fconf = fget.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    dataconf = [x for x in lst if x]  # list without empties values

    return None if not dataconf else dataconf


def get_pyinstaller():
    """
    Get pyinstaller-based package attributes to determine
    how to use sys.executable
    When a bundled app starts up, the bootloader sets the sys.frozen
    attribute and stores the absolute path to the bundle folder
    in sys._MEIPASS.
    For a one-folder bundle, this is the path to that folder.
    For a one-file bundle, this is the path to the temporary folder
    created by the bootloader.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('getattr frozen, hasattr _MEIPASS')
        frozen, meipass = True, True
        mpath = getattr(sys, '_MEIPASS', os.path.abspath(__file__))
        data_locat = mpath

    else:
        frozen, meipass = False, False
        mpath = os.path.realpath(os.path.abspath(__file__))
        data_locat = os.path.dirname(os.path.dirname(mpath))

    return frozen, meipass, mpath, data_locat


def conventional_paths():
    """
    Establish the conventional paths based on OS by installation

    """
    user_name = os.path.expanduser('~')

    if platform.system() == 'Windows':
        dirpath = "\\AppData\\Roaming\\videomass\\videomass.conf"
        file_conf = os.path.join(user_name + dirpath)
        dir_conf = os.path.join(user_name + "\\AppData\\Roaming\\videomass")
        log_dir = os.path.join(dir_conf, 'log')  # logs
        cache_dir = os.path.join(dir_conf, 'cache')  # updates executable

    elif platform.system() == "Darwin":
        dirpath = "Library/Application Support/videomass/videomass.conf"
        file_conf = os.path.join(user_name, dirpath)
        dir_conf = os.path.join(user_name, os.path.dirname(dirpath))
        log_dir = os.path.join(user_name, "Library/Logs/videomass")
        cache_dir = os.path.join(user_name, "Library/Caches/videomass")

    else:  # Linux, FreeBsd, etc.
        dirpath = ".config/videomass/videomass.conf"
        file_conf = os.path.join(user_name, dirpath)
        dir_conf = os.path.join(user_name, ".config/videomass")
        log_dir = os.path.join(user_name, ".local/share/videomass/log")
        cache_dir = os.path.join(user_name, ".cache/videomass")

    return file_conf, dir_conf, log_dir, cache_dir


def portable_paths(portdir):
    """
    Make portable-data paths based on OS by a portable mode

    """
    if platform.system() == 'Windows':
        file_conf = portdir + "\\portable_data\\videomass.conf"
        dir_conf = portdir + "\\portable_data"
        log_dir = os.path.join(dir_conf, 'log')  # logs
        cache_dir = os.path.join(dir_conf, 'cache')  # updates executable
    else:
        file_conf = portdir + "/portable_data/videomass.conf"
        dir_conf = portdir + "/portable_data"
        log_dir = os.path.join(dir_conf, 'log')  # logs
        cache_dir = os.path.join(dir_conf, 'cache')  # updates executable

    return file_conf, dir_conf, log_dir, cache_dir


class DataSource():
    """
    DataSource class determines the Videomass's configuration
    according to the used Operating System (Linux/*BSD, MacOS, Windows).
    Remember that all specifications defined in this class refer
    only to the following packaging methods:

        - Videomass Python package by PyPi (cross-platform, multiuser/user)
        - Linux's distributions packaging (multiuser)
        - Bundled app by pyinstaller (windowed for MacOs and Windows)
        - AppImage for Linux (user)

        * multiuser: root installation
        * user: local installation

    """
    FROZEN, MEIPASS, MPATH, DATA_LOCAT = get_pyinstaller()
    portdirname = os.path.dirname(sys.executable)
    portdir = os.path.join(portdirname, 'portable_data')

    if FROZEN and MEIPASS and os.path.isdir(portdir):
        # if portdir is true, make application really portable
        FILE_CONF, DIR_CONF, LOG_DIR, CACHE_DIR = portable_paths(portdirname)
        RELPATH = True if platform.system() == 'Windows' else False

    elif os.path.isdir(os.path.join(DATA_LOCAT, 'portable_data')):
        # Remember to add portable_data/ folder within videomass3/
        FILE_CONF, DIR_CONF, LOG_DIR, CACHE_DIR = portable_paths(DATA_LOCAT)
        RELPATH = False

    else:
        FILE_CONF, DIR_CONF, LOG_DIR, CACHE_DIR = conventional_paths()
        RELPATH = False
    # -------------------------------------------------------------------

    def __init__(self):
        """
        Given the pathnames defined by `DATA_LOCAT` it performs
        the initialization described in DataSource.

            `self.srcpath` > configuration folder for recovery
            `self.icodir` > set of icons
            `self.localepath` > locale folder

        """
        self.apptype = None  # appimage, pyinstaller on None
        self.workdir = os.path.dirname(os.path.dirname
                                       (os.path.dirname(DataSource.MPATH))
                                       )
        self.localepath = os.path.join(DataSource.DATA_LOCAT, 'locale')
        self.srcpath = os.path.join(DataSource.DATA_LOCAT, 'share')
        self.icodir = os.path.join(DataSource.DATA_LOCAT, 'art', 'icons')
        self.ffmpeg_pkg = os.path.join(DataSource.DATA_LOCAT, 'FFMPEG')
        launcher = os.path.isfile('%s/launcher' % self.workdir)

        if DataSource.FROZEN and DataSource.MEIPASS or launcher:
            print('frozen=%s meipass=%s launcher=%s' % (DataSource.FROZEN,
                                                        DataSource.MEIPASS,
                                                        launcher
                                                        ))
            self.apptype = 'pyinstaller' if launcher is False else None
            self.videomass_icon = "%s/videomass.png" % self.icodir

        else:
            if platform.system() == 'Windows':  # Installed with pip command
                print('Win32 executable=%s' % sys.executable)
                # HACK check this
                # dirname = os.path.dirname(sys.executable)
                # pythonpath = os.path.join(dirname, 'Script', 'videomass')
                # self.icodir = dirname + '\\share\\videomass\\icons'
                self.videomass_icon = self.icodir + "\\videomass.png"

            elif ('/tmp/.mount_' in sys.executable or os.path.exists(
                  os.path.dirname(os.path.dirname(os.path.dirname(
                      sys.argv[0]))) + '/AppRun')):
                # embedded on python appimage
                print('Embedded on python appimage')
                self.apptype = 'appimage'
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

    def get_fileconf(self):
        """
        Get videomass configuration data by videomass.conf file.
        Returns a dict object.

        This method performs the following main steps:

            1) Checks user videomass configuration dir; if not exists try to
               restore from self.srcpath
            2) Read the videomass.conf file; if not exists try to restore
               from self.srcpath
            3) Checks presets folder; if not exists try to restore from
               self.srcpath

        Note that when `copyerr` is not False, it raise a fatal error on
        videomass bootstrap.
        """
        copyerr = False
        existfileconf = True  # True > found, False > not found

        if os.path.exists(DataSource.DIR_CONF):  # if ~/.conf/videomass dir
            if os.path.isfile(DataSource.FILE_CONF):
                userconf = parsing_fileconf(DataSource.FILE_CONF)
                if not userconf:
                    existfileconf = False
                if float(userconf[0]) != 3.2:
                    existfileconf = False
            else:
                existfileconf = False

            if not existfileconf:  # try to restore only videomass.conf
                fcopy = copy_restore('%s/videomass.conf' % self.srcpath,
                                     DataSource.FILE_CONF)
                if fcopy:
                    copyerr, userconf = fcopy, None
                else:
                    userconf = parsing_fileconf(DataSource.FILE_CONF)
                    # read again file conf

            if not os.path.exists(os.path.join(DataSource.DIR_CONF,
                                               "presets")):
                # try to restoring presets directory on videomass dir
                drest = copydir_recursively(os.path.join(self.srcpath,
                                                         "presets"),
                                            DataSource.DIR_CONF)
                if drest:
                    copyerr, userconf = drest, None

        else:  # try to restore entire configuration directory
            dconf = copydir_recursively(self.srcpath,
                                        os.path.dirname(DataSource.DIR_CONF),
                                        "videomass")
            userconf = parsing_fileconf(DataSource.FILE_CONF)
            # read again file conf
            if dconf:
                copyerr, userconf = dconf, None

        getpath = (lambda path: os.path.relpath(path) if
                   DataSource.RELPATH else path)

        return ({'ostype': platform.system(),
                 'srcpath': getpath(self.srcpath),
                 'fatalerr': copyerr,
                 'localepath': getpath(self.localepath),
                 'fileconfpath': getpath(DataSource.FILE_CONF),
                 'workdir': getpath(self.workdir),
                 'confdir': getpath(DataSource.DIR_CONF),
                 'logdir': getpath(DataSource.LOG_DIR),
                 'cachedir': getpath(DataSource.CACHE_DIR),
                 'FFMPEG_videomass_pkg': getpath(self.ffmpeg_pkg),
                 'app': self.apptype,
                 'relpath': DataSource.RELPATH,
                 'getpath': getpath,
                 'confversion': userconf[0],
                 'outputfile': userconf[1],
                 'ffthreads': userconf[2],
                 'ffplayloglev': userconf[3],
                 'ffmpegloglev': userconf[4],
                 'ffmpeg_local': userconf[5],
                 'ffmpeg_bin': getpath(userconf[6]),
                 'ffprobe_local': userconf[7],
                 'ffprobe_bin': getpath(userconf[8]),
                 'ffplay_local': userconf[9],
                 'ffplay_bin': getpath(userconf[10]),
                 'icontheme': userconf[11],
                 'toolbarsize': userconf[12],
                 'toolbarpos': userconf[13],
                 'toolbartext': userconf[14],
                 'clearcache': userconf[15],
                 'enable_youtubedl': userconf[16],
                 'outputfile_samedir': userconf[17],
                 'filesuffix': userconf[18],
                 'outputdownload': userconf[19],
                 'playlistsubfolder': userconf[20]}
                )
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the configuration
        file (see `Set icon themes map:`, on paragraph `6- GUI setup`
        by Videomass.conf).
        Returns a icontheme dict object.

        """
        keys = ('videomass', 'A/V-Conv', 'startconv', 'fileproperties',
                'playback', 'concatenate', 'preview', 'clear',
                'profile_append', 'scale', 'crop', 'rotate', 'deinterlace',
                'denoiser', 'statistics', 'settings', 'audiovolume',
                'youtube', 'presets_manager', 'profile_add', 'profile_del',
                'profile_edit', 'previous', 'next', 'startdownload',
                'download_properties', 'stabilizer', 'listindx')

        ext = 'svg' if 'wx.svg' in sys.modules else 'png'

        iconames = {'Videomass-Light':  # Videomass icons for light themes
                    {'x48': '%s/Sign_Icons/48x48_light' % self.icodir,
                     'x16': '%s/Videomass-Light/16x16' % self.icodir,
                     'x22': '%s/Videomass-Light/24x24' % self.icodir},
                    'Videomass-Dark':  # Videomass icons for dark themes
                    {'x48': '%s/Sign_Icons/48x48_dark' % self.icodir,
                     'x16': '%s/Videomass-Dark/16x16' % self.icodir,
                     'x22': '%s/Videomass-Dark/24x24' % self.icodir},
                    'Videomass-Colours':  # Videomass icons for all themes
                    {'x48': '%s/Sign_Icons/48x48' % self.icodir,
                     'x16': '%s/Videomass-Colours/16x16' % self.icodir,
                     'x22': '%s/Videomass-Colours/24x24' % self.icodir},
                    'Breeze':  # Breeze for light themes
                    {'x48': '%s/Sign_Icons/48x48_light' % self.icodir,
                     'x16': '%s/Breeze/16x16' % self.icodir,
                     'x22': '%s/Breeze/22x22' % self.icodir},
                    'Breeze-Dark':  # breeze for dark themes
                    {'x48': '%s/Sign_Icons/48x48_dark' % self.icodir,
                     'x16': '%s/Breeze-Dark/16x16' % self.icodir,
                     'x22': '%s/Breeze-Dark/22x22' % self.icodir},
                    'Breeze-Blues':  # breeze custom colorized for all themes
                    {'x48': '%s/Sign_Icons/48x48' % self.icodir,
                     'x16': '%s/Breeze-Blues/16x16' % self.icodir,
                     'x22': '%s/Breeze-Blues/22x22' % self.icodir}
                    }

        choose = iconames.get(icontheme)  # set appropriate icontheme

        iconset = (self.videomass_icon,
                   '%s/icon_videoconversions.%s' % (choose.get('x48'), ext),
                   '%s/convert.%s' % (choose.get('x22'), ext),
                   '%s/properties.%s' % (choose.get('x22'), ext),
                   '%s/playback.%s' % (choose.get('x16'), ext),
                   '%s/icon_concat.%s' % (choose.get('x48'), ext),
                   '%s/preview.%s' % (choose.get('x16'), ext),
                   '%s/edit-clear.%s' % (choose.get('x16'), ext),
                   '%s/profile-append.%s' % (choose.get('x22'), ext),
                   '%s/transform-scale.%s' % (choose.get('x16'), ext),
                   '%s/transform-crop.%s' % (choose.get('x16'), ext),
                   '%s/transform-rotate.%s' % (choose.get('x16'), ext),
                   '%s/deinterlace.%s' % (choose.get('x16'), ext),
                   '%s/denoise.%s' % (choose.get('x16'), ext),
                   '%s/statistics.%s' % (choose.get('x16'), ext),
                   '%s/configure.%s' % (choose.get('x16'), ext),
                   '%s/player-volume.%s' % (choose.get('x16'), ext),
                   '%s/icon_youtube.%s' % (choose.get('x48'), ext),
                   '%s/icon_prst_mng.%s' % (choose.get('x48'), ext),
                   '%s/newprf.%s' % (choose.get('x16'), ext),
                   '%s/delprf.%s' % (choose.get('x16'), ext),
                   '%s/editprf.%s' % (choose.get('x16'), ext),
                   '%s/go-previous.%s' % (choose.get('x22'), ext),
                   '%s/go-next.%s' % (choose.get('x22'), ext),
                   '%s/download.%s' % (choose.get('x22'), ext),
                   '%s/statistics.%s' % (choose.get('x22'), ext),
                   '%s/stabilizer.%s' % (choose.get('x16'), ext),
                   '%s/playlist-append.%s' % (choose.get('x16'), ext)
                   )
        values = [os.path.join(norm) for norm in iconset]  # normalize pathns

        return dict(zip(keys, values))
