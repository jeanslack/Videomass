# -*- coding: UTF-8 -*-

#########################################################
# Name: ctrl_run.py
# Porpose: Program boot data
# Compatibility: Python3
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec. 28 2018, Aug.28 2019
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

# Set default variables
WORKdir = os.getcwd() # work current directory (where is Videomsass?)
USERName = os.path.expanduser('~') # /home/user (current user directory)
OS = platform.system()# What is the OS ??

if OS == 'Windows':
    bpath = "\\AppData\\Roaming\\videomass\\videomassWin32.conf"
    FILEconf = os.path.join(USERName + bpath)
    DIRconf = os.path.join(USERName + "\\AppData\\Roaming\\videomass")
    
else:
    bpath = "/.config/videomass/videomass.conf"
    FILEconf = os.path.join(USERName + bpath)
    DIRconf = os.path.join(USERName + "/.config/videomass")

#------------------------------------------------------------------------#

def parsing_fileconf():
    """
    Make a parsing of the configuration file and return
    object list with the current program settings data.
    
    """
    with open (FILEconf, 'r') as f:
        fconf = f.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    dataconf = [x for x in lst if x]# list without empties values
    if not dataconf:
        return 'corrupted'
    else:
        return dataconf
#------------------------------------------------------------------------#

def system_check():
    """
    assigning shared data paths and 
    checking the configuration folder  
    """
    copyerr = False
    existfileconf = True # il file conf esiste (True) o non esiste (False)

    if os.path.isdir('%s/art' % WORKdir):
        #launch without installing on any OS or .exe and .app
        localepath = 'locale'
        SRCpath = '%s/share' % WORKdir
        IS_LOCAL = True
        
    else: # Path system installation (usr, usr/local, ~/.local, \python27\)
        if OS == 'Windows':
            #Installed with 'pip install videomass' command
            pythonpath = os.path.USERName(sys.executable)
            localepath = pythonpath + '\\share\\locale'
            SRCpath = pythonpath + '\\share\\videomass\\config'
            IS_LOCAL = False
            
        else:
            binarypath = shutil.which('videomass')
            if binarypath == '/usr/local/bin/videomass':
                #usually Linux,MacOs,Unix
                localepath = '/usr/local/share/locale'
                SRCpath = '/usr/local/share/videomass/config'
                IS_LOCAL = False
            elif binarypath == '/usr/bin/videomass':
                #usually Linux
                localepath = '/usr/share/locale'
                SRCpath = '/usr/share/videomass/config'
                IS_LOCAL = False
            else:
                #installed with 'pip install --user videomass' command
                import site
                userbase = site.getuserbase()
                localepath = userbase + '/share/locale'
                SRCpath = userbase + '/share/videomass/config'
                IS_LOCAL = False

    #### check videomass.conf and config. folder
    if os.path.exists(os.path.dirname(FILEconf)):#if exist folder ~/.videomass
        if os.path.isfile(FILEconf):
            DATAconf = parsing_fileconf() # fileconf data
            if DATAconf == 'corrupted':
                print ("The file configuration is corrupted! try to restore..")
                existfileconf = False
            if float(DATAconf[0]) != 1.3:
                existfileconf = False
        else:
            existfileconf = False
        
        if not existfileconf:
            try:
                if OS == ('Linux') or OS == ('Darwin'):
                    shutil.copyfile('%s/videomass.conf' % SRCpath, 
                                    FILEconf)
                elif OS == ('Windows'):
                    shutil.copyfile('%s/videomassWin32.conf' % SRCpath, 
                                    FILEconf)
                DATAconf = parsing_fileconf() # DATAconf data, reread the file
            except IOError:
                copyerr = True
                DATAconf = 'corrupted'
    else:
        try:
            shutil.copytree(SRCpath, DIRconf)
            DATAconf = parsing_fileconf() # DATAconf data, reread the file
        except OSError:
            copyerr = True
            DATAconf = 'corrupted'
        except IOError:
            copyerr = True
            DATAconf = 'corrupted'

    return (OS, SRCpath, 
            copyerr, IS_LOCAL, 
            DATAconf, localepath,
            FILEconf, WORKdir, DIRconf)

#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
