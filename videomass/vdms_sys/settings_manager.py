# -*- coding: UTF-8 -*-
"""
Name: settings_manager.py
Porpose: Read and write the configuration file
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.07.2024
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
import json


class ConfigManager:
    """
    It represents the setting of the user parameters
    of the program and the configuration file in its
    read and write fondamentals.

    Usage:

    write a new conf.json :
        >>> from settings_manager import ConfigManager
        >>> confmng = ConfigManager('fileconfpath.json')
        >>> confmng.write_options()

    read the current fileconf.json :
        >>> settings = confmng.read_options()

    example of modify data into current file conf.json:
        >>> settings['outputdir'] = '/home/user/MyVideos'
        >>> confmng.write_options(**settings)
    ------------------------------------------------------

    Options description:

    confversion (float):
        current version of this configuration file

    outputdir (str):
        file destination path used by ffmpeg

    outputdir_asinput (bool):
        if True save each ffmpeg files to same folder as source

    filesuffix (str):
        An optional suffix to assign to output files

    ffmpeg_cmd, ffplay_cmd, ffprobe_cmd, (str):
        Absolute or relative path name of the executable.
        If an empty ("") string is found, starts the wizard.

    ffmpeg_islocal, ffplay_islocal, ffprobe_islocal, (bool):
        With True the user enables the executable locally

    ffmpeg_loglev (str):
        ffmpeg loglevel, one of `error`, `warning`, `info`,
        `verbose`, `debug`, default is `info` .

    ffplay_loglev (str):
        -loglevel one of `quiet`, `fatal`, `error`, `warning`, `info`

    warnexiting (bool):
        with True displays a message dialog before exiting the app

    icontheme (str):
        Icon theme Name (see art folder)

    toolbarsize (int):
        Set toolbar icon size, one of 16, 24, 32, 64 default is 24 px.

    toolbarpos (int):
        Set toolbar positioning. 0 placed on top side;
        1 placed at the bottom side; 2 placed at the rigth side;
        3 is placed at the left side. default is 0 .

    toolbartext (bool):
        True, enables text alongside toolbar buttons. Default is True.

    main_window_size (list):
        [int(Height), int(Width)] last current window dimension before
        exiting the application.

    main_window_pos (list):
        [int(x), in(y)] last current window position on monitor screen
        before exiting the application.

    clearcache (bool):
        with True, clear the cache before exiting the application,
        default is True

    clearlogfiles (bool):
        with True, erases all log files content before exiting the
        application, default is False.

    move_file_to_trash (bool):
        if True, move input files to videomass trash folder or in
        some other dir.
        default value is False

    user_trashdir (str):
        If None, it is set to "conf_trashdir" when the program runs
        (see configurator), user specified Path Name otherwise.

    locale_name (str):
        "Default", set system language to videomass message catalog
        if available, set to English otherwise.
        It supports canonical form of locale names as used on UNIX systems,
        eg. xx or xx_YY format, where xx is ISO 639 code of language and
        YY is ISO 3166 code of the country. Examples are "en", "en_GB",
        "en_US" or "fr_FR", etc.

    ydlp-outputdir (str):
        file destination path used by the youtube-dl UI

    use-downloader (bool):
        sets the ability to download videos from YouTube.com.
        One of True or False, where True means load/use yt_dlp
        on sturtup.

    playlistsubfolder (bool):
        Auto-create subfolders when download the playlists,
        default value is True.

    ("ssl_certificate", "add_metadata", "embed_thumbnails",
    "overwr_dl_files", "include_ID_name", "restrict_fname")
    (bool):
        Checkboxes option (see YouTube Downloader)

    subtitles_options (dict):
        (see YouTube Downloader)

    external_downloader (str):
        external downloader used by yt-dlp. Default is None

    external_downloader_args (list):
        args used by external downloader in yt-dlp. Default is None
        List should be passed using aria2c ["-j", "1", "-x", "1", "-s", "1"]

    prstmng_column_width (list of int)
        column width in the Preset Manager panel.

    filedrop_column_width (list of int)
        column width in the File Drop panel.

    fcode_column_width (list of int)
        column width in the format code panel (ytdownloader).

    """
    VERSION = 6.7
    DEFAULT_OPTIONS = {"confversion": VERSION,
                       "outputdir": f"{os.path.expanduser('~')}",
                       "outputdir_asinput": False,
                       "filesuffix": "",
                       "ffmpeg_cmd": "",
                       "ffmpeg_islocal": False,
                       "ffmpeg_loglev": "-loglevel info",
                       "ffplay_cmd": "",
                       "ffplay_islocal": False,
                       "ffplay_loglev": "-loglevel error",
                       "ffprobe_cmd": "",
                       "ffprobe_islocal": False,
                       "warnexiting": True,
                       "icontheme": "Videomass-Colours",
                       "toolbarsize": 24,
                       "toolbarpos": 0,
                       "toolbartext": True,
                       "main_window_size": [850, 560],
                       "main_window_pos": [0, 0],
                       "main_ytdl_size": [850, 560],
                       "main_ytdl_pos": [0, 0],
                       "clearcache": True,
                       "clearlogfiles": False,
                       "move_file_to_trash": False,
                       "user_trashdir": None,
                       "locale_name": "Default",
                       "ydlp-outputdir": f"{os.path.expanduser('~')}",
                       "use-downloader": False,
                       "playlistsubfolder": True,
                       "ssl_certificate": False,
                       "add_metadata": True,
                       "embed_thumbnails": False,
                       "overwr_dl_files": False,
                       "include_ID_name": False,
                       "restrict_fname": False,
                       "subtitles_options": {"writesubtitles": False,
                                             "subtitleslangs": [],
                                             "writeautomaticsub": False,
                                             "embedsubtitle": False,
                                             "skip_download": False
                                             },
                       "external_downloader": None,
                       "external_downloader_args": None,
                       "prstmng_column_width": [250, 350, 200, 220],
                       "filedrop_column_width": [30, 200, 200, 200, 150, 200],
                       "fcode_column_width": [120, 60, 200, 80, 160,
                                              110, 80, 110, 100],
                       }

    def __init__(self, filename, makeportable=None):
        """
        Expects an existing `filename` on the file system paths
        suffixed by `.json`. If `makeportable` is `True`, some
        paths on the `DEFAULT_OPTIONS` class attribute will be
        set as relative paths.
        """
        self.filename = filename

        if makeportable:
            path = os.path.join(makeportable, "My_Files")
            outputdir = os.path.relpath(path)
            ConfigManager.DEFAULT_OPTIONS['outputdir'] = outputdir
            ConfigManager.DEFAULT_OPTIONS['ydlp-outputdir'] = outputdir

    def write_options(self, **options):
        """
        Writes options to configuration file. If **options is
        given, writes the new changes to filename, writes the
        DEFAULT_OPTIONS otherwise.
        """
        if options:
            set_options = options
        else:
            set_options = ConfigManager.DEFAULT_OPTIONS

        with open(self.filename, "w", encoding='utf-8') as settings_file:

            json.dump(set_options,
                      settings_file,
                      indent=4,
                      separators=(",", ": ")
                      )

    def read_options(self):
        """
        Reads options from the current configuration file.
        Returns: current options, `None` otherwise.
        Raise: json.JSONDecodeError
        """
        with open(self.filename, 'r', encoding='utf-8') as settings_file:
            try:
                options = json.load(settings_file)
            except json.JSONDecodeError:
                return None

        return options
