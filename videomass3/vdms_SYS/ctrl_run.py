# -*- coding: UTF-8 -*-

#########################################################
# Name: ctrl_run.py
# Porpose: Program boot data
# Compatibility: Python3
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (01) December 28 2018
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

import sys
import os
import shutil
import platform

PWD = os.getcwd() # work current directory (where is Videomsass?)
DIRNAME = os.path.expanduser('~') # /home/user (current user directory)

#------------------------------------------------------------------------#

def parsing_fileconf():
    """
    Make a parsing of the configuration file localized on 
    ``~/.videomass/videomass.conf`` and return object list 
    of the current program settings.
    """
    filename = '%s/.videomass/videomass.conf' % (DIRNAME)

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
    Setting and assigning shared data paths and checking 
    the configuration folder  
    """
    copyerr = False
    existfileconf = True # il file conf esiste (True) o non esiste (False)
    
    # What is the OS ??
    OS = platform.system()

    if os.path.isdir('%s/art' % PWD):
        #launch without installing on any OS or .exe and .app
        localepath = 'locale'
        path_srcShare = '%s/share' % PWD
        IS_LOCAL = True
        
    else: # Path system installation (usr, usr/local, ~/.local, \python27\)
        if OS == 'Windows':
            #Installed with 'pip install videomass' command
            pythonpath = os.path.dirname(sys.executable)
            localepath = pythonpath + '\\share\\locale'
            path_srcShare = pythonpath + '\\share\\videomass\\config'
            IS_LOCAL = False
            
        else:
            binarypath = shutil.which('videomass')
            if binarypath == '/usr/local/bin/videomass':
                #usually Linux,MacOs,Unix
                localepath = '/usr/local/share/locale'
                path_srcShare = '/usr/local/share/videomass/config'
                IS_LOCAL = False
            elif binarypath == '/usr/bin/videomass':
                #usually Linux
                localepath = '/usr/share/locale'
                path_srcShare = '/usr/share/videomass/config'
                IS_LOCAL = False
            else:
                #installed with 'pip install --user videomass' command
                import site
                userbase = site.getuserbase()
                localepath = userbase + '/share/locale'
                path_srcShare = userbase + '/share/videomass/config'
                IS_LOCAL = False

    #### check videomass.conf and config. folder
    if os.path.exists('%s/.videomass' % DIRNAME):#if exist folder ~/.videomass
        if os.path.isfile('%s/.videomass/videomass.conf' % DIRNAME):
            fileconf = parsing_fileconf() # fileconf data
            if fileconf == 'corrupted':
                print ('videomass.conf is corrupted! try to restore..')
                existfileconf = False
            if float(fileconf[0]) != 1.3:
                existfileconf = False
        else:
            existfileconf = False
        
        if not existfileconf:
            try:
                if OS == ('Linux') or OS == ('Darwin'):
                    shutil.copyfile('%s/videomass.conf' % path_srcShare, 
                                    '%s/.videomass/videomass.conf' % DIRNAME)
                elif OS == ('Windows'):
                    shutil.copyfile('%s/videomassWin32.conf' % path_srcShare, 
                                    '%s/.videomass/videomass.conf' % DIRNAME)
                fileconf = parsing_fileconf() # fileconf data, reread the file
            except IOError:
                copyerr = True
                fileconf = 'corrupted'
    else:
        try:
            shutil.copytree(path_srcShare,'%s/.videomass' % DIRNAME)
            if OS == ('Windows'):
                os.remove("%s/.videomass/videomass.conf" % (DIRNAME))
                os.rename("%s/.videomass/videomassWin32.conf" % (DIRNAME),
                          "%s/.videomass/videomass.conf" % (DIRNAME))
            fileconf = parsing_fileconf() # fileconf data, reread the file
        except OSError:
            copyerr = True
            fileconf = 'corrupted'
        except IOError:
            copyerr = True
            fileconf = 'corrupted'

    return (OS, path_srcShare, copyerr, IS_LOCAL, fileconf, localepath)

#------------------------------------------------------------------------#
