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

get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf
ffprobe_url = get.ffprobe_url

if OS == 'Windows':
    from videomass3.vdms_PROCESS.task_processingWin32 import GeneralProcess
    from videomass3.vdms_PROCESS.volumedetectWin32 import VolumeDetectThread
    from videomass3.vdms_PROCESS.volumedetectWin32 import PopupDialog
    from videomass3.vdms_PROCESS.ffplay_reproductionWin32 import Play
    from videomass3.vdms_PROCESS.ffprobe_parserWin32 import FFProbe
else:
    from videomass3.vdms_PROCESS.task_processing import GeneralProcess
    from videomass3.vdms_PROCESS.volumedetect import VolumeDetectThread
    from videomass3.vdms_PROCESS.volumedetect import PopupDialog
    from videomass3.vdms_PROCESS.ffplay_reproduction import Play
    from videomass3.vdms_PROCESS.ffprobe_parser import FFProbe
    #from videomass3.vdms_PROCESS.import_stream_parsing import parsing_import
    
    
from videomass3.vdms_DIALOGS.mediainfo import Mediainfo
from videomass3.vdms_PROCESS.check_bin import ff_conf
from videomass3.vdms_PROCESS.check_bin import ff_formats
from videomass3.vdms_PROCESS.check_bin import ff_codecs
from videomass3.vdms_PROCESS.check_bin import ff_topics
from videomass3.vdms_PROCESS.opendir import browse
from videomass3.vdms_DIALOGS import ffmpeg_conf
from videomass3.vdms_DIALOGS import ffmpeg_formats
from videomass3.vdms_DIALOGS import ffmpeg_codecs

#-----------------------------------------------------------------------#
def process(self, varargs, panelshown, duration, time_seq, time_read):
    """
    1) TIME DEFINITION FOR THE PROGRESS BAR
        For a suitable and efficient progress bar, if a specific 
        time sequence has been set with the duration tool, the total 
        duration of each media file will be replaced with the set time 
        sequence. Otherwise the duration of each media will be the one 
        originated from its real duration.
        
    2) STARTING THE PROCESS
        Here the panel with the progress bar is instantiated which will 
        assign a corresponding thread.
        
    """
    if time_seq:
        newDuration = []
        for n in duration:
            newDuration.append(time_read['time'][1])
        duration = newDuration
        
    self.ProcessPanel = GeneralProcess(self, 
                                       panelshown, 
                                       varargs, 
                                       duration, 
                                       OS,
                                       )
#-----------------------------------------------------------------------#
def stream_info(title, filepath , ffprobe_link):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    try:
        with open(filepath):
            dialog = Mediainfo(title, 
                               filepath, 
                               ffprobe_link, 
                               OS,
                               )
            dialog.Show()

    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
        
#-----------------------------------------------------------------------#
def stream_play(filepath, timeseq, ffplay_link, param, loglevel_type):
    """
    Thread for media reproduction with ffplay
    """
    try:
        with open(filepath):
            thread = Play(filepath, 
                          timeseq, 
                          ffplay_link, 
                          param, 
                          loglevel_type, 
                          OS,
                          )
            #thread.join()# attende che finisca il thread (se no ritorna subito)
            #error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
        return
    
#-----------------------------------------------------------------------#
def probeInfo(filepath):
    """
    Get data stream informations during dragNdrop action. 
    The duration data is useful to calculate the progress bar too. 
    It is called by MyListCtrl(wx.ListCtrl) only. 
    Return tuple with two items: (dict type data object, None) or
    (None, data str error).
    
    """
    f_format = dict()
    v_streams = dict()
    a_streams = dict()
    s_streams = dict()
    
    metadata = FFProbe(filepath, ffprobe_url, 'pretty') 
        # first execute a control for errors:
    if metadata.ERROR():
        err = metadata.error
        print ("[FFprobe] Error:  %s" % err)
        return (None, err)
    
    video_list = metadata.video_stream()
    format_list = metadata.data_format()
    audio_list = metadata.audio_stream()
    subtitle_list = metadata.subtitle_stream()
    
    n = len(format_list)
    for f in range(n):
        (k,v) = format_list[f][0].strip().split('=')
        stream = 'FORMAT'
        for i in format_list[f]:
            (k,v) = i.split('=',1)
            f_format[k] = v
    
    n = len(video_list)
    for v in range(n):
        (key) = video_list[v][0].strip().split('=')[1]
        stream = 'index %s' % key[0]
        v_streams[stream] = {}
        for i in video_list[v]:
            (k,v) = i.split('=',1)
            v_streams[stream].update({k:v})
            
    n = len(audio_list)
    for a in range(n):
        (key) = audio_list[a][0].strip().split('=')[1]
        stream = 'index %s' % key[0]
        a_streams[stream] = {}
        for i in audio_list[a]:
            (k,v) = i.split('=',1)
            a_streams[stream].update({k:v})
    
    n = len(subtitle_list)
    for s in range(n):
        (key) = subtitle_list[s][0].strip().split('=')[1]
        stream = 'index %s' % key[0]
        s_streams[stream] = {}
        for i in subtitle_list[s]:
            (k,v) = i.split('=',1)
            s_streams[stream].update({k:v})
    
    
    data = {'FORMAT': f_format, 'VIDEO': v_streams, 
            'AUDIO': a_streams, 'SUBTITLES': s_streams}
    
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
    Call vdms_PROCESS.opendir.browse
    
    """
    ret = browse(OS, DIRconf, mod)
    if ret:
        wx.MessageBox(ret, 'Videomass', wx.ICON_ERROR, None)
#-------------------------------------------------------------------------#


