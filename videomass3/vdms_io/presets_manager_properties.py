# -*- coding: UTF-8 -*-
# File Name: preset_manager_properties.py
# Porpose: management of properties of the preset manager panel
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Jan.17.2021 *PEP8 compatible*
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
# ----------------------------------------------------------------------#


def json_data(arg):
    """
    Used by presets_mng_panel.py to get JSON data from `*.prst` files.
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
        with open(arg, 'r', encoding='utf8') as f:
            data = json.load(f)

    except json.decoder.JSONDecodeError as err:
        msg = _('Invalid preset loaded.\nIt is recommended to remove it or '
                'rewrite it into a JSON format compatible with Videomass.\n\n'
                'Possible solution: open the Presets Manager panel, go to '
                'the presets column and try to click the "Restore" button'
                )
        wx.MessageBox('\nERROR: {1}\n\nFile: "{0}"\n{2}'.format(arg, err, msg),
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    except FileNotFoundError as err:
        msg = _('No presets found.\n\nPossible solution: open the '
                'Presets Manager panel, go to the presets column and try '
                'to click the "Restore all..." button'
                )
        wx.MessageBox('\nERROR: {0}\n\n{1}'.format(err, msg),
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    return data
# ------------------------------------------------------------------#


def delete_profiles(path, name):
    """
    Profile deletion from Presets manager panel
    """
    with open(path, 'r', encoding='utf8') as f:
        data = json.load(f)

    new_data = [obj for obj in data if not obj["Name"] == name]

    with open(path, 'w', encoding='utf8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)
# ------------------------------------------------------------------#


def preserve_old_profiles(new, old):
    """
    Keep old profiles in the Presets manager panel when
    replaced with new presets.

    """
    with open(new, 'r', encoding='utf8') as f:
        incoming = json.load(f)

    with open(old, 'r', encoding='utf8') as f:
        outcoming = json.load(f)

    items_new = {value["Name"]: value for value in incoming}
    items_old = {value["Name"]: value for value in outcoming}

    #  Return a new set with elements in either the set or other but not both.
    diff_keys = set(items_new).symmetric_difference(items_old)

    if not diff_keys:
        return False

    backup = [items_old[x] for x in diff_keys]

    data = incoming + backup
    data.sort(key=lambda s: s["Name"])  # make sorted by name

    with open(new, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    return True
