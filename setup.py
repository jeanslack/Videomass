#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# First release: Monday, July 7 10:00:47 2014
# 
#########################################################
# Name: setup.py
# Porpose: script for building Videomass2 executable.
# Platform: Mac OsX, Gnu/Linux, Microsoft Windows
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

from distutils.core import setup
from setuptools import setup
import platform
from glob import glob
import os
import shutil
from videomass2.vdms_SYS.msg_info import current_release
from videomass2.vdms_SYS.msg_info import descriptions_release

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
            'Environment :: Graphic',
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
            'Programming Language :: Python',
            'Topic :: Multimedia :: Video :: Conversion',
            'Topic :: Multimedia :: Sound/Audio :: Conversion',
            'Topic :: Utilities',
                ]

#---------------------------------------------------------------------#
def glob_files(pattern):
    """
    Useful function for globbing that iterate on directories and 
    files marked with wildcard and put in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]


#-----------------------------------------------------------------------#
def LINUX():
    """
    ------------------------------------------------
    setup of building package for Debian based distro
    ------------------------------------------------
    
    TOOLS: 
    apt-get install python-all python-stdeb fakeroot

    USAGE: 
    - for generate both source and binary packages :
        python setup.py --command-packages=stdeb.command bdist_deb
        
    - Or you can generate source packages only :
        python setup.py --command-packages=stdeb.command sdist_dsc
        
    RESOURCES:
    - look at there for major info:
        [https://pypi.python.org/pypi/stdeb]
        [http://shallowsky.com/blog/programming/python-debian-
         packages-w-stdeb.html]
    """
    
    # this is DATA_FILE structure: 
    # ('dir/file destination of the data', ['dir/file on current place sources']
    # even path must be relative-path
    DATA_FILES = [
        ('share/videomass2/config', glob_files('share/*.vdms')),
        ('share/videomass2/config', ['share/videomass2.conf', 'share/README']),
        ('share/videomass2/icons', ['art/icons/videomass2.png']),
        ('share/applications', ['art/videomass2.desktop']),
        ('share/pixmaps', ['art/icons/videomass2.png']),]
    
    # get all icons and icons docs
    for art in os.listdir('art/icons'):
        if art not in ['videomass2_wizard.png', 'videomass2.png']:
            tmp = "art/icons/" + art
            if os.path.exists(tmp):
                pathdoc = 'share/videomass2/icons/%s' % art
                DATA_FILES.append((pathdoc, glob_files('%s/*.md' % tmp)))
                DATA_FILES.append((pathdoc, glob_files('%s/*.txt' % tmp)))
            for size in ['18x18','24x24', '36x36']:
                if os.path.exists(tmp + '/' + size):
                    path =  tmp +  '/' + size
                    pathsize = 'share/videomass2/icons/%s/%s' % (art,size)
                    DATA_FILES.append((pathsize, glob_files('%s/*.png' % path)))
        
    # Get the locale files
    for loc_dir in os.listdir("locale"):
        if not 'videomass2.pot' in loc_dir:
            tmp = "locale/" + loc_dir + "/LC_MESSAGES"
            if os.path.isdir(tmp):
                tmp2 = tmp + "/videomass2.mo"
                if os.path.exists(tmp2):
                    DATA_FILES.append(('share/' + tmp, [tmp2]))
                    
    # Get the documents files
    for docs in  ["AUTHORS", "CHANGELOG",
                  "COPYING", "INSTALL", 
                  "README.md", "TODO"]:
        DATA_FILES.append(('share/videomass2', [docs]))
        

    DEPENDENCIES = ['python', 'wxPython',]
    EXTRA_DEPEND = {'':  [""],}
    
    setup(name = PRG_NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = EMAIL,
        url = WEBSITE,
        license = LICENSE,
        platforms = [ "Many" ],
        packages = ["videomass2", "videomass2/vdms_DIALOGS", 
                    "videomass2/vdms_IO", "videomass2/vdms_MAIN", 
                    "videomass2/vdms_PANELS", "videomass2/vdms_PROCESS",
                    "videomass2/vdms_SYS",
                    ],
        scripts = ['bin/videomass2'],
        data_files = DATA_FILES,
        classifiers = CLASSIFIERS,
        install_requires = DEPENDENCIES,
        extras_require = EXTRA_DEPEND,
        )

#-----------------------------------------------------------------------#
def OSX():
    """
    ------------------------------------------------
    py2app build script for videomass2
    ------------------------------------------------
    -Usage:
        python setup.py py2app --help

    -Usage for development and debug:
        python setup.py py2app -A
    and debug with terminal: 
        ./dist/Videomass2.app/Contents/MacOS/videomass2

    -Usage for building a redistributable version standalone:
        python setup.py py2app

    -look at there for major info:
    <https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>
    <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies>
    
    IF YOU WANT SET A VIRTUALENV environment need for build the .app:
    https://wiki.wxpython.org/wxPythonVirtualenvOnMac

    On Mac OSX, I installed wxpython with Homebrew using:

    brew install wxpython
    Change into your virtualenv site-packages directory:

    cd /venv/lib/python2.7/site-packages
    then link the wx.pth
     ln -s /usr/local/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/wx.pth wx.pth
     ln -s /usr/local/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/wx-3.0-osx_cocoa wx-3.0-osx_cocoa

    """
    PWD = os.getcwd() # current work directory path
    PATH_ICON = '%s/videomass.icns' % PWD
    RESOURCES = "%s/MacOsxSetup/FFMPEG_BIN" % PWD
    # this is DATA_FILE structure: 
    # ('dir/file') > destination of the data, ['dir/file'] > on current 
    # place sources even path must be relative-path

    set_1 = 'art/icons/Flat_Color_Icons'
    set_2 = 'art/icons/Material_Design_Icons_black'
    set_3 = 'art/icons/Material_Design_Icons_white'
    DATA_FILES = [('share', glob_files('share/*.vdms')),
            ('share', ['share/videomass2.conf']), 
            #('docs/HTML', glob_files('docs/HTML/*.html')), 
            ('art/icons', glob_files('art/icons/*.png')),

            ('%s' % set_1, glob_files('%s/*.md' % set_1)),
            ('%s/36x36' % set_1, glob_files('%s/36x36/*.png' % set_1)),
            ('%s/24x24' % set_1, glob_files('%s/24x24/*.png' % set_1)),
            ('%s/18x18' % set_1, glob_files('%s/18x18/*.png' % set_1)),

            ('%s' % set_2, glob_files('%s/*.txt' % set_2)),
            ('%s/36x36' % set_2, glob_files('%s/36x36/*.png' % set_2)),
            ('%s/24x24' % set_2, glob_files('%s/24x24/*.png' % set_2)),
            ('%s/18x18' % set_2, glob_files('%s/18x18/*.png' % set_2)),

            ('%s' % set_3, glob_files('%s/*.txt' % set_3)),
            ('%s/36x36' % set_3, glob_files('%s/36x36/*.png' % set_3)),

            ('', ['AUTHORS','BUGS','CHANGELOG','INSTALL','COPYING','TODO',
                  'README.md']),]
    
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

    #--------------- This is setup: --------------------#
    if os.path.exists('%s/Videomass2.py' % PWD):
        pass
    else:
        os.rename("videomass2","Videomass2.py")
        #shutil.copyfile('%s/videomass2' % PWD, '%s/Videomass2.py' % PWD)
    
    setup(app = ['Videomass2.py'],
        packages = ['vdms_DIALOGS','vdms_IO','vdms_MAIN',
                    'vdms_PANELS','vdms_PROCESS','vdms_SYS'],
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
        platforms=['MacOS X'],
        setup_requires = ["py2app"],
        )
#------------------------------------------------------------------------#
def WIN32():
    """
    ------------------------------------------------
    py2exe build script for videomass2
    ------------------------------------------------
    -Usage:
        python setup.py py2exe --help
    """
    import py2exe
    
    PWD = os.getcwd() # current work directory path
    if not os.path.exists('%s/Videomass2.py' % PWD):
        os.rename("videomass2","Videomass2.py")
        
    if not os.path.exists('%s/Win32Setup/ORIG' % PWD):
        shutil.copytree('%s/vdms_PROCESS' % PWD, '%s/Win32Setup/ORIG' % PWD)
        files = glob("%s/Win32Setup/*.py" % PWD)
        for cp in files:
            shutil.copy(cp, '%s/vdms_PROCESS' % PWD)
    
    set_1 = 'art/icons/Flat_Color_Icons'
    set_2 = 'art/icons/Material_Design_Icons_black'
    set_3 = 'art/icons/Material_Design_Icons_white'
    DATA_FILES = [('share', glob_files('share/*.vdms')),
                  ('share', glob_files('share/*.conf')),
                  #('docs/HTML', glob_files('docs/HTML/*.html')), 
                  ('art/icons', glob_files('art/icons/*.png')),

                  ('%s' % set_1, glob_files('%s/*.md' % set_1)),
                  ('%s/36x36' % set_1, glob_files('%s/36x36/*.png' % set_1)),
                  ('%s/24x24' % set_1, glob_files('%s/24x24/*.png' % set_1)),
                  ('%s/18x18' % set_1, glob_files('%s/18x18/*.png' % set_1)),

                  ('%s' % set_2, glob_files('%s/*.txt' % set_2)),
                  ('%s/36x36' % set_2, glob_files('%s/36x36/*.png' % set_2)),
                  ('%s/24x24' % set_2, glob_files('%s/24x24/*.png' % set_2)),
                  ('%s/18x18' % set_2, glob_files('%s/18x18/*.png' % set_2)),

                  ('%s' % set_3, glob_files('%s/*.txt' % set_3)),
                  ('%s/36x36' % set_3, glob_files('%s/36x36/*.png' % set_3)),
                  
                  ('', ['AUTHORS','BUGS','CHANGELOG','INSTALL',
                        'COPYING','TODO','README.md','videomass.ico',
                        'Win32Setup/NOTICE.rtf']),
                  ('FFMPEG_BIN', glob_files('Win32Setup/FFMPEG_BIN/*')),
                  ]
    includes = ["wx.lib.pubsub.*", "wx.lib.pubsub.core.*", 
                "wx.lib.pubsub.core.kwargs.*"
                ]
    excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses',
                'email', 'pywin.debugger', 'pywin.debugger.dbgcon',
                'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter'
                ]
    packages = ['vdms_DIALOGS','vdms_IO','vdms_MAIN',
                'vdms_PANELS','vdms_PROCESS','vdms_SYS'
                ]
    dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',
                    'tcl84.dll', 'tk84.dll'
                    ]
 
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
    windows = ['Videomass2.py'],
    data_files = DATA_FILES,
    icon_resources = [(1, "videomass.ico")],
    name = RLS_NAME,
    version = VERSION,
    description = DESCRIPTION,
    author = AUTHOR,
         )

#################################################################
if platform.system() == 'Darwin':
    OSX()
elif platform.system() == 'Linux':
    LINUX()
else:
    WIN32()
##################################################################
