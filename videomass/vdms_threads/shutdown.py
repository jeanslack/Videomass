# -*- coding: UTF-8 -*-
"""
Name: shutdown.py
Purpose: Execute shutdown system using subprocess
Compatibility: Python >= 3.11 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.29.2026
Code checker: flake8, pylint, ruff

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

import shutil
import subprocess

import wx

from videomass.vdms_io.make_filelog import make_log_template, tolog


def shutdown_system(password=None):
    """
    Turn off the system using subprocess
    """
    get = wx.GetApp()
    appdata = get.appset
    ostype = appdata["ostype"]
    logfile = make_log_template("Shutdown.log", appdata["logdir"], mode="w")
    creationflags = subprocess.CREATE_NO_WINDOW if ostype == "Windows" else 0

    if ostype == "Linux":
        if password:
            password = f"{password}\n"
            cmd = ["sudo", "-S", "shutdown", "-h", "now"]
        else:
            # Dynamic detection of systemctl for modern compatibility
            # that does not require root access
            if shutil.which("systemctl"):
                cmd = ["systemctl", "poweroff"]
            else:
                cmd = ["shutdown", "-h", "now"]

    elif ostype == "Darwin":
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-h", "now"]

    elif ostype == "Windows":
        cmd = ["shutdown", "/s", "/t", "1"]

    elif ostype in ["OpenBSD", "FreeBSD"]:
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-p", "now"]

    else:
        return "Error: unsupported platform"

    tolog(
        f"INFO: VIDEOMASS COMMAND: {' '.join(cmd)}",
        logfile,
        sep=True,
        wdate=True,
    )
    try:
        with subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            creationflags=creationflags,
        ) as proc:
            # Communicates input in an isolated manner and
            # safely extracts stdout and stderr
            stdout_data, stderr_data = proc.communicate(input=password)

            # Managing the wait timeout to prevent parent thread deadlocks
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

            if stderr_data:
                tolog(f"STDERR: {stderr_data}", logfile)
            if stdout_data:
                tolog(f"STDOUT: {stdout_data}", logfile)

            # Returns success based on the actual returncode of the
            # operating process, without interpreting text strings
            return proc.returncode == 0

    except (OSError, FileNotFoundError) as err:
        tolog(f"VIDEOMASS: ERROR: {err}", logfile)
        return err

    return None
