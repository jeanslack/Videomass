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

def parsing_fileconf():
    """
    - called by bootstrap on_init -
    Make a parsing of the configuration file localized on 
    ``~/.videomass2/videomass2.conf`` and return values list of the current 
    program settings. If this file is not present or is damaged, it is marked 
    as corrupt.
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
#------------------------------------------------------------------------#

def system_check():
    """
    - called by bootstrap on_init -
    Assignment of the appropriate paths for sharing the configuration folder.
    This function checks the integrity of the Videomass2 configuration folder 
    located in each user's home directory. If this folder does not exist in 
    the user space it will be recovered from the source or installation folder 
    (this depends if portable mode or installated mode) and will be saved in 
    the user's home.  
    """
    copyerr = False
    existfileconf = True # il file conf esiste (True) o non esite (False)
    
    # What is the OS ??
    #OS = [x for x in ['Darwin','Linux','Windows'] if platform.system() in x ][0]
    OS = platform.system()

    if os.path.exists('%s/vdms_MAIN' % (PWD)) or OS == ('Darwin'):
        #Paths for MacOSX or Linux without installation (portable)
        path_srcShare = '%s/share' % PWD
        installation = 'portable'
        
    elif OS == ('Linux'): #Path for Linux (standard installation mode)
        path_srcShare = '/usr/share/videomass2/config'
        installation = 'standard linux'
        
    else: # it should be Windows OS
        path_srcShare = '%s/share' % PWD
        installation = 'portable'

    #### check videomass.conf and config. folder
    if os.path.exists('%s/.videomass2' % DIRNAME):#if exist folder ~/.videomass
        if os.path.isfile('%s/.videomass2/videomass2.conf' % DIRNAME):
            fileconf = parsing_fileconf() # fileconf data
            if fileconf == 'corrupted':
                print 'videomass2.conf is corrupted! try to restore..'
                existfileconf = False
            if float(fileconf[0]) < 1.2:
                existfileconf = False
        else:
            existfileconf = False
        
        if not existfileconf:
            try:
                if OS == ('Linux') or OS == ('Darwin'):
                    shutil.copyfile('%s/videomass2.conf' % path_srcShare, 
                                    '%s/.videomass2/videomass2.conf' % DIRNAME)
                elif OS == ('Windows'):
                    shutil.copyfile('%s/videomassWin32.conf' % path_srcShare, 
                                    '%s/.videomass2/videomass2.conf' % DIRNAME)
                fileconf = parsing_fileconf() # fileconf data, reread the file
            except IOError:
                copyerr = True
                fileconf = 'corrupted'
    else:
        try:
            shutil.copytree(path_srcShare,'%s/.videomass2' % DIRNAME)
            if OS == ('Windows'):
                os.remove("%s/.videomass2/videomass2.conf" % (DIRNAME))
                os.rename("%s/.videomass2/videomassWin32.conf" % (DIRNAME),
                          "%s/.videomass2/videomass2.conf" % (DIRNAME))
            fileconf = parsing_fileconf() # fileconf data, reread the file
        except OSError:
            copyerr = True
            fileconf = 'corrupted'
        except IOError:
            copyerr = True
            fileconf = 'corrupted'

    return (OS, path_srcShare, copyerr, installation, fileconf)

#------------------------------------------------------------------------#
