# -*- coding: UTF-8 -*-
# Name: msg_info.py
# Porpose: Gets Version, Copyright and program Description
# Compatibility: Python3, Python2
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Feb.03.2021 *PEP8 compatible*
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


def current_release():
    """
    General info strings
    NOTE: number version > major number.minor number.micro
    number(patch number) the sub release a=alpha release, b=beta
    release, c= candidate release
    Example 19.1.1c1
    """
    Release_Name = 'Videomass'
    Program_Name = 'videomass'
    Version = '3.4.1'
    Release = 'April 16 2021'
    Copyright = '2013-2021'
    Website = 'http://jeanslack.github.io/Videomass/'
    Author = ('Gianluca Pernigotto', '(aka jeanslack)')
    Mail = 'jeanlucperni@gmail.com'
    Comment = ("\nThanks to:\n"
               "- Python <https://www.python.org/>, programming language\n"
               "- wxPython <https://wxpython.org/>, cross-platform\n"
               "GUI toolkit for the Python language\n"
               "- FFmpeg, FFmpeg is a trademark of Fabrice Bellard, \n"
               "originator of the FFmpeg project:\n"
               "<http://ffmpeg.org/>\n"
               "- youtube-dl: <http://ytdl-org.github.io/youtube-dl\n"
               "Download videos from YouTube and more sites\n"
               )
    return (Release_Name, Program_Name, Version, Release,
            Copyright, Website, Author, Mail, Comment)


def descriptions_release():
    """
    General info string
    """
    Copyright = current_release()
    Author = current_release()
    Mail = current_release()

    short_d = ("Videomass is a cross-platform GUI for FFmpeg and youtube-dl")

    long_d = ("""
Videomass is a cross-platform GUI designed for FFmpeg enthusiasts who need to
manage custom profiles to automate transcoding processes.

It is based on an advanced use of presets and profiles in order to use most of
the FFmpeg commands without limits of formats and codecs.

It features graphical tools for viewing, analyzing and processing multimedia
streams and downloading videos via youtube-dl.

Videomass is written in Python3 with the wxPython-Phoenix toolkit.
""")

    short_l = ("GPL3 (Gnu Public License)")

    license = ("Copyright - %s %s\n"
               "Author and Developer: %s %s\n"
               "Mail: %s\n\n"
               "Videomass is free software: you can redistribute\n"
               "it and/or modify it under the terms of the GNU General\n"
               "Public License as published by the Free Software\n"
               "Foundation, either version 3 of the License, or (at your\n"
               "option) any later version.\n\n"

               "Videomass is distributed in the hope that it\n"
               "will be useful, but WITHOUT ANY WARRANTY; without\n"
               "even the implied warranty of MERCHANTABILITY or\n"
               "FITNESS FOR A PARTICULAR PURPOSE.\n"
               "See the GNU General Public License for more details.\n\n"

               "You should have received a copy of the GNU General\n"
               "Public License along with this program. If not, see\n"
               "http://www.gnu.org/licenses/" % (Copyright[4],
                                                 Author[6][0],
                                                 Author[6][0],
                                                 Author[6][1],
                                                 Mail[7]))
    return (short_d, long_d, short_l, license)
