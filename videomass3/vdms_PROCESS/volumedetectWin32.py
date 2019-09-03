 # -*- coding: UTF-8 -*-

#########################################################
# Name: volumedetect.py
# Porpose: Audio Peak level volume analyzes for Ms Windows
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev:  Dec.27.2018. Sept.02.2019
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
from pubsub import pub
import subprocess
from threading import Thread
from videomass3.vdms_SYS.os_interaction import copy_restore # if copy fiile log
from videomass3.vdms_IO.make_filelog import write_log # write initial log

########################################################################
not_exist_msg =  _('exist in your system?')
unrecognized_msg = _("Unrecognized Error (not in err_list):")
not_exist_msg = _("File does not exist:")

# path to the configuration directory
get = wx.GetApp()
DIRconf = get.DIRconf
PATH_log = get.path_log
#########################################################################

class PopupDialog(wx.Dialog):
    """ 
    A pop-up dialog box for temporary user messages that tell the user 
    the load in progress (required for large files).
    
    Usage:
            loadDlg = PopupDialog(None, ("Videomass - Loading..."), 
                        ("\nAttendi....\nSto eseguendo un processo .\n")
                                )
            loadDlg.ShowModal() 

            loadDlg.Destroy()
    """
    def __init__(self, parent, title, msg):
        # Create a dialog
        wx.Dialog.__init__(self, parent, -1, title, size=(350, 150), 
                            style=wx.CAPTION)
        # Add sizers
        box = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # Add an Info graphic
        bitmap = wx.Bitmap(32, 32)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, 
                                          wx.ART_MESSAGE_BOX, (32, 32)
                                           )
        graphic = wx.StaticBitmap(self, -1, bitmap)
        box2.Add(graphic, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        # Add the message
        message = wx.StaticText(self, -1, msg)
        box2.Add(message, 0, wx.EXPAND | wx.ALIGN_CENTER 
                                    | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10
                                    )
        box.Add(box2, 0, wx.EXPAND)
        # Handle layout
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Fit()
        self.Layout()

        pub.subscribe(self.getMessage, "RESULT_EVT")
        
    def getMessage(self, status):
        """
        Riceive msg and status from thread.
        All'inizio usavo self.Destroy() per chiudere il dialogo modale
        (con modeless ritornava dati None), ma dava warning e critical
        e su OsX non chiudeva affatto. Con EndModal ho risolto tutti
        i problemi e funziona bene. Ma devi ricordarti di eseguire
        Destroy() dopo ShowModal() nel chiamante.
        vedi: https://github.com/wxWidgets/Phoenix/issues/672
        Penso sia fattibile anche implementare un'interfaccia GetValue
        su questo dialogo, ma si perderebbe un po' di portabilità.
        
        """
        #self.Destroy() # do not work
        self.EndModal(1)
##############################################################################
class VolumeDetectThread(Thread):
    """
    This class represents a separate subprocess thread for detect audio
    volume peak level when required for audio normalization process.
    The volume data is a list sended to the dialog with wx.callafter.
    """
    def __init__(self, ffmpeg_bin, timeseq, filelist, OS):
        """
        self.cmd contains a unique string that comprend filename input
        and filename output also.
        """
        Thread.__init__(self)
        """initialize"""
        self.filelist = filelist
        self.ffmpeg = ffmpeg_bin
        self.time_seq = timeseq
        self.status = None
        self.data = None
        self.nul = 'NUL'
        self.logf = "%s/log/%s" %(DIRconf, 'Videomass_volumedected.log')
        
        write_log('Videomass_volumedected.log', "%s/log" % DIRconf) 
        # set initial file LOG

        self.start() # start the thread (va in self.run())
        
    #----------------------------------------------------------------#
    def run(self):
        """
        File normalization process for get volume levels data.
        It is used by normalize.py, audio_conv.py and video_conv.py
        TODO: Replace /dev/null with NUL on Windows.
        
        NOTE for subprocess.STARTUPINFO() 
        < Windows: https://stackoverflow.com/questions/1813872/running-
        a-process-in-pythonw-with-popen-without-a-console?lq=1>
        
        """
        volume = list()
        err_list = ('not found',
                    'Invalid data found when processing input',
                    'Error', 
                    'Invalid', 
                    'Option not found', 
                    'Unknown',
                    'No such file or directory',
                    'does not contain any stream',
                    'Output file is empty, nothing was encoded',
                    )
        for files in self.filelist:
            cmnd = ('{0} {1} -i "{2}" -hide_banner -af volumedetect '
                    '-vn -sn -dn -f null {3}').format(self.ffmpeg, 
                                                      self.time_seq,
                                                      files,
                                                      self.nul)
            self.logWrite(cmnd)
            
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(cmnd,
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True,
                                     startupinfo=startupinfo,
                                     )
                output, error =  p.communicate()
                raw_list = error.split() # splitta tutti gli spazi

                if 'mean_volume:' in raw_list:
                    mean_volume = raw_list.index("mean_volume:")# indx integear
                    medvol = "%s dB" % raw_list[mean_volume + 1]
                    max_volume = raw_list.index("max_volume:")# indx integear
                    maxvol = "%s dB" % raw_list[max_volume + 1]
                    volume.append([maxvol, medvol])

                else:
                    for err in err_list:
                        if err in error:
                            e = error.strip()
                    if e:
                        self.status = e
                        break
                    
            except IOError:
                e = "%s  %s" % (not_exist_msg, filepath)
                self.status = e
                break
            
            except OSError:
                e = "%s\n'ffmpeg.exe' %s" % (err, not_exist_msg)
                self.status = e
                break
            
            except UnboundLocalError:
                # local variable `e` referenced before assignment
                # dovrebbe riportare tutti gli errori di ffmpeg dato che la 
                # variabile `e` sarà referenziata prima di essere assegnata.
                e = "%s\n\n%s" % (unrecognized_msg, error)
                self.status = e
                break
        
        self.data = (volume, self.status)
        
        if self.status:
            self.logError()
        
        wx.CallAfter(pub.sendMessage, 
                     "RESULT_EVT",  
                      status=''
                      )
        
        self.pathLog()
        
    #----------------------------------------------------------------#    
    def logWrite(self, cmd):
        """
        write ffmpeg command log
        
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
            
    #----------------------------------------------------------------# 
    def logError(self):
        """
        write ffmpeg volumedected errors
        
        """
        with open(self.logf,"a") as logerr:
            logerr.write("[FFMPEG] volumedetect "
                         "ERRORS:\n%s\n\n" % (self.status))
            
    #----------------------------------------------------------------#
    def pathLog(self):
        """
        if user want file log in a specified path
        
        """
        if not 'none' in PATH_log: 
            copy_restore(self.logf, "%s/%s" % (PATH_log, 
                                               'Videomass_volumedected.log'))
            
