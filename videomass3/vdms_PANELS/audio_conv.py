# -*- coding: UTF-8 -*-

#########################################################
# Name: audio_conv
# Porpose: Intarface for ffmpeg audio conversions and normalization
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.02.2019, Sept.01.2019
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
import wx.lib.agw.floatspin as FS
import wx.lib.agw.gradientbutton as GB
from videomass3.vdms_IO.IO_tools import volumeDetectProcess
from videomass3.vdms_IO.IO_tools import FFProbe
from videomass3.vdms_IO.filedir_control import inspect
from videomass3.vdms_DIALOGS.epilogue import Formula
from videomass3.vdms_DIALOGS import  audiodialogs
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS import shownormlist

# set widget colours in some case with html rappresentetion:
azure = '#15a6a6' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
ciano = '#61ccc7' # rgb 97, 204, 199

cmd_opt = {"AudioContainer":"MP3 [.mp3]", 
           "AudioCodec":"-c:a libmp3lame", 
           "AudioChannel":("",""), 
           "AudioRate":("",""), 
           "AudioDepth":("",""),
           "AudioBitrate":("",""), 
           "Normalize":"", 
           "ExportExt":"mp3", 
           "CodecCopied":[],
           }
acodecs = {"WAV [.wav]":"-c:a pcm_s16le",
           "AIFF [.aiff]":"-c:a pcm_s16le",
           "FLAC [.flac]":"-c:a flac",
           "OGG [.ogg]":"-c:a libvorbis",
           "MP3 [.mp3]":"-c:a libmp3lame",
           "AAC [.m4a]":"-c:a aac",
           "ALAC [.m4a]":"-c:a alac",
           "AC3 [.ac3]":"-c:a ac3"
           }

