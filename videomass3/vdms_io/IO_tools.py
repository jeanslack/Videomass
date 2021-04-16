# -*- coding: UTF-8 -*-
# Name: IO_tools.py
# Porpose: input/output redirection to processes (aka threads)
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.28.2020 *PEP8 compatible*
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

import wx
import os
import shutil
import stat
import requests
from videomass3.vdms_threads.ffplay_file import File_Play
from videomass3.vdms_threads import (ffplay_url_exec,
                                     # ffplay_url_lib,
                                     generic_downloads,
                                     youtubedlupdater,
                                     )
from videomass3.vdms_threads.ffprobe_parser import FFProbe
from videomass3.vdms_threads.volumedetect import VolumeDetectThread
from videomass3.vdms_threads.check_bin import (ff_conf,
                                               ff_formats,
                                               ff_codecs,
                                               ff_topics,
                                               )
from videomass3.vdms_threads.opendir import browse
from videomass3.vdms_threads.ydl_pylibextractinfo import Ydl_EI_Pylib
from videomass3.vdms_threads.ydl_executable import Ydl_EI_Exec

from videomass3.vdms_frames import (ffmpeg_conf,
                                    ffmpeg_formats,
                                    ffmpeg_codecs,
                                    )
from videomass3.vdms_dialogs.popup import PopupDialog


def stream_info(title, filepath):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    get = wx.GetApp()
    try:
        with open(filepath):
            miniframe = Mediainfo(title,
                                  filepath,
                                  get.FFPROBE_url,
                                  get.OS,
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
        with open(filepath):
            thread = File_Play(filepath,
                               tseq,
                               param,
                               get.LOGdir,
                               get.FFPLAY_url,
                               get.FFPLAY_loglev,
                               autoexit
                               )
            # thread.join() > attende fine thread, se no ritorna subito
            # error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or is invalid:  %s") % (
            filepath), "Videomass", wx.ICON_EXCLAMATION, None)
        return
# -----------------------------------------------------------------------#


def url_play(url, quality, timestamp, autoexit):
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
    get = wx.GetApp()  # get data from bootstrap
    youtube_dl = get.pylibYdl

    dowl = ffplay_url_exec.Exec_Streaming(timestamp, autoexit, url, quality)
    """
    if youtube_dl is not None:  # run youtube-dl executable
        dowl = ffplay_url_exec.Exec_Streaming(url, quality)
    else:  # run youtube_dl library
        dowl = ffplay_url_lib.Lib_Streaming(url, quality)
    """

# -----------------------------------------------------------------------#


def probeInfo(filename):
    """
    Get data stream informations during dragNdrop action.
    It is called by MyListCtrl(wx.ListCtrl) only.
    Return tuple object with two items: (data, None) or (None, error).
    """
    get = wx.GetApp()
    metadata = FFProbe(get.FFPROBE_url, filename, parse=False, writer='json')

    if metadata.ERROR():  # first checks for errors:
        err = metadata.error
        return (None, err)

    data = metadata.custom_output()

    return (data, None)
# -------------------------------------------------------------------------#


def volumeDetectProcess(filelist, time_seq, audiomap):
    """
    Run thread to get audio peak level data and show a
    pop-up dialog with message.
    """
    get = wx.GetApp()
    thread = VolumeDetectThread(time_seq, filelist, audiomap,
                                get.LOGdir, get.FFMPEG_url)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nAudio peak analysis.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()

    return data
# -------------------------------------------------------------------------#


