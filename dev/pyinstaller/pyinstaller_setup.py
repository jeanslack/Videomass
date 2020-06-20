#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#########################################################
# Name: pyinstaller_setup.py
# Porpose: script to automatize the videomass building with pyinstaller
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
import os
import sys
import shutil
import platform
import argparse

this = os.path.realpath(os.path.abspath(__file__))
# here = os.path.dirname(this)  # if you use this script on videomass root dir
here = os.path.dirname(os.path.dirname(os.path.dirname(this)))
sys.path.insert(0, here)
videomass = os.path.join(here, 'bin', 'videomass')

if not os.path.exists(os.path.join(here, 'videomass')):  # videomass binary
    if os.path.isfile(videomass):
        try:
            shutil.copyfile(videomass, os.path.join(here, 'videomass'))
        except FileNotFoundError as err:
            sys.exit(err)
    else:
        sys.exit('ERROR: the videomass sources directory must be exists')
try:
    from videomass3.vdms_sys.msg_info import current_release
    # ---- Get info data
    cr = current_release()
    RLS_NAME = cr[0]  # first letter is Uppercase
    PRG_NAME = cr[1]
    VERSION = cr[2]
    RELEASE = cr[3]
    COPYRIGHT = cr[4]
    WEBSITE = cr[5]
    AUTHOR = cr[6]
    EMAIL = cr[7]
    COMMENT = cr[8]
except ModuleNotFoundError as error:
    sys.exit(error)

art = os.path.join(here, 'videomass3', 'art')
locale = os.path.join(here, 'videomass3', 'locale')
share = os.path.join(here, 'videomass3', 'share')
ffmpeg_win = os.path.join(here, 'Win32Setup', 'FFMPEG_BIN')
ffmpeg_mac = os.path.join(here, 'MacOsxSetup', 'FFMPEG_BIN')
notice = os.path.join(here, 'Win32Setup', 'NOTICE.rtf')
auth = os.path.join(here, 'AUTHORS')
bugs = os.path.join(here, 'BUGS')
changelog = os.path.join(here, 'CHANGELOG')
copying = os.path.join(here, 'COPYING')
install = os.path.join(here, 'INSTALL')
readme = os.path.join(here, 'README.md')
todo = os.path.join(here, 'TODO')
icns = os.path.join(here, 'videomass3', 'art', 'videomass.icns')
ico = os.path.join(here, 'videomass3', 'art', 'videomass.ico')


