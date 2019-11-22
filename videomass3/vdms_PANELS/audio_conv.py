# -*- coding: UTF-8 -*-

#########################################################
# Name: audio_conv
# Porpose: Intarface for ffmpeg audio conversions and normalization
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.02.2019, Sept.24.2019
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
from videomass3.vdms_IO.filenames_check import inspect
from videomass3.vdms_DIALOGS.epilogue import Formula
from videomass3.vdms_DIALOGS import  audiodialogs
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS import shownormlist

# setting the path to the configuration directory:
get = wx.GetApp()
DIRconf = get.DIRconf

# set widget colours in some case with html rappresentetion:
azure = '#15a6a6' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
green = '#268826'
ciano = '#61ccc7' # rgb 97, 204, 199

cmd_opt = {"AudioContainer": "MP3 [.mp3]", 
           "AudioCodec": "-c:a libmp3lame", 
           "AudioChannel": ("",""), 
           "AudioRate": ("",""), 
           "AudioDepth": ("",""),
           "AudioBitrate": ("",""), 
           "PEAK": "", 
           "RMS": "",
           "EBU": "",
           "ExportExt": "mp3", 
           "CodecCopied": [],
           }
acodecs = {("WAV [.wav]"): ("-c:a pcm_s16le"),
           ("AIFF [.aiff]"): ("-c:a pcm_s16le"),
           ("FLAC [.flac]"): ("-c:a flac"),
           ("OGG [.ogg]"): ("-c:a libvorbis"),
           ("MP3 [.mp3]"): ("-c:a libmp3lame"),
           ("AAC [.m4a]"): ("-c:a aac"),
           ("ALAC [.m4a]"): ("-c:a alac"),
           ("AC3 [.ac3]"): ("-c:a ac3"),
           ("OPUS [.opus]"): ("-c:a libopus"),
           }

