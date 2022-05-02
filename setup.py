#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: setup.py
Porpose: script to setup Videomass.
Compatibility: Python3
Platform: all
Writer: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2014-2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.22.2021
Code checker: flake8, pylint
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
import sys
import platform
from setuptools import setup, find_packages
from videomass.vdms_sys.msg_info import current_release
from videomass.vdms_sys.msg_info import descriptions_release


def source_build():
    """
    Source/Build distributions

    """
    # Get info data
    crel = current_release()
    drel = descriptions_release()

    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:

        inst_req = ["wxpython>=4.0.7; platform_system=='Windows' or "
                    "platform_system=='Darwin'",
                    "PyPubSub>=4.0.3",
                    "youtube_dl>=2020.1.1",
                    "yt_dlp>=2021.9.2",
                    "requests>=2.21.0",
                    ]
        setup_req = ["setuptools>=47.1.1",
                     "wheel>=0.34.2",
                     "twine>=3.1.1"
                     ]
        with open('README.md', 'r', encoding='utf8') as readme:
            long_descript = readme.read()

        long_description_ct = 'text/markdown'

    else:  # e.g. to make a Debian source package, include wxpython.
        inst_req = ["wxpython>=4.0.7",
                    "PyPubSub>=4.0.3",
                    "requests>=2.21.0",
                    ]
        setup_req = []
        long_descript = drel[1]
        long_description_ct = 'text'

    excluded = ['']
    # pathnames must be relative-path
    if platform.system() == 'Windows':
        data_f = [('share/pixmaps', ['videomass/art/icons/videomass.png'])]

    elif platform.system() == 'Darwin':
        data_f = [('share/pixmaps', ['videomass/art/icons/videomass.png']),
                  ('share/man/man1', ['docs/man/man1/videomass.1.gz']),
                  ]
    else:
        data_f = [('share/applications',
                   ['videomass/art/io.github.jeanslack.videomass.desktop']),
                  ('share/metainfo',
                   ['io.github.jeanslack.videomass.appdata.xml']),
                  ('share/pixmaps', ['videomass/art/icons/videomass.png']),
                  ('share/icons/hicolor/48x48/apps',
                   ['videomass/art/icons/hicolor/48x48/apps/videomass.png',
                    'videomass/art/icons/hicolor/48x48/apps/videomass.xpm']),
                  ('share/icons/hicolor/256x256/apps',
                   ['videomass/art/icons/hicolor/256x256/apps/videomass.png']
                   ),
                  ('share/icons/hicolor/scalable/apps',
                   ['videomass/art/icons/hicolor/scalable/apps/'
                    'videomass.svg']),
                  ('share/man/man1', ['docs/man/man1/videomass.1.gz']),
                  ]
    setup(name=crel[1],
          version=crel[2],
          description=drel[0],
          long_description=long_descript,
          long_description_content_type=long_description_ct,
          author=crel[6][0],
          author_email=crel[7],
          url=crel[5],
          license=drel[2],
          platforms=["All"],
          packages=find_packages(exclude=excluded),
          data_files=data_f,
          package_data={"videomass": ["art/icons/*", "locale/*"]
                        },
          exclude_package_data={"videomass": ["art/videomass.icns",
                                              "art/videomass.ico",
                                              "locale/README",
                                              "locale/videomass.pot"
                                              ]
                                },
          include_package_data=True,
          zip_safe=False,
          python_requires=">=3.7.0, <4.0",
          install_requires=inst_req,
          setup_requires=setup_req,
          entry_points={'gui_scripts':
                        ['videomass = videomass.gui_app:main']},
          classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Natural Language :: Russian',
        'Natural Language :: Dutch',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Spanish',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    )


if __name__ == '__main__':
    source_build()
