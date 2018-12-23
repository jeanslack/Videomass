#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#########################################################
# Name: setup.py
# Porpose: script to setup Videomass2.
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
#########################################################

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (05) December 15 2018
#########################################################
"""
 Videomass2 Setup Script

 USAGE:

   1) Windows:
      - python setup.py py2exe

   2) MacOSX:
      - python setup.py py2app

   3) All
      - python setup.py [options * ]
      
 * See the INSTALL file in the sources for major details

"""

#---- Imports ----#
from distutils.core import setup
from setuptools import setup, find_packages
import platform
from glob import glob
import os
import sys
import shutil
from videomass2.vdms_SYS.msg_info import current_release, descriptions_release

#---- current work directory path ----#
PWD = os.getcwd() 

#---- Get info data ----#
cr = current_release()
RLS_NAME = cr[0] # release name first letter is Uppercase
PRG_NAME = cr[1]
VERSION = cr[2]
RELEASE = cr[3]
COPYRIGHT = cr[4]
WEBSITE = cr[5]
AUTHOR = cr[6]
EMAIL = cr[7]
COMMENT = cr[8]

dr = descriptions_release()
LICENSE = dr[2] # short license
DESCRIPTION = dr[0]
LONG_DESCRIPTION = dr[1]

CLASSIFIERS = [
            'Development Status :: 4 - Beta',
            'Environment :: MacOS X :: Cocoa',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Natural Language :: Italian',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.7',
            'Topic :: Multimedia :: Video :: Conversion',
            'Topic :: Multimedia :: Sound/Audio :: Conversion',
            'Topic :: Utilities',
                ]

