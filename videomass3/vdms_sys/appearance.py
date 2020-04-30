# -*- coding: UTF-8 -*-

#########################################################
# Name: appearance.py
# Porpose: Used to set appearance on startup (icons and colours)
# Compatibility: Python3, wxPython Phoenix
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

import os


class Appearance(object):
    """
    This class determines the paths to use to set icons
    on the graphic appearance of the Videomass program.
    """
    def __init__(self, IS_LOCAL, iconset):
        """
        The paths where the icon sets are located depend where
        the program is run and on which operating system.
        Each icons set is defined by the name of the folder that
        contains it.
        """
        if IS_LOCAL:
            url = '%s/art/icons' % os.getcwd()  # work current directory
            self.videomass_icon = "%s/videomass.png" % url
            self.wizard_icon = "%s/videomass_wizard.png" % url

        else:
            import sys
            import platform
            OS = platform.system()

            if OS == 'Windows':  # Installed with 'pip install videomass'
                pythonpath = os.path.dirname(sys.executable)
                url = pythonpath + '\\share\\videomass\\icons'
                self.videomass_icon = url + "\\videomass.png"
                self.wizard_icon = url + "\\videomass_wizard.png"
            else:
                from shutil import which
                binarypath = which('videomass')
                if binarypath == '/usr/local/bin/videomass':
                    # Installed with super user 'pip install videomass'
                    # usually Linux,MacOs,Unix
                    url = '/usr/local/share/videomass/icons'
                    share = '/usr/local/share/pixmaps'
                    self.videomass_icon = share + '/videomass.png'
                    self.wizard_icon = url + '/videomass_wizard.png'
                elif binarypath == '/usr/bin/videomass':
                    # usually Linux from a custom binary installation
                    url = '/usr/share/videomass/icons'
                    share = '/usr/share/pixmaps'
                    self.videomass_icon = share + "/videomass.png"
                    self.wizard_icon = url + "/videomass_wizard.png"
                else:
                    # installed for the user 'pip install --user videomass'
                    import site
                    userbase = site.getuserbase()
                    url = userbase + '/share/videomass/icons'
                    share = '/share/pixmaps'
                    self.videomass_icon = userbase+share + "/videomass.png"
                    self.wizard_icon = userbase+url+"/videomass_wizard.png"

        # videomass sign
        if iconset == 'Videomass_Sign_Icons':  # default
            self.x48 = '%s/Videomass_Sign_Icons/48x48' % url
            self.x32 = '%s/Videomass_Sign_Icons/32x32' % url
            self.x24 = '%s/Videomass_Sign_Icons/24x24' % url
            self.x18 = '%s/Videomass_Sign_Icons/18x18' % url
        # material design black
        if iconset == 'Material_Design_Icons_black':
            self.x48 = '%s/Videomass_Sign_Icons/48x48' % url
            self.x32 = '%s/Material_Design_Icons_black/32x32' % url
            self.x24 = '%s/Material_Design_Icons_black/24x24' % url
            self.x18 = '%s/Material_Design_Icons_black/18x18' % url
            self.icons_set()
        # flat-colours
        elif iconset == 'Flat_Color_Icons':
            self.x48 = '%s/Videomass_Sign_Icons/48x48' % url
            self.x32 = '%s/Flat_Color_Icons/32x32' % url
            self.x24 = '%s/Flat_Color_Icons/24x24' % url
            self.x18 = '%s/Flat_Color_Icons/18x18' % url
            self.icons_set()

    def icons_set(self):
        """
        assignment path at the used icons in according to configuration file.
        """
        # choose topic icons 48x48:
        icon_switchvideomass = '%s/icon_videoconversions.png' % self.x48
        icon_youtube = '%s/icon_youtube.png' % self.x48
        icon_prst_mng = '%s/icon_prst_mng.png' % self.x48
        # choose topic icons 36x36:
        icon_process = '%s/icon_process.png' % self.x32
        icon_toolback = '%s/icon_mainback.png' % self.x32
        icon_toolforward = '%s/icon_mainforward.png' % self.x32
        icon_ydl = '%s/youtubeDL.png' % self.x32
        # x24 icons 24x24:
        icn_infosource = '%s/infosource.png' % self.x24
        icn_preview = '%s/preview.png' % self.x24
        icn_cut = '%s/cut.png' % self.x24
        icn_saveprf = '%s/saveprf.png' % self.x24
        icn_newprf = '%s/newprf.png' % self.x24
        icn_delprf = '%s/delprf.png' % self.x24
        icn_editprf = '%s/editprf.png' % self.x24
        # filters icons 24x24:
        icn_playfilters = '%s/playfilters.png' % self.x24
        icn_resetfilters = '%s/resetfilters.png' % self.x24
        # filters icons 18x18:
        ic_resize = '%s/resize.png' % self.x18
        ic_crop = '%s/crop.png' % self.x18
        ic_rotate = '%s/rotate.png' % self.x18
        ic_deinterlace = '%s/deinterlace.png' % self.x18
        ic_denoiser = '%s/denoiser.png' % self.x18
        ic_analyzes = '%s/analyzes.png' % self.x18
        ic_settings = '%s/settings.png' % self.x18
        ic_peaklevel = '%s/peaklevel.png' % self.x18

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
