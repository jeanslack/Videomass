# -*- coding: UTF-8 -*-

#########################################################
# Name: opendir.py
# Porpose: open file browser in a specific location (platform independent)
# Compatibility: Python2 (Unix, Windows)
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
import os

def browse(OS, pathname, mod):
    """
    open file browser in a specific location with
    file manager of the OS
    
    """
    if mod != 'dirconf':
        path = os.path.join(pathname, "log") # normalize os pathname
    
    else:
        path = pathname
        
    #------------------------ OS:
    if OS == 'Windows':
        try:
            os.startfile(path)
        except WindowsError as e:
            return(str(e))
        
    elif OS == 'Darwin':
        try:
            p = subprocess.check_output(['open', pathname], 
                                        stderr=subprocess.STDOUT,
                                        )
        except subprocess.CalledProcessError as e:
            return(e.output.decode())
    else:
        try:
            p = subprocess.check_output(['xdg-open', path],
                                    stderr=subprocess.STDOUT,
                                    )
        except subprocess.CalledProcessError as e:
            return(e.output)
        
    return
#------------------------------------------------------#
