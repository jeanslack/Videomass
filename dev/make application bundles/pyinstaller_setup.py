#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#########################################################
# Name: makebundles.py
# Porpose: Running PyInstaller from Python code
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.18.2020
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
"""
 USAGE:
    - python3 [OPTIONS] makebundles.py
"""
import os
import sys
import shutil
import platform
import PyInstaller.__main__

this = os.path.realpath(os.path.abspath(__file__))
here = os.path.dirname(this)
videomass = os.path.join(here, 'bin', 'videomass')

if not os.path.exists(os.path.join(here, 'videomass')):
    if os.path.isfile(videomass):
        try:
            shutil.copyfile(videomass, os.path.join(here, 'videomass'))
        except FileNotFoundError as err:
            sys.exit(err)
    else:
        sys.exit('ERROR: must be the base directory of videomass source')


if platform.system() == 'Windows':
    PyInstaller.__main__.run([
        '--name=Videomass',
        '--windowed',
        '--add-data=%s;art' % os.path.join('%s' % here, 'videomass3', 'art'),
        '--add-data=%s;locale' % os.path.join('%s' % here, 'videomass3', 'locale'),
        '--add-data=%s;share' % os.path.join('%s' % here, 'videomass3', 'share'),
        '--add-data=%s;FFMPEG_BIN' % os.path.join('%s' % here, 'Win32Setup',
                                                              'FFMPEG_BIN'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'Win32Setup','NOTICE.rtf'),
        # doc
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'AUTHORS'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'BUGS'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'CHANGELOG'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'COPYING'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'INSTALL'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'README.md'),
        '--add-data=%s;DOC' % os.path.join('%s' % here, 'TODO'),
        '--exclude-module=youtube_dl',
        '--icon=%s' % os.path.join('%s' % here, 'videomass3',
                                   'art', 'videomass.ico'),
        'videomass',])

elif platform.system() == 'Darwin':
    PyInstaller.__main__.run([
        '--name=Videomass',
        '--windowed',
        #'--onefile',
        '--osx-bundle-identifier=com.jeanslack.videomass',
        '--add-data=%s:art' % os.path.join('%s' % here, 'videomass3', 'art'),
        '--add-data=%s:locale' % os.path.join('%s' % here, 'videomass3', 'locale'),
        '--add-data=%s:share' % os.path.join('%s' % here, 'videomass3', 'share'),
        '--add-data=%s:FFMPEG_BIN' % os.path.join('%s' % here, 'MacOsxSetup',
                                                              'FFMPEG_BIN'),
        # doc
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'AUTHORS'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'BUGS'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'CHANGELOG'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'COPYING'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'INSTALL'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'README.md'),
        '--add-data=%s:DOC' % os.path.join('%s' % here, 'TODO'),
        '--exclude-module=youtube_dl',
        '--icon=%s' % os.path.join('%s' % here, 'videomass3',
                                   'art', 'videomass.icns'),
        'videomass',
        ])

# add to videomass.spec
#info_plist={
#                   # 'LSEnvironment': '$0',
#                   'NSPrincipalClass': 'NSApplication',
#                   'NSAppleScriptEnabled': False,
#                   'CFBundleName': 'Videomass',
#                   'CFBundleDisplayName': 'Videomass',
#                   'CFBundleGetInfoString': "Making Videomass",
#                   'CFBundleIdentifier': "com.jeanslack.videomass",
#                   'CFBundleVersion': '1.6.1',
#                   'CFBundleShortVersionString': '1.6.1',
#                   'NSHumanReadableCopyright': 'Copyright © 2013-2019, '
#                                            'Gianluca Pernigotto, '
#                                            'All Rights Reserved',
#                                            })
