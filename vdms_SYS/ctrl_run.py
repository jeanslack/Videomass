# -*- coding: UTF-8 -*-

#########################################################
# Name: ctrl_run.py
# Porpose: Used for program boot
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

# Rev (01) 17/01/2015
# Rev (02) 17/july/2018
# Rev (03) 6 Sept 2018
#########################################################

import sys
import os
import shutil
import platform

PWD = os.getcwd() # work current directory (where is Videomsass?)
DIRNAME = os.path.expanduser('~') # /home/user (current user directory)

#------------------------------------------------------------------------#
def system_check():
    """
    -This function check existing of the '/home/user/.videomass2' configuration 
    folder with videomass2.conf and vdms files content.
    It is called from videomass2 bootstrap. If these files do not 
    exist or are deleted in, this function restore them from assign paths
    established below. 
    -Check which oprative system is used to make the necessary adjustments
    On MacOSX is also created the directory that contains 
    the ffmpeg presets if not exist. 
    -Assign the paths of icons and html user manual.
    NOTE: Windows implementations: 
           - for double pass windows has not /dev/null (use NUL instead)
             https://trac.ffmpeg.org/wiki/Encode/H.264#twopass
           - Use ffmpeg.exe command on Windows
    """
    copyerr = False
    
    # What is the OS ??
    #OS = [x for x in ['Darwin','Linux','Windows'] if platform.system() in x ][0]
    OS = platform.system()
    
    """
    Assignment path where there is av_profile.xml and videomass2.conf
    This depends if portable mode or installable mode:
    """
    if os.path.exists('%s/vdms_MAIN' % (PWD)) or OS == ('Darwin'):
        """
        Paths for MacOSX or Linux without installation (portable)
        """
        path_srcShare = '%s/share' % PWD
        installation = 'portable'
        
    elif OS == ('Linux'):
        """
        Path for Linux (Videomass2 standard installation mode)
        """
        path_srcShare = '/usr/share/videomass2/config'
        installation = 'standard linux'
        
    else: # it should be Windows OS
        """
        This paths are for OS == Windows
        """
        path_srcShare = '%s/share' % PWD
        installation = 'portable'

    #### check videomass.conf and config directory
    if os.path.exists('%s/.videomass2' % DIRNAME):#if exist folder ~/.videomass
        if os.path.isfile('%s/.videomass2/videomass2.conf' % DIRNAME):
            pass
        else:
            if OS == ('Linux') or OS == ('Darwin'):
                shutil.copyfile('%s/videomass2.conf' % path_srcShare, 
                                '%s/.videomass2/videomass2.conf' % DIRNAME)
            elif OS == ('Windows'):
                shutil.copyfile('%s/videomassWin32.conf' % path_srcShare, 
                                '%s/.videomass2/videomass2.conf' % DIRNAME)
    else:
        try:
            shutil.copytree(path_srcShare, '%s/.videomass2' % DIRNAME)
            if OS == ('Windows'):
                os.remove("%s/.videomass2/videomass2.conf" % (DIRNAME))
                os.rename("%s/.videomass2/videomassWin32.conf" % (DIRNAME),
                          "%s/.videomass2/videomass2.conf" % (DIRNAME))
        except OSError:
            copyerr = True

    return (OS, path_srcShare, copyerr, installation)

#------------------------------------------------------------------------#
def parsing_fileconf():
    """
    This function is called by videomass on_init. It make a parsing of the
    configuration file localized on '~/.videomass2/videomass2.conf' 
    and return values list of the current program settings.
    """
    filename = '%s/.videomass2/videomass2.conf' % (DIRNAME)

    with open (filename, 'r') as f:
        fconf = f.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    curr_conf = [x for x in lst if x]# list without empties values
    if not curr_conf:
        return 'corrupted'
    else:
        return curr_conf
