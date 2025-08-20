# -*- coding: UTF-8 -*-
"""
Name: configurator.py
Porpose: Set Videomass configuration on startup
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.14.2025
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
import platform
from videomass.vdms_utils.utils import copydir_recursively
from videomass.vdms_sys.settings_manager import ConfigManager


def msg(arg):
    """
    print logging messages during startup
    """
    print(arg)


def create_dirs(dirname, fconf):
    """
    This function is responsible for the recursive creation
    of directories required for Videomass if they do not exist.
    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname, mode=0o777)
        except Exception as err:
            return {'ERROR': err}

    return {'R': None}


def restore_dirconf(dirconf, srcdata, portable):
    """
    This function is responsible for restoring the
    configuration directory if it is missing and
    populating it with its essential files.
    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    if not os.path.exists(dirconf):  # create the configuration directory
        try:
            os.mkdir(dirconf, mode=0o777)
        except FileNotFoundError as err:  # parent directory does not exist
            return {'ERROR': err}

    if not os.path.exists(os.path.join(dirconf, "presets")):
        drest = copydir_recursively(os.path.join(srcdata, "presets"), dirconf)
        if drest:
            return {'ERROR': drest}

    if portable:
        transoutdir = os.path.join(dirconf, "Media", "Transcoding")
        try:
            if not os.path.exists(transoutdir):
                os.makedirs(transoutdir, mode=0o777)
        except Exception as err:
            return {'ERROR': err}

    return {'R': None}


def get_options(fileconf, makeportable):
    """
    Check the application options. Reads the `settings.json`
    file; if it does not exist or is unreadable try to restore
    it. If VERSION is not the same as the version readed, it adds
    new missing items while preserving the old ones with the same
    values.

    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    conf = ConfigManager(fileconf, makeportable)
    version = ConfigManager.VERSION

    if os.path.isfile(fileconf):
        data = {'R': conf.read_options()}
        if not data['R']:
            conf.write_options()
            data = {'R': conf.read_options()}
        if float(data['R']['confversion']) != version:  # conf version
            data['R']['confversion'] = version
            new = ConfigManager.DEFAULT_OPTIONS  # model
            data = {'R': {**new, **data['R']}}
            conf.write_options(**data['R'])
    else:
        conf.write_options()
        data = {'R': conf.read_options()}

    diff = conf.default_outputdirs(**data['R'])
    if diff != data['R']:
        conf.write_options(**diff)  # write default outputdirs
        data = {'R': conf.read_options()}

    return data


def conventional_paths():
    """
    Establish the conventional paths based on OS

    """
    user_name = os.path.expanduser('~')

    if platform.system() == 'Windows':
        fpath = "\\AppData\\Roaming\\videomass\\settings.json"
        file_conf = os.path.join(user_name + fpath)
        dir_conf = os.path.join(user_name + "\\AppData\\Roaming\\videomass")
        log_dir = os.path.join(dir_conf, 'log')  # logs
        cache_dir = os.path.join(dir_conf, 'cache')  # updates executable
        trash_dir = os.path.join(dir_conf, "Trash")

    elif platform.system() == "Darwin":
        fpath = "Library/Application Support/videomass/settings.json"
        file_conf = os.path.join(user_name, fpath)
        dir_conf = os.path.join(user_name, os.path.dirname(fpath))
        log_dir = os.path.join(user_name, "Library/Logs/videomass")
        cache_dir = os.path.join(user_name, "Library/Caches/videomass")
        trash_dir = os.path.join(dir_conf, "Trash")

    else:  # Linux, FreeBsd, etc.
        fpath = ".config/videomass/settings.json"
        file_conf = os.path.join(user_name, fpath)
        dir_conf = os.path.join(user_name, ".config/videomass")
        log_dir = os.path.join(user_name, ".local/share/videomass/log")
        cache_dir = os.path.join(user_name, ".cache/videomass")
        trash_dir = os.path.join(dir_conf, "Trash")

    return file_conf, dir_conf, log_dir, cache_dir, trash_dir


def portable_paths(portdirname):
    """
    Make portable-data paths based on OS

    """
    dir_conf = portdirname
    file_conf = os.path.join(dir_conf, "settings.json")
    log_dir = os.path.join(dir_conf, 'log')  # logs
    cache_dir = os.path.join(dir_conf, 'cache')  # updates executable
    trash_dir = os.path.join(dir_conf, "Trash")

    return file_conf, dir_conf, log_dir, cache_dir, trash_dir


