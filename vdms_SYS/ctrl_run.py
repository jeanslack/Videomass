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

PWD = os.getcwd() # work current directory (where are Videomsass?)
DIRNAME = os.path.expanduser('~') # /home/user (current user directory)

########################################################################
# CONTROLS CONFIGURATION FILE AND PARSINGS
########################################################################

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
    FIXME: Windows implementations: 
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
        This paths are for portable mode or if OS == Darwin
        """
        path_srcShare = '%s/share' % PWD
        """
        assignment path at the used icons:
        """
        maintoolbar = '%s/art/material-design-icons/maintoolbar_36' % PWD
        toolbar = '%s/art/material-design-icons/toolbar_24' % PWD
        filters24 = '%s/art/material-design-icons/filters_24' % PWD
        filters18 = '%s/art/material-design-icons/filters_18' % PWD
        # 128x128
        videomass_icon = "%s/art/videomass2.png" % PWD
        # main toolbar icons 32x32 - 36x36:
        icon_import = '%s/icon_import.png' % maintoolbar
        icon_presets = '%s/icon_presets.png' % maintoolbar
        icon_switchvideomass = '%s/icon_videoconversions.png' % maintoolbar
        icon_headphones = '%s/icon_audioconversions.png' % maintoolbar
        icon_process = '%s/art/icon_process.png' % PWD
        icon_help = '%s/icon_help.png' % maintoolbar
        # toolbar icons 24x24:
        icn_infosource = '%s/infosource.png' % toolbar
        icn_preview = '%s/preview.png' % toolbar
        icn_cut = '%s/cut.png' % toolbar
        icn_saveprf = '%s/saveprf.png' % toolbar
        icn_newprf = '%s/newprf.png' % toolbar
        icn_delprf = '%s/delprf.png' % toolbar
        icn_editprf = '%s/editprf.png' % toolbar
        # filters icons 24x24:
        icn_playfilters = '%s/playfilters.png' % filters24
        icn_resetfilters = '%s/resetfilters.png' % filters24
        # filters icons 18x18:
        ic_resize = '%s/resize.png' % filters18
        ic_crop = '%s/crop.png' % filters18
        ic_rotate = '%s/rotate.png' % filters18
        ic_deinterlace = '%s/deinterlace.png' % filters18
        ic_denoiser = '%s/denoiser.png' % filters18
        ic_analyzes = '%s/analyzes.png' % filters18
        ic_settings = '%s/settings.png' % filters18
        
        
        
    elif OS == ('Linux'):
        """
        This paths are for installable mode
        """
        path_srcShare = '/usr/share/videomass2/config'

        """
        assignment path at the used icons:
        """
        url = '/usr/share/pixmaps/videomass2/icons'
        # main videomass2 icon
        videomass_icon = "/usr/share/pixmaps/videomass2.png"
        # main toolbar icons 32x32 - 36x36:
        icon_import = '%s/material-design-icons/maintoolbar_36/icon_import.png' % url
        icon_presets = '%s/material-design-icons/maintoolbar_36/icon_presets.png' % url
        icon_switchvideomass = '%s/material-design-icons/maintoolbar_36/icon_videoconversions.png' % url
        icon_headphones = '%s/material-design-icons/maintoolbar_36/icon_audioconversions.png' % url
        icon_process = '/usr/share/videomass2/icons/icon_process.png'
        icon_help = '%s/material-design-icons/maintoolbar_36/icon_help.png' % url
        # toolbar icons 24x24:
        icn_infosource = '%s/material-design-icons/toolbar_24/infosource.png' % url
        icn_preview = '%s/material-design-icons/toolbar_24/preview.png' % url
        icn_cut = '%s/material-design-icons/toolbar_24/cut.png' % url
        icn_saveprf = '%s/material-design-icons/toolbar_24/saveprf.png' % url
        icn_newprf = '%s/material-design-icons/toolbar_24/newprf.png' % url
        icn_delprf = '%s/material-design-icons/toolbar_24/delprf.png' % url
        icn_editprf = '%s/material-design-icons/toolbar_24/editprf.png' % url
        # filters icons 24x24:
        icn_playfilters = '%s/material-design-icons/filters_24/playfilters.png' % url
        icn_resetfilters = '%s/material-design-icons/filters_24/resetfilters.png' % url
        # filters icons 18x18:
        ic_resize = '%s/material-design-icons/filters_18/resize.png' % url
        ic_crop = '%s/material-design-icons/filters_18/crop.png' % url
        ic_rotate = '%s/material-design-icons/filters_18/rotate.png' % url
        ic_deinterlace = '%s/material-design-icons/filters_18/deinterlace.png' % url
        ic_denoiser = '%s/material-design-icons/filters_18/denoiser.png' % url
        ic_analyzes = '%s/material-design-icons/filters_18/analyzes.png' % url
        ic_settings = '%s/material-design-icons/filters_18/settings.png' % url
            
    else: # it should be Windows OS
        """
        This paths are for OS == Windows
        """
        path_srcShare = '%s/share' % PWD
        """
        assignment path at the used icons:
        """
        maintoolbar = '%s/art/material-design-icons/maintoolbar_36' % PWD
        toolbar = '%s/art/material-design-icons/toolbar_24' % PWD
        filters24 = '%s/art/material-design-icons/filters_24' % PWD
        filters18 = '%s/art/material-design-icons/filters_18' % PWD
        # 128x128
        videomass_icon = "%s/art/videomass2.png" % PWD
        # main toolbar icons 32x32 - 36x36:
        icon_import = '%s/icon_import.png' % maintoolbar
        icon_presets = '%s/icon_presets.png' % maintoolbar
        icon_switchvideomass = '%s/icon_videoconversions.png' % maintoolbar
        icon_headphones = '%s/icon_audioconversions.png' % maintoolbar
        icon_process = '%s/art/icon_process.png' % PWD
        icon_help = '%s/icon_help.png' % maintoolbar
        # toolbar icons 24x24:
        icn_infosource = '%s/infosource.png' % toolbar
        icn_preview = '%s/preview.png' % toolbar
        icn_cut = '%s/cut.png' % toolbar
        icn_saveprf = '%s/saveprf.png' % toolbar
        icn_newprf = '%s/newprf.png' % toolbar
        icn_delprf = '%s/delprf.png' % toolbar
        icn_editprf = '%s/editprf.png' % toolbar
        # filters icons 24x24:
        icn_playfilters = '%s/playfilters.png' % filters24
        icn_resetfilters = '%s/resetfilters.png' % filters24
        # filters icons 18x18:
        ic_resize = '%s/resize.png' % filters18
        ic_crop = '%s/crop.png' % filters18
        ic_rotate = '%s/rotate.png' % filters18
        ic_deinterlace = '%s/deinterlace.png' % filters18
        ic_denoiser = '%s/denoiser.png' % filters18
        ic_analyzes = '%s/analyzes.png' % filters18
        ic_settings = '%s/settings.png' % filters18
        
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

    return (videomass_icon, icon_presets, icon_switchvideomass, icon_process, 
            icon_help, OS, path_srcShare, copyerr, icon_headphones, 
            icon_import, icn_infosource, icn_preview, icn_cut, icn_playfilters, 
            icn_resetfilters, icn_saveprf, icn_newprf, icn_delprf, icn_editprf,
            ic_resize, ic_crop, ic_rotate, ic_deinterlace, ic_denoiser,
            ic_analyzes, ic_settings,
            )
#------------------------------------------------------------------#
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
