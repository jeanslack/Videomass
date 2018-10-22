# -*- coding: UTF-8 -*-

#########################################################
# Name: streams_tools.py
# Porpose: Redirect any input/output resources for process
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (01) 21/july/2018, (02) October/13/2018
#########################################################
import wx
from vdms_PROCESS.task_processing import GeneralProcess
from vdms_PROCESS.task_processing import ProcThread
from vdms_PROCESS.task_processing import DoublePassThread
from vdms_PROCESS.task_processing import GrabAudioProc
from vdms_PROCESS.task_processing import SingleProcThread
from vdms_PROCESS.volumedetect import VolumeDetectThread, PopupDialog
from vdms_PROCESS.ffplay_reproduction import Play
from vdms_PROCESS.ffprobe_parser import FFProbe
from vdms_DIALOGS.mediainfo import Mediainfo


#-----------------------------------------------------------------------#
def process(self, varargs, path_log, panelshown, duration, OS):
    """
    Here the most suitable thread is assigned to the type of process 
    to be executed. Instead for the 'GeneralProcess' panel things 
    should not change.
    """
    if varargs[0] == 'normal':# video conv and audio conv panels
        ProcThread(varargs, duration, OS) 
        
    elif varargs[0] == 'doublepass': # video conv panel
        DoublePassThread(varargs, duration, OS)
        
    elif varargs[0] == 'saveimages': # video conv panel
        SingleProcThread(varargs, duration, OS)
        
    elif varargs[0] == 'grabaudio':# audio conv panel
        GrabAudioProc(varargs, duration, OS)

    self.ProcessPanel = GeneralProcess(self, path_log, panelshown, varargs)
#-----------------------------------------------------------------------#
def stream_info(title, filepath , ffprobe_link):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    try:
        with open(filepath):
            dialog = Mediainfo(title, filepath, ffprobe_link)
            dialog.Show()

    except IOError:
        wx.MessageBox("File does not exist or not a valid file:  %s" % (
            filepath), "Warning - Videomass2", wx.ICON_EXCLAMATION, None)
        
#-----------------------------------------------------------------------#
def stream_play(filepath, param, ffplay_link, loglevel_type, OS):
    """
    Thread for media reproduction with ffplay
    """
    try:
        with open(filepath):
            thread = Play(filepath, param, ffplay_link, loglevel_type, OS)
            #thread.join()# attende che finisca il thread (se no ritorna subito)
            #error = thread.data
    except IOError:
        wx.MessageBox("File does not exist or not a valid file:  %s" % (
            filepath), "Warning - Videomass2", wx.ICON_EXCLAMATION, None)
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
        print "[FFprobe] Error:  %s" % err
        #wx.MessageBox("%s\nFile not supported!" % (metadata.error),
                      #"Error - Videomass2", 
                      #wx.ICON_ERROR, None)
        duration = 0
        return duration, err
    try:
        for items in metadata.data_format()[0]:
            if items.startswith('duration='):
                duration = (int(items[9:16].split('.')[0]))
    except ValueError as ve:
        duration = 0
        if ve[0] == "invalid literal for int() with base 10: 'N/A'":
            return duration, 'N/A'
        else:
            return duration, ve
    
    return duration , None
#-------------------------------------------------------------------------#
def volumeDetectProcess(ffmpeg, filelist, OS):
    """
    Run a thread for get audio peak level data and show a pop-up dialog 
    with message. 
    """
    thread = VolumeDetectThread(ffmpeg, filelist, OS) 
    loadDlg = PopupDialog(None, 
                          "Videomass2 - Loading...", 
                          "\nWait....\nAudio peak analysis.\n"
                          )
    loadDlg.ShowModal()
    #thread.join()
    data = thread.data
    loadDlg.Destroy()
    
    return data
    

