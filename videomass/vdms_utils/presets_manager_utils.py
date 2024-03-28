# -*- coding: UTF-8 -*-
"""
File Name: presets_manager_utils.py
Porpose: management of properties of the preset manager panel
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.08.2024
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
import wx


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
            for xex in exclude:
                file_sources.remove(xex)
            if not file_sources:
                wx.MessageBox(_("The selected profile is not suitable to "
                                "convert the following file formats:"
                                "\n\n%s\n\n") % ('\n'.join(exclude)),
                              "Videomass",
                              wx.ICON_INFORMATION | wx.OK,
                              )
                return None

    return file_sources
# ----------------------------------------------------------------------#


def json_data(arg):
    """
    Used by presets_mng_panel.py to get JSON data files.
    The `arg` parameter refer to each file name to parse. Return a list
    type object from getting data using `json` module in the following
    form:

    [{"Name": "",
      "Descritpion": "",
      "First_pass": "",
      "Second_pass": "",
      "Supported_list": "",
      "Output_extension": "",
      "Preinput_1": "",
      "Preinput_2": ""
    }]

    """
    try:
        with open(arg, 'r', encoding='utf8') as fln:
            data = json.load(fln)

    except json.decoder.JSONDecodeError as err:
        msg = _('You are attempting to load a preset written with '
                'invalid JSON encoding.\n\n'
                'You can try to restore it or import a correct one, '
                'otherwise it is recommended to remove it.'
                )
        wx.MessageBox(f'\nERROR: {err}\nFILE: "{arg}"\n\n{msg}',
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    except FileNotFoundError as err:
        msg = _('No presets found.\n\nPossible solution: open the '
                'Presets Manager panel, go to the presets column and try '
                'to click the "Restore all..." button'
                )
        wx.MessageBox(f'\nERROR: {err}\n\n{msg}',
                      ("Videomass"), wx.ICON_ERROR | wx.OK, None)

        return 'error'

    return data
# ------------------------------------------------------------------#


def delete_profiles(path, name):
    """
    Profile deletion from Presets manager panel
    """
    with open(path, 'r', encoding='utf8') as fln:
        data = json.load(fln)

    new_data = [obj for obj in data if not obj["Name"] == name]

    with open(path, 'w', encoding='utf8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)
# ------------------------------------------------------------------#


def update_oudated_profiles(new, old):
    """
    Updates (replaces with new ones) old profiles with same
    name as new profiles but Keep all others.
    """
    msg = _("Operation aborted due to possible JSON encoding/decoding "
            "error.\nFix any errors in the JSON code contained on the FILE "
            "before performing this operation again.")
    if new and old:
        with open(new, 'r', encoding='utf8') as newf:
            try:
                incoming = json.load(newf)
            except json.decoder.JSONDecodeError as err:
                return f"ERROR: {str(err)}\nFILE: '{new}'\n\n{msg}"

        with open(old, 'r', encoding='utf8') as oldf:
            try:
                outcoming = json.load(oldf)
            except json.decoder.JSONDecodeError as err:
                return f"ERROR: {str(err)}\nFILE: '{old}'\n\n{msg}"

        items_new = {value["Name"]: value for value in incoming}
        items_old = {value["Name"]: value for value in outcoming}

        items_old.update(items_new)
        items_old = list(items_old.values())
        items_old.sort(key=lambda s: s["Name"])  # make sorted by name

        with open(old, 'w', encoding='utf8') as outfile:
            json.dump(items_old, outfile, ensure_ascii=False, indent=4)
    return None
# ------------------------------------------------------------------#


def write_new_profile(path_prst, **kwargs):
    """
    Write a new profile using json data

    """
    with open(path_prst, 'r', encoding='utf8') as infile:
        stored_data = json.load(infile)

    for x in stored_data:
        if x["Name"] == kwargs['Name']:
            return 'already exist'

    new_data = stored_data + [kwargs]
    new_data.sort(key=lambda s: s["Name"])  # make sorted by name

    with open(path_prst, 'w', encoding='utf8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)

    return None
# ------------------------------------------------------------------#


def edit_existing_profile(path_prst, selected_profile, **kwargs):
    """
    Edit an exixting profile using json data

    """
    with open(path_prst, 'r', encoding='utf8') as infile:
        stored_data = json.load(infile)

    names = [x['Name'] for x in stored_data]
    names = [x for x in names if selected_profile != x]

    if kwargs['Name'] in names:
        return 'already exist'

    for item in stored_data:
        if item["Name"] == selected_profile:
            item["Name"] = kwargs['Name']
            item["Description"] = kwargs['Description']
            item["First_pass"] = kwargs['First_pass']
            item["Second_pass"] = kwargs['Second_pass']
            item["Supported_list"] = kwargs['Supported_list']
            item["Output_extension"] = kwargs['Output_extension']
            item["Preinput_1"] = kwargs['Preinput_1']
            item["Preinput_2"] = kwargs['Preinput_2']

    stored_data.sort(key=lambda s: s["Name"])  # make sorted by name

    with open(path_prst, 'w', encoding='utf8') as outfile:
        json.dump(stored_data, outfile, ensure_ascii=False, indent=4)

    return None
