# -*- coding: UTF-8 -*-
"""
File Name: checkup.py
Porpose: input/output file check
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.02.2022
Code checker:
    flake8: --ignore F821
    pylint: --ignore E0602, E1101
########################################################

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


def check_inout(already_existing,
                file_sources,
                output_list
                ):
    """
    check for overwriting and file/dir existence.

    return following values:

    file_sources: a file list filtered by checking.
    output_list: contains output paths as many as the file sources
    lenghmax: lengh list useful for count the loop index on the batch process.

    if already exists or file does not exist or output folder
    does not exist, return
        (False, None, None, None, None) .

    """
    if already_existing:
        if wx.MessageBox(_('Already exist: \n\n{}\n\n'
                           'Do you want to overwrite? ').format(
                         '\n'.join(already_existing)),
                         _('Please Confirm'),
                         wx.ICON_QUESTION | wx.YES_NO, None) == wx.NO:
            return None

    # --------------- CHECK EXISTING FILES AND DIRECTORIES:
    for fln in file_sources:
        if not os.path.isfile(os.path.abspath(fln)):
            wx.MessageBox(_('File does not exist:\n\n"{}"\n').format(fln),
                          "Videomass", wx.ICON_ERROR
                          )
            return None

    for drn in output_list:
        drn = os.path.abspath(os.path.dirname(drn))
        if not os.path.isdir(drn):
            wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(
                          drn), 'Videomass', wx.ICON_ERROR
                          )
            return None

    return (file_sources, output_list, len(file_sources))


def check_files(file_sources,
                dir_destin,
                same_destin,
                suffix,
                extout,
                outputnames
                ):
    """
    Create data structures related to processable files.

    if no file or one of the conditions returned by the
    check_inout function, return
        (False, None, None, None, None)

    return (file_sources, output_list, len(file_sources)) otherwise

    """
    if not file_sources:
        return None

    already_existing = []  # already exist file names list
    output_list = []  # output path names list
    # base_name = []  # represents the complete final basenames

    # --------------- CHECK OVERWRITING:
    for path, fname in zip(file_sources, outputnames):
        dirname = os.path.dirname(path)

        if not extout:  # uses more extensions (copy formats)
            basename = os.path.basename(path)
            copyext = os.path.splitext(basename)[1]  # ext
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}{copyext}')
                output_list.append(pathname)
                # base_name.append(os.path.basename(pathname))
            else:
                pathname = os.path.join(dir_destin, f'{fname}.{copyext}')
                output_list.append(pathname)
                # base_name.append(basename)

            if os.path.exists(pathname):
                already_existing.append(pathname)

        else:  # uses one extension for all output
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}.{extout}')
                output_list.append(pathname)
            else:
                pathname = os.path.join(dir_destin, f'{fname}.{extout}')
                output_list.append(pathname)

            if os.path.exists(pathname):
                already_existing.append(pathname)

    return check_inout(already_existing, file_sources, output_list)
