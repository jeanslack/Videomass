# -*- coding: UTF-8 -*-

#########################################################
# Name: youtubedl_ui.py
# Porpose: youtube-dl user interface
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
import itertools

# constants

MSG_1 = _('At least one "Format Code" must be selected for each URL.')

RED = '#ea312d'
ORANGE = 206, 57, 35

VQUALITY = {('Best quality video'): ['best', 'best'],
            ('Worst quality video'): ['worst', 'worst']}

AFORMATS = {("Default audio format"): ("best", "--extract-audio"),
            ("wav"): ("wav", "--extract-audio --audio-format wav"),
            ("mp3"): ("mp3", "--extract-audio --audio-format mp3"),
            ("aac"): ("aac", "--extract-audio --audio-format aac"),
            ("m4a"): ("m4a", "--extract-audio --audio-format m4a"),
            ("vorbis"): ("vorbis", "--extract-audio --audio-format vorbis"),
            ("opus"): ("opus", "--extract-audio --audio-format opus"),
            ("flac"): ("flac", "--extract-audio --audio-format flac"),
            }

AQUALITY = {('Best quality audio'): ['best', 'best'],
            ('Worst quality audio'): ['worst', 'worst']}

# variables

opt = {("NO_PLAYLIST"): [True, "--no-playlist"],
       ("THUMB"): [False, ""],
       ("METADATA"): [False, ""],
       ("V_QUALITY"): ["best", "best"],
       ("A_FORMAT"): ["best", "--extract-audio"],
       ("A_QUALITY"): ["best", "best"],
       ("SUBTITLES"): [False, ""],
       }

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
PYLIB_YDL = get.pylibYdl


