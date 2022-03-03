# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Porpose: input/output redirection to processes (aka threads)
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.02.2022
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
import os
import requests
import wx
from videomass.vdms_threads.ffplay_file import FilePlay
from videomass.vdms_threads import (ffplay_url,
                                    generic_downloads,
                                    appimage_updater,
                                    )
from videomass.vdms_threads.ffprobe import ffprobe
from videomass.vdms_threads.volumedetect import VolumeDetectThread
from videomass.vdms_threads.check_bin import (ff_conf,
                                              ff_formats,
                                              ff_codecs,
                                              ff_topics,
                                              )
from videomass.vdms_threads.opendir import browse
from videomass.vdms_threads.ydl_extractinfo import YdlExtractInfo

from videomass.vdms_frames import (ffmpeg_conf,
                                   ffmpeg_formats,
                                   ffmpeg_codecs,
                                   )
from videomass.vdms_dialogs.widget_utils import PopupDialog
from videomass.vdms_io.make_filelog import make_log_template


def stream_info(title, filepath):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    get = wx.GetApp()
    try:
        with open(filepath, encoding='utf8'):
            miniframe = Mediainfo(title,
                                  filepath,
                                  get.appset['ffprobe_cmd'],
                                  get.appset['ostype'],
                                  )
            miniframe.Show()

    except IOError:
        wx.MessageBox(_("File does not exist or is invalid:  %s") % (
            filepath), "Videomass", wx.ICON_EXCLAMATION, None)
# -----------------------------------------------------------------------#


def stream_play(filepath, tseq, param, autoexit):
    """
    Call Thread for playback with ffplay
    """
    get = wx.GetApp()  # get data from bootstrap
    tseq = tseq if tseq != "-ss 00:00:00.000 -t 00:00:00.000" else ''
    try:
        with open(filepath, encoding='utf8'):
            FilePlay(filepath,
                     tseq,
                     param,
                     get.appset['logdir'],
                     get.appset['ffplay_cmd'],
                     get.appset['ffplayloglev'],
                     get.appset['ffplay+params'],
                     autoexit
                     )
            # thread.join() > attende fine thread, se no ritorna subito
            # error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or is invalid:  %s") % (
            filepath), "Videomass", wx.ICON_EXCLAMATION, None)
        return
# -----------------------------------------------------------------------#


def url_play(url, quality, timestamp, autoexit, ssl):
    """
    directs to the corresponding thread for playing
    online media streams.

    NOTE I'm looking for a way to tell the youtube_dl thread to terminate
    (gracefully or not, whatever) when the user clicks the "stop" button.
    The command-line version of youtube_dl just catches KeyboardInterrupt
    and terminates, but I've found no documentation on how to do this
    cleanly (if there's a way at all) when using the embedded module.
    So I'm still forced to use youtube-dl with the command-line and
    subprocess module.
    See https://github.com/ytdl-org/youtube-dl/issues/16175

    """
    ffplay_url.Streaming(timestamp, autoexit, ssl, url, quality)

# -----------------------------------------------------------------------#


def probe_getinfo(filename):
    """
    Get data stream informations during dragNdrop action.
    It is called by MyListCtrl(wx.ListCtrl) only.
    Return tuple object with two items: (data, None) or (None, error).
    """
    get = wx.GetApp()
    probe = ffprobe(filename, get.appset['ffprobe_cmd'],
                    hide_banner=None, pretty=None)

    return probe
# -------------------------------------------------------------------------#


def volume_detect_process(filelist, time_seq, audiomap):
    """
    Run thread to get audio peak level data and show a
    pop-up dialog with message.
    """
    get = wx.GetApp()
    thread = VolumeDetectThread(time_seq,
                                filelist,
                                audiomap,
                                get.appset['logdir'],
                                get.appset['ffmpeg_cmd']
                                )
    dlgload = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("Wait....\nAudio peak analysis."))
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()

    return data
# -------------------------------------------------------------------------#


