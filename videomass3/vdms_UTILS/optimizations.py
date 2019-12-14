# -*- coding: UTF-8 -*-

#########################################################
# Name: optimizations.py
# Porpose: contains the optimization presets for av_conversions.py
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev December.12.2019
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
#self.Bind(wx.EVT_COMBOBOX, self.videoCodec, self.cmb_Vcod)
        #self.Bind(wx.EVT_COMBOBOX, self.on_Container, self.cmb_Vcont)
        #self.Bind(wx.EVT_COMBOBOX, self.on_Media, self.cmb_Media)
        #self.Bind(wx.EVT_RADIOBOX, self.on_Deadline, self.rdb_deadline)
        #self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        #self.Bind(wx.EVT_CHECKBOX, self.on_WebOptimize, self.ckbx_web)
        #self.Bind(wx.EVT_SPINCTRL, self.on_Bitrate, self.spin_Vbrate)
        #self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Crf, self.slider_CRF)
        #self.Bind(wx.EVT_BUTTON, self.on_Enable_vsize, self.btn_videosize)
        #self.Bind(wx.EVT_BUTTON, self.on_Enable_crop, self.btn_crop)
        #self.Bind(wx.EVT_BUTTON, self.on_Enable_rotate, self.btn_rotate)
        #self.Bind(wx.EVT_BUTTON, self.on_Enable_lacing, self.btn_lacing)
        #self.Bind(wx.EVT_BUTTON, self.on_Enable_denoiser, self.btn_denois)
        #self.Bind(wx.EVT_BUTTON, self.on_FiltersPreview, self.btn_preview)
        #self.Bind(wx.EVT_BUTTON, self.on_FiltersClear, self.btn_reset)
        #self.Bind(wx.EVT_COMBOBOX, self.on_Vaspect, self.cmb_Vaspect)
        #self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmb_Fps)
        #self.Bind(wx.EVT_RADIOBOX, self.on_AudioCodecs, self.rdb_a)
        #self.Bind(wx.EVT_BUTTON, self.on_AudioParam, self.btn_aparam)
        #self.Bind(wx.EVT_COMBOBOX, self.on_audioINstream, self.cmb_A_inMap)
        #self.Bind(wx.EVT_COMBOBOX, self.on_audioOUTstream, self.cmb_A_outMap)
        #self.Bind(wx.EVT_RADIOBOX, self.onNormalize, self.rdbx_normalize)
        #self.Bind(wx.EVT_SPINCTRL, self.on_enter_Ampl, self.spin_target)
        #self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_voldect)
        #self.Bind(wx.EVT_COMBOBOX, self.on_xOptimize, self.cmb_264optimize)
        #self.Bind(wx.EVT_COMBOBOX, self.on_vpOptimize, self.cmb_vp9optimize)
        #self.Bind(wx.EVT_COMBOBOX, self.on_xPreset, self.cmb_preset)
        #self.Bind(wx.EVT_COMBOBOX, self.on_xProfile, self.cmb_profile)
        #self.Bind(wx.EVT_COMBOBOX, self.on_Level, self.cmb_level)
        #self.Bind(wx.EVT_COMBOBOX, self.on_xTune, self.cmb_tune)
        #self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)

        ##-------------------------------------- initialize default layout:
        #self.rdb_a.SetSelection(0), self.cmb_Vcod.SetSelection(1)
        #self.cmb_Media.SetSelection(0), self.cmb_Vcont.SetSelection(0)
        #self.ckbx_pass.SetValue(False), self.slider_CRF.SetValue(23)
        #self.cmb_Fps.SetSelection(0), self.cmb_Vaspect.SetSelection(0)
        #self.cmb_Pixfrm.SetSelection(1), self.cmb_Submap.SetSelection(1)
        #self.cmb_A_outMap.SetSelection(1), self.cmb_A_inMap.SetSelection(0)
        #self.UI_set()
        #self.audio_default()
        #self.normalize_default()


#------------------------------------------------------------------------
def vp9(prename):
    """
    evaluate the prename of optimization and return an corresponding
    string object wich must be evaluate by builtin function eval()
    
    """
    if prename == 'Vp9 best for Archive':
    
        return '''(
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('Vp9'), self.videoCodec(self),
                self.spin_Vbrate.SetValue(0), self.on_Vbitrate(self),
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.slider_CRF.SetValue(30), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('best'), 
                self.on_Deadline(self), self.spin_cpu.SetValue(1), 
                self.ckbx_multithread.SetValue(True),
                self.cmb_Pixfrm.SetSelection(0), 
                self.rdb_a.SetStringSelection('OPUS'),
                self.on_AudioCodecs(self),)'''
                
    elif prename == 'Vp9 CBR Web streaming':
        return '''(
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('Vp9'), self.videoCodec(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.spinMinr.SetValue(1000), self.spinMaxr.SetValue(1000),
                self.spinBufsize.SetValue(0),
                self.slider_CRF.SetValue(-1), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('good'), 
                self.on_Deadline(self), self.spin_cpu.SetValue(0), 
                self.ckbx_multithread.SetValue(True),
                self.cmb_Pixfrm.SetSelection(1),)'''
    
    elif prename == 'Vp9 Constrained ABR-VBV live streaming':
        return '''(
                self.cmb_Vcod.SetStringSelection('Vp9'), self.videoCodec(self),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.spinMaxr.SetValue(0),
                self.spinMinr.SetValue(1000), self.spinBufsize.SetValue(2000),
                self.slider_CRF.SetValue(-1), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('good'), 
                self.on_Deadline(self), self.spin_cpu.SetValue(0), 
                self.ckbx_multithread.SetValue(True),
                self.cmb_Pixfrm.SetSelection(0),)'''

#------------------------------------------------------------------------
def hevc_avc(prename):
    """
    x264, x265
    evaluate the prename of optimization and return an corresponding
    string object wich must be evaluate by builtin function eval()
    
    """
    if prename == 'x264 best for Archive':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.slider_CRF.SetValue(23), self.on_Crf(self), 
                self.cmb_Pixfrm.SetSelection(0),)'''
    
    elif prename == 'x265 best for Archive':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x265'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.slider_CRF.SetValue(28), self.on_Crf(self), 
                self.cmb_Pixfrm.SetSelection(0),)'''
    
    elif prename == 'x264 ABR for devices':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self), 
                self.cmb_Pixfrm.SetSelection(1),)'''
    
    elif prename == 'x264 ABR for devices':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x265'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self), 
                self.cmb_Pixfrm.SetSelection(1),)'''
    
    elif prename == 'x265 ABR for devices':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self), 
                self.cmb_Pixfrm.SetSelection(1),)'''
    

    elif prename == 'x264 ABR for devices':
    
        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'), self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self), 
                self.cmb_Pixfrm.SetSelection(1),)'''
    
    

