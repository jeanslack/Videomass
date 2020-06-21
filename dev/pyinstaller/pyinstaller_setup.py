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
    sys.path.insert(0, here)
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

ART = os.path.join(here, 'videomass3', 'art')
LOCALE = os.path.join(here, 'videomass3', 'locale')
SHARE = os.path.join(here, 'videomass3', 'share')
FFMPEG_WIN = os.path.join(here, 'Win32Setup', 'FFMPEG_BIN')
FFMPEG_MACOS = os.path.join(here, 'MacOsxSetup', 'FFMPEG_BIN')
NOTICE = os.path.join(here, 'Win32Setup', 'NOTICE.rtf')
AUTH = os.path.join(here, 'AUTHORS')
BUGS = os.path.join(here, 'BUGS')
CHANGELOG = os.path.join(here, 'CHANGELOG')
COPYING = os.path.join(here, 'COPYING')
INSTALL = os.path.join(here, 'INSTALL')
README = os.path.join(here, 'README.md')
TODO = os.path.join(here, 'TODO')
ICNS = os.path.join(here, 'videomass3', 'art', 'videomass.icns')
ICO = os.path.join(here, 'videomass3', 'art', 'videomass.ico')


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
             pathex=[r'{here}'],
             binaries=[],
             datas=[(r'{ART}', 'art'),
                    (r'{LOCALE}', 'locale'),
                    (r'{SHARE}', 'share'),
                    (r'{FFMPEG_WIN}', 'FFMPEG_BIN'),
                    (r'{NOTICE}', 'DOC'),
                    (r'{AUTH}', 'DOC'),
                    (r'{BUGS}', 'DOC'),
                    (r'{CHANGELOG}', 'DOC'),
                    (r'{COPYING}', 'DOC'),
                    (r'{INSTALL}', 'DOC'),
                    (r'{README}', 'DOC'),
                    (r'{TODO}', 'DOC')],
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
          icon=r'{ICO}')
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
             datas=[('{ART}', 'art'),
                    ('{LOCALE}', 'locale'),
                    ('{SHARE}', 'share'),
                    ('{FFMPEG_MACOS}', 'FFMPEG_BIN'),
                    ('{AUTH}', 'DOC'),
                    ('{BUGS}', 'DOC'),
                    ('{CHANGELOG}', 'DOC'),
                    ('{COPYING}', 'DOC'),
                    ('{INSTALL}', 'DOC'),
                    ('{README}', 'DOC'),
                    ('{TODO}', 'DOC')],
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
          icon='{ICNS}')
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
             icon='{ICNS}',
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
                                '--add-data=%s;art' % ART,
                                '--add-data=%s;locale' % LOCALE,
                                '--add-data=%s;share' % SHARE,
                                '--add-data=%s;FFMPEG_BIN' % FFMPEG_WIN,
                                '--add-data=%s;DOC' % NOTICE,
                                # doc
                                '--add-data=%s;DOC' % AUTH,
                                '--add-data=%s;DOC' % BUGS,
                                '--add-data=%s;DOC' % CHANGELOG,
                                '--add-data=%s;DOC' % COPYING,
                                '--add-data=%s;DOC' % INSTALL,
                                '--add-data=%s;DOC' % README,
                                '--add-data=%s;DOC' % TODO,
                                '--exclude-module=youtube_dl',
                                '--icon=%s' % ICO,
                                'videomass',
                                ])

    elif platform.system() == 'Darwin':
        PyInstaller.__main__.run([
                                '--name=Videomass',
                                '--windowed',
                                # '--onefile',
                                '--osx-bundle-identifier=com.jeanslack.videomass',
                                '--add-data=%s:art' % ART,
                                '--add-data=%s:locale' % LOCALE,
                                '--add-data=%s:share' % SHARE,
                                '--add-data=%s:FFMPEG_BIN' % FFMPEG_MACOS,
                                # doc
                                '--add-data=%s:DOC' % AUTH,
                                '--add-data=%s:DOC' % BUGS,
                                '--add-data=%s:DOC' % CHANGELOG,
                                '--add-data=%s:DOC' % COPYING,
                                '--add-data=%s:DOC' % INSTALL,
                                '--add-data=%s:DOC' % README,
                                '--add-data=%s:DOC' % TODO,
                                '--exclude-module=youtube_dl',
                                '--icon=%s' % ICNS,
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