def test_conf():
    """
    Call *check_bin.ffmpeg_conf* to get data to test the building
    configurations of the installed or imported FFmpeg executable
    and send it to dialog box.

    """
    get = wx.GetApp()
    out = ff_conf(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    if 'Not found' in out[0]:
        wx.MessageBox(f"\n{out[1]}", "Videomass", wx.ICON_ERROR, None)
        return

    miniframe = ffmpeg_conf.Checkconf(out,
                                      get.appset['ffmpeg_cmd'],
                                      get.appset['ffprobe_cmd'],
                                      get.appset['ffplay_cmd'],
                                      get.appset['ostype'],
                                      )
    miniframe.Show()
# -------------------------------------------------------------------------#


def test_formats():
    """
    Call *check_bin.ff_formats* to get available formats by
    imported FFmpeg executable and send it to dialog box.

    """
    get = wx.GetApp()
    diction = ff_formats(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    if 'Not found' in diction:
        wx.MessageBox(f"\n{diction['Not found']}", "Videomass",
                      wx.ICON_ERROR,
                      None)
        return

    miniframe = ffmpeg_formats.FFmpeg_formats(diction, get.appset['ostype'])
    miniframe.Show()
# -------------------------------------------------------------------------#


def test_codecs(type_opt):
    """
    Call *check_bin.ff_codecs* to get available encoders
    and decoders by FFmpeg executable and send it to
    corresponding dialog box.

    """
    get = wx.GetApp()
    diction = ff_codecs(get.appset['ffmpeg_cmd'],
                        type_opt,
                        get.appset['ostype']
                        )
    if 'Not found' in diction:
        wx.MessageBox(f"\n{diction['Not found']}", "Videomass",
                      wx.ICON_ERROR,
                      None)
        return

    miniframe = ffmpeg_codecs.FFmpeg_Codecs(diction,
                                            get.appset['ostype'],
                                            type_opt
                                            )
    miniframe.Show()
# -------------------------------------------------------------------------#


def findtopic(topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic..

    """
    get = wx.GetApp()
    retcod = ff_topics(get.appset['ffmpeg_cmd'], topic, get.appset['ostype'])

    if 'Not found' in retcod[0]:
        notf = (f"\n{retcod[1]}")
        return notf

    return retcod[1]
# -------------------------------------------------------------------------#


def openpath(where):
    """
    Call vdms_threads.opendir.browse to open file browser into
    configuration directory or log directory.

    """
    get = wx.GetApp()
    ret = browse(get.appset['ostype'], where)
    if ret:
        wx.MessageBox(ret, 'Videomass', wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def youtubedl_getstatistics(url, ssl):
    """
    Call `YdlExtractInfo` thread to extract data info.
    During this process a wait pop-up dialog is shown.

    Returns a generator.

    Usage example without pop-up dialog:
        thread = YdlExtractInfo(url)
        thread.join()
        data = thread.data
        yield data
    """
    thread = YdlExtractInfo(url, ssl)
    dlgload = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("Wait....\nRetrieving required data."))
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()
    yield data
# --------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API:
        https://developer.github.com/v3/repos/releases/#get-the-latest-release

    see keyname examples here:
    <https://api.github.com/repos/jeanslack/Videomass/releases>

    """
    try:
        response = requests.get(url)
        not_found = None, None

    except Exception as err:
        not_found = 'request error:', err

    else:

        try:
            version = response.json()[f"{keyname}"]

        except Exception as err:
            not_found = 'response error:', err

    if not_found[0]:
        return not_found

    return version, None
# --------------------------------------------------------------------------#


def get_presets(url, dest, msg):
    """
    get latest Videomass presets
    """
    thread = generic_downloads.FileDownloading(url, dest)
    dlgload = PopupDialog(None, _("Videomass - Downloading..."), msg)
    dlgload.ShowModal()
    # thread.join()
    status = thread.data
    dlgload.Destroy()

    return status
# --------------------------------------------------------------------------#


def appimage_update(appimage, script):
    """
    Call appropriate thread to update Python package
    inside Videomass AppImage.
    """
    get = wx.GetApp()  # get data from bootstrap
    logname = 'AppImage_Updates.log'
    logfile = os.path.join(get.appset['logdir'], logname)
    make_log_template(logname, get.appset['logdir'])  # write log file first

    thread = appimage_updater.AppImageUpdate(appimage, script, logfile)

    waitmsg = _('Be patient...\nthis can take a few minutes.')

    dlgload = PopupDialog(None, _("Videomass - Updating..."), waitmsg)
    dlgload.ShowModal()
    # thread.join()
    update = thread.status
    dlgload.Destroy()

    if update:
        return update

    ret = None
    with open(logfile, 'r', encoding='utf8') as fln:
        for line in fln:
            if '**Successfully updated**\n' in line:
                ret = 'success'
    return 'success' if ret == 'success' else 'error'
# --------------------------------------------------------------------------#
