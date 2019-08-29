# -*- coding: UTF-8 -*-

#########################################################
# Name: opendir.py
# Porpose: open file browser in a specific location (platform independent)
# Compatibility: Python3 (Unix, Windows)
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.29 2019
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

def browse(OS, pathname):
    """
    open file browser in a specific location with
    file manager of the OS
    
    """
    if OS == 'Windows':
        os.startfile(pathname)
        
    elif OS == 'Darwin':
        p = subprocess.run(['open', pathname], capture_output=True)
        if p.stderr:
            return(p.stderr.decode())
        
    else:
        try:
            p = subprocess.Popen(['xdg-open', pathname])
        except OSError:
            print('error, think of something else to try\n'
                  'xdg-open *should* be supported by recent Gnome, KDE, Xfce\n'
                  )
            # er, think of something else to try
            # xdg-open *should* be supported by recent Gnome, KDE, Xfce
    return
#------------------------------------------------------#
