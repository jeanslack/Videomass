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

# Rev (01) September 24 2014
# Rev (02) January 21 2015
# Rev (03) May 04 2015
# Rev (04) Nov 10 2017
# Rev (05) Sept 3 2018
#########################################################

from distutils.core import setup
from setuptools import setup
import platform
from glob import glob
import os
import shutil
from vdms_SYS.msg_info import current_release, descriptions_release

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

#---------------------------------------------------------------------#
def glob_files(pattern):
    """
    Useful function for globbing that iterate on directories and 
    files marked with wildcard and put in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]

#---------------------------------------------------------------------#
def LINUX_SLACKWARE(id_distro, id_version):
    """
    ------------------------------------------------
    setup of building package for Slackware
    ------------------------------------------------
    
    REQUIRED TOOLS: 
    pysetuptools
    
    USAGE: 
    Use in a SlackBuild combination
    """
    setup(name = PRG_NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = EMAIL,
        url = WEBSITE,
        license = LICENSE,
        platforms = ['Gnu/Linux (%s %s)' % (id_distro, id_version)],
        packages = ['vdms_DIALOGS','vdms_IO','vdms_MAIN',
                    'vdms_PANELS','vdms_PROCESS','vdms_SYS'],
        scripts = ['videomass2']
        )
#-----------------------------------------------------------------------#
def LINUX_DEBIAN_UBUNTU(id_distro, id_version):
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
        ('share/videomass2/icons', glob_files('art/*.png')),
        ('share/videomass2/icons/36x36', glob_files('art/icons/36x36/*.png')),
        ('share/videomass2/icons/24x24', glob_files('art/icons/24x24/*.png')),
        ('share/videomass2/icons/18x18', glob_files('art/icons/18x18/*.png')),
        ('share/applications', ['videomass2.desktop']),
        ('share/pixmaps', ['art/videomass2.png']),
        #('share/doc/python-videomass2/HTML', glob_files('docs/HTML/*.html')),
                ]
    
    DEPENDENCIES = ['python', 'wxpython', 'ffmpeg']
    #EXTRA_DEPEND = {'ffmpeg':  ["ffmpeg"],}
    
    setup(name = PRG_NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = EMAIL,
        url = WEBSITE,
        license = LICENSE,
        platforms = ['Gnu/Linux (%s %s)' % (id_distro, id_version)],
        packages = ['vdms_DIALOGS','vdms_IO','vdms_MAIN',
                    'vdms_PANELS','vdms_PROCESS','vdms_SYS'],
        scripts = ['videomass2'],
        data_files = DATA_FILES,
        install_requires = DEPENDENCIES,
        extras_require = EXTRA_DEPEND
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
    OSX_CLASSIFIERS = [
                    'Development Status :: %s' % (VERSION),
                    'Environment :: Graphic',
                    'Environment :: MacOS X :: Cocoa',
                    'Intended Audience :: Users',
                    'License :: %s' %(LICENSE),
                    'Natural Language :: English',
                    'Operating System :: MacOS :: MacOS X',
                    'Programming Language :: Python',
                    ]
    RESOURCES = "%s/MacOsxSetup/FFMPEG_BIN" % PWD
    # this is DATA_FILE structure: 
    # ('dir/file') > destination of the data, ['dir/file'] > on current 
    # place sources even path must be relative-path
    DATA_FILES = [('share', glob_files('share/*.vdms')),
            ('share', ['share/videomass2.conf']), 
            #('docs/HTML', glob_files('docs/HTML/*.html')), 
            ('art', glob_files('art/*.png')),
            ('art/icons/36x36', glob_files('art/icons/36x36/*.png')),
            ('art/icons/24x24', glob_files('art/icons/24x24/*.png')),
            ('art/icons/18x18', glob_files('art/icons/18x18/*.png')),
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
        classifiers = OSX_CLASSIFIERS,
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
    
    DATA_FILES = [('share', glob_files('share/*.vdms')),
                  ('share', glob_files('share/*.conf')),
                  #('docs/HTML', glob_files('docs/HTML/*.html')), 
                  ('art', glob_files('art/*.png')),
                  ('art/icons/36x36', glob_files('art/icons/36x36/*.png')),
                  ('art/icons/24x24', glob_files('art/icons/24x24/*.png')),
                  ('art/icons/18x18', glob_files('art/icons/18x18/*.png')),
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
    dist_name = platform.linux_distribution()[0]
    dist_version = platform.linux_distribution()[1]
    
    if dist_name == 'Slackware ':
        LINUX_SLACKWARE(dist_name, dist_version)
    else:
        LINUX_DEBIAN_UBUNTU(dist_name, dist_version)
else:
    WIN32()
##################################################################
