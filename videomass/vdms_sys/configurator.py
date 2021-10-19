# -*- coding: UTF-8 -*-
"""
Name: configurator.py
Porpose: Set Videomass configuration on startup
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.01.2021
Code checker: pycodestyle, flake8, pylint .

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
from videomass.vdms_utils.utils import copydir_recursively
from videomass.vdms_utils.utils import copy_restore


def readconf(fileconf):
    """
    Reads the videomass.conf configuration file, parses it,
    and returns a list of current user settings objects.
    Returns None if no data is found.
    """
    with open(fileconf, 'r', encoding='utf8') as fget:
        fconf = fget.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    dataconf = [x for x in lst if x]  # list without empties values

    return None if not dataconf else dataconf


def checkconf(dirconf, fileconf, srcpath):
    """
    Check applicatin configuration.
    This method performs the following main steps:

        1) Checks user videomass configuration dir; if not exists try to
           restore from srcpath
        2) Read the videomass.conf file; if not exists (or version is
           different) try to restore from srcpath.
        3) Checks presets folder; if not exists try to restore from
           srcpath

    if not errors, return dict key == 'R' else return a dict key == ERROR
    """
    existfileconf = True  # True > found, False > not found or outdated

    if os.path.exists(dirconf):  # if ~/.conf/videomass dir
        if os.path.isfile(fileconf):
            data = {'R': readconf(fileconf)}
            if not data['R']:
                existfileconf = False
            if float(data['R'][0]) != 3.4:  # version
                existfileconf = False
        else:
            existfileconf = False

        if existfileconf is False:  # try to restore only videomass.conf
            fcopy = copy_restore(f'{srcpath}/videomass.conf', fileconf)
            data = {'ERROR': fcopy} if fcopy else {'R': readconf(fileconf)}

        if not os.path.exists(os.path.join(dirconf, "presets")):
            # try to restoring presets directory on videomass dir
            drest = copydir_recursively(os.path.join(srcpath, "presets"),
                                        dirconf)
            if drest:
                return {'ERROR': drest}

    else:  # try to restore entire configuration directory
        dconf = copydir_recursively(srcpath, os.path.dirname(dirconf),
                                    "videomass")
        data = {'ERROR': dconf} if dconf else {'R': readconf(fileconf)}

    return data


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
    Establish the conventional paths based on OS

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
    Make portable-data paths based on OS

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


def get_outdir(outdir, relpath, apptype):
    """
    Set default or user-custom output folders
    """
    if not outdir == 'none':
        outputdir = outdir
    elif relpath is True:
        appdir = (os.path.dirname(sys.prefix) if
                  apptype == 'embed' else os.getcwd())
        outputdir = os.path.relpath(os.path.join(appdir, 'My_Files'))

        if not os.path.exists(outputdir):
            try:  # make a files folder
                os.mkdir(outputdir, mode=0o777)
            except OSError as err:
                return None, err
            except TypeError as err:
                return None, err
    else:
        outputdir = os.path.expanduser('~')

    return outputdir, None


def get_color_scheme(theme):
    """
    Returns the corrisponding colour scheme according to
    chosen theme in ("Videomass-Light",
                     "Videomass-Dark",
                     "Videomass-Colours",
                     "Breeze",
                     "Breeze-Dark",
                     "Breeze-Blues"
                     )
    """
    if theme in ('Breeze-Blues', 'Videomass-Colours'):
        c_scheme = {'BACKGRD': '#1c2027ff',  # DARK_SLATE background color
                    'TXT0': '#FFFFFF',  # WHITE for title or URL in progress
                    'TXT1': '#959595',  # GREY for all other text messages
                    'ERR0': '#FF4A1B',  # ORANGE for error text messages
                    'WARN': '#dfb72f',  # YELLOW for warning text messages
                    'ERR1': '#EA312D',  # LIGHTRED for errors 2
                    'SUCCESS': '#30ec30',  # Light GREEN when it is successful
                    'TXT2': '#3f5e6b',  # dark ciano
                    'TXT3': '#11b584',  # medium green
                    'TXT4': '#87ceebff',  # light azure
                    'TXT5': '#dd7ad0',  # LILLA
                    'INFO': '#3298FB',  # AZURE
                    'DEBUG': '#0ce3ac',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme in ('Breeze-Blues', 'Breeze-Dark', 'Videomass-Dark'):
        c_scheme = {'BACKGRD': '#232424',  # DARK Grey background color
                    'TXT0': '#FFFFFF',  # WHITE for title or URL in progress
                    'TXT1': '#959595',  # GREY for all other text messages
                    'ERR0': '#FF4A1B',  # ORANGE for error text messages
                    'WARN': '#dfb72f',  # YELLOW for warning text messages
                    'ERR1': '#EA312D',  # LIGHTRED for errors 2
                    'SUCCESS': '#30ec30',  # Light GREEN when it is successful
                    'TXT2': '#008000',  # dark green
                    'TXT3': '#11b584',  # medium green
                    'TXT4': '#87ceebff',  # light azure
                    'TXT5': '#dd7ad0',  # LILLA
                    'INFO': '#118db5',  # AZURE
                    'DEBUG': '#0ce3ac',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme in ('Breeze', 'Videomass-Light'):
        c_scheme = {'BACKGRD': '#ced0d1',  # WHITE background color
                    'TXT0': '#1f1f1fff',  # BLACK for title or URL in progress
                    'TXT1': '#778899ff',  # LIGHT_SLATE for all other text msg
                    'ERR0': '#d25c07',  # ORANGE for error text messages
                    'WARN': '#988313',  # YELLOW for warning text messages
                    'ERR1': '#c8120b',  # LIGHTRED for errors 2
                    'SUCCESS': '#35a735',  # DARK_GREEN when it is successful
                    'TXT2': '#008000',  # dark green
                    'TXT3': '#005c00',  # Light Green
                    'TXT4': '#2651b8',  # blue
                    'TXT5': '#dd7ad0',  # LILLA
                    'INFO': '#3298FB',  # AZURE
                    'DEBUG': '#005c00',  # Light Green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    else:
        c_scheme = {'ERROR': f'Unknow theme "{theme}"'}

    return c_scheme


def msg(arg):
    """
    print logging messages during startup
    """
    print('Info:', arg)


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
        RELPATH = platform.system() == 'Windows'

    elif os.path.isdir(os.path.join(DATA_LOCAT, 'portable_data')):
        # Remember to add portable_data/ folder within videomass/
        FILE_CONF, DIR_CONF, LOG_DIR, CACHE_DIR = portable_paths(DATA_LOCAT)
        RELPATH = '-embed-' in os.path.basename(sys.prefix)

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
        launcher = os.path.isfile(f'{self.workdir}/launcher')

        if DataSource.FROZEN and DataSource.MEIPASS or launcher:
            msg(f'frozen={DataSource.FROZEN} '
                f'meipass={DataSource.MEIPASS} '
                f'launcher={launcher}')

            self.apptype = 'pyinstaller' if not launcher else None
            self.videomass_icon = f"{self.icodir}/videomass.png"

        elif ('/tmp/.mount_' in sys.executable or os.path.exists(
              os.path.dirname(os.path.dirname(os.path.dirname(
                  sys.argv[0]))) + '/AppRun')):
            # embedded on python appimage
            msg('Embedded on python appimage')
            self.apptype = 'appimage'
            userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
            pixmaps = '/share/pixmaps/videomass.png'
            self.videomass_icon = os.path.join(userbase + pixmaps)

        else:
            binarypath = shutil.which('videomass')
            if platform.system() == 'Windows':  # any other packages
                exe = binarypath if binarypath else sys.executable
                msg(f'Win32 executable={exe}')
                # HACK check this
                # dirname = os.path.dirname(sys.executable)
                # pythonpath = os.path.join(dirname, 'Script', 'videomass')
                # self.icodir = dirname + '\\share\\videomass\\icons'
                self.videomass_icon = self.icodir + "\\videomass.png"
                if '-embed-' in os.path.basename(sys.prefix):
                    self.apptype = 'embed'

            elif binarypath == '/usr/local/bin/videomass':
                msg(f'executable={binarypath}')
                # pip as super user, usually Linux, MacOs, Unix
                share = '/usr/local/share/pixmaps'
                self.videomass_icon = share + '/videomass.png'

            elif binarypath == '/usr/bin/videomass':
                msg(f'executable={binarypath}')
                # installed via apt, rpm, etc, usually Linux
                share = '/usr/share/pixmaps'
                self.videomass_icon = share + "/videomass.png"

            else:
                msg(f'executable={binarypath}')
                # pip as normal user, usually Linux, MacOs, Unix
                userbase = os.path.dirname(os.path.dirname(binarypath))
                pixmaps = '/share/pixmaps/videomass.png'
                self.videomass_icon = os.path.join(userbase + pixmaps)
    # ---------------------------------------------------------------------

    def get_fileconf(self):
        """
        Get videomass configuration data and returns a dict object
        with current data-set for bootstrap.

        Note: If returns a dict key == ERROR it will raise a windowed
        fatal error in the gui_app bootstrap.
        """
        userconf = checkconf(DataSource.DIR_CONF,
                             DataSource.FILE_CONF,
                             self.srcpath
                             )
        if userconf.get('ERROR'):
            return userconf
        userconf = userconf['R']

        # set color scheme
        theme = get_color_scheme(userconf[11])
        if theme.get('ERROR'):
            return theme

        # set output directories
        outfile = get_outdir(userconf[1], DataSource.RELPATH, self.apptype)
        outdownl = get_outdir(userconf[19], DataSource.RELPATH, self.apptype)
        if outfile[1]:
            return {'ERROR': f'{outfile[1]}'}
        if outdownl[1]:
            return {'ERROR': f'{outdownl[1]}'}

        def _relativize(path, relative=DataSource.RELPATH):
            """
            Returns a relative pathname if *relative* param is True.
            If not, it returns the given pathname. This function is called
            several times during program execution.
            """
            try:
                return os.path.relpath(path) if relative else path
            except ValueError as error:
                return {'ERROR': f'{error}'}

        # set downloader
        execlist = (('youtube_dl', 'youtube-dl'),
                    ('yt_dlp', 'yt-dlp'),
                    ('Disable all', 'Downloader'),
                    ('false', '')
                    )
        downloader = [exe for exe in execlist if exe[0] == userconf[16]]
        if not downloader:
            return {'ERROR': f'Unknow downloader "{userconf[16]}"'}

        return ({'ostype': platform.system(),
                 'srcpath': _relativize(self.srcpath),
                 'localepath': _relativize(self.localepath),
                 'fileconfpath': _relativize(DataSource.FILE_CONF),
                 'workdir': _relativize(self.workdir),
                 'confdir': _relativize(DataSource.DIR_CONF),
                 'logdir': _relativize(DataSource.LOG_DIR),
                 'cachedir': _relativize(DataSource.CACHE_DIR),
                 'FFMPEG_videomass_pkg': _relativize(self.ffmpeg_pkg),
                 'app': self.apptype,
                 'relpath': DataSource.RELPATH,
                 'getpath': _relativize,
                 'confversion': userconf[0],
                 'outputfile': outfile[0],
                 'ffthreads': userconf[2],
                 'ffplayloglev': userconf[3],
                 'ffmpegloglev': userconf[4],
                 'ffmpeg_local': userconf[5],
                 'ffmpeg_bin': _relativize(userconf[6]),
                 'ffprobe_local': userconf[7],
                 'ffprobe_bin': _relativize(userconf[8]),
                 'ffplay_local': userconf[9],
                 'ffplay_bin': _relativize(userconf[10]),
                 'icontheme': (userconf[11], theme),
                 'toolbarsize': userconf[12],
                 'toolbarpos': userconf[13],
                 'toolbartext': userconf[14],
                 'clearcache': userconf[15],
                 'downloader': downloader[0],
                 'outputfile_samedir': userconf[17],
                 'filesuffix': userconf[18],
                 'outputdownload': outdownl[0],
                 'playlistsubfolder': userconf[20],
                 'warnexiting': userconf[21]}
                )
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the configuration
        file (see `Set icon themes map:`, on paragraph `6- GUI setup`
        in the videomass.conf file).
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
                    {'x48': f'{self.icodir}/Sign_Icons/48x48_light',
                     'x16': f'{self.icodir}/Videomass-Light/16x16',
                     'x22': f'{self.icodir}/Videomass-Light/24x24'},
                    'Videomass-Dark':  # Videomass icons for dark themes
                    {'x48': f'{self.icodir}/Sign_Icons/48x48_dark',
                     'x16': f'{self.icodir}/Videomass-Dark/16x16',
                     'x22': f'{self.icodir}/Videomass-Dark/24x24'},
                    'Videomass-Colours':  # Videomass icons for all themes
                    {'x48': f'{self.icodir}/Sign_Icons/48x48',
                     'x16': f'{self.icodir}/Videomass-Colours/16x16',
                     'x22': f'{self.icodir}/Videomass-Colours/24x24'},
                    'Breeze':  # Breeze for light themes
                    {'x48': f'{self.icodir}/Sign_Icons/48x48_light',
                     'x16': f'{self.icodir}/Breeze/16x16',
                     'x22': f'{self.icodir}/Breeze/22x22'},
                    'Breeze-Dark':  # breeze for dark themes
                    {'x48': f'{self.icodir}/Sign_Icons/48x48_dark',
                     'x16': f'{self.icodir}/Breeze-Dark/16x16',
                     'x22': f'{self.icodir}/Breeze-Dark/22x22'},
                    'Breeze-Blues':  # breeze custom colorized for all themes
                    {'x48': f'{self.icodir}/Sign_Icons/48x48',
                     'x16': f'{self.icodir}/Breeze-Blues/16x16',
                     'x22': f'{self.icodir}/Breeze-Blues/22x22'}
                    }

        choose = iconames.get(icontheme)  # set appropriate icontheme

        iconset = (self.videomass_icon,
                   f"{choose.get('x48')}/icon_videoconversions.{ext}",
                   f"{choose.get('x22')}/convert.{ext}",
                   f"{choose.get('x22')}/properties.{ext}",
                   f"{choose.get('x16')}/playback.{ext}",
                   f"{choose.get('x48')}/icon_concat.{ext}",
                   f"{choose.get('x16')}/preview.{ext}",
                   f"{choose.get('x16')}/edit-clear.{ext}",
                   f"{choose.get('x22')}/profile-append.{ext}",
                   f"{choose.get('x16')}/transform-scale.{ext}",
                   f"{choose.get('x16')}/transform-crop.{ext}",
                   f"{choose.get('x16')}/transform-rotate.{ext}",
                   f"{choose.get('x16')}/deinterlace.{ext}",
                   f"{choose.get('x16')}/denoise.{ext}",
                   f"{choose.get('x16')}/statistics.{ext}",
                   f"{choose.get('x16')}/configure.{ext}",
                   f"{choose.get('x16')}/player-volume.{ext}",
                   f"{choose.get('x48')}/icon_youtube.{ext}",
                   f"{choose.get('x48')}/icon_prst_mng.{ext}",
                   f"{choose.get('x16')}/newprf.{ext}",
                   f"{choose.get('x16')}/delprf.{ext}",
                   f"{choose.get('x16')}/editprf.{ext}",
                   f"{choose.get('x22')}/go-previous.{ext}",
                   f"{choose.get('x22')}/go-next.{ext}",
                   f"{choose.get('x22')}/download.{ext}",
                   f"{choose.get('x22')}/statistics.{ext}",
                   f"{choose.get('x16')}/stabilizer.{ext}",
                   f"{choose.get('x16')}/playlist-append.{ext}",
                   )
        values = [os.path.join(norm) for norm in iconset]  # normalize pathns

        return dict(zip(keys, values))
