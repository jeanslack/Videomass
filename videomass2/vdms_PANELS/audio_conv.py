# -*- coding: UTF-8 -*-

#########################################################
# Name: audio_conv
# Porpose: Intarface for ffmpeg audio conversions and normalization
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

# Rev (02) August 2 2019
#########################################################

import wx
import os
import wx.lib.agw.floatspin as FS
import wx.lib.agw.gradientbutton as GB
from videomass2.vdms_IO.IO_tools import volumeDetectProcess, FFProbe
from videomass2.vdms_IO.filedir_control import inspect
from videomass2.vdms_DIALOGS.epilogue import Formula
from videomass2.vdms_DIALOGS import  audiodialogs, presets_addnew
                    
dirname = os.path.expanduser('~') # /home/user

# set widget colours in some case with html rappresentetion:
azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'
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
                 cpu_used, loglevel_type, ffprobe_link, OS,
                 iconanalyzes, iconsettings,):
        # passed attributes
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.threads = threads
        self.cpu_used = cpu_used
        self.loglevel_type = loglevel_type
        self.ffprobe_link = ffprobe_link
        self.OS = OS
        # others attributes:
        self.file_sources = []
        self.file_destin = ''

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
                 (_(u"Save audio from movie"))], style=wx.CB_DROPDOWN | 
                                                       wx.CB_READONLY)
        self.cmbx_a.SetSelection(4)
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_param = GB.GradientButton(self,
                                           size=(-1,25),
                                           bitmap=setbmp,
                                           label=_(u"Audio Options"))
        self.btn_param.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28,28))
        self.btn_param.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_param.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_param.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_param.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.txt_options = wx.TextCtrl(self, wx.ID_ANY, size=(265,-1),
                                          style=wx.TE_READONLY)
        self.ckb_onlynorm = wx.CheckBox(self, wx.ID_ANY, (
                                               _(u"Only Normalization")))
        self.ckb_norm = wx.CheckBox(self, wx.ID_ANY, (
                                               _(u"Audio Normalization")))
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self,
                                           size=(-1,25),
                                           bitmap=analyzebmp,
                                           label=_(u"Analyzes"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopEndColour(wx.Colour(205, 235, 222))
        
        
        self.lab_volmax = wx.StaticText(self, wx.ID_ANY, (_(u"Max Volume db.")))
        self.txt_volmax = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.lab_volmid = wx.StaticText(self, wx.ID_ANY, 
                                                   (_(u"Average Volume db."))
                                        )
        self.txt_volmid = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.lab_amplitude = wx.StaticText(self, wx.ID_ANY, (
                                    _(u"Max Peak Level Threshold:   ")))
        self.spin_amplitude = FS.FloatSpin(self, wx.ID_ANY, min_val=-99.0, 
                                    max_val=0.0, increment=1.0, value=-1.0, 
                                    agwStyle=FS.FS_LEFT, size=(-1,-1))
        self.spin_amplitude.SetFormat("%f")
        self.spin_amplitude.SetDigits(1)
        #----------------------Set Properties----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_global = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                "")), wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(7, 2, 0, 0)
        grid_sizer_1 = wx.GridSizer(2, 1, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(2, 4, 0, 0)
        #grid_sizer_5 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _(u"Audio Container Selection"))), 
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
        grid_sizer_3.Add(self.lab_volmax, 0, wx.TOP, 10)
        grid_sizer_3.Add(self.txt_volmax, 0, wx.TOP, 5)
        grid_sizer_3.Add(self.lab_volmid, 0, wx.TOP, 10)
        grid_sizer_3.Add(self.txt_volmid, 0, wx.TOP, 5)
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
        self.btn_param.SetToolTipString(_(u"Enable advanced settings as audio "
                                    u"bit-rate, audio channel and audio rate "
                                    u"of the selected audio codec.")
                                              )
        self.btn_analyzes.SetToolTipString(_(u"Calculate the maximum and average "
                                    u"peak in dB values of the one audio track "
                                    u"imported. This feature is disabled for "
                                    u"multiple file to process.")
                                              )
        self.txt_volmax.SetToolTipString(_(u"Maximum peak scanned in dB values."))
        self.txt_volmid.SetToolTipString(_(u"Average peak scanned in dB values."))
        self.spin_amplitude.SetToolTipString(_(u"Threshold for the maximum peak "
                                    u"level in dB values. The default setting "
                                    u"is -1.0 dB and is good for most of the "
                                    u"processes."))
        
        #----------------------Binding (EVT)----------------------#
        self.cmbx_a.Bind(wx.EVT_COMBOBOX, self.audioFormats)
        self.Bind(wx.EVT_BUTTON, self.on_Param, self.btn_param)
        self.Bind(wx.EVT_CHECKBOX, self.on_Enable_norm, self.ckb_norm)
        self.Bind(wx.EVT_CHECKBOX, self.on_OnlyNorm, self.ckb_onlynorm)
        self.Bind(wx.EVT_BUTTON, self.on_Analyzes, self.btn_analyzes)
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
        self.ckb_norm.SetValue(False),
        self.btn_analyzes.Disable(), self.lab_volmax.Disable()
        self.txt_volmax.Disable(), self.lab_volmid.Disable()
        self.txt_volmid.Disable(), self.lab_amplitude.Disable()
        self.txt_volmax.SetValue(""), self.txt_volmid.SetValue("")
        self.spin_amplitude.Disable(), self.spin_amplitude.SetValue(-1.0)
        cmd_opt["Normalize"] = ""
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
        if self.cmbx_a.GetValue() == _(u"Save audio from movie"):
            if self.ckb_norm.IsChecked():
                self.normalization_disabled()
            self.ckb_norm.Disable(), self.ckb_onlynorm.Disable()
            self.txt_options.Disable(), self.btn_param.Disable()
            file_sources = self.parent.file_sources[:]
            self.audiocopy(file_sources)
        else:
            if not self.ckb_norm.IsChecked():# è l'unico caso questo
                self.ckb_norm.Enable(), self.ckb_onlynorm.Enable(), 
                self.txt_options.Enable(), self.btn_param.Enable()
            cmd_opt["AudioContainer"] = self.cmbx_a.GetValue()
            cmd_opt["AudioCodec"] = \
                                    acodecs[self.cmbx_a.GetValue()]
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
                if 'Not set' in data[3][0]:
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
        Try copying and saving the audio stream on a video by recognizing 
        the codec and then assigning a container/format. If there is more than
        one audio stream in a video, a choice is made to the user.
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
            audio_list = metadata.get_audio_codec_name()
            # ...and proceed to checkout:
            if audio_list == None:
                wx.MessageBox(_(u"There are no audio streams:\n%s ") % (files), 
                            'Videomass: warning', wx.ICON_EXCLAMATION, self)
                return

            elif len(audio_list) > 1:
                dlg = wx.SingleChoiceDialog(self, 
                        _(u"The imported video contains multiple audio\n" 
                        u"streams. Select which stream you want to\n"
                        u"export between these:"), 
                        _(u"Videomass: Stream choice"),
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
                        cmd_opt["ExportExt"].append(cn)
                    else:
                        wx.MessageBox(_(u"Nothing choice:\n%s ") % (files), 
                            'Videomass: Error', wx.ICON_ERROR, self)
                        return
                else:
                    pass
                dlg.Destroy()
            else:
                cn = ''.join(audio_list[0]).split()[4]
                indx = ''.join(audio_list[0]).split()[1]
                cmd_opt["AudioCodec"].append("-map 0:%s -c copy" % indx)
                cmd_opt["CodecCopied"].append(cn)#used for epilogue
                if cn in ('aac','alac'): cn = 'm4a'
                if cn in ('ogg','vorbis'): cn = 'oga'
                cmd_opt["ExportExt"].append(cn)

    #------------------------------------------------------------------#
    def on_Enable_norm(self, evt):
        """
        Choice if use or not audio normalization
        """
        msg = (_(u"Tip: check the volume peak by pressing the Analyzes button; "
               u"set the normalize maximum amplitude or accept "
               u"default dB value (-1.0)"))
        if self.ckb_norm.IsChecked():# if checked
            self.parent.statusbar_msg(msg, greenolive)
            self.btn_analyzes.SetForegroundColour(wx.Colour(28,28,28))
            self.btn_analyzes.Enable(), self.spin_amplitude.Enable(),
            self.lab_amplitude.Enable(), 
            if len(self.parent.file_sources) == 1:# se solo un file
                self.lab_volmid.Enable(), self.txt_volmid.Enable(),
                self.lab_volmax.Enable(), self.txt_volmax.Enable(),

        else:# is not checked
            self.parent.statusbar_msg(_(u"Disable audio normalization"), None)
            self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
            self.btn_analyzes.Disable(), self.lab_volmax.Disable()
            self.txt_volmax.SetValue(""), self.txt_volmid.SetValue("")
            self.txt_volmax.Disable(), self.lab_volmid.Disable()
            self.txt_volmid.Disable(), self.lab_amplitude.Disable()
            self.spin_amplitude.Disable(), self.spin_amplitude.SetValue(-1.0)
            
        cmd_opt["Normalize"] = ""
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
        else:
            self.cmbx_a.Enable(), self.btn_param.Enable(),
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
        msg = (_(u"The audio stream peak level is equal to or higher " 
               u"than the level set on the threshold. If you proceed, "
               u"there will be no changes."))
        self.parent.statusbar_msg("",None)
        normalize = self.spin_amplitude.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, file_sources, self.OS)

        if data[1]:
            wx.MessageBox(data[1], "Videomass: ERROR!", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for v in data[0]:
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(normalize)
                if float(maxvol) >= float(normalize):
                    self.parent.statusbar_msg(msg, yellow)

                volume.append("-af volume=%sdB" % (str(offset)[1:]))
                    
                if len(data[0]) == 1:# append in textctrl
                    self.txt_volmax.SetValue("")
                    self.txt_volmid.SetValue("")
                    self.txt_volmax.AppendText(v[0])
                    self.txt_volmid.AppendText(v[1])
        print volume
        cmd_opt["Normalize"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        
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
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        File existence verification procedures, overwriting control and 
        data redirecting .
        """
        # check normalization data offset, if enable.
        if self.ckb_norm.IsChecked():
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_(u"Missing volume dectect!\n"
                              u"Press the analyze button before proceeding."),
                                "Videomass: Warning!", wx.ICON_WARNING)
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
        # lenghmax: count processing cicles for batch mode
        typeproc, file_sources, dir_destin,\
        filename, base_name, lenghmax = checking


        if self.cmbx_a.GetValue() == _(u"Save audio from movie"):
            self.grabaudioProc(file_sources, dir_destin, lenghmax, logname)
        else:
            self.stdProc(file_sources, dir_destin, lenghmax, logname)

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, lenghmax, logname):
        """
        Composes the ffmpeg command strings for the batch mode processing.
        """
        if self.ckb_onlynorm.IsChecked():
            title = 'Audio Normalization'
            cmd = ("-loglevel %s %s -vn %s %s -y" % (self.loglevel_type, 
                                                  self.time_seq, 
                                                  self.threads,
                                                  self.cpu_used,)
                                                  )
            command = " ".join(cmd.split())# mi formatta la stringa
            valupdate = self.update_dict(lenghmax)
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
                                           lenghmax, 
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#call function more above
        else:
            title = 'Audio Conversion'
            command = ("-loglevel %s %s -vn %s %s %s %s %s %s %s -y" % (
                                                self.loglevel_type, 
                                                self.time_seq,
                                                cmd_opt["AudioCodec"],
                                                cmd_opt["AudioBitrate"][1], 
                                                cmd_opt["AudioDepth"][1], 
                                                cmd_opt["AudioRate"][1], 
                                                cmd_opt["AudioChannel"][1], 
                                                self.threads,
                                                self.cpu_used,)
                                                                    )
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(lenghmax)
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
                                           lenghmax,
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).split('.')[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                              cmd_opt["ExportExt"]))
        
    #------------------------------------------------------------------#
    def grabaudioProc(self, file_sources, dir_destin, 
                             lenghmax, logname):
        """
        Composes the ffmpeg command strings for the batch_process_changes.
        """
        title = _(u'Save audio from movies')
        cmdsplit1 = ("-loglevel %s %s -vn" % (self.loglevel_type, 
                                              self.time_seq)
                                              )
        cmdsplit2 = ("%s %s -y" % (self.threads, self.cpu_used,))

        valupdate = self.update_dict(lenghmax)
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
                                       lenghmax, #list
                                       )
            # used for play preview and mediainfo:
            f = os.path.basename(file_sources[0]).split('.')[0]
            self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                             cmd_opt["ExportExt"][0]))

    #------------------------------------------------------------------#
    def update_dict(self, lenghmax):
        """
        This method is required for update all cmd_opt
        dictionary values before send at epilogue
        """
        numfile = "%s file in pending" % str(lenghmax)
        if cmd_opt["Normalize"]:
            normalize = 'Enable'
        else:
            normalize = 'Disable'
            
        if self.ckb_onlynorm.IsChecked():
            formula = (_(u"SUMMARY:\n\nFile Queue:\
                       \nAudio Normalization:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s" % (numfile, 
                                            normalize, 
                                            self.time_seq
                                            )
                        )
        elif self.cmbx_a.GetValue() == _(u"Save audio from movie"):
            formula = (_(u"SUMMARY:\n\nFile Queue:\
                      \nAudio Container:\nCodec copied:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s\n%s" % (numfile, 
                                                cmd_opt["ExportExt"],
                                                cmd_opt["CodecCopied"], 
                                                self.time_seq)
                                                )
        else:
            formula = (_(u"SUMMARY:\n\nFile Queue:\
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
        if cmd_opt["Normalize"]:
            
            if wx.MessageBox(_(u"Audio normalization is a specific process "
                             u"applied track by track.\n\n"
                             u"Are you sure to proceed ?"), 
                             _(u'Videomass: Audio normalization enabled!'), 
                             wx.ICON_QUESTION | wx.YES_NO, 
                            None) == wx.NO:
                return #Se L'utente risponde no
            else:
                normalize = cmd_opt["Normalize"][0]# tengo il primo valore lista
        else:
            normalize = ''
        
        if self.ckb_onlynorm.IsChecked():
            command = ("-vn %s" % normalize)
            command = ' '.join(command.split())# sistemo gli spazi
            list = [command, cmd_opt["ExportExt"]]
            
        elif self.cmbx_a.GetValue() == _(u"Save audio from movie"):
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
        full_pathname = '%s/.videomass/preset-v1-Personal.vdms' % dirname
        
        prstdlg = presets_addnew.MemPresets(self, 'addprofile', full_pathname, 
                                            filename, list, 
                    _(u'Videomass: Create a new profile on "%s" preset') % (
                                                                name_preset))
        prstdlg.ShowModal()
