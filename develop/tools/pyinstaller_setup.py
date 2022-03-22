#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: pyinstaller_setup.py
Porpose: Setup the videomass.spec and build bundle via Pyinstaller
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2020-2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sept.04.2021
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
import sys
import shutil
import platform
import argparse
import time
import subprocess

this = os.path.realpath(os.path.abspath(__file__))
HERE = os.path.dirname(os.path.dirname(os.path.dirname(this)))
sys.path.insert(0, HERE)
try:
    from videomass.vdms_sys.msg_info import current_release
except ModuleNotFoundError as error:
    sys.exit(error)

SCRIPT = 'launcher'
NAME = 'videomass'
BINARY = os.path.join(HERE, SCRIPT)
SPECFILE = os.path.join(HERE, '%s.spec' % NAME)
# BINARY = os.path.join(HERE, 'bin', 'videomass')
# SPECFILE = os.path.join(HERE, 'videomass.spec')


def data(here=HERE, name=NAME):
    """
    Returns a dict object of the Videomass data
    and pathnames needed to spec file.
    """
    release = current_release()  # Gets data list

    return dict(RLS_NAME=release[0],  # first letter is Uppercase
                PRG_NAME=release[1],  # first letter is lower
                NAME=name,
                VERSION=release[2],
                RELEASE=release[3],
                COPYRIGHT=release[4],
                WEBSITE=release[5],
                AUTHOR=release[6],
                EMAIL=release[7],
                COMMENT=release[8],
                ART=os.path.join(here, 'videomass', 'art'),
                LOCALE=os.path.join(here, 'videomass', 'locale'),
                SHARE=os.path.join(here, 'videomass', 'share'),
                FFMPEG=os.path.join(here, 'videomass', 'FFMPEG'),
                NOTICE=os.path.join(here, 'videomass',
                                    'FFMPEG', 'NOTICE.rtf'),
                AUTH=os.path.join(here, 'AUTHORS'),
                BUGS=os.path.join(here, 'BUGS'),
                CHANGELOG=os.path.join(here, 'CHANGELOG'),
                COPYING=os.path.join(here, 'LICENSE'),
                INSTALL=os.path.join(here, 'INSTALL'),
                README=os.path.join(here, 'README.md'),
                TODO=os.path.join(here, 'TODO'),
                ICNS=os.path.join(here, 'videomass',
                                  'art', 'videomass.icns'),
                ICO=os.path.join(here, 'videomass', 'art', 'videomass.ico'),
                )


class PyinstallerSpec():
    """
    This class structures the information data flow,
    arranges the paths of the files and directories
    and manages the options to generate a videomass.spec
    file based to the operating system in use.

    """

    def __init__(self, onedf='--onedir'):
        """
        The following OS's are supported:
        Linux, MacOS and MS-Windows
        """
        self.onedf = onedf  # is None if --start_build option is given
        self.getdata = data()
        sep = ';' if platform.system() == 'Windows' else ':'

        self.datas = (f"--add-data {self.getdata['ART']}{sep}art "
                      f"--add-data {self.getdata['LOCALE']}{sep}locale "
                      f"--add-data {self.getdata['SHARE']}{sep}share "
                      f"--add-data {self.getdata['FFMPEG']}{sep}FFMPEG "
                      f"--add-data {self.getdata['AUTH']}{sep}DOC "
                      f"--add-data {self.getdata['BUGS']}{sep}DOC "
                      f"--add-data {self.getdata['CHANGELOG']}{sep}DOC "
                      f"--add-data {self.getdata['COPYING']}{sep}DOC "
                      f"--add-data {self.getdata['INSTALL']}{sep}DOC "
                      f"--add-data {self.getdata['README']}{sep}DOC "
                      f"--add-data {self.getdata['TODO']}{sep}DOC "
                      )
    # ---------------------------------------------------------#

    def windows_platform(self):
        """
        Set options flags and spec file pathname
        on MS-Windows platform.
        """
        options = (f"--name {self.getdata['RLS_NAME']} {self.onedf} "
                   f"--windowed --noconsole --icon {self.getdata['ICO']} "
                   # f"--exclude-module youtube_dl --exclude-module 'yt_dlp' "
                   f"{self.datas} ")

        return options
    # ---------------------------------------------------------#

    def darwin_platform(self):
        """
        Set options flags and spec file pathname
        on MacOS platform.
        FIXME : use codesign identity when pyinstaller is fixed to v.4.5.2
        """
        rlsname = self.getdata['RLS_NAME']
        version = self.getdata['VERSION']
        cright = self.getdata['COPYRIGHT']

        opts = (f"--name '{rlsname}' {self.onedf} "
                f"--windowed --noconsole --icon "
                f"'{self.getdata['ICNS']}' --osx-bundle-identifier "
                f"'com.jeanslack.videomass' "
                # f"--codesign-identity IDENTITY "
                # f"--osx-entitlements-file FILENAME "
                # f"--exclude-module 'youtube_dl' --exclude-module 'yt_dlp' "
                f"{self.datas} ")

        plist = (
            f"""             info_plist={{# 'LSEnvironment': '$0',
             'NSPrincipalClass': 'NSApplication',
             'NSAppleScriptEnabled': False,
             'CFBundleName': '{rlsname}',
             'CFBundleDisplayName': '{rlsname}',
             'CFBundleGetInfoString': "Making {rlsname}",
             'CFBundleIdentifier': "com.jeanslack.videomass",
             'CFBundleVersion': '{version}',
             'CFBundleShortVersionString': '{version}',
             'NSHumanReadableCopyright':'Copyright {cright}, '
                                        'Gianluca Pernigotto, '
                                        'All Rights Reserved',}})
""")

        return opts, plist
    # ---------------------------------------------------------#

    def linux_platform(self):
        """
        Set options flags and spec file pathname
        on Linux platform.
        """
        options = (f"--name {self.getdata['NAME']} {self.onedf} "
                   f"--windowed --noconsole {self.datas}"
                   )

        return options
