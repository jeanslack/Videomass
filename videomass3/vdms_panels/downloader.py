# -*- coding: UTF-8 -*-

#########################################################
# Name: downloader.py
# Porpose: sets youtube-dl options
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
from videomass3.vdms_io import IO_tools
from videomass3.vdms_utils.utils import format_bytes
from videomass3.vdms_utils.utils import time_human
from videomass3.vdms_frames.ydl_mediainfo import YDL_Mediainfo
import wx

vquality = {'Best quality video': 'best',
            'Worst quality video': 'worst'}

aformats = {("Default audio format"): ("best"),
            ("wav"): ("wav"),
            ("mp3"): ("mp3"),
            ("aac"): ("aac"),
            ("m4a"): ("m4a"),
            ("vorbis"): ("vorbis"),
            ("opus"): ("opus"),
            ("flac"): ("flac"),
            }

aquality = {'Best quality audio': 'best',
            'Worst quality audio': 'worst'}

opt = {"NO_PLAYLIST": True, "THUMB": False, "METADATA": False,
       "V_QUALITY": "best", "A_FORMAT": "best", "A_QUALITY": "best",
       "SUBTITLES": False,
       }

yellow = '#a29500'
red = '#ea312d'


class Downloader(wx.Panel):
    """
    This panel gives a graphic layout to some features of youtube-dl
    """
    def __init__(self, parent, OS):
        """
        The first item of the self.info is a complete list of all
        informations getting by extract_info method from youtube_dl
        module. The second item can be a status error witch sets the
        self.error attribute.
        """
        self.parent = parent
        self.OS = OS
        self.info = []
        self.error = False
        wx.Panel.__init__(self, parent, -1)
        """constructor"""
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        frame = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                                "")), wx.VERTICAL)
        sizer_base.Add(frame, 1, wx.ALL | wx.EXPAND, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        frame.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)
        self.choice = wx.Choice(self, wx.ID_ANY,
                                choices=[_('Default'),
                                         _('Video + Audio'),
                                         _('Audio only'),
                                         _('Format code')],
                                size=(-1, -1),
                                )
        self.choice.SetSelection(0)
        sizer.Add(self.choice, 0, wx.EXPAND | wx.ALL, 15)
        grid_v = wx.FlexGridSizer(1, 7, 0, 0)
        sizer.Add(grid_v, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        f = [x for x in vquality.keys()]
        self.cmbx_vq = wx.ComboBox(self, wx.ID_ANY, choices=f,
                                   size=(150, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_vq.SetSelection(0)
        # grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_vq, 0, wx.ALL, 5)
        self.cmbx_aq = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in aquality.keys()],
                                   size=(150, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        self.cmbx_aq.Disable()
        # grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_aq, 0, wx.ALL, 5)
        self.cmbx_af = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in aformats.keys()],
                                   size=(150, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        grid_v.Add(self.cmbx_af, 0, wx.ALL, 5)

        self.txt_code = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER, size=(50, -1)
                                    )
        self.txt_code.Disable()
        self.stext = wx.StaticText(self, wx.ID_ANY,
                                   (_('Enter Format Code here:'))
                                   )
        self.stext.Disable()
        grid_v.Add(self.stext, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_v.Add(self.txt_code, 0, wx.ALL, 5)
        self.txt_code.WriteText('18')
        # -------------opt
        grid_opt = wx.FlexGridSizer(1, 4, 0, 0)
        sizer.Add(grid_opt, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.ckbx_pl = wx.CheckBox(self, wx.ID_ANY,
                                   (_('Download all playlist'))
                                   )
        grid_opt.Add(self.ckbx_pl, 0, wx.ALL, 5)
        self.ckbx_thumb = wx.CheckBox(self, wx.ID_ANY,
                                      (_('Embed thumbnail in audio file'))
                                      )
        grid_opt.Add(self.ckbx_thumb, 0, wx.ALL, 5)
        self.ckbx_meta = wx.CheckBox(self, wx.ID_ANY,
                                     (_('Add metadata to file'))
                                     )
        grid_opt.Add(self.ckbx_meta, 0, wx.ALL, 5)
        self.ckbx_sb = wx.CheckBox(self, wx.ID_ANY,
                                   (_('Write subtitles to video'))
                                   )
        grid_opt.Add(self.ckbx_sb, 0, wx.ALL, 5)
        line_1 = wx.StaticLine(self, pos=(25, 50), size=(650, 0))
        sizer.Add(line_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT |
                                 wx.SUNKEN_BORDER
                                 )
        sizer.Add(self.fcode, 1, wx.EXPAND | wx.ALL |
                  wx.ALIGN_CENTER_HORIZONTAL, 10
                  )
        self.fcode.InsertColumn(0, (_('TITLE')), width=180)
        self.fcode.InsertColumn(1, (_('URL')), width=80)
        self.fcode.InsertColumn(2, (_('Format Code')), width=100)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution')), width=140)
        self.fcode.InsertColumn(5, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(6, (_('fps')), width=60)
        self.fcode.InsertColumn(7, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(8, (_('Size')), width=80)
        self.fcode.Hide()

        if OS == 'Darwin':
            self.fcode.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.fcode.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.SetSizer(sizer_base)
        self.Layout()
        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_Choice)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_Vq)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_Af)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_Aq)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_Playlist)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_Thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_Metadata)
        self.ckbx_sb.Bind(wx.EVT_CHECKBOX, self.on_Subtitles)

    # -----------------------------------------------------------------#

    def parse_info(self):
        """
        Data parsing from youtube-dl extract_info. This method should
        also populate the listctrl and fill the self.info list.

        If meta[1] is None, sets self.info attribute with dict objetc
        items and return error=False. Otherwise self.info is a empty
        list and return error=True.
        """
        index = 0
        if not self.info:
            for link in self.parent.data_url:
                data = IO_tools.youtube_info(link)
                for meta in data:
                    if meta[1]:
                        # self.parent.statusbar_msg('Youtube Downloader', None)
                        wx.MessageBox(meta[1], 'youtube_dl ERROR',
                                      wx.ICON_ERROR
                                      )
                        self.info, self.error = [], True
                        return self.error
                    if 'entries' in meta[0]:
                        meta[0]['entries'][0]  # not parse all playlist
                    ftime = '%s (%s sec.)' % (time_human(meta[0]['duration']),
                                              meta[0]['duration'])
                    date = '%s/%s/%s' % (meta[0]['upload_date'][:4],
                                         meta[0]['upload_date'][4:6],
                                         meta[0]['upload_date'][6:8])
                    self.info.append({
                                'url': link,
                                'title': meta[0]['title'],
                                'categories': meta[0]['categories'],
                                'license': meta[0]['license'],
                                'format': meta[0]['format'],
                                'upload_date': date,
                                'uploader': meta[0]['uploader'],
                                'view': meta[0]['view_count'],
                                'like': meta[0]['like_count'],
                                'dislike': meta[0]['dislike_count'],
                                'average_rating': meta[0]['average_rating'],
                                'id': meta[0]['id'],
                                'duration': ftime,
                                'description': meta[0]['description'],
                                    })
                    self.fcode.InsertItem(index, meta[0]['title'])
                    self.fcode.SetItem(index, 1, link)
                    self.fcode.SetItemBackgroundColour(index, 'GREEN')

                    formats = meta[0].get('formats', [meta[0]])
                    for f in formats:
                        index += 1
                        if f['vcodec'] == 'none':
                            vcodec = ''
                            fps = ''
                        else:
                            vcodec = f['vcodec']
                            fps = '%sfps' % f['fps']
                        if f['acodec'] == 'none':
                            acodec = 'Video only'
                        else:
                            acodec = f['acodec']
                        if f['filesize']:
                            size = format_bytes(float(f['filesize']))
                        else:
                            size = ''

                        self.fcode.InsertItem(index, '')
                        self.fcode.SetItem(index, 1, '')
                        self.fcode.SetItem(index, 2, f['format_id'])
                        self.fcode.SetItem(index, 3, f['ext'])
                        self.fcode.SetItem(index, 4, f['format'].split('-')[1])
                        self.fcode.SetItem(index, 5, vcodec)
                        self.fcode.SetItem(index, 6, fps)
                        self.fcode.SetItem(index, 7, acodec)
                        self.fcode.SetItem(index, 8, size)

        # self.parent.statusbar_msg(_('Ready, Youtube Downloader'), None)

        return self.error
    # -----------------------------------------------------------------#

    def on_show_info(self):
        """
        show data information. This method is called by the main frame
        when the 'show stream information' button is pressed.

        """
        if not self.info:
            error = self.parse_info()
            if error:
                return

        dialog = YDL_Mediainfo(self.info, self.OS)
        dialog.Show()
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        Show listctrl to choose format code

        """
        if not self.info:
            error = self.parse_info()
            if error:
                return

        self.fcode.Show()
        self.Layout()
    # -----------------------------------------------------------------#

    def on_Choice(self, event):
        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable(), self.cmbx_aq.Disable()
            self.cmbx_vq.Enable(), self.txt_code.Disable()
            self.fcode.Hide(), self.stext.Disable()

        elif self.choice.GetSelection() == 1:
            self.cmbx_af.Disable(), self.cmbx_aq.Enable()
            self.cmbx_vq.Enable(), self.txt_code.Disable()
            self.fcode.Hide(), self.stext.Disable()

        elif self.choice.GetSelection() == 2:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Enable(), self.txt_code.Disable()
            self.fcode.Hide(), self.stext.Disable()

        elif self.choice.GetSelection() == 3:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Disable(), self.txt_code.Enable()
            # self.fcode.Enable(),
            self.stext.Enable()
            self.on_format_codes()
    # -----------------------------------------------------------------#

    def on_Vq(self, event):
        opt["V_QUALITY"] = vquality[self.cmbx_vq.GetValue()]
    # -----------------------------------------------------------------#

    def on_Af(self, event):
        opt["A_FORMAT"] = aformats.get(self.cmbx_af.GetValue())
    # -----------------------------------------------------------------#

    def on_Aq(self, event):
        opt["A_QUALITY"] = aquality.get(self.cmbx_aq.GetValue())
    # -----------------------------------------------------------------#

    def on_Playlist(self, event):
        if self.ckbx_pl.IsChecked():
            opt["NO_PLAYLIST"] = False
        else:
            opt["NO_PLAYLIST"] = True
    # -----------------------------------------------------------------#

    def on_Thumbnails(self, event):
        if self.ckbx_thumb.IsChecked():
            opt["THUMB"] = True
        else:
            opt["THUMB"] = False
    # -----------------------------------------------------------------#

    def on_Metadata(self, event):
        if self.ckbx_meta.IsChecked():
            opt["METADATA"] = True
        else:
            opt["METADATA"] = False
    # -----------------------------------------------------------------#

    def on_Subtitles(self, event):
        if self.ckbx_sb.IsChecked():
            opt["SUBTITLES"] = True
        else:
            opt["SUBTITLES"] = False
    # -----------------------------------------------------------------#

    def on_Start(self):

        logname = 'Youtube_downloader.log'
        urls = self.parent.data_url

        if self.choice.GetSelection() == 0:
            data = {'format': opt["V_QUALITY"],
                    'noplaylist': opt["NO_PLAYLIST"],
                    'writethumbnail': opt["THUMB"],
                    'outtmpl': '%(title)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': opt["METADATA"],
                    'writesubtitles': opt["SUBTITLES"],
                    'postprocessors': []
                    }
        if self.choice.GetSelection() == 1:
            data = {'format': '{}video,{}audio'.format(opt["V_QUALITY"],
                                                       opt["A_QUALITY"]),
                    'noplaylist': opt["NO_PLAYLIST"],
                    'writethumbnail': opt["THUMB"],
                    'outtmpl': '%(title)s.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': opt["METADATA"],
                    'writesubtitles': opt["SUBTITLES"],
                    'postprocessors': []
                    }
        elif self.choice.GetSelection() == 2:  # audio only

            data = {'format': 'best',
                    'noplaylist': opt["NO_PLAYLIST"],
                    'writethumbnail': opt["THUMB"],
                    'outtmpl': '%(title)s.%(ext)s',
                    'extractaudio': True,
                    'addmetadata': opt["METADATA"],
                    'writesubtitles': False,
                    'postprocessors': [{'key': 'FFmpegExtractAudio',
                                        'preferredcodec': opt["A_FORMAT"],
                                        }]
                    }
        if self.choice.GetSelection() == 3:
            code = self.txt_code.GetValue().strip()
            if not code.isdigit() or not code:
                wx.MessageBox(_('Enter a `Format Code` number in the text '
                                'box, please'),
                              'Videomass', wx.ICON_INFORMATION
                              )
                self.txt_code.SetBackgroundColour((255, 192, 255))
                return

            data = {'format': code,
                    'noplaylist': opt["NO_PLAYLIST"],
                    'writethumbnail': opt["THUMB"],
                    'outtmpl': '%(title)s.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': opt["METADATA"],
                    'writesubtitles': opt["SUBTITLES"],
                    'postprocessors': []
                    }
        self.parent.switch_Process('youtubedl downloader',
                                   urls,
                                   '',
                                   self.parent.file_destin,
                                   data,
                                   None,
                                   '',
                                   '',
                                   logname,
                                   len(urls),
                                   )