class Audio_Conv(wx.Panel):
    """
    Interface panel for audio conversions and volume normalizations,
    with preset storing feature (TODO)
    """
    def __init__(self, parent, ffmpeg_link, threads, ffmpeg_loglev, 
                 ffprobe_link, OS, iconanalyzes, iconsettings, 
                 iconpeaklevel, btn_color, fontBtncolor):

        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.threads = threads
        self.ffmpeg_loglevel = ffmpeg_loglev
        self.ffprobe_link = ffprobe_link
        self.OS = OS
        self.btnC = btn_color
        self.fBtnC = fontBtncolor
        #self.DIRconf = DIRconf
        self.file_src = []
        self.normdetails = []

        wx.Panel.__init__(self, parent, -1)
        """ constructor"""
        # Widgets definitions:
        txtformat = wx.StaticText(self, wx.ID_ANY, (_("Output format:")))
        self.a_choice = wx.Choice(self, wx.ID_ANY,
                                  choices=[x for x in acodecs.keys()],
                                  size=(-1,-1)
                                  )
        self.a_choice.SetSelection(4)
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_param = GB.GradientButton(self,
                                           size=(-1,25),
                                           bitmap=setbmp,
                                           label=_("Audio Options"))
        self.btn_param.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_param.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_param.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_param.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_param.SetTopEndColour(wx.Colour(self.btnC))
        
        self.txt_options = wx.TextCtrl(self, wx.ID_ANY, size=(-1,-1),
                                          style=wx.TE_READONLY
                                          )
        self.rdbx_norm = wx.RadioBox(self,wx.ID_ANY,(_("Audio Normalization")), 
                                     choices=[
                                       ('Off'), 
                                       ('PEAK'), 
                                       ('RMS'),
                                       ('EBU R128'),
                                              ], 
                                     majorDimension=1, 
                                     style=wx.RA_SPECIFY_ROWS,
                                            )
                                     
        self.peakpanel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self.peakpanel,
                                           size=(-1,25),
                                           bitmap=analyzebmp,
                                           label=_("Volumedected"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetTopEndColour(wx.Colour(self.btnC))
        
        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.peakpanel,
                                            size=(-1,25),
                                            bitmap=peaklevelbmp,
                                            label=_("Volume Statistics"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_details.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_details.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopEndColour(wx.Colour(self.btnC))
        
        self.lab_amplitude = wx.StaticText(self.peakpanel, wx.ID_ANY, (
                            _("Target level:")))
        self.spin_target = FS.FloatSpin(self.peakpanel, wx.ID_ANY, min_val=-99.0, 
                                    max_val=0.0, increment=0.5, value=-1.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        
        self.ebupanel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.lab_i = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                             _("Set integrated loudness target:  ")))
        self.spin_i = FS.FloatSpin(self.ebupanel, wx.ID_ANY, min_val=-70.0, 
                                    max_val=-5.0, increment=0.5, value=-24.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        
        self.lab_tp = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                                    _("Set maximum true peak:")))
        self.spin_tp = FS.FloatSpin(self.ebupanel, wx.ID_ANY, min_val=-9.0, 
                                    max_val=0.0, increment=0.5, value=-2.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        
        self.lab_lra = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                                    _("Set loudness range target:")))
        self.spin_lra = FS.FloatSpin(self.ebupanel, wx.ID_ANY, min_val=1.0, 
                                    max_val=20.0, increment=0.5, value=7.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        #--------------------------------------------------------#
        sizer = wx.BoxSizer(wx.VERTICAL)
        frame = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                                "")), wx.VERTICAL)
        sizer.Add(frame, 1, wx.ALL | wx.EXPAND, 5)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        frame.Add(sizer_base, 1, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add((20, 20), 0,)
        sizer_audio_frm = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_audio_frm, 0, wx.ALL|wx.EXPAND, 10)
        sizer_audio_frm.Add(txtformat,0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        sizer_audio_frm.Add((5, 0), 0,)
        sizer_audio_frm.Add(self.a_choice, 1, wx.ALL|wx.EXPAND, 5)
        sizer_audio_opt = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_audio_opt, 0, wx.ALL|wx.EXPAND, 10)
        sizer_audio_opt.Add(self.btn_param, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        sizer_audio_opt.Add((5, 0), 0,) # stesso i sizer_audio_opt.AddSpacer(5)
        sizer_audio_opt.Add(self.txt_options, 1, wx.ALL|wx.EXPAND, 5)
        sizer_base.Add(self.rdbx_norm, 0, wx.ALL|wx.EXPAND, 15)
        sizer_peak = wx.FlexGridSizer(1, 4, 15, 15)
        sizer_peak.Add(self.btn_analyzes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_peak.Add(self.btn_details, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_peak.Add(self.lab_amplitude, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_peak.Add(self.spin_target, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.peakpanel.SetSizer(sizer_peak) # set panel
        sizer_base.Add(self.peakpanel, 0, wx.ALL, 15)
        sizer_ebu = wx.FlexGridSizer(3, 2, 5, 5)
        sizer_ebu.Add(self.lab_i, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_ebu.Add(self.spin_i, 0, wx.ALL, 0)
        sizer_ebu.Add(self.lab_tp, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_ebu.Add(self.spin_tp, 0, wx.ALL, 0)
        sizer_ebu.Add(self.lab_lra, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_ebu.Add(self.spin_lra, 0, wx.ALL, 0)
        self.ebupanel.SetSizer(sizer_ebu) # set panel
        sizer_base.Add(self.ebupanel, 0, wx.ALL, 15)
        self.SetSizer(sizer)
        # Set tooltip:
        self.btn_param.SetToolTip(_('Audio bit-rate, audio channel and audio '
                                    'rate of the selected audio codec.'))
        self.btn_analyzes.SetToolTip(_('Gets maximum volume and average volume '
                'data in dBFS, then calculates the offset amount for audio '
                'normalization.'))
        self.spin_target.SetToolTip(_('Limiter for the maximum peak level or '
                'the mean level (when switch to RMS) in dBFS. From -99.0 to '
                '+0.0; default for PEAK level is -1.0; default for RMS is '
                '-20.0'))
        self.spin_i.SetToolTip(_('Integrated Loudness Target in LUFS. '
                                 'From -70.0 to -5.0, default is -24.0'
                                 ))
        self.spin_tp.SetToolTip(_('Maximum True Peak in dBTP. From -9.0 '
                                  'to +0.0, default is -2.0'
                                  ))
        self.spin_lra.SetToolTip(_('Loudness Range Target in LUFS. '
                                   'From +1.0 to +20.0, default is +7.0'
                                   ))
        
        #----------------------Binding (EVT)----------------------#
        self.a_choice.Bind(wx.EVT_CHOICE, self.audioFormats)
        self.Bind(wx.EVT_BUTTON, self.on_Param, self.btn_param)
        self.Bind(wx.EVT_RADIOBOX, self.on_Enable_norm, self.rdbx_norm)
        self.Bind(wx.EVT_BUTTON, self.on_Analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        self.Bind(wx.EVT_SPINCTRL, self.enter_Amplitude, self.spin_target)
        
        # set default :
        self.normalization_default()

    #-------------------------------------------------------------------#
    def normalization_default(self):
        """
        Set default normalization parameters. This method is called by 
        main_frame module on MainFrame.switch_audio_conv() during first 
        run and when there are changing on dragNdrop panel, 
        (like make a clear file list or append new file, etc)
        
        """
        self.rdbx_norm.SetSelection(0), 
        self.spin_target.SetValue(-1.0)
        self.peakpanel.Hide(), self.ebupanel.Hide()
        cmd_opt["PEAK"], cmd_opt["EBU"], cmd_opt["RMS"] = "", "", ""
        del self.normdetails[:]
        
    #----------------------Event handler (callback)----------------------#

    def audioFormats(self, evt):
        """
        Get selected option from combobox
        
        """
        val = self.a_choice.GetString(self.a_choice.GetSelection())
        self.rdbx_norm.Enable()
        self.txt_options.Enable(), self.btn_param.Enable()
        self.btn_param.SetForegroundColour(wx.Colour(self.fBtnC))
        cmd_opt["AudioContainer"] = val
        cmd_opt["AudioCodec"] = acodecs[val]
        ext = val.split()[1].strip('[.]')
        cmd_opt["ExportExt"] = ext
        
        self.txt_options.SetValue("")
        cmd_opt["AudioChannel"] = ["",""]
        cmd_opt["AudioRate"] = ["",""]
        cmd_opt["AudioBitrate"] = ["",""]
        cmd_opt["AudioDepth"] = ["",""]
        self.btn_param.SetBottomEndColour(wx.Colour(self.btnC))
    #------------------------------------------------------------------#
    def on_Param(self, evt):
        """
        Get the container type and set value dictionary codec in the
        AudioCodec key used for ffmpeg command..
        Send identifier data of the container to audio_parameters method
        """
        if not cmd_opt["AudioContainer"]:
            val = self.a_choice.GetString(self.a_choice.GetSelection())
            cmd_opt["AudioContainer"] = val
        #--------------------------------------------#
        for k,v in acodecs.items():
            if cmd_opt["AudioContainer"] == k:
                self.audio_parameters(k.split()[0].lower(),
                                      "%s export parameters (%s)" 
                                      %(k.split()[0].lower(),v.split()[1])
                                        )
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
            self.btn_param.SetBottomEndColour(wx.Colour(self.btnC))
        else:
            self.btn_param.SetBottomEndColour(wx.Colour(255, 255, 0))
        
        audiodialog.Destroy()
        
    #------------------------------------------------------------------#
    def on_Enable_norm(self, evt):
        """
        Sets a corresponding choice for audio normalization
        
        """
        msg_1 = (_('Activate peak level normalization, which will produce '
                   'a maximum peak level equal to the set target level.'
                   ))
        msg_2 = (_('Activate RMS-based normalization, which according to '
                   'mean volume calculates the amount of gain to reach same '
                   'average power signal.'
                   ))
        msg_3 = (_('Activate two passes normalization. It Normalizes the '
                   'perceived loudness using the "​loudnorm" filter, which '
                   'implements the EBU R128 algorithm.'
                   ))
        if self.rdbx_norm.GetSelection() in [1,2]: # PEAK or RMS
            
            if self.rdbx_norm.GetSelection() == 1:
                self.parent.statusbar_msg(msg_1, azure)
                self.spin_target.SetValue(-1.0)
            else:
                self.parent.statusbar_msg(msg_2, '#15A660')
                self.spin_target.SetValue(-20.0)
            self.peakpanel.Show(), self.ebupanel.Hide()
            self.btn_analyzes.Enable(), self.btn_details.Hide()
            self.btn_analyzes.SetForegroundColour(wx.Colour(self.fBtnC))
            cmd_opt["PEAK"], cmd_opt["RMS"], cmd_opt["EBU"] = "", "", ""
            del self.normdetails[:]
            
        elif self.rdbx_norm.GetSelection() == 3: # EBU
            self.parent.statusbar_msg(msg_3, '#87A615')
            self.peakpanel.Hide(), self.ebupanel.Show()
            cmd_opt["PEAK"], cmd_opt["RMS"], cmd_opt["EBU"] = "", "", ""

        else: # usually it is 0
            self.parent.statusbar_msg(_("Audio normalization off"), None)
            self.normalization_default()
            
        self.Layout()
    #------------------------------------------------------------------#
    def enter_Amplitude(self, evt):
        """
        when spin_amplitude is changed enable 'Volumedected' to
        update new incomming
        
        """
        if not self.btn_analyzes.IsEnabled():
            self.btn_analyzes.Enable()
            self.btn_analyzes.SetForegroundColour(wx.Colour(self.fBtnC))
        
    #------------------------------------------------------------------#
    
    def on_Analyzes(self, evt):  # Volumedected button
        """
        Evaluates the user's choices and directs them to the references 
        for audio normalizations based on PEAK or RMS .
        
        """
        if self.rdbx_norm.GetSelection() == 1:
            self.max_volume_PEAK()
            
        elif self.rdbx_norm.GetSelection() == 2:
            self.mean_volume_RMS()
    #------------------------------------------------------------------#
    
    def max_volume_PEAK(self):
        """
        Analyzes to get MAXIMUM peak levels data to calculates offset in
        dBFS values need for audio normalization process.

        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>
        
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, 
                                   self.file_src, 
                                   self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(self.file_src, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(target)
                result = float(maxvol) - offset
                
                if float(maxvol) == float(target):
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)
                    
                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)

        cmd_opt["PEAK"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.Layout()
    #------------------------------------------------------------------#
    
    def mean_volume_RMS(self):  # Volumedetect button
        """
        Analyzes to get MEAN peak levels data to calculates RMS offset in
        dBFS need for audio normalization process.
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, 
                                   self.file_src, 
                                   self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(self.file_src, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(meanvol) - float(target)
                result = float(maxvol) - offset
                
                if offset == 0.0:
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)
                    
                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)
       
        cmd_opt["RMS"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.Layout()
    #------------------------------------------------------------------#
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog with volumedected data
        """
        if cmd_opt["PEAK"]:
            title = _('PEAK-based volume statistics')
        elif cmd_opt["RMS"]:
            title = _('RMS-based volume statistics')
            
        audionormlist = shownormlist.NormalizationList(title, 
                                                       self.normdetails, 
                                                       self.OS)
        audionormlist.Show()

    #------------------------------------------------------------------#
    def update_allentries(self):
        """
        Last step for set definitively all values before to proceed
        with std_conv or batch_conv methods.
        Update _allentries is callaed by on_ok method.
        
        """
        self.time_seq = self.parent.time_seq

    #------------------------------------------------------------------#
    def on_ok(self):
        """
        File existence verification procedures, overwriting control and 
        data redirecting .
        
        """
        # check normalization data offset, if enable.
        if self.rdbx_norm.GetSelection() in [1,2]: # PEAK or RMS
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_('Undetected volume values! use the '
                                '"Volumedetect" control button to analyze '
                                'the data on the audio volume.'),
                                "Videomass", wx.ICON_INFORMATION)
                return
            
        self.update_allentries()# last update of all setting interface
        checking = inspect(self.file_src, 
                           self.parent.file_destin,  
                           cmd_opt["ExportExt"])
        if not checking[0]: # the user changing idea or not such files exist
            return
        # typeproc: batch or single process
        # filename: nome file senza ext.
        # base_name: nome file con ext.
        # countmax: count processing cicles for batch mode
        (typeproc, f_src, f_dest, filename, base_name, countmax) = checking
        
        # used for file name log 
        logname = 'Videomass_AudioConversion.log'

        if self.rdbx_norm.GetSelection() == 3:
            self.ebu_Doublepass(f_src, f_dest, countmax, logname)
            
        else:
            self.stdProc(f_src, f_dest, countmax, logname)

    #------------------------------------------------------------------#
    def stdProc(self, f_src, f_dest, countmax, logname):
        """
        Composes the ffmpeg command strings for the batch mode processing.
        
        """
        audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]
        title = _('Audio conversions')
        command = ('-vn %s %s %s %s %s %s' % (cmd_opt["AudioCodec"],
                                              cmd_opt["AudioBitrate"][1], 
                                              cmd_opt["AudioDepth"][1], 
                                              cmd_opt["AudioRate"][1], 
                                              cmd_opt["AudioChannel"][1], 
                                              self.threads,
                                               ))
        command = " ".join(command.split())# mi formatta la stringa
        valupdate = self.update_dict(countmax)
        ending = Formula(self, valupdate[0], valupdate[1], title)

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('onepass',
                                        f_src,
                                        cmd_opt["ExportExt"],
                                        f_dest,
                                        command,
                                        None,
                                        '',
                                        audnorm,
                                        logname, 
                                        countmax,
                                        )
    #------------------------------------------------------------------#
    def ebu_Doublepass(self, f_src, f_dest, countmax, logname):
        """
        Perform EBU R128 normalization as 'only norm.' and as 
        standard conversion
        
        """
        cmd_opt["EBU"] = True
        loudfilter = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' 
                                              %(str(self.spin_i.GetValue()),
                                                str(self.spin_tp.GetValue()),
                                                str(self.spin_lra.GetValue())))
        title = _('Audio EBU normalization')
        cmd_1 = ('-vn %s' % (self.threads))
        cmd_2 = ('-vn %s %s %s %s %s %s' % (cmd_opt["AudioCodec"],
                                            cmd_opt["AudioBitrate"][1], 
                                            cmd_opt["AudioDepth"][1], 
                                            cmd_opt["AudioRate"][1], 
                                            cmd_opt["AudioChannel"][1], 
                                            self.threads,
                                            ))
        pass1 = " ".join(cmd_1.split())
        pass2 = " ".join(cmd_2.split())
        valupdate = self.update_dict(countmax)
        ending = Formula(self, valupdate[0], valupdate[1], title)

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('twopass EBU',
                                        f_src,
                                        '',
                                        f_dest,
                                        cmd_opt["ExportExt"],
                                        [pass1, pass2, loudfilter, False],
                                        self.ffmpeg_link,
                                        '',
                                        logname, 
                                        countmax,
                                        )
    #------------------------------------------------------------------#
    def update_dict(self, countmax):
        """
        This method is required for update all cmd_opt
        dictionary values before send at epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        
        if cmd_opt["PEAK"]:
            normalize = 'PEAK'
        elif cmd_opt["RMS"]:
            normalize = 'RMS'
        elif cmd_opt["EBU"]:
            normalize = 'EBU R128'
        else:
            normalize = _('Disabled')
            
        if not self.parent.time_seq:
            time = _('Not set')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0], 
                                                t[1][0], t[1][1][0])
        formula = (_("SUMMARY\n\nFile Queue\
                \nAudio Container\nAudio Codec\nAudio bit-rate\
                \nAudio Channels\nAudio Rate\nBit per Sample\
                \nAudio Normalization\nTime selection\nThreads"))
        dictions = ("\n\n%s\n%s\n%s\n%s\n%s"
                    "\n%s\n%s\n%s\n%s\n%s" % (numfile, 
                                              cmd_opt["AudioContainer"], 
                                              cmd_opt["AudioCodec"], 
                                              cmd_opt["AudioBitrate"][0], 
                                              cmd_opt["AudioChannel"][0], 
                                              cmd_opt["AudioRate"][0], 
                                              cmd_opt["AudioDepth"][0] , 
                                              normalize, 
                                              time,
                                              self.threads.split()[1],)
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
        
        if cmd_opt["PEAK"]:
            normalize = cmd_opt["PEAK"][0]# tengo il primo valore lista 
        elif cmd_opt["RMS"]:
            normalize = cmd_opt["RMS"][0]# tengo il primo valore lista 
        else:
            normalize = ''
  
        command = ("-vn %s %s %s %s %s %s %s" % (normalize, 
                                                 cmd_opt["AudioCodec"], 
                                                 cmd_opt["AudioBitrate"][1], 
                                                 cmd_opt["AudioDepth"][1], 
                                                 cmd_opt["AudioRate"][1], 
                                                 cmd_opt["AudioChannel"][1],
                                                 self.threads,
                                              ))
        vinc = DIRconf.split('videomass')[0] + 'vinc'
        if os.path.exists(vinc):
            with wx.FileDialog(self, _("Videomass: Choose a preset "
                                       "to storing data"), 
                defaultDir=os.path.join(vinc, 'presets'),
                wildcard="Vinc presets (*.vip;)|*.vip;",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     
                filename = fileDialog.GetPath()
                t = _('Videomass: Create a new Vinc profile')
        else:
            with wx.FileDialog(self, "Enter name for new preset", 
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

        param = [' '.join(command.split()), '', cmd_opt["ExportExt"]]
        
        prstdlg = presets_addnew.MemPresets(self, filename, param, t)
        prstdlg.ShowModal()