def genspec():
    """
    Generate a videomass.spec file on Windows and MacOs .
    To running videomass.spec use:
        `pyinstaller videomass.spec`
    """
    if platform.system() == 'Windows':
        content = f"""# -*- mode: python ; coding: utf-8 -*-
block_cipher = None


a = Analysis(['{PRG_NAME}'],
             pathex=['{here}'],
             binaries=[],
             datas=[('{art}', 'art'),
                    ('{locale}', 'locale'),
                    ('{share}', 'share'),
                    ('{ffmpeg_win}', 'FFMPEG_BIN'),
                    ('{notice}', 'FFMPEG_BIN'),
                    ('{auth}', 'DOC'),
                    ('{bugs}', 'DOC'),
                    ('{changelog}', 'DOC'),
                    ('{copying}', 'DOC'),
                    ('{install}', 'DOC'),
                    ('{readme}', 'DOC'),
                    ('{todo}', 'DOC')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['youtube_dl'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='{RLS_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='{ico}')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='{RLS_NAME}')
    """

    elif platform.system() == 'Darwin':
        content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{PRG_NAME}'],
             pathex=['{here}'],
             binaries=[],
             datas=[('{art}', 'art'),
                    ('{locale}', 'locale'),
                    ('{share}', 'share'),
                    ('{ffmpeg_mac}', 'FFMPEG_BIN'),
                    ('{auth}', 'DOC'),
                    ('{bugs}', 'DOC'),
                    ('{changelog}', 'DOC'),
                    ('{copying}', 'DOC'),
                    ('{install}', 'DOC'),
                    ('{readme}', 'DOC'),
                    ('{todo}', 'DOC')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['youtube_dl'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='{RLS_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='{icns}')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='{RLS_NAME}')
app = BUNDLE(coll,
             name='{RLS_NAME}.app',
             icon='{icns}',
             bundle_identifier='com.jeanslack.videomass',
             info_plist={{
                   # 'LSEnvironment': '$0',
                   'NSPrincipalClass': 'NSApplication',
                   'NSAppleScriptEnabled': False,
                   'CFBundleName': '{RLS_NAME}',
                   'CFBundleDisplayName': '{RLS_NAME}',
                   'CFBundleGetInfoString': "Making {RLS_NAME}",
                   'CFBundleIdentifier': "com.jeanslack.videomass",
                   'CFBundleVersion': '{VERSION}',
                   'CFBundleShortVersionString': '{VERSION}',
                   'NSHumanReadableCopyright': 'Copyright {COPYRIGHT}, '
                                               'Gianluca Pernigotto, '
                                               'All Rights Reserved',
                                               }})

    """
    specfile = os.path.join(here, 'videomass.spec')
    with open(specfile, 'w') as spec:
        spec.write(content)


def startbuild():
    """
    Running pyInstaller from Python code and start to build a
    videomass bundle and videomass.spec too.
    """
    import PyInstaller.__main__

    if platform.system() == 'Windows':
        PyInstaller.__main__.run([
                                '--name=Videomass',
                                '--windowed',
                                '--add-data=%s;art' % art,
                                '--add-data=%s;locale' % locale,
                                '--add-data=%s;share' % share,
                                '--add-data=%s;FFMPEG_BIN' % ffmpeg_win,
                                '--add-data=%s;DOC' % notice,
                                # doc
                                '--add-data=%s;DOC' % auth,
                                '--add-data=%s;DOC' % bugs,
                                '--add-data=%s;DOC' % changelog,
                                '--add-data=%s;DOC' % copying,
                                '--add-data=%s;DOC' % install,
                                '--add-data=%s;DOC' % readme,
                                '--add-data=%s;DOC' % todo,
                                '--exclude-module=youtube_dl',
                                '--icon=%s' % ico,
                                'videomass',
                                ])

    elif platform.system() == 'Darwin':
        PyInstaller.__main__.run([
                                '--name=Videomass',
                                '--windowed',
                                # '--onefile',
                                '--osx-bundle-identifier=com.jeanslack.videomass',
                                '--add-data=%s:art' % art,
                                '--add-data=%s:locale' % locale,
                                '--add-data=%s:share' % share,
                                '--add-data=%s:FFMPEG_BIN' % ffmpeg_mac,
                                # doc
                                '--add-data=%s:DOC' % auth,
                                '--add-data=%s:DOC' % bugs,
                                '--add-data=%s:DOC' % changelog,
                                '--add-data=%s:DOC' % copying,
                                '--add-data=%s:DOC' % install,
                                '--add-data=%s:DOC' % readme,
                                '--add-data=%s:DOC' % todo,
                                '--exclude-module=youtube_dl',
                                '--icon=%s' % icns,
                                'videomass',
                                ])


def args():
    """
    Parser of the users inputs (positional/optional arguments)
    """
    parser = argparse.ArgumentParser(
                description='Automatize the pyinstaller setup for Videomass',)
    parser.add_argument(
                '-s', '--genspec',
                help="Generate a videomass.spec file to start building with",
                action="store_true",
                       )
    parser.add_argument(
                '-b', '--startbuild',
                help=("Start building by import PyInstaller.__main__"),
                action="store_true",
                       )
    args = parser.parse_args()

    if args.genspec:
        genspec()
    elif args.startbuild:
        startbuild()
    else:
        print("Type 'pyinstaller_setup.py -h' for help.")
        return


if __name__ == '__main__':
    if platform.system() in ('Windows', 'Darwin'):
        args()
    else:
        sys.exit('ERROR: invalid platform. This script work on Windows and '
                 'Mac-Os only for now, exit.')
