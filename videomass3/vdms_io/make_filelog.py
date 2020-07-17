# -*- coding: UTF-8 -*-
# File Name: make_filelog.py
# Porpose: generate log file
# Compatibility: Python3, Python2
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.30.2020 *PEP8 compatible*
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
    Before starting the process, a log file stored in the conventional
    path of the OS is created, see `vdms_sys/ctrl_run.py` .

    - logfile è il nome del pannello da cui è stato composto il comando
    """
    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir, mode=0o777)
        except OSError as error:
            return error

    current_date = time.strftime("%c")  # date/time
    path = os.path.join(logdir, logfile)

    with open(path, "w") as log:
        log.write("""[PYTHON] CURRENT DATE/TIME:
%s\n
-----------------------------------------
[VIDEOMASS] INFO FOR USERS:
-----------------------------------------
All FFmpeg and FFplay output messages are on stderr (excluse ffprobe),
and include both information messages and error messages.
Changing the logging level into setting dialog would also change the
behavior of the output on log messages.
-----------------------------------------
On Videomass default ffmpeg loglevel is fixed to 'warning';
ffplay to 'error' .
For more details, see videomass.conf or videomassWin32.conf
into configuration directory.
-----------------------------------------

[VIDEOMASS] COMMAND LINE:

""" % (current_date))
