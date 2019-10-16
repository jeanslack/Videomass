# -*- coding: UTF-8 -*-

#########################################################
# File Name: preset_manager_properties.py
# Porpose: management of properties of the preset manager panel
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (12) December 28 2018
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

import wx
import os
import json

#------------------------------------------------------------------#
def supported_formats(array4, file_sources):
    """
    check for supported formats by selected profile in the
    presets manager panel

    """
    supported = array4.split()
    exclude = []# se viene riempita la usano i dialoghi MessageBox

    #-------------- SUPPORTED CONTROL
    if supported:
        for sources in file_sources:#itero su ogni file input
            basename = os.path.basename(sources)#nome file (con ext)
            base_ext = os.path.splitext(basename)[1]#estensione con dot
            ext = base_ext.replace('.','')
            if  ext not in supported:
                exclude.append(sources)
        if exclude:
            for x in exclude:
                file_sources.remove(x)
            if not file_sources:
                wx.MessageBox(_("The selected profile is not suitable to "
                                "convert the following file formats:\n\n%s\n\n") 
                              % ('\n'.join(exclude)), 
                              _("Videomass: Unsuitable format"), 
                              wx.ICON_INFORMATION | wx.OK, 
                              None
                              )
                return (False)
            
    return (file_sources)

########################################################################
# PARSINGS XML FILES AND FUNCTION FOR DELETING
########################################################################

def json_data(arg):
    """
    Used by presets_mng_panel.py to get JSON data from `*.vdms` files. 
    The `arg` parameter refer to each file name to parse. Return a list 
    type object from getting data using `json` module in the following 
    form:
    
    [{"Name": "", 
      "Descritpion": "", 
      "First_pass": "", 
      "Second_pass": "",
      "Supported_list": "",
      "Output_extension": ""
    }]
    
    """
    try:
        with open(arg, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    except json.decoder.JSONDecodeError as err:
        msg = _('Is not a compatible Videomass presets. It is recommended '
                'removing it or rewrite it with a compatible JSON data '
                'structure.\n\n'
                'Possible solution: open Presets Manager panel, then use '
                'menu "File" > "Reset all presets" to safe repair all '
                'presets. Remember, those that are not compatible you '
                'have to manually remove them.'
                )
        wx.MessageBox('\nERROR: {1}\n\nFile: "{0}"\n{2}'.format(arg,err,msg),
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)
        
        return 'error'
    
    except FileNotFoundError as err:
        msg = _('The presets folder is empty, or there are invalid files. '
                'Open the Presets Manager panel, then Perform a repair in '
                'the "File" > "Reset all presets" menu.'
                )
        wx.MessageBox('\nERROR: {1}\n\nFile: "{0}"\n{2}'.format(arg,err,msg), 
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)
        
        return 'error'
        

    return data
#------------------------------------------------------------------#

def delete_profiles(path, name):
    """
    Profile deletion from Presets manager panel

    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = [obj for obj in data if not obj["Name"] == name]

    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)
