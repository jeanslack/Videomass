# -*- coding: UTF-8 -*-
"""
File Name: presets_manager_utils.py
Porpose: management of properties of the preset manager panel
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.11.2024
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
from videomass.vdms_dialogs.list_warning import ListWarning


def supported_formats(supp, file_sources):
    """
    check for supported formats from selected profile in the
    presets manager panel
    """
    items = ''.join(supp.split()).split(',')
    errors = {}

    if not items == ['']:
        for src in file_sources:
            if os.path.splitext(src)[1].split('.')[1] not in items:
                ext = os.path.splitext(src)[1].split('.')[1]
                errors[f'"{src}"'] = (_('Supports ({0}) formats only, '
                                        'not ({1})').format(supp, ext))
        if errors:
            msg = _('File formats not supported by the selected profile')
            with ListWarning(None,
                             errors,
                             caption=_('Warning'),
                             header=msg,
                             buttons='OK',
                             ) as log:
                log.ShowModal()
            return None

    return file_sources
# ----------------------------------------------------------------------#


def json_data(filename):
    """
    Used by presets_mng_panel.py to get JSON data files.
    The `filename` parameter refer to each file name to parse.
    Return a list type object from getting data using `json`
    module in the following form:

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
        with open(filename, 'r', encoding='utf-8') as fln:
            data = json.load(fln)
    except json.decoder.JSONDecodeError as err:
        wx.MessageBox(f"ERROR: {str(err)}.\nInvalid file: «{filename}»",
                      _('Videomass - Error!'), wx.ICON_ERROR | wx.OK, None)
        return 'error'

    except FileNotFoundError as err:
        msg = _('No presets found.\n\nPossible solution: open the '
                'Presets Manager panel, go to the presets column and try '
                'to click the "Restore all..." button'
                )
        wx.MessageBox(f'{err}\n\n{msg}',
                      _('Videomass - Error!'), wx.ICON_ERROR | wx.OK, None)
        return 'error'

    return data
# ------------------------------------------------------------------#


def delete_profiles(filename, profilename):
    """
    Profile deletion from Presets manager panel
    """
    with open(filename, 'r', encoding='utf-8') as fln:
        data = json.load(fln)

    new_data = [obj for obj in data if not obj["Name"] == profilename]

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)
# ------------------------------------------------------------------#


def update_oudated_profiles(new, old):
    """
    Updates (replaces with new ones) old profiles with same
    name as new profiles but Keep all others.
    """
    if new and old:
        with open(new, 'r', encoding='utf-8') as newf:
            try:
                incoming = json.load(newf)
            except json.decoder.JSONDecodeError as err:
                return f"ERROR: {str(err)}.\nInvalid file: «{new}»"

        with open(old, 'r', encoding='utf-8') as oldf:
            try:
                outcoming = json.load(oldf)
            except json.decoder.JSONDecodeError as err:
                return f"ERROR: {str(err)}.\nInvalid file: «{old}»"

        items_new = {value["Name"]: value for value in incoming}
        items_old = {value["Name"]: value for value in outcoming}

        items_old.update(items_new)
        items_old = list(items_old.values())
        items_old.sort(key=lambda s: s["Name"])  # make sorted by name

        with open(old, 'w', encoding='utf-8') as outfile:
            json.dump(items_old, outfile, ensure_ascii=False, indent=4)

    return None
# ------------------------------------------------------------------#


def write_new_profile(filename, **kwargs):
    """
    Write a new profile using json data
    """
    with open(filename, 'r', encoding='utf-8') as infile:
        try:
            stored_data = json.load(infile)
        except json.decoder.JSONDecodeError as err:
            return f"ERROR: {str(err)}.\nInvalid file: «{filename}»"

    keys = ('Name', 'Description', 'First_pass',
            'Second_pass', 'Supported_list', 'Output_extension',
            'Preinput_1', 'Preinput_2',)
    for ck in stored_data:
        for key in keys:
            if key not in ck:
                return 'invalid JSON file'

    for x in stored_data:
        if x["Name"] == kwargs['Name']:
            return 'already exist'

    new_data = stored_data + [kwargs]
    new_data.sort(key=lambda s: s["Name"])  # make sorted by name

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(new_data, outfile, ensure_ascii=False, indent=4)

    return None
# ------------------------------------------------------------------#


def edit_existing_profile(filename, selected_profile, **kwargs):
    """
    Edit an exixting profile using json data

    """
    with open(filename, 'r', encoding='utf-8') as infile:
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

    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(stored_data, outfile, ensure_ascii=False, indent=4)

    return None
