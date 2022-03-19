# -*- coding: UTF-8 -*-
"""
Name: ydl_downloader.py
Porpose: long processing task with youtube_dl python library
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.14.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
from threading import Thread
import itertools
import wx
from pubsub import pub
from videomass.vdms_io.make_filelog import logwrite
if 'youtube_dl' in sys.modules:
    import youtube_dl
elif 'yt_dlp' in sys.modules:
    import yt_dlp


class MyLogger():
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd315
    7df2457df7274d0c842421945#embedding-youtube-dl>
    """

    def __init__(self):
        """
        define instace attributes
        """
        self.msg = None

    def debug(self, msg):
        """
        Get debug messages
        """
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='DEBUG',
                     )
        self.msg = msg

    def warning(self, msg):
        """
        Get warning messages
        """
        msg = f'WARNING: {msg}'
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='WARNING',
                     )

    def error(self, msg):
        """
        Get error messages
        """
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='ERROR',
                     )
# -------------------------------------------------------------------------#


def my_hook(data):
    """
    progress_hooks is A list of functions that get called on
    download progress. See  `help(youtube_dl.YoutubeDL)`
    """
    if data['status'] == 'downloading':
        keys = ('_percent_str', '_total_bytes_str', '_speed_str', '_eta_str')

        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output='',
                     duration={x: data.get(x, 'N/A') for x in keys},
                     status='DOWNLOAD',)

    if data['status'] == 'finished':
        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count='',
                     fsource='',
                     destination='',
                     duration='',
                     end='ok',
                     )
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output='',
                     duration='Done downloading, now converting ...',
                     status='FINISHED',
                     )
# -------------------------------------------------------------------------#


class YdlDownloader(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output in real time during downloading and conversion .
    For a list of available options see:

    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L279>
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/options.py>

    or by help(youtube_dl.YoutubeDL)

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    FFMPEG_URL = appdata['ffmpeg_cmd']
    DOWNLOADER = appdata['downloader']

    if appdata['playlistsubfolder'] is True:
        SUBDIR = '%(uploader)s/%(playlist_title)s/%(playlist_index)s - '
    else:
        SUBDIR = ''

    def __init__(self, varargs, logname):
        """
        Attributes defined here:
        self.stop_work_thread:  process terminate value
        self.args['urls']:          urls list
        self.opt:           option dict data type to adding
        self.args['outdir']:     pathname destination
        self.args['code']:          Format Code, else empty string ''
        self.count:         increases progressive account elements
        self.args['countmax']:      length of urls items list
        self.args['logname']:       file name to log messages for logging
        """
        self.stop_work_thread = False  # process terminate
        self.opt = varargs[4]
        self.count = 0
        self.args = {'urls': varargs[1],
                     'code': varargs[6],
                     'outdir': varargs[3],
                     'logname': logname,
                     'countmax': len(varargs[1]),
                     }

        Thread.__init__(self)
        self.start()  # run()

    def run(self):
        """
        Apply the options passed by the user for the
        download process with youtube_dl

        """
        for url, code in itertools.zip_longest(self.args['urls'],
                                               self.args['code'],
                                               fillvalue='',
                                               ):
            if '/playlist' in url or not self.opt['noplaylist']:
                outtmpl = YdlDownloader.SUBDIR + self.opt['outtmpl']
            else:
                outtmpl = self.opt['outtmpl']

            format_code = code if code else self.opt['format']
            self.count += 1
            count = f"URL {self.count}/{self.args['countmax']}"

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source: {url}',
                         destination='',
                         duration=100,
                         end='',
                         )

            if self.stop_work_thread:
                break

            ydl_opts = {
                'compat_opts': 'all',
                'format': format_code,
                'extractaudio': self.opt['format'],
                'outtmpl': f"{self.args['outdir']}/{outtmpl}",
                'writesubtitles': self.opt['writesubtitles'],
                'subtitleslangs': self.opt['subtitleslangs'],
                'skip_download': self.opt['skip_download'],
                'addmetadata': self.opt['addmetadata'],
                'restrictfilenames': self.opt['restrictfilenames'],
                'ignoreerrors': True,
                'no_warnings': False,
                'writethumbnail': self.opt['writethumbnail'],
                'noplaylist': self.opt['noplaylist'],
                'playlist_items': self.opt['playlist_items'].get(url, None),
                'nooverwrites': self.opt['nooverwrites'],
                'no_color': True,
                'nocheckcertificate': self.opt['nocheckcertificate'],
                'ffmpeg_location': f'{YdlDownloader.FFMPEG_URL}',
                'postprocessors': self.opt['postprocessors'],
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
            }

            logwrite(ydl_opts, '', self.args['logname'])  # write log cmd

            if YdlDownloader.DOWNLOADER == 'youtube_dl':
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"{url}"])

            elif YdlDownloader.DOWNLOADER == 'yt_dlp':
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"{url}"])

        wx.CallAfter(pub.sendMessage, "END_EVT", msg=None)

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
