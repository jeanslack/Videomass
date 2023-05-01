# -*- coding: UTF-8 -*-
"""
Name: msg_info.py
Porpose: Gets version, copyr and program Description
Compatibility: Python3, Python2
author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
lic: GPL3
Rev: Jan.21.2023
Code checker: flake8, pylint

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


def current_release():
    """
    General info strings
    NOTE: number version > major number.minor number.micro
    number(patch number) the sub release a=alpha release, b=beta
    release, c= candidate release
    Example 19.1.1c1
    """
    release_name = 'Videomass'
    program_name = 'videomass'
    version = '5.0.2'
    release = 'released'
    copyr = '2013-2023'
    website = 'http://jeanslack.github.io/Videomass/'
    author = ('Gianluca Pernigotto', '(aka jeanslack)')
    mail = 'jeanlucperni@gmail.com'
    comment = ("\nThanks to:\n"
               "- Python <https://www.python.org/>, programming language\n"
               "- wxPython <https://wxpython.org/>, cross-platform\n"
               "GUI toolkit for the Python language\n"
               "- FFmpeg, FFmpeg is a trademark of Fabrice Bellard, \n"
               "originator of the FFmpeg project:\n"
               "<http://ffmpeg.org/>\n"
               "- yt-dlp: <https://github.com/yt-dlp/yt-dlp>\n"
               "Download videos from YouTube and more sites\n"
               )
    return (release_name, program_name, version, release,
            copyr, website, author, mail, comment)


def descriptions_release():
    """
    General info string
    """
    copyr = current_release()
    author = current_release()
    mail = current_release()

    short_d = "Videomass is a cross-platform GUI for FFmpeg and yt-dlp"

    long_d = """
Videomass is a powerful, multitasking and cross-platform graphical user
interface (GUI) for FFmpeg and yt-dlp. It offers a wide range of features and
functions, making it a comprehensive software solution.

Videomass is written in Python3 using the wxPython4-Phoenix toolkit.
"""

    short_l = "GPL3 (Gnu Public License)"

    lic = (f"Copyleft - all rights reversed - {copyr[4]} {author[6][0]}\n"
           f"Author and developer: {author[6][0]} {author[6][1]}\n"
           f"Mail: {mail[7]}\n\n"
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
           "http://www.gnu.org/licenses/"
           )
    return (short_d, long_d, short_l, lic)
