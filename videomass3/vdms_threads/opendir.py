# -*- coding: UTF-8 -*-
# Name: opendir.py
# Porpose: open file browser on given pathname
# Compatibility: Python3 (Unix, Windows)
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import subprocess
import os


def browse(OS, pathname):
    """
    open file browser in a specific location (OS independent)

    """
    status = 'Unrecognized error'
    if OS == 'Windows':
        #cmd = ' '.join(['cmd', '/c', 'start', pathname])
        cmd = r'cmd /c start "%s"' % pathname
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    elif OS == 'Darwin':
        cmd = ['open', pathname]
        info = None

    else:  # xdg-open *should* be supported by recent Gnome, KDE, Xfce
        cmd = ['xdg-open', pathname]
        info = None
    try:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True,  # mod text
                             startupinfo=info,
                             )
        out = p.communicate()

    except (OSError, FileNotFoundError) as oserr:  # exec. do not exist
        status = '%s' % oserr
    else:
        if p.returncode:  # if returncode == 1
            status = out[0]
        else:
            status = None
    return status

    """
    NOTE The following code work, but on MS-Windows it show a short of
         Dos-window
    -----------------

    try:
        p = subprocess.run(cmd)
        if p.stderr:
            return(p.stderr.decode())
            '''
            if not *capture_output=True* on subprocess instance
            use .decode() here.
            '''
    except FileNotFoundError as err:
        return('%s' % (err))
    """
