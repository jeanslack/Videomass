# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Porpose: input/output redirection to processes (aka threads)
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.18.2025
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
import requests
import wx
from videomass.vdms_threads import generic_downloads
from videomass.vdms_threads.volumedetect import VolumeDetectThread
from videomass.vdms_threads.check_bin import (ff_conf,
                                              ff_formats,
                                              ff_codecs,
                                              ff_topics,
                                              )
from videomass.vdms_utils.utils import open_default_application
from videomass.vdms_dialogs.widget_utils import PopupDialog


def show_msg_notify(parent, warnlev: str = 'error', logname: str = 'log',
                    addmsg=None, showlogdialog=True):
    """
    This function shows and characterizes pop-up dialog messages
    according to the passed arguments. It can be used to notify
    errors, warnings, and information at the end of threads.

    The `parent` is the child (given by `GetParent()` method) and must
    descend from the first ancestor which is a top-level window
    (i.e `main_frame`).

    Default parameter `warnlev` accepts one of the following
    strings: "info", "warning", "error", default is "error".

    Default parameter `logname` must be a string containing
    the basename of the file to be displayed in the log file
    dialog. See `applognames` for a list of supported lognames.

    Default parameter `addmsg`, which represents the body of a message.
    Default parameter `showlogdialog`, which displays the additional
    log file dialog after the pop-up message has been confirmed.

    """
    get = wx.GetApp()
    applognames = get.appset['applognames']  # list of logs files included

    if addmsg:
        msg = addmsg
    else:
        msg = _('Please, see «{0}» file for details.').format(logname)

    if warnlev in ('info', 'information'):
        ico = wx.ICON_INFORMATION
        caption = 'Videomass'
    elif warnlev in ('warn', 'warning'):
        ico = wx.ICON_INFORMATION
        caption = _('Videomass - Warning!')
    elif warnlev in ('err', 'error'):
        caption = _('Videomass - Error!')
        ico = wx.ICON_ERROR
    else:
        raise ValueError("The `warnlev` argument only accepts 'information', "
                         "'warning', 'error' or, more briefly, 'info', "
                         "'warn', 'err'. Default is 'error'")

    wx.MessageBox(msg, caption, ico, parent)

    if showlogdialog and logname in applognames:
        toplevparent = wx.GetTopLevelParent(parent)
        toplevparent.view_logs(None, flog=logname)
# ----------------------------------------------------------------#


def volume_detect_process(filelist, timeseq, audiomap, parent=None):
    """
    Run thread to get audio peak level data
    showing a pop-up message dialog.
    """
    if timeseq:
        splseq = timeseq.split()
        tseq = f'{splseq[0]} {splseq[1]}', f'{splseq[2]} {splseq[3]}'
    else:
        tseq = '', ''

    thread = VolumeDetectThread(tseq, filelist, audiomap)
    dlgload = PopupDialog(parent,
                          _("Videomass - Loading..."),
                          _("Wait....\nAudio peak analysis."),
                          thread,
                          )
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()

    if data[1]:
        if data[1] == 'ERROR':
            show_msg_notify(parent, logname='volumedetected.log')

        elif data[1] == 'STOP':
            msg = 'volumedetect: STOP command event received.'
            show_msg_notify(parent, warnlev='info',
                            logname='volumedetected.log',
                            addmsg=msg, showlogdialog=False)

    return data
# -------------------------------------------------------------------------#


def test_conf():
    """
    Call `check_bin.ffmpeg_conf` to get data to test the building
    configurations of the used FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_conf(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    return out
# -------------------------------------------------------------------------#


def test_formats():
    """
    Call `check_bin.ff_formats` to get available formats by
    FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_formats(get.appset['ffmpeg_cmd'], get.appset['ostype'])
    return out
# -------------------------------------------------------------------------#


def test_codecs(type_opt):
    """
    Call `check_bin.ff_codecs` to get available encoders
    and decoders by FFmpeg executable.
    """
    get = wx.GetApp()
    out = ff_codecs(get.appset['ffmpeg_cmd'],
                    type_opt,
                    get.appset['ostype'],
                    )
    return out
# -------------------------------------------------------------------------#


def findtopic(topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic..
    """
    get = wx.GetApp()
    retcod = ff_topics(get.appset['ffmpeg_cmd'], topic, get.appset['ostype'])

    if 'Not found' in retcod[0]:
        notf = f"\n{retcod[1]}"
        return notf

    return retcod[1]
# -------------------------------------------------------------------------#


def openpath(where):
    """
    Call `vdms_threads.opendir.open_default_application`.
    """
    ret = open_default_application(where)
    if ret:
        wx.MessageBox(ret, _('Videomass - Error!'), wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API:
        https://developer.github.com/v3/repos/releases/#get-the-latest-release

    see keyname examples here:
    <https://api.github.com/repos/jeanslack/Videomass/releases>
    """
    try:
        response = requests.get(url, timeout=15)
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


def get_presets(url, dest, msg, parent=None):
    """
    get latest Videomass presets
    """
    thread = generic_downloads.FileDownloading(url, dest)
    dlgload = PopupDialog(parent, _("Videomass - Downloading..."), msg)
    dlgload.ShowModal()
    # thread.join()
    status = thread.data
    dlgload.Destroy()

    return status
# --------------------------------------------------------------------------#
