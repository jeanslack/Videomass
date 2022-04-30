# -*- coding: UTF-8 -*-
"""
Name: settings_manager.py
Porpose: Read and write the configuration file
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.26.2022
Code checker: flake8, pylint .

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
    read and write aspects.

    Usage:

    write a new conf.json :
        >>> from settings_manager import ConfigManager
        >>> confmng = ConfigManager('fileconfpath.json')
        >>> confmng.write_options()

    read the current fileconf.json :
        >>> settings = confmng.read_options()

    example of modify data into current file conf.json:
        >>> settings['outputfile'] = '/home/user/MyVideos'
        >>> confmng.write_options(**settings)
    ------------------------------------------------------

    Options description:

    confversion (float):
        current version of this configuration file

    outputfile (str):
        output path used by ffmpeg for file saving

    outputfile_samedir (bool):
        if True save any ffmpeg files to same folder as source

    filesuffix (str):
        An optional suffix to assign to output files

    outputdownload (str):
        output path used by the downloader for file saving

    ffmpeg_cmd, ffplay_cmd, ffprobe_cmd, (str):
        Absolute or relative path name of the executable.
        if empty string ("") starts the wizard.

    ffmpeg_islocal, ffplay_islocal, ffprobe_islocal, (bool):
        With True the user enables the executable locally

    ffmpegloglev (str):
        -loglevel one of `error`, `warning`, `info`, `verbose`, `debug`

    ffthreads (str):
        Set the number of threads (from 0 to 32)

    ffplayloglev (str):
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
        True, enables text alongside toolbar buttons. Default is False.

    panel_size (list):
        [Height, Width] current window dimension.

    clearcache (bool):
        with True deleting file cache on exit the app,
        default is False

    clearlogfiles (bool):
        with True deleting log file content on exit the app,
        default is False.

    downloader (bool, str):
        sets the downloader to use when application startup.
        one of `disabled`,` youtube_dl`, `yt_dlp` or False
        Where `disabled` means not load anything, `youtube_dl`
        means load/use youtube-dl on sturtup, `yt_dlp` means load/use
        yt_dl on sturtup, `false` means *not set at all* and the
        wizard dialog will be displayed.

    playlistsubfolder (bool):
        Auto-create subfolders when download the playlists,
        default value is True.

    move_file_to_trash (bool):
        if True, move input files to videomass trash folder or inside
        some other dir.
        default value is False

    trashfolder (str):
        An absolute or relative dirname of some trash folder.

    """
    VERSION = 4.2
    DEFAULT_OPTIONS = {
        "confversion": VERSION,
        "outputfile": f"{os.path.expanduser('~')}",
        "outputfile_samedir": False,
        "filesuffix": "",
        "outputdownload": f"{os.path.expanduser('~')}",
        "ffmpeg_cmd": "",
        "ffmpeg_islocal": False,
        "ffmpegloglev": "-loglevel warning",
        "ffthreads": "-threads 4",
        "ffplay_cmd": "",
        "ffplay_islocal": False,
        "ffplayloglev": "-loglevel error",
        "ffprobe_cmd": "",
        "ffprobe_islocal": False,
        "warnexiting": True,
        "icontheme": "Videomass-Colours",
        "toolbarsize": 24,
        "toolbarpos": 0,
        "toolbartext": False,
        "panel_size": [980, 640],
        "clearcache": False,
        "clearlogfiles": False,
        "downloader": False,
        "playlistsubfolder": True,
        "move_file_to_trash": False,
        "trashfolder": ""
        }

    def __init__(self, filename, relativepath=False):
        """
        Accepts an existing `filename` on the file system paths
        suffixed by `.json`. If `relativepath` is `True`, some
        paths on the `DEFAULT_OPTIONS` class attribute will be
        set as relative paths.
        """
        self.filename = filename
        if relativepath is True:
            appdir = os.getcwd()
            outputdir = os.path.relpath(os.path.join(appdir, 'My_Files'))
            ConfigManager.DEFAULT_OPTIONS['outputfile'] = outputdir
            ConfigManager.DEFAULT_OPTIONS['outputdownload'] = outputdir

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