# --------------------------------------------------------#


def onefile_onedir():
    """
    Pyinstaller offer two options to generate stand-alone executables.
    The `--onedir` option is the default.
    """
    onedf = input('\nChoose from the following options:\n'
                  '[1] Create a one-folder bundle containing an '
                  'executable (default)\n'
                  '[2] Create a one-file bundled executable\n'
                  '(1/2) ')

    return '--onefile' if onedf == '2' else '--onedir'
# --------------------------------------------------------#


def fetch_exec(binary=BINARY):
    """
    fetch the videomass binary on bin folder
    """
    if not os.path.exists(binary):  # binary
        sys.exit("ERROR: no file found named '%s'" % binary)
# --------------------------------------------------------#


def genspec(options, specfile=SPECFILE, addplist=None, script=SCRIPT):
    """
    Generate a videomass.spec file for platform in use.
    Support for the following platforms is expected:
            [Windows, Darwin, Linux]
    The videomass.spec file will be saved in the root directory
    of the videomass sources.
    To running videomass.spec is required ``pyinstaller``.
    To use videomass.spec type:
        `pyinstaller videomass.spec`
    or use this script with option -s to start the building by
    an existing videomass.spec file.
    """
    try:
        subprocess.run('pyi-makespec %s %s' % (options, script),
                       shell=True, check=True)
    except subprocess.CalledProcessError as err:
        sys.exit('\nERROR: %s\n' % err)

    if platform.system() == 'Darwin' and addplist is not None:
        with open(specfile, 'r', encoding='utf8') as specf:
            arr = specf.readlines()

        idx = arr.index("             bundle_identifier='com."
                        "jeanslack.videomass')\n")
        arr[idx] = ("             bundle_identifier='com."
                    "jeanslack.videomass',\n")
        newspec = ''.join(arr) + addplist
        with open(specfile, 'w', encoding='utf8') as specf:
            specf.write(newspec)
# --------------------------------------------------------#


def clean_buildingdirs(here=HERE):
    """
    called by run_pyinst().
    Asks the user if they want to clean-up building
    directories, usually "dist" and "build" dirs.
    """

    clean = input('Want you remove "dist" and "build" folders (y/n)? ')
    if clean in ('y', 'Y'):
        if os.path.exists(os.path.join(here, 'dist')):
            try:
                shutil.rmtree(os.path.join(here, 'dist'))
            except OSError as err:
                sys.exit("ERROR: %s" % (err.strerror))

        if os.path.exists(os.path.join(here, 'build')):
            try:
                shutil.rmtree(os.path.join(here, 'build'))
            except OSError as err:
                sys.exit("ERROR: %s" % (err.strerror))
