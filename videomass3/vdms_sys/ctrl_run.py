# -*- coding: UTF-8 -*-

#########################################################
# Name: ctrl_run.py
# Porpose: Program startup data; get system data on startup
# Compatibility: Python3
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

import sys
import os
import shutil
import platform

# Set default variables
WORKdir = os.getcwd()  # work current directory (where is Videomsass?)
USERName = os.path.expanduser('~')  # /home/user (current user directory)
OS = platform.system()  # What is the OS ??

# Establish the conventional paths on the different OS where
# the videomass directories will be stored:
if OS == 'Windows':
    bpath = "\\AppData\\Roaming\\videomass\\videomassWin32.conf"
    FILEconf = os.path.join(USERName + bpath)
    DIRconf = os.path.join(USERName + "\\AppData\\Roaming\\videomass")
    LOGdir = os.path.join(DIRconf, 'log') # logs
    CACHEdir = os.path.join(DIRconf, 'cache')  # updates executable

elif OS == "Darwin":
    bpath = "Library/Application Support/videomass/videomass.conf"
    FILEconf = os.path.join(USERName, bpath)
    DIRconf = os.path.join(USERName, os.path.dirname(bpath))
    LOGdir = os.path.join(USERName, "Library/Logs/videomass")  # logs
    CACHEdir = os.path.join(USERName, "Library/Caches/videomass")  # upds

else:  # Linux, FreeBsd, etc.
    bpath = ".config/videomass/videomass.conf"
    FILEconf = os.path.join(USERName, bpath)
    DIRconf = os.path.join(USERName, ".config/videomass")
    LOGdir = os.path.join(USERName, ".local/share/videomass/log")  # logs
    CACHEdir = os.path.join(USERName, ".cache/videomass")  # updates
# ------------------------------------------------------------------------#


def parsing_fileconf():
    """
    Make a parsing of the configuration file and return
    object list with the current program settings data.
    """
    with open(FILEconf, 'r') as f:
        fconf = f.readlines()
    lst = [line.strip() for line in fconf if not line.startswith('#')]
    dataconf = [x for x in lst if x]  # list without empties values
    if not dataconf:
        return
    else:
        return dataconf
# ------------------------------------------------------------------------#


def system_check():
    """
    assigning shared data paths and
    checking the configuration folder
    """
    # ----------------------------------------------------------- #
    # ### Set resources location #
    # ------------------------------------------------------------#
    if os.path.isdir('%s/art' % WORKdir):
        # local launch on any O.S. (even if installed also as .exe and .app)
        localepath = 'locale'
        SRCpath = '%s/share' % WORKdir
        IS_LOCAL = True

    else:  # Path system installation (usr, usr/local, ~/.local)
        if OS == 'Windows':
            # Installed with 'pip install videomass' command
            dirname = os.path.dirname(sys.executable)
            pythonpath = os.path.join(dirname, 'Script', 'videomass')
            localepath =  os.path.join(dirname, 'share', 'locale')
            SRCpath = os.path.join(dirname, 'share', 'videomass', 'config')
            IS_LOCAL = False
        else:
            binarypath = shutil.which('videomass')
            if binarypath == '/usr/local/bin/videomass':
                # usually Linux,MacOs,Unix
                localepath = '/usr/local/share/locale'
                SRCpath = '/usr/local/share/videomass/config'
                IS_LOCAL = False
            elif binarypath == '/usr/bin/videomass':
                # usually Linux
                localepath = '/usr/share/locale'
                SRCpath = '/usr/share/videomass/config'
                IS_LOCAL = False
            else:
                # installed with 'pip install --user videomass' command
                import site
                userbase = site.getuserbase()
                localepath = userbase + '/share/locale'
                SRCpath = userbase + '/share/videomass/config'
                IS_LOCAL = False

    # --------------------------------------------#
    # ### check videomass configuration folder #
    # --------------------------------------------#
    copyerr = False
    existfileconf = True  # True > found, False > not found

    if os.path.exists(DIRconf):  # if exist conf. folder
        if os.path.isfile(FILEconf):
            DATAconf = parsing_fileconf()  # fileconf data
            if not DATAconf:
                print("The file configuration is damaged! try to restore..")
                existfileconf = False
            if float(DATAconf[0]) != 2.0:
                existfileconf = False
        else:
            existfileconf = False

        if not existfileconf:
            try:
                if OS == ('Windows'):
                    shutil.copyfile('%s/videomassWin32.conf' % SRCpath,
                                    FILEconf)
                else:
                    shutil.copyfile('%s/videomass.conf' % SRCpath, FILEconf)
                DATAconf = parsing_fileconf()  # read again file conf
            except IOError as e:
                copyerr = e
                DATAconf = None
        if not os.path.exists(os.path.join(DIRconf, "presets")):
            try:
                shutil.copytree(os.path.join(SRCpath, "presets"),
                                os.path.join(DIRconf, "presets"))
            except (OSError, IOError) as e:
                copyerr = e
                DATAconf = None
    else:
        try:
            shutil.copytree(SRCpath, DIRconf)
            DATAconf = parsing_fileconf()  # read again file conf
        except (OSError, IOError) as e:
            copyerr = e
            DATAconf = None

    return (OS,
            SRCpath,
            copyerr,
            IS_LOCAL,
            DATAconf,
            localepath,
            FILEconf,
            WORKdir,
            DIRconf,
            LOGdir,
            CACHEdir,
            )
