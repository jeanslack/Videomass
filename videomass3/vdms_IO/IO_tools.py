# -*- coding: UTF-8 -*-

#########################################################
# Name: streams_tools.py
# Porpose: Redirect any input/output resources to process
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (02) December 28 2018
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
def process(self, varargs, panelshown, duration, time_seq):
    """
    1) TIME DEFINITION FOR THE PROGRESS BAR
        For a suitable and efficient progress bar, if a specific 
        time sequence has been set with the duration tool, the total duration 
        of each media file will be replaced with the set time sequence. 
        Otherwise the duration of each media will be the one originated from 
        its real duration.
        
    2) STARTING THE PROCESS
        Than, the process is assigned to the most suitable thread and at 
        the same time the panel with the progress bar is instantiated.
    """
    if time_seq:
        newDuration = []
        dur = time_seq.split()[3] # the -t flag
        h,m,s = dur.split(':')
        totalsum = (int(h)*60+ int(m)*60+ int(s))
        for n in duration:
            newDuration.append(totalsum)
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
def probeDuration(path_list, ffprobe_link):
    """
    Parsa i metadati riguardanti la durata (duration) dei media importati, 
    utilizzata per il calcolo della progress bar. Questa funzione viene 
    chiamata nella MyListCtrl(wx.ListCtrl) con il pannello dragNdrop.
    Se i file non sono supportati da ffprobe e quindi da ffmpeg, avvisa
    con un messaggio di errore.
    """
    metadata = FFProbe(path_list, ffprobe_link, 'no_pretty') 
        # first execute a control for errors:
    if metadata.ERROR():
        err = metadata.error
        print ("[FFprobe] Error:  %s" % err)
        #wx.MessageBox("%s\nFile not supported!" % (metadata.error),
                      #"Error - Videomass", 
                      #wx.ICON_ERROR, None)
        duration = 0
        return duration, err
    try:
        for items in metadata.data_format()[0]:
            if items.startswith('duration='):
                duration = (int(items[9:16].split('.')[0]))
    except ValueError as ve:
        duration = 0
        if ve.args[0] == "invalid literal for int() with base 10: 'N/A'":
            return duration, 'N/A'
        else:
            return duration, ve.args
    
    return duration , None
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