class Audio_Conv(wx.Panel):
    """
    Interface panel for audio conversions and volume normalizations,
    with preset storing feature (TODO)
    """
    def __init__(self, parent, ffmpeg_link, threads, 
                 cpu_used, ffmpeg_loglev, ffprobe_link, OS,
                 iconanalyzes, iconsettings):
        # passed attributes
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.threads = threads
        self.cpu_used = cpu_used if not cpu_used == 'Disabled' else ''
        self.ffmpeg_loglevel = ffmpeg_loglev
        self.ffprobe_link = ffprobe_link
        self.OS = OS
        #self.DIRconf = DIRconf
        # others attributes:
        self.file_sources = []
        self.file_destin = ''
        self.normdetails = []

        wx.Panel.__init__(self, parent, -1)
        """ constructor"""
        # Widgets definitions:
        self.cmbx_a = wx.ComboBox(self, wx.ID_ANY,
        choices=[("WAV [.wav]"), 
                 ("AIFF [.aiff]"), 
                 ("FLAC [.flac]"), 
                 ("OGG [.ogg]"), 
                 ("MP3 [.mp3]"), 
                 ("AAC [.m4a]"), 
                 ("ALAC [.m4a]"), 
                 ("AC3 [.ac3]"),
                 (_("Save audio from movie"))], style=wx.CB_DROPDOWN | 
                                                       wx.CB_READONLY)
        self.cmbx_a.SetSelection(4)
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_param = GB.GradientButton(self,
                                           size=(-1,25),
                                           bitmap=setbmp,
                                           label=_("Audio Options"))
        self.btn_param.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28,28))
        self.btn_param.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_param.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_param.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_param.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.txt_options = wx.TextCtrl(self, wx.ID_ANY, size=(265,-1),
                                          style=wx.TE_READONLY)
        self.ckb_onlynorm = wx.CheckBox(self, wx.ID_ANY, (
                                               _("Only Normalization")))
        self.ckb_norm = wx.CheckBox(self, wx.ID_ANY, (
                                               _("Audio Normalization")))
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self,
                                           size=(-1,25),
                                           bitmap=analyzebmp,
                                           label=_("Volumedected"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.btn_details = GB.GradientButton(self,
                                            #size=(-1,25),
                                            #bitmap=analyzebmp,
                                            label=_("Details list"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_details.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_details.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.lab_amplitude = wx.StaticText(self, wx.ID_ANY, (
                                    _("Max peak level threshold   ")))
        self.spin_amplitude = FS.FloatSpin(self, wx.ID_ANY, min_val=-99.0, 
                                    max_val=0.0, increment=1.0, value=-1.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_amplitude.SetFormat("%f")
        self.spin_amplitude.SetDigits(1)
        #----------------------Set Properties----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_global = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                "")), wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(5, 2, 0, 0)
        grid_sizer_1 = wx.GridSizer(2, 1, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(2, 4, 0, 0)
        #grid_sizer_5 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _("Audio Container Selection"))), 
                                                       wx.VERTICAL
                                                       )
        sizer_3.Add(self.cmbx_a, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        grid_sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_2.Add(self.btn_param, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_2.Add(self.txt_options, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.lab_bitdepth, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.txt_bitdepth, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.lab_bitrate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.txt_bitrate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.lab_channel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_4.Add(self.txt_channel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_2.Add(grid_sizer_4, 0, wx.TOP, 5)
        grid_sizer_1.Add(grid_sizer_2, 1, 0, 0)
        sizer_2.Add(grid_sizer_1, 1, wx.ALL | wx.EXPAND, 20)
        grid_sizer_3.Add(self.ckb_norm, 0, wx.TOP, 5)
        grid_sizer_3.Add(self.ckb_onlynorm, 0, wx.TOP, 5)
        grid_sizer_3.Add(self.btn_analyzes, 0, wx.TOP, 10)
        grid_sizer_3.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_3.Add(self.btn_details, 0, wx.TOP, 10)
        grid_sizer_3.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_3.Add(self.lab_amplitude, 0, wx.TOP, 10)
        grid_sizer_3.Add(self.spin_amplitude, 0, wx.TOP, 5)
        #--------------------------------------------------------------
        grid_sizer_3.Add((0, 55), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_3.Add((0, 55), 0, wx.EXPAND | wx.TOP, 5)
        #sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    #"Export Preferences")), wx.VERTICAL)
        #sizer_4.Add(grid_sizer_5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #grid_sizer_5.Add(self.ckb_test, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        #grid_sizer_5.Add(self.label_sec, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        #grid_sizer_5.Add(self.spin_ctrl_test, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        #grid_sizer_3.Add(sizer_4, 0, wx.TOP|wx.BOTTOM, 20)
        #--------------------------------------------------------------
        sizer_2.Add(grid_sizer_3, 1, wx.ALL | wx.EXPAND, 20)
        sizer_global.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add(sizer_global, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_base)
        # Set tooltip:
        self.btn_param.SetToolTip(_("Enable advanced settings as audio "
                                    "bit-rate, audio channel and audio rate "
                                    "of the selected audio codec.")
                                              )
        self.btn_analyzes.SetToolTip(_("Calculates the maximum and average "
                                       "peak level of audio streams expressed "
                                       "in dB values")
                                              )
        self.spin_amplitude.SetToolTip(_("Threshold for the maximum peak "
                                    "level in dB values. The default setting "
                                    "is -1.0 dB and is good for most of the "
                                    "processes."))
        
        #----------------------Binding (EVT)----------------------#
        self.cmbx_a.Bind(wx.EVT_COMBOBOX, self.audioFormats)
        self.Bind(wx.EVT_BUTTON, self.on_Param, self.btn_param)
        self.Bind(wx.EVT_CHECKBOX, self.on_Enable_norm, self.ckb_norm)
        self.Bind(wx.EVT_CHECKBOX, self.on_OnlyNorm, self.ckb_onlynorm)
        self.Bind(wx.EVT_BUTTON, self.on_Analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        #self.Bind(wx.EVT_SPINCTRL, self.enter_normalize, self.spin_amplitude)
        
        # set default :
        self.normalization_disabled()

    # used Methods:
    def normalization_disabled(self):
        """
        Disable all widget of normalization feature and Set default values. 
        This is the start default setting and when there are changes in the 
        dragNdrop panel. Also, if enable 'Perform only normalization' enable 
        conversion widgets.
        """
        self.ckb_norm.SetValue(False), self.btn_analyzes.Disable(), 
        self.btn_details.Disable()
        self.btn_details.SetForegroundColour(wx.Colour(165,165, 165))
        self.lab_amplitude.Disable()
        self.spin_amplitude.Disable(), self.spin_amplitude.SetValue(-1.0)
        cmd_opt["Normalize"] = ""
        del self.normdetails[:]
        if self.ckb_onlynorm.IsChecked():
            self.ckb_onlynorm.SetValue(False)
            self.cmbx_a.Enable(), self.btn_param.Enable(),
            self.ckb_norm.Enable(), self.txt_options.Enable(),

    #----------------------Event handler (callback)----------------------#
    #------------------------------------------------------------------#
    
    def audioFormats(self, evt):
        """
        Get selected container from combobox
        """
        if self.cmbx_a.GetValue() == _("Save audio from movie"):
            if self.ckb_norm.IsChecked():
                self.normalization_disabled()
            self.ckb_norm.Disable(), self.ckb_onlynorm.Disable()
            self.txt_options.Disable(), self.btn_param.Disable()
            self.btn_param.SetForegroundColour(wx.Colour(165,165, 165))
            
        else:
            if not self.ckb_norm.IsChecked():# è l'unico caso questo
                self.ckb_norm.Enable(), self.ckb_onlynorm.Enable(), 
                self.txt_options.Enable(), self.btn_param.Enable()
                self.btn_param.SetForegroundColour(wx.Colour(28,28,28))
                
            cmd_opt["AudioContainer"] = self.cmbx_a.GetValue()
            cmd_opt["AudioCodec"] = acodecs[self.cmbx_a.GetValue()]
            ext = self.cmbx_a.GetValue().split()[1].strip('[.]')
            cmd_opt["ExportExt"] = ext
        
        self.txt_options.SetValue("")
        cmd_opt["AudioChannel"] = ["",""]
        cmd_opt["AudioRate"] = ["",""]
        cmd_opt["AudioBitrate"] = ["",""]
        cmd_opt["AudioDepth"] = ["",""]
        self.btn_param.SetBottomEndColour(wx.Colour(205, 235, 222))
    #------------------------------------------------------------------#
    def on_Param(self, evt):
        """
        Get the container type and set value dictionary codec in the
        AudioCodec key used for ffmpeg command..
        Send identifier data of the container to audio_parameters method
        """
        if not cmd_opt["AudioContainer"]:
            cmd_opt["AudioContainer"] = self.cmbx_a.GetValue()
        #--------------------------------------------#
        if cmd_opt["AudioContainer"] == "WAV [.wav]":
            self.audio_parameters("wav", "Audio WAV Parameters - Videomass")
            
        elif cmd_opt["AudioContainer"] == "AIFF [.aiff]":
            self.audio_parameters("aiff", "Audio AIFF Parameters - Videomass")

        elif cmd_opt["AudioContainer"] == "FLAC [.flac]":
            self.audio_parameters("flac", "Audio FLAC Parameters - Videomass")
            
        elif cmd_opt["AudioContainer"] == "OGG [.ogg]":
            self.audio_parameters("ogg", "Audio OGG Parameters - Videomass")
            
        elif cmd_opt["AudioContainer"] == "MP3 [.mp3]":
            self.audio_parameters("mp3", "Audio MP3 Parameters - Videomass")
        
        elif cmd_opt["AudioContainer"] == "AAC [.m4a]":
            self.audio_parameters("aac", "Audio AAC Parameters - Videomass")
        
        elif cmd_opt["AudioContainer"] == "ALAC [.m4a]":
            self.audio_parameters("alac", "Audio ALAC Parameters - Videomass")
            
        elif cmd_opt["AudioContainer"] == "AC3 [.ac3]":
            self.audio_parameters("ac3", "Audio AC3 Parameters - Videomass")
            
        #elif self.cmbx_a.GetValue() == "Save audio from movie":
            #self.audiocopy()
    #-------------------------------------------------------------------#
    def audio_parameters(self, audio_type, title):
        """
        Run a dialogs to choices audio parameters then set dictionary 
        at proper values. Also text is placed in the textctrl's fields.
        NOTE: The data[X] tuple contains the command parameters on the index [1] 
              and the descriptive parameters on the index [0].
              exemple: data[0] contains parameters for channel then
              data[0][1] is ffmpeg option command for audio channels and
              data[0][0] is a simple description for view.
        """
        audiodialog = audiodialogs.AudioSettings(self, 
                                                 audio_type, 
                                                 cmd_opt["AudioRate"],
                                                 cmd_opt["AudioDepth"],
                                                 cmd_opt["AudioBitrate"], 
                                                 cmd_opt["AudioChannel"],
                                                 title,
                                                 )
        retcode = audiodialog.ShowModal()
        
        if retcode == wx.ID_OK:
            data = audiodialog.GetValue()
            cmd_opt["AudioChannel"] = data[0]
            cmd_opt["AudioRate"] = data[1]
            cmd_opt["AudioBitrate"] = data[2]
            if audio_type in ('wav','aiff'):
                if 'Default' in data[3][0]:
                    cmd_opt["AudioCodec"] = "-c:a pcm_s16le"
                else:
                    cmd_opt["AudioCodec"] = data[3][1]
                cmd_opt["AudioDepth"] = ("%s" % (data[3][0]),
                                         "%s" % (data[3][1]))
            else:# entra su tutti gli altri tranne wav aiff
                cmd_opt["AudioDepth"] = data[3]
        else:
            data = None
            audiodialog.Destroy()
            return

        self.txt_options.SetValue("")
        count = 0
        for d in [cmd_opt["AudioRate"],cmd_opt["AudioDepth"],
                 cmd_opt["AudioBitrate"], cmd_opt["AudioChannel"]
                 ]:
            if d[1]:
                count += 1
                self.txt_options.AppendText(" %s | " % d[0])

        if count == 0:
            self.btn_param.SetBottomEndColour(wx.Colour(205, 235, 222))
        else:
            self.btn_param.SetBottomEndColour(wx.Colour(0, 240, 0))
        
        audiodialog.Destroy()
    #------------------------------------------------------------------#
    def audiocopy(self,file_sources):
        """
        Try copying and saving the audio stream on a video by 
        recognizing the codec and then assigning a container/format. 
        If there is more than one audio stream in a video, a choice 
        is made to the user.
        """
        cmd_opt["ExportExt"] = []
        cmd_opt["AudioCodec"] = []
        cmd_opt["CodecCopied"] = []

        for files in file_sources:
            metadata = FFProbe(files, self.ffprobe_link, '-pretty') 
            # first execute a control for errors:
            if metadata.ERROR():
                wx.MessageBox("[FFprobe] Error:  %s" % (metadata.error), 
                              "ERROR - Videomass",
                wx.ICON_ERROR, self)
                return
            # Proceed with the istance method call:
            datastream = metadata.get_audio_codec_name()
            audio_list = datastream[0]

            if audio_list == None:
                wx.MessageBox(_("There are no audio streams:\n%s ") % (files), 
                            'Videomass', wx.ICON_INFORMATION, self)
                return

            elif len(audio_list) > 1:
                title = datastream[1]
                
                dlg = wx.SingleChoiceDialog(self, 
                        _("{0}\n\n"
                          "Contains multiple audio streams. " 
                          "Select which audio stream you want to "
                          "export between these:").format(title), 
                        _("Videomass: Stream choice"),
                        audio_list, wx.CHOICEDLG_STYLE
                                            )
                if dlg.ShowModal() == wx.ID_OK:
                    if dlg.GetStringSelection() in audio_list:
                        cn = ''.join(dlg.GetStringSelection()).split()[4]
                        indx = ''.join(dlg.GetStringSelection()).split()[1]
                        cmd_opt["AudioCodec"].append(
                                            "-map 0:%s -c copy" % indx)
                        cmd_opt["CodecCopied"].append(cn)#used for epilogue
                        if cn in ('aac','alac'): cn = 'm4a'
                        if cn in ('ogg','vorbis'): cn = 'oga'
                        if cn.startswith('pcm_'): cn = 'wav'
                        cmd_opt["ExportExt"].append(cn)
                    else:
                        wx.MessageBox(_(u"Nothing choice:\n%s ") % (files), 
                            'Videomass: Error', wx.ICON_ERROR, self)
                        return
                else: # there must be some choice (default first item list)
                    cn = ''.join(audio_list[0]).split()[4]
                    indx = ''.join(audio_list[0]).split()[1]
                    cmd_opt["AudioCodec"].append("-map 0:%s -c copy" % indx)
                    cmd_opt["CodecCopied"].append(cn)#used for epilogue
                    if cn in ('aac','alac'): cn = 'm4a'
                    if cn in ('ogg','vorbis'): cn = 'oga'
                    if cn.startswith('pcm_'): cn = 'wav'
                    cmd_opt["ExportExt"].append(cn)
                dlg.Destroy()
            else:
                cn = ''.join(audio_list[0]).split()[4]
                indx = ''.join(audio_list[0]).split()[1]
                cmd_opt["AudioCodec"].append("-map 0:%s -c copy" % indx)
                cmd_opt["CodecCopied"].append(cn)#used for epilogue
                if cn in ('aac','alac'): cn = 'm4a'
                if cn in ('ogg','vorbis'): cn = 'oga'
                if cn.startswith('pcm_'): cn = 'wav'
                cmd_opt["ExportExt"].append(cn)

    #------------------------------------------------------------------#
    def on_Enable_norm(self, evt):
        """
        Choice if use or not audio normalization
        """
        msg = (_('Tip: set the maximum peak level threshold or accept default '
                 'dB value (-1.0); then check peak level by pressing the '
                 '"Volumedetect" button'))
        if self.ckb_norm.IsChecked():# if checked
            self.parent.statusbar_msg(msg, azure)
            self.btn_analyzes.SetForegroundColour(wx.Colour(28,28,28))
            self.btn_analyzes.Enable(), self.spin_amplitude.Enable(),
            self.lab_amplitude.Enable(), 

        else:# is not checked
            self.parent.statusbar_msg(_("Disable audio normalization"), None)
            self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
            self.btn_analyzes.Disable(), self.lab_amplitude.Disable()
            self.spin_amplitude.Disable(), self.spin_amplitude.SetValue(-1.0)
            self.btn_details.SetForegroundColour(wx.Colour(165,165, 165))
            self.btn_details.Disable()
            
        cmd_opt["Normalize"] = ""
        del self.normdetails[:]
    #------------------------------------------------------------------#
    def on_OnlyNorm(self, evt):
        """
        If checked, disable audio conversion and use only normalization
        process to audio file
        """
        if self.ckb_onlynorm.IsChecked():# if checked
            if not self.ckb_norm.IsChecked():
                self.ckb_norm.SetValue(True), self.on_Enable_norm(self)
            self.ckb_norm.Disable()
            self.cmbx_a.Disable(), self.btn_param.Disable(),
            self.txt_options.Disable(),
            self.btn_param.SetForegroundColour(wx.Colour(165,165, 165))
        else:
            self.cmbx_a.Enable(), self.btn_param.Enable(),
            self.btn_param.SetForegroundColour(wx.Colour(28,28, 28))
            self.ckb_norm.Enable(),
            self.txt_options.Enable(),
    #------------------------------------------------------------------#
    def on_Analyzes(self, evt):  # analyzes button
        """
        If check, send to audio_analyzes.
        """
        file_sources = self.parent.file_sources[:]
        self.audio_analyzes(file_sources)
    #------------------------------------------------------------------#
    
    def audio_analyzes(self, file_sources):
        """
        Start control for values volume in db. 
        Then call 'os_processing.proc_volumedetect'.
        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>
        """
        msg1 = (_("Audio normalization will be applied"))
        msg2 = (_("Audio normalization is required only for some files"))
        msg3 = (_("Audio normalization is not required in relation to "
                  "the set threshold"))
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        normalize = self.spin_amplitude.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, 
                                   file_sources, 
                                   self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "Volumedected error!", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(file_sources, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(normalize)
                if float(maxvol) >= float(normalize):
                    volume.append('  ')
                    self.normdetails.append((f, 
                                             maxvol, 
                                             meanvol,
                                             ' ',
                                             _('Not Required')
                                             ))
                else:
                    volume.append("-af volume=%sdB" % (str(offset)[1:]))
                    self.normdetails.append((f, 
                                             maxvol,
                                             meanvol,
                                             str(offset)[1:],
                                             _('Required')
                                             ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 self.parent.statusbar_msg(msg1, greenolive)
            else:
                self.parent.statusbar_msg(msg2, yellow)
                
        cmd_opt["Normalize"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Enable()
        self.btn_details.SetForegroundColour(wx.Colour(28,28,28))
        
    #------------------------------------------------------------------#
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog to list data of peak levels
        """
        title = _('Audio normalization details list')
        audionormlist = shownormlist.NormalizationList(title, 
                                                       self.normdetails, 
                                                       self.OS)
        audionormlist.Show()
    #-----------------------------------------------------------------------#
    def disableParent(self):
        """
        disabling the main fraim also automatically disables this panel.
        Used on batch mode only with ProgressDialog gauge. 
        """
        self.parent.Disable()
    #-----------------------------------------------------------------------#
    def enableParent(self):
        """
        Enabling the main fraim also automatically enable this panel
        """
        self.parent.Enable()
    #------------------------------------------------------------------#
    def exportStreams(self, exported):
        """
        Set the parent.post_process attribute for communicate it the
        file disponibilities for play or metadata functionalities.
        """
        if not exported:
            return

        else:
            self.parent.post_process = exported
            self.parent.postExported_enable()
    #------------------------------------------------------------------#
    def update_allentries(self):
        """
        Last step for set definitively all values before to proceed
        with std_conv or batch_conv methods.
        Update _allentries is callaed by on_ok method.
        """
        self.time_seq = self.parent.time_seq
        if self.cmbx_a.GetValue() == _("Save audio from movie"):
            file_sources = self.parent.file_sources[:]
            self.audiocopy(file_sources)
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        File existence verification procedures, overwriting control and 
        data redirecting .
        """
        # check normalization data offset, if enable.
        if self.ckb_norm.IsChecked():
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_("Missing volume dectect!\n"
                              "Press the Volumedected button before proceeding."),
                                "Videomass", wx.ICON_INFORMATION)
                return
        self.update_allentries()# last update of all setting interface
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file name log 
        logname = 'Videomass_AudioConversion.log'

        ######## ------------ VALIDAZIONI: --------------
        if self.ckb_onlynorm.IsChecked():
            checking = inspect(file_sources, dir_destin, '')
        else:
            checking = inspect(file_sources, dir_destin, 
                            cmd_opt["ExportExt"])
        if not checking[0]:#user non vuole continuare o files assenti
            return
        # typeproc: batch or single process
        # filename: nome file senza ext.
        # base_name: nome file con ext.
        # countmax: count processing cicles for batch mode
        typeproc, file_sources, dir_destin,\
        filename, base_name, countmax = checking


        if self.cmbx_a.GetValue() == _("Save audio from movie"):
            self.grabaudioProc(file_sources, dir_destin, countmax, logname)
        else:
            self.stdProc(file_sources, dir_destin, countmax, logname)

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, countmax, logname):
        """
        Composes the ffmpeg command strings for the batch mode processing.
        """
        if self.ckb_onlynorm.IsChecked():
            title = _('Start audio norm.')
            cmd = ("-loglevel %s -vn %s %s -y" % (self.ffmpeg_loglevel, 
                                                  self.threads,
                                                  self.cpu_used,)
                                                  )
            command = " ".join(cmd.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax)
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('normal',
                                           file_sources, 
                                           '', 
                                           dir_destin, 
                                           command, 
                                           None, 
                                           self.ffmpeg_link,
                                           cmd_opt["Normalize"], 
                                           logname, 
                                           countmax, 
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#call function more above
        else:
            title = _('Start audio conversion')
            command = ("-loglevel %s -vn %s %s %s %s %s %s %s -y" % (
                                                self.ffmpeg_loglevel,
                                                cmd_opt["AudioCodec"],
                                                cmd_opt["AudioBitrate"][1], 
                                                cmd_opt["AudioDepth"][1], 
                                                cmd_opt["AudioRate"][1], 
                                                cmd_opt["AudioChannel"][1], 
                                                self.threads,
                                                self.cpu_used,)
                                                                    )
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax)
            ending = Formula(self, valupdate[0], valupdate[1], title)

            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('normal',
                                           file_sources,
                                           cmd_opt["ExportExt"],
                                           dir_destin,
                                           command,
                                           None,
                                           self.ffmpeg_link,
                                           cmd_opt["Normalize"],
                                           logname, 
                                           countmax,
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["ExportExt"]))
        
    #------------------------------------------------------------------#
    def grabaudioProc(self, file_sources, dir_destin, 
                             countmax, logname):
        """
        Composes the ffmpeg command strings for the batch_process_changes.
        """
        title = _('Start audio export')
        cmdsplit1 = ("-loglevel %s -vn" % (self.ffmpeg_loglevel,))
        cmdsplit2 = ("%s %s -y" % (self.threads, self.cpu_used,))

        valupdate = self.update_dict(countmax)
        ending = Formula(self, valupdate[0], valupdate[1], title)
        
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('grabaudio',
                                       self.ffmpeg_link, 
                                       file_sources, #list
                                       dir_destin, #list
                                       cmdsplit1, 
                                       cmd_opt["AudioCodec"],#list
                                       cmdsplit2, 
                                       cmd_opt["ExportExt"],#list
                                       logname, 
                                       countmax, #list
                                       )
            # used for play preview and mediainfo:
            f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
            self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                             cmd_opt["ExportExt"][0]))

    #------------------------------------------------------------------#
    def update_dict(self, countmax):
        """
        This method is required for update all cmd_opt
        dictionary values before send at epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        if cmd_opt["Normalize"]:
            normalize = _('Enable')
        else:
            normalize = _('Disable')
            
        if self.ckb_onlynorm.IsChecked():
            formula = (_("SUMMARY:\n\nFile Queue:\
                       \nAudio Normalization:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s" % (numfile, 
                                            normalize, 
                                            self.time_seq
                                            )
                        )
        elif self.cmbx_a.GetValue() == _("Save audio from movie"):
            formula = (_("SUMMARY:\n\nFile Queue:\
                      \nAudio Container:\nCodec copied:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s\n%s" % (numfile, 
                                                cmd_opt["ExportExt"],
                                                cmd_opt["CodecCopied"], 
                                                self.time_seq)
                                                )
        else:
            formula = (_("SUMMARY:\n\nFile Queue:\
                    \nAudio Container:\nAudio Codec:\nAudio bit-rate:\
                    \nAudio channel:\nAudio sample rate:\nBit per Sample:\
                    \nAudio Normalization:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
                    numfile, cmd_opt["AudioContainer"], 
                    cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][0], 
                    cmd_opt["AudioChannel"][0], cmd_opt["AudioRate"][0], 
                    cmd_opt["AudioDepth"][0] , normalize, self.time_seq)
                        )
        return formula, dictions
    
#------------------------------------------------------------------#
    def Addprof(self):
        """
        Storing new profile in the 'Preset Manager' panel with the same 
        current setting. All profiles saved in this way will also be stored 
        in the preset 'User Presets'
        
        NOTE: For multiple processes involving audio normalization and those 
              for saving audio streams from movies, only the data from the 
              first file in the list will be considered.
        
        FIXME have any problem with xml escapes in special character
        (like && for ffmpeg double pass), so there is some to get around it 
        (escamotage), but work .
        
        """
        get = wx.GetApp()
        dirconf = os.path.join(get.DIRconf, 'vdms')
        
        if cmd_opt["Normalize"]:
            normalize = cmd_opt["Normalize"][0]# tengo il primo valore lista
        else:
            normalize = ''
        
        if self.ckb_onlynorm.IsChecked():
            command = ("-vn %s" % normalize)
            command = ' '.join(command.split())# sistemo gli spazi
            list = [command, cmd_opt["ExportExt"]]
            
        elif self.cmbx_a.GetValue() == _("Save audio from movie"):
            command = ("-vn %s" % cmd_opt["AudioCodec"][0])
            command = ' '.join(command.split())# sistemo gli spazi
            list = [command, cmd_opt["ExportExt"][0]]
  
        else:
            command = ("-vn %s %s %s %s %s %s" % (normalize, 
                                                  cmd_opt["AudioCodec"], 
                                                  cmd_opt["AudioBitrate"][1], 
                                                  cmd_opt["AudioDepth"][1], 
                                                  cmd_opt["AudioRate"][1], 
                                                  cmd_opt["AudioChannel"][1],
                                                  ))
            command = ' '.join(command.split())# sistemo gli spazi
            list = [command, cmd_opt["ExportExt"]]

        filename = 'preset-v1-Personal'# nome del file preset senza ext
        name_preset = 'User Profiles'
        full_pathname = os.path.join(dirconf, 'preset-v1-Personal.vdms')
        
        prstdlg = presets_addnew.MemPresets(self, 'addprofile', full_pathname, 
                                            filename, list, 
                    _('Videomass: Create a new profile on "%s" preset') % (
                                                                name_preset))
        prstdlg.ShowModal()
