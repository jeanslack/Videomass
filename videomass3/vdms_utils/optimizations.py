# -*- coding: UTF-8 -*-
# Name: optimizations.py
# Porpose: contains the optimization presets for av_conversions.py
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
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

def vp9(prename):
    """
    evaluate the prename of optimization and return an corresponding
    string object wich must be evaluate by builtin function eval()

    """
    if prename == 'Default':

        return '''(
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False),
                self.cmb_Vcod.SetStringSelection('Vp9'),
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0), self.cmb_Pixfrm.SetSelection(1),
                self.videoCodec(self),)'''

    elif prename == 'Vp9 best for Archive':
        return '''(
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('Vp9'),
                self.videoCodec(self),
                self.spin_Vbrate.SetValue(0), self.on_Vbitrate(self),
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.slider_CRF.SetValue(30), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('best'),
                self.on_Deadline(self), self.spin_cpu.SetValue(1),
                self.ckbx_rowMt1.SetValue(True),
                self.cmb_Pixfrm.SetSelection(0),
                self.rdb_a.SetStringSelection('OPUS'),
                self.on_AudioCodecs(self),)'''

    elif prename == 'Vp9 CBR Web streaming':
        return '''(
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('Vp9'),
                self.videoCodec(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.spinMinr.SetValue(1000), self.spinMaxr.SetValue(1000),
                self.spinBufsize.SetValue(0),
                self.slider_CRF.SetValue(-1), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('good'),
                self.on_Deadline(self), self.spin_cpu.SetValue(0),
                self.ckbx_rowMt1.SetValue(True),
                self.cmb_Pixfrm.SetSelection(1),)'''

    elif prename == 'Vp9 Constrained ABR-VBV live streaming':
        return '''(
                self.cmb_Vcod.SetStringSelection('Vp9'),
                self.videoCodec(self),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.spinMaxr.SetValue(0),
                self.spinMinr.SetValue(1000), self.spinBufsize.SetValue(2000),
                self.slider_CRF.SetValue(-1), self.on_Crf(self),
                self.rdb_deadline.SetStringSelection('good'),
                self.on_Deadline(self), self.spin_cpu.SetValue(0),
                self.ckbx_rowMt1.SetValue(True),
                self.cmb_Pixfrm.SetSelection(0),)'''


def hevc_avc(prename):
    """
    x264, x265
    evaluate the prename of optimization and return an corresponding
    string object wich must be evaluate by builtin function eval()

    """
    if prename == 'Default':

        return '''(
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False),
                self.cmb_Vcod.SetStringSelection('x264'),
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0), self.cmb_Pixfrm.SetSelection(1),
                self.videoCodec(self),)'''

    elif prename == 'x264 best for Archive':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'),
                self.videoCodec(self), self.cmb_Vcont.SetSelection(0),
                self.on_Container(self), self.cmb_Pixfrm.SetSelection(0),)'''

    elif prename == 'x265 best for Archive':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(False), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(False), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x265'),
                self.videoCodec(self), self.cmb_Vcont.SetSelection(0),
                self.on_Container(self), self.cmb_Pixfrm.SetSelection(0),)'''

    elif prename == 'x264 ABR for devices':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'),
                self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.cmb_Pixfrm.SetSelection(1),)'''

    elif prename == 'x265 ABR for devices':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(0),
                self.spinBufsize.SetValue(0),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x265'),
                self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.cmb_Pixfrm.SetSelection(1),)'''

    elif prename == 'x264 ABR-VBV live streaming':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(1000),
                self.spinBufsize.SetValue(2000),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x264'),
                self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.cmb_Pixfrm.SetSelection(1),)'''

    elif prename == 'x265 ABR-VBV live streaming':

        return '''(
                self.spinMinr.SetValue(0), self.spinMaxr.SetValue(1000),
                self.spinBufsize.SetValue(2000),
                self.ckbx_web.SetValue(True), self.on_WebOptimize(self),
                self.ckbx_pass.SetValue(True), self.on_Pass(self),
                self.cmb_Vcod.SetStringSelection('x265'),
                self.videoCodec(self),
                self.cmb_Vcont.SetSelection(0), self.on_Container(self),
                self.spin_Vbrate.SetValue(1000), self.on_Vbitrate(self),
                self.cmb_Pixfrm.SetSelection(1),)'''
