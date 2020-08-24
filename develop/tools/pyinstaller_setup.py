#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#########################################################
# Name: pyinstaller_setup.py
# Porpose: Wrap the videomass building with pyinstaller
# Compatibility: Python3
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


class Data(object):
    """
    Get data from current sources code directory

    """
    this = os.path.realpath(os.path.abspath(__file__))
    here = os.path.dirname(os.path.dirname(os.path.dirname(this)))
    binary = os.path.join(here, 'bin', 'videomass')
    sys.path.insert(0, here)
    try:
        from videomass3.vdms_sys.msg_info import current_release
    except ModuleNotFoundError as error:
        sys.exit(error)

    cr = current_release()  # Gets informations
    RLS_NAME = cr[0]  # first letter is Uppercase
    PRG_NAME = cr[1]  # first letter is lower
    VERSION = cr[2]
    RELEASE = cr[3]
    COPYRIGHT = cr[4]
    WEBSITE = cr[5]
    AUTHOR = cr[6]
    EMAIL = cr[7]
    COMMENT = cr[8]
    ART = os.path.join(here, 'videomass3', 'art')
    LOCALE = os.path.join(here, 'videomass3', 'locale')
    SHARE = os.path.join(here, 'videomass3', 'share')
    FFMPEG = os.path.join(here, 'videomass3', 'FFMPEG')
    NOTICE = os.path.join(FFMPEG, 'NOTICE.rtf')
    AUTH = os.path.join(here, 'AUTHORS')
    BUGS = os.path.join(here, 'BUGS')
    CHANGELOG = os.path.join(here, 'CHANGELOG')
    COPYING = os.path.join(here, 'COPYING')
    INSTALL = os.path.join(here, 'INSTALL')
    README = os.path.join(here, 'README.md')
    TODO = os.path.join(here, 'TODO')
    ICNS = os.path.join(here, 'videomass3', 'art', 'videomass.icns')
    ICO = os.path.join(here, 'videomass3', 'art', 'videomass.ico')

    WIN32_TEMPL = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{PRG_NAME}'],
            pathex=[r'{here}'],
            binaries=[],
            datas=[(r'{ART}', 'art'),
                    (r'{LOCALE}', 'locale'),
                    (r'{SHARE}', 'share'),
                    (r'{FFMPEG}', 'FFMPEG'),
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

    DARWIN_TEMPL = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{PRG_NAME}'],
            pathex=['{here}'],
            binaries=[],
            datas=[('{ART}', 'art'),
                    ('{LOCALE}', 'locale'),
                    ('{SHARE}', 'share'),
                    ('{FFMPEG}', 'FFMPEG'),
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

    LINUX_TEMPL = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{PRG_NAME}'],
            pathex=['{here}'],
            binaries=[],
            datas=[('{ART}', 'art'),
                    ('{LOCALE}', 'locale'),
                    ('{SHARE}', 'share'),
                    ('{FFMPEG}', 'FFMPEG'),
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
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='{PRG_NAME}',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False )
"""


class MakePyinstallerBuild(Data):
    """
    Wrap the pyinstaller building for Videomass

    """
    def check(self):
        """
        Check some integrity of sources

        """
        if not os.path.exists(os.path.join(self.here, 'videomass')):  # binary
            if os.path.isfile(self.binary):
                try:
                    shutil.copyfile(self.binary, os.path.join(self.here,
                                                              'videomass'))
                except FileNotFoundError as err:
                    sys.exit(err)
            else:
                sys.exit("ERROR: no 'bin/videomass' file found on videomass "
                         "base sources directory.")

    def genspec(self, build=False):
        """
        Generate a videomass.spec file on the specified platform.
        The valid platforms to work are only Windows and MacOs and Linux.
        The videomass.spec file will be saved in the root directory
        of the videomass sources.
        To running videomass.spec is required ``pyinstaller``.
        To use videomass.spec type:

            `pyinstaller videomass.spec`

        or use option -gb to generate and start with building too.
        """
        if platform.system() == 'Windows':
            contents = self.WIN32_TEMPL
        elif platform.system() == 'Darwin':
            contents = self.DARWIN_TEMPL
        elif platform.system() == 'Linux':
            contents = self.LINUX_TEMPL
        else:
            sys.exit("Unsupported platform. You create a spec file "
                     "using this command:\n"
                     "   pyi-makespec options videomass.py\n")

        specfile = os.path.join(self.here, 'videomass.spec')

        with open(specfile, 'w') as spec:
            spec.write(contents)
        print("ready videomass.spec on '%s'" % self.here)
        if build:
            self.run_pyinst(specfile)

    def run_pyinst(self, specfile):
        """
        wrap `pyinstaller videomass.spec`
        """
        if os.path.exists(specfile) and os.path.isfile(specfile):
            os.system("pyinstaller --clean %s" % specfile)
            print("\npyinstaller_setup.py: Build finished.\n")
        else:
            sys.exit("ERROR: no such file videomass.spec")

    def usemodule(self):
        """
        Run pyinstaller from Python code starting to build a
        videomass bundle and videomass.spec too.
        To use this function is required ``pyinstaller``.
        """
        try:
            import PyInstaller.__main__
        except ModuleNotFoundError as error:
            sys.exit('ERROR: %s - pyinstaller is required.' % error)

        if platform.system() == 'Windows':
            PyInstaller.__main__.run([
                                '--name=Videomass',
                                '--windowed',
                                '--add-data=%s;art' % self.ART,
                                '--add-data=%s;locale' % self.LOCALE,
                                '--add-data=%s;share' % self.SHARE,
                                '--add-data=%s;FFMPEG' % self.FFMPEG,
                                '--add-data=%s;DOC' % self.NOTICE,
                                # doc
                                '--add-data=%s;DOC' % self.AUTH,
                                '--add-data=%s;DOC' % self.BUGS,
                                '--add-data=%s;DOC' % self.CHANGELOG,
                                '--add-data=%s;DOC' % self.COPYING,
                                '--add-data=%s;DOC' % self.INSTALL,
                                '--add-data=%s;DOC' % self.README,
                                '--add-data=%s;DOC' % self.TODO,
                                '--exclude-module=youtube_dl',
                                '--icon=%s' % self.ICO,
                                'videomass',
                                ])

        elif platform.system() == 'Darwin':
            PyInstaller.__main__.run([
                            '--name=Videomass',
                            '--windowed',
                            # '--onefile',
                            '--osx-bundle-identifier=com.jeanslack.videomass',
                            '--add-data=%s:art' % self.ART,
                            '--add-data=%s:locale' % self.LOCALE,
                            '--add-data=%s:share' % self.SHARE,
                            '--add-data=%s:FFMPEG' % self.FFMPEG,
                            # doc
                            '--add-data=%s:DOC' % self.AUTH,
                            '--add-data=%s:DOC' % self.BUGS,
                            '--add-data=%s:DOC' % self.CHANGELOG,
                            '--add-data=%s:DOC' % self.COPYING,
                            '--add-data=%s:DOC' % self.INSTALL,
                            '--add-data=%s:DOC' % self.README,
                            '--add-data=%s:DOC' % self.TODO,
                            '--exclude-module=youtube_dl',
                            '--icon=%s' % self.ICNS,
                            'videomass',
                            ])

        elif platform.system() in ('Linux', 'FreeBSD'):
            PyInstaller.__main__.run([
                                '--name=videomass',
                                '--windowed',  # console=False
                                '--onefile',
                                '--add-data=%s:art' % self.ART,
                                '--add-data=%s:locale' % self.LOCALE,
                                '--add-data=%s:share' % self.SHARE,
                                '--add-data=%s:FFMPEG' % self.FFMPEG,
                                # doc
                                '--add-data=%s:DOC' % self.AUTH,
                                '--add-data=%s:DOC' % self.BUGS,
                                '--add-data=%s:DOC' % self.CHANGELOG,
                                '--add-data=%s:DOC' % self.COPYING,
                                '--add-data=%s:DOC' % self.INSTALL,
                                '--add-data=%s:DOC' % self.README,
                                '--add-data=%s:DOC' % self.TODO,
                                '--exclude-module=youtube_dl',
                                'videomass',
                                ])


def main():
    """
    Users inputs parser (positional/optional arguments)
    """
    parser = argparse.ArgumentParser(
                description='Wrap the pyinstaller setup for Videomass',)
    parser.add_argument(
                '-g', '--gen_spec',
                help="Generate a videomass.spec file to start building with, "
                     "but NOT start to building the bundle",
                action="store_true",
                       )

    parser.add_argument(
                '-m', '--use_module',
                help=("Start building by import PyInstaller.__main__ module\n"
                      "Warning: using this option pyinstaller will "
                      "overwrite the previously generated .spec file "
                      "each time"),
                action="store_true",
                       )
    parser.add_argument(
                '-gb', '--genspec_build',
                help="Generate a videomass.spec file and start directly "
                     "with building. Warning: same as the -m option",
                action="store_true",
                       )
    parser.add_argument(
                '-s', '--start_build',
                help="Start the building by an existing videomass.spec file",
                action="store_true",
                       )
    args = parser.parse_args()

    if args.gen_spec:
        wrap = MakePyinstallerBuild()
        wrap.check()
        wrap.genspec()

    elif args.use_module:
        wrap = MakePyinstallerBuild()
        wrap.check()
        wrap.usemodule()

    elif args.genspec_build:
        wrap = MakePyinstallerBuild()
        wrap.check()
        wrap.genspec(build=True)

    elif args.start_build:
        wrap = MakePyinstallerBuild()
        wrap.check()
        wrap.run_pyinst(os.path.join(Data.here, 'videomass.spec'))

    else:
        print("\nType 'pyinstaller_setup.py -h' for help.\n")
        return


if __name__ == '__main__':
    main()
