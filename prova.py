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
import platform
from glob import glob
import os
import shutil


#---------------------------------------------------------------------#
def glob_files(pattern):
    """
    Useful function for globbing that iterate on directories and 
    files marked with wildcard and put in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]
#-----------------------------------------------------------------------#
def main():

    #set_1 = ['share/videomass2/icons/Flat_Color_Icons', 
             #'art/icons/Flat_Color_Icons']
    #set_2 = ['share/videomass2/icons/Material_Design_Icons_black', 
             #'art/icons/Material_Design_Icons_black']
    #set_3 = ['share/videomass2/icons/Material_Design_Icons_white', 
             #'art/icons/Material_Design_Icons_white']
    #DATA_FILES = [
        #('share/videomass2/config', glob_files('share/*.vdms')),
        #('share/videomass2/config', ['share/videomass2.conf', 'share/README']),
        #('share/videomass2/icons', ['art/icons/videomass2.png']),
        #('%s' % set_1[0], glob_files('%s/*.md' % set_1[1])),
        #('%s/36x36' % set_1[0], glob_files('%s/36x36/*.png' % set_1[1])),
        #('%s/24x24' % set_1[0], glob_files('%s/24x24/*.png' % set_1[1])),
        #('%s/18x18' % set_1[0], glob_files('%s/18x18/*.png' % set_1[1])),
        
        #('%s' % set_2[0], glob_files('%s/*.txt' % set_2[1])),
        #('%s/36x36' % set_2[0], glob_files('%s/36x36/*.png' % set_2[1])),
        #('%s/24x24' % set_2[0], glob_files('%s/24x24/*.png' % set_2[1])),
        #('%s/18x18' % set_2[0], glob_files('%s/18x18/*.png' % set_2[1])),
        
        #('%s' % set_3[0], glob_files('%s/*.txt' % set_3[1])),
        #('%s/36x36' % set_3[0], glob_files('%s/36x36/*.png' % set_3[1])),
        
        #('share/applications', ['art/videomass2.desktop']),
        #('share/pixmaps', ['art/icons/videomass2.png']),]
    
    #DATA_FILES = [
        #('share/videomass2/config', glob_files('share/*.vdms')),
        #('share/videomass2/config', ['share/videomass2.conf', 'share/README']),
        #('share/videomass2/icons', ['art/icons/videomass2.png']),
        #('share/applications', ['art/videomass2.desktop']),
        #('share/pixmaps', ['art/icons/videomass2.png']),]
    DATA_FILES = []
    
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
                    print pathsize
                    #pathsys = 'share/videomass2/icons/%s' % art
                    DATA_FILES.append((pathsize, glob_files('%s/*.png' % path)))
                    #print l
    print DATA_FILES
        
main()
                    
