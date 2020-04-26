#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import PyInstaller.__main__

PWD = os.getcwd()

if platform.system() == 'Windows':
    PyInstaller.__main__.run([
        '--name=Videomass',
        '--windowed',
        '--add-data=%s;art' % os.path.join('%s' % PWD, 'art'),
        '--add-data=%s;locale' % os.path.join('%s' % PWD, 'locale'),
        '--add-data=%s;share' % os.path.join('%s' % PWD, 'share'),
        '--add-data=%s;FFMPEG_BIN' % os.path.join('%s' % PWD, 'Win32Setup',
                                                              'FFMPEG_BIN'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'Win32Setup','NOTICE.rtf'),
        # doc
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'AUTHORS'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'BUGS'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'CHANGELOG'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'COPYING'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'INSTALL'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'README.md'),
        '--add-data=%s;DOC' % os.path.join('%s' % PWD, 'TODO'),
        '--icon=%s' % os.path.join('%s' % PWD, 'art', 'videomass.ico'),
                                                      'videomass',])
elif platform.system() == 'Darwin':
    PyInstaller.__main__.run([
        '--name=Videomass',
        '--windowed',
        #'--onefile',
        '--osx-bundle-identifier=com.jeanslack.videomass',
        '--add-data=%s:art' % os.path.join('%s' % PWD, 'art'),
        '--add-data=%s:locale' % os.path.join('%s' % PWD, 'locale'),
        '--add-data=%s:share' % os.path.join('%s' % PWD, 'share'),
        '--add-data=%s:videomass3' % os.path.join('%s' % PWD, 'videomass3'),
        '--add-data=%s:FFMPEG_BIN' % os.path.join('%s' % PWD, 'MacOsxSetup',
                                                              'FFMPEG_BIN'),
        # doc
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'AUTHORS'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'BUGS'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'CHANGELOG'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'COPYING'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'INSTALL'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'README.md'),
        '--add-data=%s:DOC' % os.path.join('%s' % PWD, 'TODO'),
        '--icon=%s' % os.path.join('%s' % PWD, 'art', 'videomass.icns'),
                                                      'videomass',
        ])

# add to videomass.spec
#info_plist={
#                   # 'LSEnvironment': '$0',
#                   'NSPrincipalClass': 'NSApplication',
#                   'NSAppleScriptEnabled': False,
#                   'CFBundleName': 'Videomass',
#                   'CFBundleDisplayName': 'Videomass',
#                   'CFBundleGetInfoString': "Making Videomass",
#                   'CFBundleIdentifier': "com.jeanslack.videomass",
#                   'CFBundleVersion': '1.6.1',
#                   'CFBundleShortVersionString': '1.6.1',
#                   'NSHumanReadableCopyright': 'Copyright © 2013-2019, '
#                                            'Gianluca Pernigotto, '
#                                            'All Rights Reserved',
#                                            })
