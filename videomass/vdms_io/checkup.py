# -*- coding: UTF-8 -*-
"""
File Name: checkup.py
Porpose: input/output file check
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.02.2022
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
import wx


def check_inout(file_sources, file_dest):
    """
    check for overwriting and file/dir existence.
    return tuple([file_sources], [file_dest]).
    return None otherwise.

    """
    # --------------- CHECK FOR OVERWRITING:
    files_exist = []  # already exist file LIST
    for files in file_dest:
        if os.path.exists(files):
            files_exist.append(files)

    if files_exist:
        if wx.MessageBox(_('Already exist: \n\n{}\n\n'
                           'Do you want to overwrite? ').format(
                         '\n'.join(files_exist)),
                         _('Please Confirm'),
                         wx.ICON_QUESTION | wx.YES_NO, None) == wx.NO:
            return None
    # --------------- CHECK FOR EXISTING FILES:
    for fln in file_sources:
        if not os.path.isfile(os.path.abspath(fln)):
            wx.MessageBox(_('File does not exist:\n\n"{}"\n').format(fln),
                          "Videomass", wx.ICON_ERROR
                          )
            return None
    # --------------- CHECK FOR EXISTING DIRECTORIES:
    for drn in file_dest:
        drn = os.path.abspath(os.path.dirname(drn))
        if not os.path.isdir(drn):
            wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(
                          drn), 'Videomass', wx.ICON_ERROR
                          )
            return None

    return (file_sources, file_dest)
# ------------------------------------------------------------------------#


def check_files(file_sources,
                dir_destin,
                same_destin,
                suffix,
                extout,
                outputnames
                ):
    """
    Build the full path filename for output files.
    return ([file_sources], [file_dest])
    None otherwise.

    """
    if not file_sources:
        return None

    file_dest = []  # output path names (not files)

    for path, fname in zip(file_sources, outputnames):
        dirname = os.path.dirname(path)

        if not extout:  # uses more extensions (copy formats)
            basename = os.path.basename(path)
            copyext = os.path.splitext(basename)[1]  # ext
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}{copyext}')
                file_dest.append(pathname)
            else:
                pathname = os.path.join(dir_destin, f'{fname}.{copyext}')
                file_dest.append(pathname)

        else:  # uses one extension for all output
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}.{extout}')
                file_dest.append(pathname)
            else:
                pathname = os.path.join(dir_destin, f'{fname}.{extout}')
                file_dest.append(pathname)

    return check_inout(file_sources, file_dest)