class Downloader(wx.Panel):
    """
    This panel gives a graphic layout to some features of youtube-dl
    """
    def __init__(self, parent, OS):
        """
        The first item of the self.info is a complete list of all
        informations getting by extract_info method from youtube_dl
        module.
        """
        self.parent = parent
        self.oS = OS
        self.info = list()  # has data information for Show More button
        self.format_dict = dict()  # format codes order with URL matching
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
                                         _('Download audio and video splitted'),
                                         _('Download Audio only'),
                                         _('Download by format code')],
                                size=(-1, -1),
                                )
        self.choice.SetSelection(0)
        sizer.Add(self.choice, 0, wx.EXPAND | wx.ALL, 15)
        grid_v = wx.FlexGridSizer(1, 3, 0, 0)
        sizer.Add(grid_v, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        f = [x for x in VQUALITY.keys()]
        self.cmbx_vq = wx.ComboBox(self, wx.ID_ANY, choices=f,
                                   size=(200, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_vq.SetSelection(0)
        # grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_vq, 0, wx.ALL, 5)
        self.cmbx_aq = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in AQUALITY.keys()],
                                   size=(200, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        self.cmbx_aq.Disable()
        # grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_aq, 0, wx.ALL, 5)
        self.cmbx_af = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in AFORMATS.keys()],
                                   size=(200, -1), style=wx.CB_DROPDOWN |
                                   wx.CB_READONLY
                                   )
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        grid_v.Add(self.cmbx_af, 0, wx.ALL, 5)
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
        self.labcode = wx.StaticText(self, label=_("URLs loaded"))
        sizer.Add(self.labcode, 0, wx.ALL, 5)
        self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT |
                                 wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                 )
        sizer.Add(self.fcode, 1, wx.EXPAND, 10)
        self.codText = wx.TextCtrl(self, wx.ID_ANY, "",
                                   style=wx.TE_MULTILINE |
                                   wx.TE_READONLY |
                                   wx.TE_RICH2,
                                   # size=(500, -1)
                                   )
        sizer.Add(self.codText, 1, wx.ALL | wx.EXPAND, 10)
        self.codText.Disable()
        # -----------------------
        self.SetSizer(sizer_base)
        self.Layout()
        #----------------------- Properties
        if OS == 'Darwin':
            self.codText.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))
        else:
            self.codText.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))
        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_Choice)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_Vq)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_Af)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_Aq)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_Playlist)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_Thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_Metadata)
        self.ckbx_sb.Bind(wx.EVT_CHECKBOX, self.on_Subtitles)
        self.fcode.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
        self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.onCheck)
        self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.onCheck)
    # -----------------------------------------------------------------#

    def onCheck(self, event):
        """
        get data from row in the enabled checkbox and set the values
        on corresponding key e.g.:
        `key=url: values=a: audio v: video format list`
        Otherwise, reset values when disabled checkbox.
        """
        if not self.parent.sb.GetStatusText() == 'Youtube Downloader':
            self.parent.statusbar_msg('Youtube Downloader', None)

        if PYLIB_YDL is not None: # YuotubeDL is not used as module
            viddisp, auddisp = 'video ', 'audio '
        else:
            viddisp, auddisp = 'video', 'audio only'

        num = self.fcode.GetItemCount()
        for url in self.parent.data_url:
            self.format_dict[url] = []
            for i in range(num):
                if self.fcode.IsItemChecked(i):
                    if (self.fcode.GetItemText(i, 0)) == url:
                        if viddisp in self.fcode.GetItemText(i, 4):
                            dv = self.fcode.GetItemText(i, 2)
                            self.format_dict[url].append('Video: ' + dv)
                        elif auddisp in self.fcode.GetItemText(i, 4):
                            da = self.fcode.GetItemText(i, 2)
                            self.format_dict[url].append('Audio: ' + da)
                        else:
                            dv = self.fcode.GetItemText(i, 2)
                            self.format_dict[url].append('Video: ' + dv)

        self.codText.Clear()
        for k, v in self.format_dict.items():
            if not v:
                self.codText.SetDefaultStyle(wx.TextAttr(wx.Colour(ORANGE)))
                self.codText.AppendText('- %s  >>>  %s\n' % (k, v))
                self.codText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            else:
                self.codText.AppendText('- %s  >>>  %s\n' % (k, v))
        #print(self.format_dict)
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID2"):
            self.popupID2 = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID2)

        # build the menu
        menu = wx.Menu()
        itemfive = menu.Append(self.popupID2, _("Play selected url"))
        # show the popup menu
        self.PopupMenu(menu)

        menu.Destroy()
    # ----------------------------------------------------------------------

    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        if menuItem.GetItemLabel() == _("Play selected url"):
            self.parent.ExportPlay(self)
    # ----------------------------------------------------------------------

    def get_libraryformatcode(self):
        """
        Get URLs format code by generator object *youtube_info* and set
        populate the list control with new entries.
        """
        self.fcode.ClearAll()
        self.fcode.EnableCheckBoxes(enable=True)
        self.fcode.InsertColumn(0, (_('Url')), width=60)
        self.fcode.InsertColumn(1, (_('Title')), width=200)
        self.fcode.InsertColumn(2, (_('Format Code')), width=120)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution')), width=160)
        self.fcode.InsertColumn(5, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(6, (_('fps')), width=60)
        self.fcode.InsertColumn(7, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(8, (_('Size')), width=80)
        index = 0
        for link in self.parent.data_url:
            data = IO_tools.youtube_info(link)
            for meta in data:
                if meta[1]:
                    # self.parent.statusbar_msg('Youtube Downloader', None)
                    wx.MessageBox(meta[1], 'youtube_dl ERROR', wx.ICON_ERROR)
                    return True

            formats = iter(meta[0].get('formats', [meta[0]]))
            for n, f in enumerate(formats):
                if f.get('vcodec'):
                    vcodec, fps = f['vcodec'], '%sfps' % f.get('fps')
                else:
                    vcodec, fps = '', ''
                if f.get('acodec'):
                    acodec = f['acodec']
                else:
                    acodec = 'Video only'
                if f.get('filesize'):
                    size = format_bytes(float(f['filesize']))
                else:
                    size = 'N/A'

                self.fcode.InsertItem(index, link)
                self.fcode.SetItem(index, 1, meta[0]['title'])
                self.fcode.SetItem(index, 2, f['format_id'])
                self.fcode.SetItem(index, 3, f['ext'])
                self.fcode.SetItem(index, 4, f['format'].split('-')[1])
                self.fcode.SetItem(index, 5, vcodec)
                self.fcode.SetItem(index, 6, fps)
                self.fcode.SetItem(index, 7, acodec)
                self.fcode.SetItem(index, 8, size)
                if n == 0:
                    self.fcode.SetItemBackgroundColour(index, 'GREEN')
                index += 1
        return None
    # ----------------------------------------------------------------------

    def get_info(self):
        """
        Get media url informations by generator object *youtube_info*  .
        If meta[1] is None set self.info attribute with dict objetc items
        and return None. Otherwise self.info is a empty list and return True
        """
        for link in self.parent.data_url:
            data = IO_tools.youtube_info(link)
            for meta in data:
                if meta[1]:
                    # self.parent.statusbar_msg('Youtube Downloader', None)
                    wx.MessageBox(meta[1], 'youtube_dl ERROR', wx.ICON_ERROR)
                    del self.info[:]
                    return True
                if 'entries' in meta[0]:
                    meta[0]['entries'][0]  # not parse all playlist
                if 'duration' in meta[0]:
                    ftime = '%s (%s sec.)' % (time_human(meta[0]['duration']),
                                              meta[0]['duration'])
                else:
                    ftime = 'N/A'
                date = meta[0].get('upload_date')
                self.info.append({
                            'url': link,
                            'title': meta[0].get('title'),
                            'categories': meta[0].get('categories'),
                            'license': meta[0].get('license'),
                            'format': meta[0].get('format'),
                            'upload_date': date,
                            'uploader': meta[0].get('uploader'),
                            'view': meta[0].get('view_count'),
                            'like': meta[0].get('like_count'),
                            'dislike': meta[0].get('dislike_count'),
                            'average_rating': meta[0].get('average_rating'),
                            'id': meta[0].get('id'),
                            'duration': ftime,
                            'description': meta[0].get('description'),
                            })
        return None
    # -----------------------------------------------------------------#

    def get_executableformatcode(self):
        """
        Get format code and set new items for list control by generator object
        *youtube_getformatcode_exec*
        """
        self.fcode.ClearAll()
        self.fcode.EnableCheckBoxes(enable=True)
        self.fcode.InsertColumn(0, (_('Url')), width=200)
        self.fcode.InsertColumn(1, (_('Title')), width=50)
        self.fcode.InsertColumn(2, (_('Format Code')), width=120)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution note')), width=500)

        index = 0
        for link in self.parent.data_url:
            data = IO_tools.youtube_getformatcode_exec(link)
            for meta in data:
                if meta[1]:
                    wx.MessageBox(meta[0], 'Videomass', wx.ICON_ERROR)
                    self.info = []
                    return True
                self.info.append(link)
                i = 0
                for count, fc in enumerate(meta[0].split('\n')):
                    if not count > i:
                        i += 1
                    elif fc != '':
                        self.fcode.InsertItem(index, link)
                        self.fcode.SetItem(index, 1, 'N/A')
                        self.fcode.SetItem(index, 2, fc.split()[0])
                        self.fcode.SetItem(index, 3, fc.split()[1])
                        note = ' '.join(fc.split()[2:])
                        self.fcode.SetItem(index, 4, note)

                        if i + 1 == count:
                            self.fcode.SetItemBackgroundColour(index, 'GREEN')
                        index += 1

                    if fc.startswith('format code '):
                        i = count  # limit
        return None
    # -----------------------------------------------------------------#

    def on_urls_list(self, quality):
        """
        Populate list control with new entries as urls and
        related resolutions
        """
        self.codText.Disable()
        msg = _('URLs loaded')
        self.labcode.SetLabel(msg)
        self.fcode.ClearAll()
        self.fcode.EnableCheckBoxes(enable=False)
        self.fcode.InsertColumn(0, (_('Url')), width=500)
        self.fcode.InsertColumn(1, (_('Title')), width=50)
        self.fcode.InsertColumn(2, (_('Resolution note')), width=250)

        if self.parent.data_url:
            index = 0
            for link in self.parent.data_url:
                self.fcode.InsertItem(index, link)
                self.fcode.SetItem(index, 1, 'N/A')
                self.fcode.SetItem(index, 2, quality)
                index += 1
    # -----------------------------------------------------------------#

    def on_show_info(self):
        """
        show data information. This method is called by the main frame
        when the 'Show More' button is pressed.
        """
        if PYLIB_YDL is not None:  # YuotubeDL is not used as module
            wx.MessageBox(_('"Show more" only is enabled when Videomass '
                            'uses youtube-dl as imported library.'),
                          'Videomass', wx.ICON_INFORMATION)
            return

        if not self.info:
            ret = self.get_info()
            if ret:
                return

        dialog = YDL_Mediainfo(self.info, self.oS)
        dialog.Show()
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        get data and info and show listctrl to choose format code
        """
        msg = _('To select the "Format Code" enable the '
                'corresponding checkbox')
        self.labcode.SetLabel(msg)
        self.codText.Enable()

        if PYLIB_YDL is not None:  # youtube-dl as executable
            ret = self.get_executableformatcode()
            if ret:
                return  # do not enable fcode

        else:
            ret = self.get_libraryformatcode()
            if ret:
                return  # do not enable fcode

    # -----------------------------------------------------------------#

    def on_Choice(self, event):
        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable(), self.cmbx_aq.Disable()
            self.cmbx_vq.Enable()
            self.on_urls_list(opt["V_QUALITY"][1])

        elif self.choice.GetSelection() == 1:
            self.cmbx_af.Disable(), self.cmbx_aq.Enable()
            self.cmbx_vq.Enable()
            self.on_urls_list('%svideo+%saudio' % (opt["V_QUALITY"][1],
                                                   opt["A_QUALITY"][1]))

        elif self.choice.GetSelection() == 2:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Enable()
            self.on_urls_list('')

        elif self.choice.GetSelection() == 3:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Disable()
            self.on_format_codes()
    # -----------------------------------------------------------------#

    def on_Vq(self, event):
        opt["V_QUALITY"] = VQUALITY[self.cmbx_vq.GetValue()]
        index = 0
        if self.choice.GetSelection() == 0:
            q = opt["V_QUALITY"][1]
        elif self.choice.GetSelection() == 1:
            q = '%svideo+%saudio' % (opt["V_QUALITY"][1], opt["A_QUALITY"][1])
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 2, q)
            index += 1
    # -----------------------------------------------------------------#

    def on_Af(self, event):
        opt["A_FORMAT"] = AFORMATS.get(self.cmbx_af.GetValue())
        index = 0
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 2, '')
            index += 1
    # -----------------------------------------------------------------#

    def on_Aq(self, event):
        opt["A_QUALITY"] = AQUALITY.get(self.cmbx_aq.GetValue())

        index = 0
        q = '%svideo+%saudio' % (opt["V_QUALITY"][1], opt["A_QUALITY"][1])
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 2, q)
            index += 1
    # -----------------------------------------------------------------#

    def on_Playlist(self, event):
        if self.ckbx_pl.IsChecked():
            opt["NO_PLAYLIST"] = [False, "--yes-playlist"]
        else:
            opt["NO_PLAYLIST"] = [True, "--no-playlist"]
    # -----------------------------------------------------------------#

    def on_Thumbnails(self, event):
        if self.ckbx_thumb.IsChecked():
            opt["THUMB"] = [True, "--embed-thumbnail"]
        else:
            opt["THUMB"] = [False, ""]
    # -----------------------------------------------------------------#

    def on_Metadata(self, event):
        if self.ckbx_meta.IsChecked():
            opt["METADATA"] = [True, "--add-metadata"]
        else:
            opt["METADATA"] = [False, ""]
    # -----------------------------------------------------------------#

    def on_Subtitles(self, event):
        if self.ckbx_sb.IsChecked():
            opt["SUBTITLES"] = [True, "--write-auto-sub"]
        else:
            opt["SUBTITLES"] = [False, ""]
    # -----------------------------------------------------------------#

    def on_start(self):
        """
        Builds command string to use with an embed youtube_dl as
        python library or using standard youtube-dl command line
        with subprocess. This depends on some cases.
        """
        urls = self.parent.data_url
        logname = 'Youtube_LIB_downloader.log'

        def _getformatcode():
            """
            return format code list
            """
            format_code = []

            for url, key, val in zip(urls,
                                     self.format_dict.keys(),
                                     self.format_dict.values()):
                if key == url:
                    video, audio = '', ''
                    if len(val) == 1:
                        if val[0].startswith('Audio: '):
                            audio = val[0].split('Audio: ')[1]
                        elif val[0].startswith('Video: '):
                            video = val[0].split('Video: ')[1]
                        else:
                            video = val[0].split('Video: ')[1]
                    else:
                        index_1, index_2 = 0, 0
                        for i in val:
                            if i.startswith('Video: '):
                                index_1 += 1
                                if index_1 > 1:
                                    video += '/%s' % i.split('Video: ')[1]
                                else:
                                    video = i.split('Video: ')[1]

                            elif i.startswith('Audio: '):
                                index_2 += 1
                                if index_2 > 1:
                                    audio += '/%s' % i.split('Audio: ')[1]
                                else:
                                    audio = i.split('Audio: ')[1]
                            else:
                                index_1 += 1
                                if index_1 > 1:
                                    video += '/%s' % i.split('Video: ')[1]
                                else:
                                    video = i.split('Video: ')[1]

                    if video and audio:
                        format_code.append('%s+%s' % (video, audio))
                    elif video:
                        format_code.append('%s' % video)
                    elif audio:
                        format_code.append('%s' % audio)

            if len(format_code) != len(urls):
                return None
            return format_code

        if PYLIB_YDL is None:  # ----------- youtube-dl is used as library
            postprocessors = []
            if self.choice.GetSelection() == 2:
                postprocessors.append({'key': 'FFmpegExtractAudio',
                                       'preferredcodec': opt["A_FORMAT"][0],
                                       })
            if opt["METADATA"][0]:
                postprocessors.append({'key': 'FFmpegMetadata'})

            if opt["THUMB"][0]:
                postprocessors.append({'key': 'EmbedThumbnail',
                                       'already_have_thumbnail': False
                                       })
            if opt["SUBTITLES"][0]:
                postprocessors.append({'key': 'FFmpegEmbedSubtitle'})

            if self.choice.GetSelection() == 0:
                code = []
                data = {'format': opt["V_QUALITY"][0],
                        'noplaylist': opt["NO_PLAYLIST"][0],
                        'writethumbnail': opt["THUMB"][0],
                        'outtmpl': '%(title)s.%(ext)s',
                        'extractaudio': False,
                        'addmetadata': opt["METADATA"][0],
                        'writesubtitles': opt["SUBTITLES"][0],
                        'writeautomaticsub': opt["SUBTITLES"][0],
                        'allsubtitles': opt["SUBTITLES"][0],
                        'postprocessors': postprocessors
                        }
            if self.choice.GetSelection() == 1:  # audio files and video files
                code = []
                data = {'format': '%svideo,%saudio' % (opt["V_QUALITY"][0],
                                                       opt["A_QUALITY"][0]),
                        'noplaylist': opt["NO_PLAYLIST"][0],
                        'writethumbnail': opt["THUMB"][0],
                        'outtmpl': '%(title)s.f%(format_id)s.%(ext)s',
                        'extractaudio': False,
                        'addmetadata': opt["METADATA"][0],
                        'writesubtitles': opt["SUBTITLES"][0],
                        'writeautomaticsub': opt["SUBTITLES"][0],
                        'allsubtitles': opt["SUBTITLES"][0],
                        'postprocessors': postprocessors
                        }
            elif self.choice.GetSelection() == 2:  # audio only
                code = []
                data = {'format': 'best',
                        'noplaylist': opt["NO_PLAYLIST"][0],
                        'writethumbnail': opt["THUMB"][0],
                        'outtmpl': '%(title)s.%(ext)s',
                        'extractaudio': True,
                        'addmetadata': opt["METADATA"][0],
                        'writesubtitles': opt["SUBTITLES"][0],
                        'writeautomaticsub': opt["SUBTITLES"][0],
                        'allsubtitles': opt["SUBTITLES"][0],
                        'postprocessors': postprocessors
                        }
            if self.choice.GetSelection() == 3:  # format code
                code = _getformatcode()
                if not code:
                    self.parent.statusbar_msg(MSG_1, RED)
                    return
                data = {'format': '',
                        'noplaylist': opt["NO_PLAYLIST"][0],
                        'writethumbnail': opt["THUMB"][0],
                        'outtmpl': '%(title)s.f%(format_id)s.%(ext)s',
                        'extractaudio': False,
                        'addmetadata': opt["METADATA"][0],
                        'writesubtitles': opt["SUBTITLES"][0],
                        'writeautomaticsub': opt["SUBTITLES"][0],
                        'allsubtitles': opt["SUBTITLES"][0],
                        'postprocessors': postprocessors
                        }
            self.parent.switch_to_processing('youtube_dl python package',
                                             urls,
                                             '',
                                             self.parent.file_destin,
                                             data,
                                             None,
                                             code,
                                             '',
                                             'Youtube_LIB_downloader.log',
                                             len(urls),
                                             )
        else:  # ----------- with youtube-dl command line execution

            if self.choice.GetSelection() == 0:  # default
                code = []
                cmd = [(f'--format '
                        f'{opt["V_QUALITY"][1]} '
                        f'{opt["METADATA"][1]} '
                        f'{opt["SUBTITLES"][1]} '
                        f'{opt["THUMB"][1]} '
                        f'{opt["NO_PLAYLIST"][1]}'),
                       ('%(title)s.%(ext)s')
                       ]

            if self.choice.GetSelection() == 1:  # audio files + video files
                code = []
                cmd = [(f'--format '
                        f'{opt["V_QUALITY"][1]}video,'
                        f'{opt["A_QUALITY"][1]}audio '
                        f'{opt["METADATA"][1]} '
                        f'{opt["SUBTITLES"][1]} '
                        f'{opt["THUMB"][1]} '
                        f'{opt["NO_PLAYLIST"][1]}'),
                       ('%(title)s.f%(format_id)s.%(ext)s')
                       ]
            elif self.choice.GetSelection() == 2:  # audio only
                code = []
                cmd = [(f'{opt["A_FORMAT"][1]} '
                        f'{opt["METADATA"][1]} '
                        f'{opt["SUBTITLES"][1]} '
                        f'{opt["THUMB"][1]} '
                        f'{opt["NO_PLAYLIST"][1]}'),
                       ('%(title)s.%(ext)s')
                       ]
            if self.choice.GetSelection() == 3:  # format code
                code = _getformatcode()
                if not code:
                    self.parent.statusbar_msg(MSG_1, RED)
                    return
                cmd = [(f'{opt["METADATA"][1]} '
                        f'{opt["SUBTITLES"][1]} '
                        f'{opt["THUMB"][1]} '
                        f'{opt["NO_PLAYLIST"][1]}'),
                       ('%(title)s.f%(format_id)s.%(ext)s')
                       ]
            self.parent.switch_to_processing('youtube-dl executable',
                                             urls,
                                             '',
                                             self.parent.file_destin,
                                             cmd,
                                             None,
                                             code,
                                             '',
                                             'Youtube_EXEC_downloader.log',
                                             len(urls),
                                             )