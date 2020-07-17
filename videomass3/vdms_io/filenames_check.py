# -*- coding: UTF-8 -*-
# File Name: filenames_check.py
# Porpose: input/output file check
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


def inspect(file_sources, dir_destin, extoutput):
    """
    La funzione offre un controllo per gestire l'overwriting demandando
    all'utente la scelta se sovrascrive o meno file già esistenti, e
    un'altro controllo per la verifica dell'esistenza reale di files
    e cartelle e un ultimo controllo per la modalità batch o single process.

    The function return following values:
    typeproc: if one singol file is alone, if multiple file is batch.
    file_sources: a file list filtered by checking.
    outputdir: contains output paths as many as the file sources
    filename: file names without path and extension
    base_name: file names without path but with extensions
    lenghmax: lengh list useful for count the loop index on the batch process.

    """
    if not file_sources:
        return (False, None, None, None, None)

    exclude = []  # se viene riempita, la usano i dialoghi MessageBox
    outputdir = []  # contiene percorsi di uscita quanti sono i file_sources
    base_name = []  # stesso nome e formato di uscita

    # --------------- OVERWRITING CONTROL:
    for path in file_sources:
        dirname = os.path.dirname(path)  # solo path
        basename = os.path.basename(path)  # nome file con ext.
        filename = os.path.splitext(basename)[0]  # nome file senza ext.
        # ext. del filesources:
        # sameext = os.path.splitext(basename)[1].replace('.','')
        if not extoutput:  # uses more extension identity
            pathname = '%s/%s' % (dir_destin, basename)
            outputdir.append(dir_destin)
            base_name.append(basename)
            if os.path.exists(pathname):
                exclude.append(pathname)

        else:  # uses only one extension identity
            pathname = '%s/%s.%s' % (dir_destin, filename, extoutput)
            outputdir.append(dir_destin)
            if os.path.exists(pathname):
                exclude.append(pathname)
    if exclude:
        if wx.MessageBox(_('Already exist: \n\n- %s\n\n'
                           'Do you want to overwrite? ') %
                         ('\n- '.join(exclude)),
                         _('Videomass: Please Confirm'),
                         wx.ICON_QUESTION | wx.YES_NO,
                         None) == wx.NO:
            return (False, None, None, None, None)  # user risponde no

    # --------------- EXISTING FILES AND DIRECTORIES CONTROL:
    for f in file_sources:
        if not os.path.isfile(os.path.abspath(f)):
            wx.MessageBox(_('The file does not exist:\n\n"%s"\n') % (f),
                          _("Videomass: Input file error"), wx.ICON_ERROR
                          )
            return (False, None, None, None, None)

    for d in outputdir:
        if not os.path.isdir(os.path.abspath(d)):
            wx.MessageBox(_('The folder does not exist:\n\n"%s"\n') % (d),
                          _('Videomass: Output folder error'), wx.ICON_ERROR
                          )
            return (False, None, None, None, None)

    # ---------------- SINGLE OR BATCH PROCESS
    if len(file_sources) > 1:
        typeproc = 'batch'
    else:
        typeproc = 'alone'
    lenghmax = len(file_sources)

    return (typeproc, file_sources, outputdir, filename, base_name, lenghmax)
