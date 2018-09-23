# -*- coding: UTF-8 -*-

#########################################################
# Name: msg_info.py
# Porpose: Version, Copyright, Description, etc strings organization
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

# creation date: 10 Nov. 2017
#########################################################

def current_release():
    """
    General info strings
    NOTE: number version > major number.minor number.micro number(patch number)
    the sub release a=alpha release, b=beta release, c= candidate release
    Example 19.1.1c1
    """

    Release_Name = 'Videomass2'
    Program_Name = 'videomass2'
    Version = '1.0.1'
    Release = 'Sept 23 2018'
    Copyright = u'© 2013-2018'
    Website = 'http://jeanslack.github.io/Videomass2/'
    Author = 'Gianluca Pernigotto (aka jeanslack)'
    Mail = '<jeanlucperni@gmail.com>'
    Comment = ("Thanks to:\n"
               "FFmpeg\n"
               "FFmpeg is a trademark of Fabrice Bellard, \n"
               "originator of the FFmpeg project.\n"
               "http://ffmpeg.org/")
               
              
    
    return (Release_Name, Program_Name, Version, Release, Copyright, 
            Website, Author, Mail, Comment)

def descriptions_release():
    """
    General info string 
    """
    Copyright = current_release()
    Author = current_release()
    Mail = current_release()

    short_d = (u"Videomass2 is a cross-platform GUI for FFmpeg.")
    
    long_d = ("-Videomass2- provides a graphical interface for\n "
              "managing audio and video streams through\n "
              "FFmpeg even in batch mode.")

    short_l = (u"GPL3 (Gnu Public License)")

    license = (u"Copyright - %s %s\n"
                "Author and Developer: %s\n"
                "Mail: %s\n\n"
                "Videomass2 is free software: you can redistribute\n"
                "it and/or modify it under the terms of the GNU General\n"
                "Public License as published by the Free Software\n"
                "Foundation, either version 3 of the License, or (at your\n"
                "option) any later version.\n\n"

                "Videomass2 is distributed in the hope that it\n"
                "will be useful, but WITHOUT ANY WARRANTY; without\n"
                "even the implied warranty of MERCHANTABILITY or\n" 
                "FITNESS FOR A PARTICULAR PURPOSE.\n" 
                "See the GNU General Public License for more details.\n\n"

                "You should have received a copy of the GNU General\n" 
                "Public License along with this program. If not, see\n" 
                "http://www.gnu.org/licenses/" %(Copyright[4],Author[6],
                                                Author[6],Mail[7]))
    
    return (short_d, long_d, short_l, license)

