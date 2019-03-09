#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#########################################################
# Name: setup.py
# Porpose: script to setup DrumsT
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (00) Feb 5 2019
#########################################################

# This file is part of DrumsT.

#    DrumsT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    DrumsT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with DrumsT.  If not, see <http://www.gnu.org/licenses/>.

#########################################################

#---- Imports ----#
from distutils.core import setup
from setuptools import setup, find_packages
import platform
from glob import glob
import os
import sys
import shutil
    
if platform.system() in ['Windows','Darwin']:
    REQUIRES = ['wxpython>=4.0.3"','PyPubSub>=4.0.0']
    
else:
    REQUIRES = []

#---- current work directory path ----#
PWD = os.getcwd() 

#---- Get info data ----#
from drumsT.drumsT_DATA.data_info import prg_info
cr = prg_info()
RLS_NAME = cr[0] # release name first letter is Uppercase
PRG_NAME = cr[1]
VERSION = cr[2]
RELEASE = cr[3]
COPYRIGHT = cr[4]
WEBSITE = cr[5]
AUTHOR = cr[6]
EMAIL = cr[7]
COMMENT = cr[8]
DESCRIPTION = cr[9]
LONG_DESCRIPTION = cr[10]
LICENSE = cr[11] # short license

#---- categorize with ----#
CLASSIFIERS = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X :: Cocoa',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
        'Topic :: Utilities',
                ]

#-----------------------------------------------------------------#
def glob_files(pattern):
    """
    Useful function for globbing that iterate on a pattern marked 
    with wildcard and put it in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]
#-----------------------------------------------------------------#

def AppendPackageFiles(data, baselocale):
    """
    Add all locale files to data list
    """
    # Get the locale files
    for loc_dir in os.listdir("locale"):
        if loc_dir not in ['drumst.pot', 'README', 'make_pot.sh']:
            tmp = "locale/" + loc_dir + "/LC_MESSAGES"
            if os.path.isdir(tmp):
                tmp2 = tmp + "/drumst.mo"
                if os.path.exists(tmp2):
                    data.append((baselocale + tmp, [tmp2]))
                    
    return data

#-----------------------------------------------------------------#

def SOURCE_BUILD():
    """
    Source/Build distributions
    
    USAGE:
        python setup.py sdist bdist_wheel
      
    * See the INSTALL file in the sources for major details

    """
    DATA_FILES = [ # even path must be relative-path
            ('share/drumst/config', ['share/drumsT.conf',]),
            ('share/drumst/icons', glob_files('art/*.png')),
            ('share/applications', ['art/drumst.desktop']),
            ('share/pixmaps', ['art/drumsT.png']),
            ('share/drumst', ['AUTHORS','BUGS',
                              'CHANGELOG','INSTALL',
                              'COPYING','TODO','README.md']),
            ]
    # get the package data
    DATA_FILES = AppendPackageFiles(DATA_FILES, 'share/',
                                    )
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
        scripts = ['bin/drumst'],
        data_files = DATA_FILES,
        classifiers = CLASSIFIERS,
        install_requires = REQUIRES,
        entry_points = {
        'console_scripts': ['drumst=drumsT.DrumsT:main'],},
        )
#-----------------------------------------------------------------#
if __name__ == '__main__':
    
    if 'sdist' or 'bdist_wheel' in sys.argv:
        SOURCE_BUILD()
