# -*- coding: UTF-8 -*-

#########################################################
# Name: streams_tools.py
# Porpose: Redirect any input/output resources to process
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev Dec.28.2018, Sept.19.2019
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

get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf
ffprobe_url = get.ffprobe_url

from videomass3.vdms_THREADS.ffplay_reproduction import Play
from videomass3.vdms_THREADS.ffprobe_parser import FFProbe
from videomass3.vdms_THREADS.volumedetect import VolumeDetectThread
from videomass3.vdms_THREADS.volumedetect import PopupDialog
from videomass3.vdms_THREADS.check_bin import ff_conf
from videomass3.vdms_THREADS.check_bin import ff_formats
from videomass3.vdms_THREADS.check_bin import ff_codecs
from videomass3.vdms_THREADS.check_bin import ff_topics
from videomass3.vdms_THREADS.opendir import browse
from videomass3.vdms_DIALOGS import ffmpeg_conf
from videomass3.vdms_DIALOGS import ffmpeg_formats
from videomass3.vdms_DIALOGS import ffmpeg_codecs
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_THREADS.ydl_extract_info import Extract_Info

#-----------------------------------------------------------------------#
def stream_info(title, filepath):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    try:
        with open(filepath):
            dialog = Mediainfo(title, 
                               filepath, 
                               ffprobe_url, 
                               OS,
                               )
            dialog.Show()

    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
        
#-----------------------------------------------------------------------#
def stream_play(filepath, timeseq, param):
    """
    Thread for media reproduction with ffplay
    """
    try:
        with open(filepath):
            thread = Play(filepath, timeseq, param)
            #thread.join()# attende che finisca il thread (se no ritorna subito)
            #error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
        return
    
#-----------------------------------------------------------------------#
def probeInfo(filename):
    """
    Get data stream informations during dragNdrop action.  
    It is called by MyListCtrl(wx.ListCtrl) only. 
    Return tuple object with two items: (data, None) or
    (None, error).
    
    """
    metadata = FFProbe(ffprobe_url, filename, parse=False, writer='json')
        
    if metadata.ERROR(): # first execute a control for errors:
        err = metadata.error
        print ("[FFprobe] Error:  %s" % err)
        return (None, err)
    
    data = metadata.custom_output()
    
    return (data , None)
#-------------------------------------------------------------------------#
def volumeDetectProcess(ffmpeg, filelist, time_seq):
    """
    Run a thread to get audio peak level data and show a 
    pop-up dialog with message. 
    """
    thread = VolumeDetectThread(ffmpeg, time_seq, filelist, OS) 
    loadDlg = PopupDialog(None, _("Videomass - Loading..."), 
                                _("\nWait....\nAudio peak analysis.\n")
                          )
    loadDlg.ShowModal()
    #thread.join()
    data = thread.data
    loadDlg.Destroy()
    
    return data
#-------------------------------------------------------------------------#
def test_conf(ffmpeg_link, ffprobe_link, ffplay_link):
    """
    Call *check_bin.ffmpeg_conf* to get data to test the building 
    configurations of the installed or imported FFmpeg executable 
    and send it to dialog box.
    
    """
    out = ff_conf(ffmpeg_link, OS)
    if 'Not found' in out[0]:
        wx.MessageBox("\n{0}".format(out[1]), 
                        "Videomass: error",
                        wx.ICON_ERROR, 
                        None)
        return
    else:
        dlg = ffmpeg_conf.Checkconf(out, 
                                    ffmpeg_link, 
                                    ffprobe_link,
                                    ffplay_link, 
                                    OS,
                                    )
        dlg.Show()
#-------------------------------------------------------------------------#
def test_formats(ffmpeg_link):
    """
    Call *check_bin.ff_formats* to get available formats by 
    imported FFmpeg executable and send it to dialog box.
    
    """
    diction = ff_formats(ffmpeg_link, OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']), 
                        "Videomass: error",
                        wx.ICON_ERROR, 
                        None)
        return
    else:
        dlg = ffmpeg_formats.FFmpeg_formats(diction, OS)
        dlg.Show()
#-------------------------------------------------------------------------#
def test_codecs(ffmpeg_link, type_opt):
    """
    Call *check_bin.ff_codecs* to get available encoders 
    and decoders by FFmpeg executable and send it to
    corresponding dialog box.
    
    """
    diction = ff_codecs(ffmpeg_link, type_opt, OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']), 
                        "Videomass: error",
                        wx.ICON_ERROR, 
                        None)
        return
    else:
        dlg = ffmpeg_codecs.FFmpeg_Codecs(diction, OS, type_opt)
        dlg.Show()
#-------------------------------------------------------------------------#
def findtopic(ffmpeg_link, topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic. The ffmpeg_link is given by ffmpeg-search dialog.
    
    """
    retcod = ff_topics(ffmpeg_link, topic, OS)
    
    if 'Not found' in retcod[0]:
        s = ("\n{0}".format(retcod[1]))
        return(s)
    else:
        return(retcod[1])
#-------------------------------------------------------------------------#
def openpath(mod):
    """
    Call vdms_THREADS.opendir.browse to open file browser into
    configuration directory and log directory.
    
    """
    ret = browse(OS, DIRconf, mod)
    if ret:
        wx.MessageBox(ret, 'Videomass', wx.ICON_ERROR, None)
#-------------------------------------------------------------------------#
def youtube_info(url):
    """
    Call a separated thread to get extract info data object from 
    youtube_dl module. 
    """
    thread = Extract_Info(url) 
    thread.join()
    data = thread.data
    
    yield data
#--------------------------------------------------------------------------#
def create_vinc_profile(parameters):
    """
    Save a profile on a vinc preset or create new preset if not vinc
    exist
    """
    vinc = DIRconf.split('videomass')[0] + 'vinc'
    if os.path.exists(vinc):
        with wx.FileDialog(None, _("Videomass: Choose a preset to "
                                    "storing new profile"), 
            defaultDir=os.path.join(vinc, 'presets'),
            wildcard="Vinc presets (*.vip;)|*.vip;",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     
            filename = fileDialog.GetPath()
            t = _('Videomass: Create a new Vinc profile')
    else:
        with wx.FileDialog(None, "Enter name for new preset", 
                            wildcard="Vinc presets (*.vip;)|*.vip;",
                            style=wx.FD_SAVE | 
                                    wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = "%s.vip" % fileDialog.GetPath()
            t = _('Videomass: Create a new Vinc preset')
            try:
                with open(filename, 'w') as file:
                    file.write('[]')
            except IOError:
                wx.LogError("Cannot save current "
                            "data in file '%s'." % filename)
                return
    
    prstdlg = presets_addnew.MemPresets(filename, parameters, t)
    prstdlg.Show()


