# -*- coding: UTF-8 -*-

#########################################################
# File Name: make_filelog.py
# Porpose: Module to generate log files durin jobs start
# Compatibility: Python3, Python2
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (10) December 28 2018
#########################################################

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

#########################################################

import time
import os

DIRNAME = os.path.expanduser('~') # /home/user

def write_log(logname):
    """
    During the process, it write log about what the program does,
    command output and including errors.
    The log is stored in ~/user/.videomass2 by default.

    - logname è il nome del pannello da cui è stato composto il comando
    """
    current_date =  time.strftime("%c") # date/time

    with open("%s/.videomass2/%s" % (DIRNAME, logname),"w") as log:
        log.write("""[PYTHON] CURRENT DATE/TIME:
%s\n
-----------------------------------------
[VIDEOMASS] INFO FOR USERS: 
-----------------------------------------
If you want to save the log file in other places of
your drives, set it by videomass preferences dialog.
-----------------------------------------
Videomass2 default ffmpeg loglevel fixed to 'error'.
See ~/.videomass2/videomass2.conf for more details.
-----------------------------------------

[VIDEOMASS] COMMAND LINE:

""" % (current_date))