#######################################################################
def glob_files(pattern):
    """
    Useful function for globbing that iterate on a pattern marked 
    with wildcard and put it in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]


########################################################################
def AppendPackageFiles(data, baseicons, baselocale):
    """
    Add all icons and all locale files to data list
    """
    # get all icons and icons docs
    for art in os.listdir('art/icons'):
        if art not in ['videomass2_wizard.png', 'videomass2.png']:
            tmp = "art/icons/" + art
            if os.path.exists(tmp):
                pathdoc = '%s/%s' % (baseicons,art)
                data.append((pathdoc, glob_files('%s/*.md' % tmp)))
                data.append((pathdoc, glob_files('%s/*.txt' % tmp)))
            for size in ['18x18','24x24', '36x36']:
                if os.path.exists(tmp + '/' + size):
                    path =  tmp +  '/' + size
                    pathsize = '%s/%s/%s' % (baseicons,art,size)
                    print pathsize
                    data.append((pathsize, glob_files('%s/*.png' % path)))
        
    # Get the locale files
    for loc_dir in os.listdir("locale"):
        if loc_dir not in ['videomass2.pot', 'README', 'make_pot.sh']:
            tmp = "locale/" + loc_dir + "/LC_MESSAGES"
            if os.path.isdir(tmp):
                tmp2 = tmp + "/videomass2.mo"
                if os.path.exists(tmp2):
                    data.append((baselocale + tmp, [tmp2]))
                    
    return data

########################################################################
def SOURCE_BUILD():
    """
    Source/Build distributions

    """
    DATA_FILES = [ # even path must be relative-path
            ('share/videomass2/config', glob_files('share/*.vdms')),
            ('share/videomass2/config', ['share/videomass2.conf',
                                        'share/videomassWin32.conf',
                                        'share/README']),
            ('share/videomass2/icons', glob_files('art/icons/*.png')),
            ('share/applications', ['art/videomass.icns',
                                    'art/videomass.ico',
                                    'art/videomass2.desktop']),
            ('share/pixmaps', ['art/icons/videomass2.png']),
            ('share/videomass2', ['AUTHORS','BUGS',
                                'CHANGELOG','INSTALL',
                                'COPYING','TODO','README.md']),
            ]
    # get the package data
    DATA_FILES = AppendPackageFiles(DATA_FILES, 'share/videomass2/icons', 'share/')

    setup(name = PRG_NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = open('README.md').read(),
        long_description_content_type='text/markdown',
        author = AUTHOR,
        author_email = EMAIL,
        url = WEBSITE,
        license = LICENSE,
        platforms = ["All"],
        packages = find_packages(),
        scripts = ['bin/videomass2'],
        data_files = DATA_FILES,
        classifiers = CLASSIFIERS,
        install_requires = ['wxPython',],
        )

########################################################################
def OSX():
    """
    build videomass2.app

    """
    PATH_ICON = '%s/art/videomass.icns' % PWD
    RESOURCES = "%s/MacOsxSetup/FFMPEG_BIN" % PWD

    # place sources even path must be relative-path
    data = [('share', glob_files('share/*.vdms')),
            ('share', ['share/videomass2.conf']), 
            ('art/icons', glob_files('art/icons/*.png')),
            ('', ['AUTHORS', 'BUGS',
                  'CHANGELOG', 'INSTALL',
                  'COPYING', 'TODO', 'README.md']),
            ]
    # get the package data
    DATA_FILES = AppendPackageFiles(data, 'art/icons/', '')
    
    OPTIONS = {'argv_emulation' : False,
               'resources' : RESOURCES,
               'iconfile' : PATH_ICON, 
               'site_packages': True,
               'optimize' : '2',
               'plist': {
               #'LSEnvironment':'$0',
               'CFBundleName': RLS_NAME,
               'CFBundleDisplayName': RLS_NAME,
               'CFBundleGetInfoString': "Making Videomass2",
               'CFBundleIdentifier': "com.jeanslack.videomass2",
               'CFBundleVersion': "%s" % VERSION,
               'CFBundleShortVersionString': "%s" % VERSION,
               'NSHumanReadableCopyright': u"Copyright %s, "
                                            "Gianluca Pernigotto, "
                                            "All Rights Reserved" % COPYRIGHT,
                            }
                }
               
    if not os.path.exists('%s/bin/Videomass2.py' % PWD):
        shutil.copyfile('%s/bin/videomass2' % PWD, 
                        '%s/bin/Videomass2.py' % PWD
                        )
    #--------------- setup: --------------------#
    setup(app = ['bin/Videomass2.py'],
        packages = find_packages(),
        include = ['python', 'wx',],
        name = RLS_NAME,
        version = VERSION,
        options = {'py2app': OPTIONS},
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        classifiers = CLASSIFIERS,
        author = AUTHOR,
        author_email = EMAIL,
        url = WEBSITE,
        license = LICENSE,
        data_files =  DATA_FILES,
        platforms = ['MacOS X'],
        setup_requires = ["py2app"],
        )
        
########################################################################
def WIN32():
    """
    build videomass2.exe
    
    -Usage:
        python setup.py py2exe --help

    """
    import py2exe
    
    if not os.path.exists('%s/bin/Videomass2.py' % PWD):
        shutil.copyfile('%s/bin/videomass2' % PWD, 
                        '%s/bin/Videomass2.py' % PWD
                        )

    data = [('share', glob_files('share/*.vdms')),
            ('share', glob_files('share/*.conf')), 
            ('art/icons', glob_files('art/icons/*.png')),
            ('', ['art/videomass.ico']),
            ('', ['AUTHORS', 'BUGS',
                  'CHANGELOG', 'INSTALL',
                  'COPYING', 'TODO', 'README.md',
                  'Win32Setup/NOTICE.rtf']),
            ('FFMPEG_BIN', glob_files('Win32Setup/FFMPEG_BIN/*')),
             ]
    # get the package data
    DATA_FILES = AppendPackageFiles(data, 'art/icons/', '')
                    
    includes = ["wx.lib.pubsub.*", "wx.lib.pubsub.core.*", 
                "wx.lib.pubsub.core.kwargs.*"
                ]
    excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses',
                'email', 'pywin.debugger', 'pywin.debugger.dbgcon',
                'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter'
                ]
    packages = find_packages()
    dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',
                    'tcl84.dll', 'tk84.dll'
                    ]
    #--------------- Setup: --------------------#
    setup(options = {"py2exe": {"compressed": 2, 
                                "optimize": 2,
                                "includes": includes,
                                "excludes": excludes,
                                "packages": packages,
                                "dll_excludes": dll_excludes,
                                "bundle_files": 3,
                                "dist_dir": "dist",
                                "xref": False,
                                "skip_archive": False,
                                "ascii": False,
                                "custom_boot_script": '',
                                }
                    },
    console = [],
    windows = ['bin/Videomass2.py'],
    data_files = DATA_FILES,
    icon_resources = [(1, "art/videomass.ico")],
    name = RLS_NAME,
    version = VERSION,
    description = DESCRIPTION,
    author = AUTHOR,
         )

########################################################################

if __name__ == '__main__':
    if platform.system() == 'Windows' and 'py2exe' in sys.argv:
        WIN32()
    elif platform.system() == 'Darwin' and 'py2app' in sys.argv:
        OSX()
    else:
        SOURCE_BUILD()
