# -*- coding: UTF-8 -*-

#########################################################
# Name: configurator.py
# Porpose: Set configuration and appearance on startup
# Compatibility: Python3
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.15.2020 *PEP8 compatible*
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
import os
import sys
import shutil
import platform

PATH = os.path.realpath(os.path.abspath(__file__))
WORKdir = os.path.dirname(os.path.dirname(os.path.dirname(PATH)))  # where is?
USERName = os.path.expanduser('~')  # /home/user (current user directory)
OS = platform.system()  # What is the OS ??

# Establish the conventional paths on the different OS where
# the videomass directories will be stored:
if OS == 'Windows':
    bpath = "\\AppData\\Roaming\\videomass\\videomassWin32.conf"
    FILEconf = os.path.join(USERName + bpath)
    DIRconf = os.path.join(USERName + "\\AppData\\Roaming\\videomass")
    LOGdir = os.path.join(DIRconf, 'log')  # logs
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


class Data_Source(object):
    """
    This class determines the paths to use to set icons
    on the graphic appearance of the Videomass program.
    """
    def __init__(self):
        """
        The paths where the icon sets are located depend where
        the program is run and on which operating system.
        Each icons set is defined by the name of the folder that
        contains it.
        """
        if os.path.isdir('%s/art' % WORKdir):
            # local launch on any O.S. (even for .exe and .app)
            self.localepath = 'locale'
            self.SRCpath = '%s/share' % WORKdir
            # ----- for icons
            self.icodir = '%s/art/icons' % WORKdir  # work current directory
            self.videomass_icon = "%s/videomass.png" % self.icodir
            self.wizard_icon = "%s/videomass_wizard.png" % self.icodir

        else: # Path system installation (usr, usr/local, ~/.local)
            binarypath = shutil.which('videomass')

            if OS == 'Windows':  # Installed with 'pip install videomass'
                dirname = os.path.dirname(sys.executable)
                pythonpath = os.path.join(dirname, 'Script', 'videomass')
                self.localepath = os.path.join(dirname, 'share', 'locale')
                self.SRCpath = os.path.join(dirname, 'share',
                                            'videomass', 'config')
                # --- for icons
                self.icodir = dirname + '\\share\\videomass\\icons'
                self.videomass_icon = self.icodir + "\\videomass.png"
                self.wizard_icon = self.icodir + "\\videomass_wizard.png"
            else:
                if binarypath == '/usr/local/bin/videomass':
                    # Installed with super user 'pip install videomass'
                    self.localepath = '/usr/local/share/locale'
                    self.SRCpath = '/usr/local/share/videomass/config'
                    # usually Linux,MacOs,Unix
                    self.icodir = '/usr/local/share/videomass/icons'
                    share = '/usr/local/share/pixmaps'
                    self.videomass_icon = share + '/videomass.png'
                    self.wizard_icon = self.icodir + '/videomass_wizard.png'
                elif binarypath == '/usr/bin/videomass':
                    # usually Linux
                    self.localepath = '/usr/share/locale'
                    self.SRCpath = '/usr/share/videomass/config'
                    self.icodir = '/usr/share/videomass/icons'
                    share = '/usr/share/pixmaps'
                    self.videomass_icon = share + "/videomass.png"
                    self.wizard_icon = self.icodir + "/videomass_wizard.png"
                else:
                    # installed with 'pip install --user videomass' command
                    userbase = os.path.dirname(os.path.dirname(binarypath))
                    self.localepath = os.path.join(userbase + '/share/locale')
                    self.SRCpath = os.path.join(userbase +
                                           '/share/videomass/config')
                    self.icodir = os.path.join(userbase +
                                               '/share/videomass/icons')
                    pixmaps = '/share/pixmaps/videomass.png'
                    self.videomass_icon = os.path.join(userbase + pixmaps)
                    self.wizard_icon = os.path.join(self.icodir +
                                                    "/videomass_wizard.png")
    # --------------------------------------------------------------------

    def get_fileconf(self):
        """
        check videomass configuration folder
        """
        copyerr = False
        existfileconf = True  # True > found, False > not found

        if os.path.exists(DIRconf):  # if exist conf. folder
            if os.path.isfile(FILEconf):
                DATAconf = parsing_fileconf()  # fileconf data
                if not DATAconf:
                    existfileconf = False
                if float(DATAconf[0]) != 2.0:
                    existfileconf = False
            else:
                existfileconf = False

            if not existfileconf:
                try:
                    if OS == ('Windows'):
                        shutil.copyfile('%s/videomassWin32.conf' %
                                        self.SRCpath, FILEconf)
                    else:
                        shutil.copyfile('%s/videomass.conf' % self.SRCpath,
                                        FILEconf)
                    DATAconf = parsing_fileconf()  # read again file conf
                except IOError as e:
                    copyerr = e
                    DATAconf = None
            if not os.path.exists(os.path.join(DIRconf, "presets")):
                try:
                    shutil.copytree(os.path.join(self.SRCpath, "presets"),
                                    os.path.join(DIRconf, "presets"))
                except (OSError, IOError) as e:
                    copyerr = e
                    DATAconf = None
        else:
            try:
                shutil.copytree(self.SRCpath, DIRconf)
                DATAconf = parsing_fileconf()  # read again file conf
            except (OSError, IOError) as e:
                copyerr = e
                DATAconf = None

        return (OS,
                self.SRCpath,
                copyerr,
                None,
                DATAconf,
                self.localepath,
                FILEconf,
                WORKdir,
                DIRconf,
                LOGdir,
                CACHEdir,
                )
    # --------------------------------------------------------------------

    def icons_set(self, iconset):
        """
        assignment path at the used icons in according to configuration file.
        """
        # videomass sign
        if iconset == 'Videomass_Sign_Icons':  # default
            x48 = '%s/Videomass_Sign_Icons/48x48' % self.icodir
            x32 = '%s/Videomass_Sign_Icons/32x32' % self.icodir
            x24 = '%s/Videomass_Sign_Icons/24x24' % self.icodir
            x18 = '%s/Videomass_Sign_Icons/18x18' % self.icodir
        # material design black
        if iconset == 'Material_Design_Icons_black':
            x48 = '%s/Videomass_Sign_Icons/48x48' % self.icodir
            x32 = '%s/Material_Design_Icons_black/32x32' % self.icodir
            x24 = '%s/Material_Design_Icons_black/24x24' % self.icodir
            x18 = '%s/Material_Design_Icons_black/18x18' % self.icodir
        # flat-colours
        elif iconset == 'Flat_Color_Icons':
            x48 = '%s/Videomass_Sign_Icons/48x48' % self.icodir
            x32 = '%s/Flat_Color_Icons/32x32' % self.icodir
            x24 = '%s/Flat_Color_Icons/24x24' % self.icodir
            x18 = '%s/Flat_Color_Icons/18x18' % self.icodir


        # choose topic icons 48x48:
        icon_switchvideomass = '%s/icon_videoconversions.png' % x48
        icon_youtube = '%s/icon_youtube.png' % x48
        icon_prst_mng = '%s/icon_prst_mng.png' % x48
        # choose topic icons 36x36:
        icon_process = '%s/icon_process.png' % x32
        icon_toolback = '%s/icon_mainback.png' % x32
        icon_toolforward = '%s/icon_mainforward.png' % x32
        icon_ydl = '%s/youtubeDL.png' % x32
        # x24 icons 24x24:
        icn_infosource = '%s/infosource.png' % x24
        icn_preview = '%s/preview.png' % x24
        icn_cut = '%s/cut.png' % x24
        icn_saveprf = '%s/saveprf.png' % x24
        icn_newprf = '%s/newprf.png' % x24
        icn_delprf = '%s/delprf.png' % x24
        icn_editprf = '%s/editprf.png' % x24
        # filters icons 24x24:
        icn_playfilters = '%s/playfilters.png' % x24
        icn_resetfilters = '%s/resetfilters.png' % x24
        # filters icons 18x18:
        ic_resize = '%s/resize.png' % x18
        ic_crop = '%s/crop.png' % x18
        ic_rotate = '%s/rotate.png' % x18
        ic_deinterlace = '%s/deinterlace.png' % x18
        ic_denoiser = '%s/denoiser.png' % x18
        ic_analyzes = '%s/analyzes.png' % x18
        ic_settings = '%s/settings.png' % x18
        ic_peaklevel = '%s/peaklevel.png' % x18

        return [os.path.join(norm) for norm in [self.videomass_icon,  # 0
                                                icon_switchvideomass,  # 1
                                                icon_process,  # 2
                                                icn_infosource,  # 3
                                                icn_preview,  # 4
                                                icn_cut,  # 5
                                                icn_playfilters,  # 6
                                                icn_resetfilters,   # 7
                                                icn_saveprf,  # 8
                                                ic_resize,  # 9
                                                ic_crop,  # 10
                                                ic_rotate,  # 11
                                                ic_deinterlace,  # 12
                                                ic_denoiser,  # 13
                                                ic_analyzes,  # 14
                                                ic_settings,  # 15
                                                self.wizard_icon,  # 16
                                                ic_peaklevel,  # 17
                                                icon_youtube,  # 18
                                                icon_prst_mng,  # 19
                                                icn_newprf,  # 20
                                                icn_delprf,  # 21
                                                icn_editprf,  # 22
                                                icon_toolback,  # 23
                                                icon_toolforward,  # 24
                                                icon_ydl,  # 25
                                                ]]
