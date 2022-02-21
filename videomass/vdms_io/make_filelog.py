# -*- coding: UTF-8 -*-
"""
File Name: make_filelog.py
Porpose: log file generator
Compatibility: Python3, Python2
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.20.2022
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

import time
import os


def logwrite(cmd, stderr, logfile):
    """
    This function writes status messages
    to a given `logfile` during a process.
    """
    if stderr:
        apnd = f"...{stderr}\n\n"
    else:
        apnd = f"{cmd}\n\n"

    with open(logfile, "a", encoding='utf8') as log:
        log.write(apnd)


def make_log_template(logname, logdir):
    """
    Most log files are initialized from a template
    before starting a process and writing status
    messages to a given log file.

    - logname,  example: `mylog.log`
    - logdir, log files location

    Returns the absolute/relative pathname of the log
    """
    current_date = time.strftime("%c")  # date/time
    logfile = os.path.join(logdir, logname)

    with open(logfile, "a", encoding='utf8') as log:
        log.write(f"""
==============================================================================
[DATE]:
{current_date}

[LOCATION]:
{logfile}

[VIDEOMASS]:
""")

    return logfile