# --------------------------------------------------------#


def run_pyinst(specfile=SPECFILE):
    """
    wrap `pyinstaller --clean videomass.spec`
    """
    if os.path.exists(specfile) and os.path.isfile(specfile):
        clean_buildingdirs()  # remove temp folders
        fetch_exec()  # fetch videomass binary
        time.sleep(1)
        try:
            subprocess.run('pyinstaller --clean %s' % specfile,
                           shell=True, check=True)
        except subprocess.CalledProcessError as err:
            sys.exit('\nERROR: %s\n' % err)

        print("\nSUCCESS: pyinstaller_setup.py: Build finished.\n")
    else:
        sys.exit("ERROR: no such file %s" % specfile)
# --------------------------------------------------------#


def make_portable(here=HERE):
    """
    Optionally, you can create a portable_data folder for Videomass
    stand-alone executable to keep all application data inside
    the program folder.
    Note:
       with `--onedir` option, the 'portable_data' directory should
       be inside the videomass directory.
        with `--onefile` option, the 'portable_data' directory should
        be next to the videomass directory.
    """
    portable = input('Do you want to keep all application data inside '
                     'the program folder? (makes stand-alone executable '
                     'fully portable and stealth) (y/n) ')
    if portable in ('y', 'Y'):
        portabledir = 'portable_data'
    else:
        return

    def makedir(datashare):
        """
        make portable_data folder
        """
        if not os.path.exists(datashare):
            try:
                os.mkdir(datashare)
            except OSError as err:
                sys.exit('ERROR: %s' % err)
            else:
                sys.exit('\nDONE: "portable_data" folder is created\n')
        else:
            sys.exit('INFO: "portable_data" folder already exists')

    if platform.system() == 'Windows':
        if os.path.exists(os.path.join(here, 'dist', 'Videomass.exe')):
            datashare = os.path.join(here, 'dist', portabledir)
        else:
            datashare = os.path.join(here, 'dist', 'Videomass', portabledir)

    elif platform.system() == 'Darwin':
        if os.path.exists(os.path.join(here, 'dist', 'Videomass.app')):
            datashare = os.path.join(here, 'dist', 'Videomass.app',
                                     'Contents', 'MacOS', portabledir)
        else:
            datashare = os.path.join(here, 'dist', portabledir)
    else:
        if os.path.isfile(os.path.join(here, 'dist', 'videomass')):
            datashare = os.path.join(here, 'dist', portabledir)
        else:
            datashare = os.path.join(here, 'dist', 'videomass', portabledir)

    makedir(datashare)
# --------------------------------------------------------#


def main():
    """
    Users inputs parser (positional/optional arguments)
    """
    def checkin():
        """
        """
        if not platform.system() in ('Windows', 'Darwin', 'Linux'):
            sys.exit("\nERROR: Unsupported platform. Maybe you "
                     "could create a 'spec' file using this command:\n"
                     "pyi-makespec [options] videomass.py\n"
                     )

        wrap = PyinstallerSpec(onefile_onedir())

        if platform.system() == 'Linux':
            getopts = wrap.linux_platform()
            genspec(getopts)

        elif platform.system() == 'Darwin':
            getopts = wrap.darwin_platform()
            genspec(getopts[0], addplist=getopts[1])

        elif platform.system() == 'Windows':
            getopts = wrap.windows_platform()
            genspec(getopts)
    # ----------------------------------------------#

    parser = argparse.ArgumentParser(
        description='Wrap the pyinstaller setup for Videomass application',)
    parser.add_argument(
        '-g', '--gen_spec',
        help="Generates a ready-to-use videomass.spec file.",
        action="store_true",
    )
    parser.add_argument(
        '-gb', '--genspec_build',
        help="Generate a videomass.spec file and start building bundle.",
        action="store_true",
    )
    parser.add_argument(
        '-s', '--start_build',
        help="Start the building bundle by an existing videomass.spec file.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.gen_spec:
        checkin()

    elif args.genspec_build:
        checkin()
        run_pyinst()
        make_portable()

    elif args.start_build:
        run_pyinst()
        make_portable()

    else:
        print("\nType 'pyinstaller_setup.py -h' for help.\n")
        return


if __name__ == '__main__':
    main()
