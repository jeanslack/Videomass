# -*- coding: UTF-8 -*-
"""
Name: shutdown.py
Porpose: Execute shutdown system using subprocess
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.23.2024
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
import subprocess
import wx
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import make_log_template, tolog


def shutdown_system(password=None):
    """
    Turn off the system using subprocess
    """
    get = wx.GetApp()
    appdata = get.appset
    ostype = appdata['ostype']
    logfile = make_log_template("Shutdown.log", appdata['logdir'], mode="w")

    if ostype == 'Linux':
        if password:
            password = f"{password}\n"
            cmd = ["sudo", "-S", "shutdown", "-h", "now"]
        else:  # using root
            cmd = ["/sbin/shutdown", "-h", "now"]

    elif ostype == 'Darwin':
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-h", "now"]

    elif ostype == 'Windows':
        cmd = ["shutdown", "/s", "/t", "1"]

    elif ostype in ['OpenBSD', 'FreeBSD']:
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-p", "now"]

    else:
        return 'Error: unsupported platform'

    tolog(f'INFO: VIDEOMASS COMMAND: {" ".join(cmd)}',
          logfile, sep=True, wdate=True
          )

    try:
        with Popen(cmd,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True,
                   encoding='utf-8',
                   ) as proc:

            output = proc.communicate(password)[1]
            proc.wait()
            tolog(output, logfile)
            return not output or output == "Password:"

    except (OSError, FileNotFoundError) as err:
        tolog(f'VIDEOMASS: ERROR: {err}', logfile)
        return err

    return None
