# -*- coding: UTF-8 -*-
# File Name: make_filelog.py
# Porpose: log file generator
# Compatibility: Python3, Python2
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: October.27.2020 *PEP8 compatible*
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

import time
import os


def write_log(logfile, logdir):
    """
    Before starting a process, a log file is created from this
    template and then written later by the process.
    see also `vdms_sys/ctrl_run.py` .

    - logfile,  log name from which the command was generated
    - logdir, log files location
    """
    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir, mode=0o777)
        except OSError as error:
            return error

    current_date = time.strftime("%c")  # date/time
    path = os.path.join(logdir, logfile)

    with open(path, "a", encoding='utf8') as log:
        log.write("""
[DATE]:
%s

[LOCATION]:
%s

[VIDEOMASS]:
""" % (current_date, path))