def get_color_scheme(theme):
    """
    Returns the corrisponding colour scheme according to
    chosen theme in ("Videomass-Light",
                     "Videomass-Dark",
                     "Videomass-Colours",
                     "Ubuntu-Light-Aubergine",
                     "Ubuntu-Dark-Aubergine",
                     )
    """
    if theme == 'Videomass-Colours':
        c_scheme = {'BACKGRD': '#8dc6c2',  # Ciano: background color
                    'TXT0': '#d01d7a',  # Magenta: titles & end messages)
                    'TXT1': '#ae11db',  # Purple for debug and others
                    'ERR0': '#FF4A1B',  # ORANGE: errors 1 and others
                    'WARN': '#7b6e01',  # YELLOW: warnings
                    'ERR1': '#EA312D',  # LIGHTRED: errors 2
                    'SUCCESS': '#017001',  # Light GREEN: successful
                    'TXT3': '#333333',  # Dark grey: standard text
                    'INFO': '#194c7e',  # Blue: other info messages
                    'DEBUG': '#333333',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # RED_DEEP if abort
                    }
    elif theme == 'Videomass-Dark':
        c_scheme = {'BACKGRD': '#232424',  # DARK Grey background color
                    'TXT0': '#FFFFFF',  # WHITE for title or URL in progress
                    'TXT1': '#959595',  # GREY for all other text messages
                    'ERR0': '#FF4A1B',  # ORANGE for error text messages
                    'WARN': '#dfb72f',  # YELLOW for warning text messages
                    'ERR1': '#EA312D',  # LIGHTRED for errors 2
                    'SUCCESS': '#30ec30',  # Light GREEN when it is successful
                    'TXT3': '#11b584',  # medium green
                    'INFO': '#118db5',  # AZURE
                    'DEBUG': '#0ce3ac',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme == 'Videomass-Light':
        c_scheme = {'BACKGRD': '#ced0d1',  # WHITE background color
                    'TXT0': '#1f1f1f',  # BLACK for title or URL in progress
                    'TXT1': '#576470',  # LIGHT_SLATE for all other text msg
                    'ERR0': '#d25c07',  # ORANGE for error text messages
                    'WARN': '#988313',  # YELLOW for warning text messages
                    'ERR1': '#c8120b',  # LIGHTRED for errors 2
                    'SUCCESS': '#35a735',  # DARK_GREEN when it is successful
                    'TXT3': '#005c00',  # Light Green
                    'INFO': '#3298FB',  # AZURE
                    'DEBUG': '#005c00',  # Light Green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme in ('Ubuntu-Dark-Aubergine', 'Ubuntu-Light-Aubergine'):
        c_scheme = {'BACKGRD': '#2C001E',  # Dark-Aubergine background color
                    'TXT0': '#FFFFFF',  # WHITE for titles
                    'TXT1': '#8AB8E6',  # light Blue
                    'ERR0': '#E95420',  # ORANGE for error text messages
                    'WARN': '#dfb72f',  # YELLOW for warning messages
                    'ERR1': '#F90808',  # RED_DEEP
                    'SUCCESS': '#ABD533',  # Light GREEN when it is successful
                    'TXT3': '#AEA79F',  # Ubuntu warm grey (base foreground)
                    'INFO': '#F7C3B1',  # Ubuntu orange light 30%
                    'DEBUG': '#8AB8E6',  # light Blue
                    'FAILED': '#F90808',  # RED_DEEP
                    'ABORT': '#F90808',  # RED_DEEP
                    }
    else:
        c_scheme = {'ERROR': f'Unknow theme "{theme}"'}

    return c_scheme


def data_location(kwargs):
    """
    Determines data location and modes to make the app
    portable, fully portable or using conventional paths.
    Returns data location dict.
    """
    if kwargs['make_portable']:
        portdir = kwargs['make_portable']
        (conffile, confdir, logdir,
         cachedir, trash_dir) = portable_paths(portdir)
    else:
        conffile, confdir, logdir, cachedir, trash_dir = conventional_paths()

    return {"conffile": conffile,
            "confdir": confdir,
            "logdir": logdir,
            "cachedir": cachedir,
            "trashdir_default": trash_dir,
            }


class DataSource():
    """
    DataSource class determines the Videomass's
    configuration according to the used Operating
    System and installed package.

    """
    def __init__(self, kwargs):
        """
        Having the pathnames returned by `dataloc`
        it performs the initialization described in
        DataSource.

        """
        self.dataloc = data_location(kwargs)
        self.relativepaths = bool(kwargs['make_portable'])
        self.makeportable = kwargs['make_portable']

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            sitepkg = getattr(sys, '_MEIPASS', os.path.abspath(__file__))
            srcdata = sitepkg
            self.dataloc["app"] = 'pyinstaller'
            msg('Info: Stand-Alone application bundle (build by pyinstaller)')
        else:
            sitepkg = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))
            srcdata = os.path.join(sitepkg, 'videomass', 'data')
            self.dataloc["app"] = None
            msg(f"Info: Package: «videomass»\nInfo: Location: «{sitepkg}»")

        self.dataloc["localepath"] = os.path.join(srcdata, 'locale')
        self.dataloc["srcdata"] = srcdata
        self.dataloc["icodir"] = os.path.join(srcdata, 'icons')
        self.dataloc["FFMPEG_DIR"] = os.path.join(srcdata, 'FFMPEG')

        self.prg_icon = os.path.join(self.dataloc['icodir'], "videomass.png")
    # ---------------------------------------------------------------------

    def get_configuration(self):
        """
        Get configuration data of the application.
        Returns a dict object with current data-set for bootstrap.

        Note: If returns a dict key == ERROR it will raise a windowed
        fatal error in the gui_app bootstrap.
        """
        # checks configuration directory
        ckdconf = restore_dirconf(self.dataloc['confdir'],
                                  self.dataloc['srcdata'],
                                  self.makeportable,
                                  )
        if ckdconf.get('ERROR'):
            return ckdconf

        # handle configuration file
        userconf = get_options(self.dataloc['conffile'], self.makeportable)
        if userconf.get('ERROR'):
            return userconf
        userconf = userconf['R']

        # create the required directories if not existing
        requiredirs = (os.path.join(self.dataloc['cachedir'], 'tmp'),
                       self.dataloc['logdir'],
                       self.dataloc['trashdir_default']
                       )
        if not userconf['trashdir_loc'].strip():
            userconf['trashdir_loc'] = self.dataloc['trashdir_default']
        for dirs in requiredirs:
            create = create_dirs(dirs, self.dataloc['conffile'],)
            if create.get('ERROR'):
                return create

        # set color scheme
        theme = get_color_scheme(userconf['icontheme'])
        userconf['colorscheme'] = theme
        if theme.get('ERROR'):
            return theme

        def _relativize(path, relative=self.relativepaths):
            """
            Returns a relative pathname if *relative* param is True.
            If not, it returns the given pathname. Also return the given
            pathname if `ValueError` is raised. This function is called
            several times during program execution.
            """
            try:
                return os.path.relpath(path) if relative else path
            except (ValueError, TypeError):
                # return {'ERROR': f'{error}'}  # used `as error` here
                return path

        return ({'ostype': platform.system(),
                 'app': self.dataloc['app'],
                 'srcdata': _relativize(self.dataloc['srcdata']),
                 'localepath': _relativize(self.dataloc['localepath']),
                 'fileconfpath': _relativize(self.dataloc['conffile']),
                 'confdir': _relativize(self.dataloc['confdir']),
                 'logdir': _relativize(self.dataloc['logdir']),
                 'cachedir': _relativize(self.dataloc['cachedir']),
                 'trashdir_default':
                     _relativize(self.dataloc['trashdir_default']),
                 'FFMPEG_DIR': _relativize(self.dataloc['FFMPEG_DIR']),
                 'relpath': self.relativepaths,
                 'getpath': _relativize,
                 'ffmpeg_cmd': _relativize(userconf['ffmpeg_cmd']),
                 'ffprobe_cmd': _relativize(userconf['ffprobe_cmd']),
                 'ffplay_cmd': _relativize(userconf['ffplay_cmd']),
                 'ffmpeg-default-args': '-y -stats -hide_banner',
                 'ffplay-default-args': '-hide_banner',
                 'auto-restart-app': False,
                 'make_portable': self.makeportable,
                 **userconf
                 })
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the
        configuration file.
        Returns a icontheme dict object.
        """
        keys = ('videomass', 'A/V-Conv', 'startconv', 'fileproperties',
                'playback', 'concatenate', 'preview', 'clear',
                'addtoprst', 'scale', 'crop', 'rotate', 'deinterlace',
                'denoiser', 'volanalyze', 'settings', 'audiovolume',
                'presets_manager', 'profile_add', 'profile_del',
                'profile_edit', 'previous', 'next', 'stabilizer',
                'preview_audio', 'profile_copy', 'slideshow',
                'videotopictures', 'atrack', 'timerset', 'coloreq',
                'stop', 'home', 'play', 'proc-queue',
                'add-queue', 'delpreset', 'exportall', 'exportselected',
                'importfolder', 'importpreset', 'newpreset', 'reload',
                'restoreall', 'restoreselected', 'cmdshow', 'start_time',
                'end_time', 'waveform'
                )  # must match with items on `iconset` tuple, see following

        icodir = self.dataloc['icodir']
        iconames = {'Videomass-Light':  # Videomass icons for light themes
                    {'x48': f'{icodir}/Sign_Icons/48x48_light',
                     'x16': f'{icodir}/Videomass-Light/16x16',
                     'x22': f'{icodir}/Videomass-Light/24x24'},
                    'Videomass-Dark':  # Videomass icons for dark themes
                    {'x48': f'{icodir}/Sign_Icons/48x48_dark',
                     'x16': f'{icodir}/Videomass-Dark/16x16',
                     'x22': f'{icodir}/Videomass-Dark/24x24'},
                    'Videomass-Colours':  # Videomass icons for all themes
                    {'x48': f'{icodir}/Sign_Icons/48x48',
                     'x16': f'{icodir}/Videomass-Colours/16x16',
                     'x22': f'{icodir}/Videomass-Colours/24x24'},
                    'Ubuntu-Dark-Aubergine':  # Videomass icons for all themes
                    {'x48': f'{icodir}/Sign_Icons/48x48_dark',
                     'x16': f'{icodir}/Videomass-Dark/16x16',
                     'x22': f'{icodir}/Videomass-Dark/24x24'},
                    'Ubuntu-Light-Aubergine':  # Videomass icons for all themes
                    {'x48': f'{icodir}/Sign_Icons/48x48_light',
                     'x16': f'{icodir}/Videomass-Light/16x16',
                     'x22': f'{icodir}/Videomass-Light/24x24'},
                    }

        choose = iconames.get(icontheme)  # set appropriate icontheme
        ext = 'svg' if 'wx.svg' in sys.modules else 'png'
        iconset = (self.prg_icon,
                   f"{choose.get('x48')}/icon_videoconversions.{ext}",
                   f"{choose.get('x22')}/convert.{ext}",
                   f"{choose.get('x22')}/properties.{ext}",
                   f"{choose.get('x16')}/playback.{ext}",
                   f"{choose.get('x48')}/icon_concat.{ext}",
                   f"{choose.get('x16')}/preview.{ext}",
                   f"{choose.get('x16')}/edit-clear.{ext}",
                   f"{choose.get('x16')}/addtoprst.{ext}",
                   f"{choose.get('x16')}/transform-scale.{ext}",
                   f"{choose.get('x16')}/transform-crop.{ext}",
                   f"{choose.get('x16')}/transform-rotate.{ext}",
                   f"{choose.get('x16')}/deinterlace.{ext}",
                   f"{choose.get('x16')}/denoise.{ext}",
                   f"{choose.get('x16')}/volanalyze.{ext}",
                   f"{choose.get('x16')}/settings.{ext}",
                   f"{choose.get('x16')}/player-volume.{ext}",
                   f"{choose.get('x48')}/icon_prst_mng.{ext}",
                   f"{choose.get('x16')}/newprf.{ext}",
                   f"{choose.get('x16')}/delprf.{ext}",
                   f"{choose.get('x16')}/editprf.{ext}",
                   f"{choose.get('x22')}/go-previous.{ext}",
                   f"{choose.get('x22')}/go-next.{ext}",
                   f"{choose.get('x16')}/stabilizer.{ext}",
                   f"{choose.get('x16')}/preview_audio.{ext}",
                   f"{choose.get('x16')}/copyprf.{ext}",
                   f"{choose.get('x48')}/icon_slideshow.{ext}",
                   f"{choose.get('x48')}/icon_videopictures.{ext}",
                   f"{choose.get('x16')}/audiotrack.{ext}",
                   f"{choose.get('x16')}/timer.{ext}",
                   f"{choose.get('x16')}/coloreq.{ext}",
                   f"{choose.get('x22')}/stop.{ext}",
                   f"{choose.get('x22')}/home.{ext}",
                   f"{choose.get('x22')}/play.{ext}",
                   f"{choose.get('x22')}/proc-queue.{ext}",
                   f"{choose.get('x22')}/add-queue.{ext}",
                   f"{choose.get('x16')}/delpreset.{ext}",
                   f"{choose.get('x16')}/exportall.{ext}",
                   f"{choose.get('x16')}/exportselected.{ext}",
                   f"{choose.get('x16')}/importfolder.{ext}",
                   f"{choose.get('x16')}/importpreset.{ext}",
                   f"{choose.get('x16')}/newpreset.{ext}",
                   f"{choose.get('x16')}/reload.{ext}",
                   f"{choose.get('x16')}/restoreall.{ext}",
                   f"{choose.get('x16')}/restoreselected.{ext}",
                   f"{choose.get('x16')}/cmdshow.{ext}",
                   f"{choose.get('x16')}/start_time.{ext}",
                   f"{choose.get('x16')}/end_time.{ext}",
                   f"{choose.get('x16')}/waveform.{ext}",
                   )
        values = (os.path.join(norm) for norm in iconset)  # normalize pathns

        return dict(zip(keys, values))