def test_conf():
    """
    Call *check_bin.ffmpeg_conf* to get data to test the building
    configurations of the installed or imported FFmpeg executable
    and send it to dialog box.

    """
    get = wx.GetApp()
    out = ff_conf(get.FFMPEG_url, get.OS)
    if 'Not found' in out[0]:
        wx.MessageBox("\n{0}".format(out[1]),
                      "Videomass",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_conf.Checkconf(out,
                                          get.FFMPEG_url,
                                          get.FFPROBE_url,
                                          get.FFPLAY_url,
                                          get.OS,
                                          )
        miniframe.Show()
# -------------------------------------------------------------------------#


def test_formats():
    """
    Call *check_bin.ff_formats* to get available formats by
    imported FFmpeg executable and send it to dialog box.

    """
    get = wx.GetApp()
    diction = ff_formats(get.FFMPEG_url, get.OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']),
                      "Videomass",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_formats.FFmpeg_formats(diction, get.OS)
        miniframe.Show()
# -------------------------------------------------------------------------#


def test_codecs(type_opt):
    """
    Call *check_bin.ff_codecs* to get available encoders
    and decoders by FFmpeg executable and send it to
    corresponding dialog box.

    """
    get = wx.GetApp()
    diction = ff_codecs(get.FFMPEG_url, type_opt, get.OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']),
                      "Videomass",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_codecs.FFmpeg_Codecs(diction, get.OS, type_opt)
        miniframe.Show()
# -------------------------------------------------------------------------#


def findtopic(topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic..

    """
    get = wx.GetApp()
    retcod = ff_topics(get.FFMPEG_url, topic, get.OS)

    if 'Not found' in retcod[0]:
        s = ("\n{0}".format(retcod[1]))
        return(s)
    else:
        return(retcod[1])
# -------------------------------------------------------------------------#


def openpath(where):
    """
    Call vdms_threads.opendir.browse to open file browser into
    configuration directory or log directory.

    """
    get = wx.GetApp()
    ret = browse(get.OS, where)
    if ret:
        wx.MessageBox(ret, 'Videomass', wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def youtubedl_getstatistics(url):
    """
    Call the thread to get extract info data object with
    youtube_dl python package and show a wait pop-up dialog .
    youtube_dl module.
    example without pop-up dialog:
    thread = Ydl_EI_Pylib(url)
    thread.join()
    data = thread.data
    yield data
    """
    thread = Ydl_EI_Pylib(url)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nRetrieving required data.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()
    yield data
# --------------------------------------------------------------------------#


def youtube_getformatcode_exec(url):
    """
    Call the thread to get format code data object with youtube-dl
    executable, (e.g. `youtube-dl -F url`) .
    While waiting, a pop-up dialog is shown.
    """
    thread = Ydl_EI_Exec(url)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nRetrieving required data.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()
    yield data
# --------------------------------------------------------------------------#


'''
def youtubedl_latest(url):
    """
    Call the thread to read the latest version of youtube-dl via the web.
    While waiting, a pop-up dialog is shown.
    """
    thread = youtubedlupdater.CheckNewRelease(url)

    loadDlg = PopupDialog(None, _("Videomass - Reading..."),
                          _("\nWait....\nCheck for update.\n"))
    loadDlg.ShowModal()
    # thread.join()
    latest = thread.data
    loadDlg.Destroy()

    return latest'''
# --------------------------------------------------------------------------#


def youtubedl_update(cmd, waitmsg):
    """
    Call thread to execute generic tasks as updates youtube-dl executable
    or read the installed version. All these tasks are intended only for
    the local copy (not installed by the package manager) of youtube-dl.
    While waiting, a pop-up dialog is shown.
    """
    thread = youtubedlupdater.Command_Execution(cmd)

    loadDlg = PopupDialog(None, _("Videomass - Loading..."), waitmsg)
    loadDlg.ShowModal()
    # thread.join()
    update = thread.data
    loadDlg.Destroy()

    return update
# --------------------------------------------------------------------------#


def youtubedl_upgrade(latest, executable, upgrade=False):
    """
    Run thread to download locally the latest version of youtube-dl
    or youtube-dl.exe . While waiting, a pop-up dialog is shown.
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    if get.OS == 'Windows':
        url = ('https://youtube-dl.org/downloads/latest/youtube-dl.exe')
    else:
        url = ('https://yt-dl.org/downloads/latest/youtube-dl')

    name = os.path.basename(executable)
    if upgrade:
        msg = _('\nWait....\nUpgrading {}\n').format(name)
    else:
        msg = _('\nWait....\nDownloading {}\n').format(name)
    '''
    url = ('https://github.com/ytdl-org/youtube-dl/releases/'
           'download/%s/%s' % (latest, name))
    '''

    if os.path.exists(executable):
        try:  # make back-up for outdated
            os.rename(executable, '%s_OLD' % executable)
        except FileNotFoundError as err:
            return None, err
    elif not os.path.exists(os.path.dirname(executable)):
        try:  # make cache dir
            os.makedirs(os.path.dirname(executable), mode=0o777)
        except OSError as err:
            return None, err

    thread = generic_downloads.File_Downloading(url, executable)
    loadDlg = PopupDialog(None, _("Videomass - Downloading..."), msg)
    loadDlg.ShowModal()
    # thread.join()
    status = thread.data
    loadDlg.Destroy()

    if os.path.exists('%s_OLD' % executable):
        # remove outdated back-up
        if not status[1]:
            if os.path.isfile('%s_OLD' % executable):
                os.remove('%s_OLD' % executable)
            elif os.path.isdir('%s_OLD' % executable):
                shutil.rmtree('%s_OLD' % executable)
        else:
            # come back previous status
            os.rename('%s_OLD' % executable, executable)

    if not name == 'youtube-dl.exe':
        # make it executable by everyone
        if os.path.isfile(executable):
            st = os.stat(executable)
            os.chmod(executable, st.st_mode | stat.S_IXUSR |
                     stat.S_IXGRP | stat.S_IXOTH)
    return status
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
            version = response.json()["%s" % keyname]

        except Exception as err:
            not_found = 'response error:', err

    if not_found[0]:
        return not_found
    else:
        return version, None
# --------------------------------------------------------------------------#


def get_presets(url, dest, msg):
    """
    """
    thread = generic_downloads.File_Downloading(url, dest)
    loadDlg = PopupDialog(None, _("Videomass - Downloading..."), msg)
    loadDlg.ShowModal()
    # thread.join()
    status = thread.data
    loadDlg.Destroy()

    return status
# --------------------------------------------------------------------------#


def appimage_update_youtube_dl(appimage):
    """
    Call appropriate thread to update or installing youtube_dl
    package inside Videomass AppImage.
    """
    get = wx.GetApp()  # get data from bootstrap
    log = os.path.join(get.LOGdir, 'youtube_dl-update-on-AppImage.log')
    thread = youtubedlupdater.Update_Youtube_dl_Appimage(log, appimage)

    waitmsg = _('...Be patient, this can take a few minutes.')

    loadDlg = PopupDialog(None, _("Videomass - Updating..."), waitmsg)
    loadDlg.ShowModal()
    # thread.join()
    update = thread.status
    loadDlg.Destroy()

    if update:
        return update

    ret = None
    with open(log, 'r', encoding='utf8') as f:
        for line in f:
            if '**Successfully updated**\n' in line:
                ret = 'success'
    return 'success' if ret == 'success' else 'error'
