# -*- coding: UTF-8 -*-
# File Name: preset_manager_properties.py
# Porpose: management of properties of the preset manager panel
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

import wx
import os
import json


def supported_formats(supp, file_sources):
    """
    check for supported formats from selected profile in the
    presets manager panel
    """
    items = ''.join(supp.split()).split(',')
    exclude = []

    if not items == ['']:
        for src in file_sources:
            if os.path.splitext(src)[1].split('.')[1] not in items:
                exclude.append(src)
        if exclude:
            for x in exclude:
                file_sources.remove(x)
            if not file_sources:
                wx.MessageBox(_("The selected profile is not suitable to "
                                "convert the following file formats:"
                                "\n\n%s\n\n") % ('\n'.join(exclude)),
                              "Videomass",
                              wx.ICON_INFORMATION | wx.OK,
                              )
                return

    return (file_sources)

########################################################################
# PARSINGS XML FILES AND FUNCTION FOR DELETING
########################################################################


def json_data(arg):
    """
    Used by presets_mng_panel.py to get JSON data from `*.vip` files.
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
        wx.MessageBox('\nERROR: {1}\n\nFile: "{0}"\n{2}'.format(arg, err, msg),
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    except FileNotFoundError as err:
        msg = _('The presets folder is empty, or there are invalid files. '
                'Open the Presets Manager panel, then Perform a repair in '
                'the "File" > "Reset all presets" menu.'
                )
        wx.MessageBox('\nERROR: {1}\n\nFile: "{0}"\n{2}'.format(arg, err, msg),
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    return data
# ------------------------------------------------------------------#


def delete_profiles(path, name):
    """
    Profile deletion from Presets manager panel
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = [obj for obj in data if not obj["Name"] == name]

    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)
