# -*- coding: UTF-8 -*-
"""
Name: youtubedl_ui.py
Porpose: youtube-dl user interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.14.2022
Code checker: flake8 --ignore=F821,W503,
              pylint disable=E0602, E1101, C0415, E0401, C0103, W0613
########################################################

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import wx
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_io import io_tools
from videomass.vdms_utils.utils import format_bytes
from videomass.vdms_utils.utils import timehuman
from videomass.vdms_dialogs.ydl_mediainfo import YdlMediaInfo
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.playlist_indexing import Indexing


def join_opts(optvideo=None, optaudio=None, vformat=None, selection=None):
    """
    Return a convenient string for audio/video selectors

    - optvideo = string given by self.opt["V_QUALITY"]
    - optaudio = string given by self.opt["A_QUALITY"] on choice 2 only
    - vformat = Preferred video format (Default, webm, mp4)
    - selection = Current choice list selection (0, 1, 2, 3, 4)

    """
    if vformat == 'Default':  # Preferred video format
        if selection == 1:
            options = optvideo

        elif selection == 2:
            vqual = optvideo.split('+')[0]
            aqual, lqual = optvideo.split('+')[1].split('/')
            aqual = aqual if not optaudio else optaudio
            options = f'{vqual},{aqual}/{lqual}'

    else:
        vqual = optvideo.split('+')[0] + f'[ext={vformat}]'
        aqual, lqual = optvideo.split('+')[1].split('/')
        aqual = aqual if not optaudio else optaudio

        if selection == 1:
            aformat = 'm4a' if vformat == 'mp4' else 'webm'
            aqual = aqual + f'[ext={aformat}]'
            options = f'{vqual}+{aqual}/{lqual}'

        elif selection == 2:
            aqual = aqual + '[ext=m4a]'
            options = f'{vqual},{aqual}/{lqual}'

    return options


if not hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
    import wx.lib.mixins.listctrl as listmix

    class TestListCtrl(wx.ListCtrl,
                       listmix.CheckListCtrlMixin,
                       listmix.ListCtrlAutoWidthMixin
                       ):
        """
        This class is responsible for maintaining backward
        compatibility of wxPython which do not have a `ListCtrl`
        module with checkboxes feature:

        Examples of errors raised using a ListCtrl with checkboxes
        not yet implemented:

        AttributeError:
            - 'ListCtrl' object has no attribute 'EnableCheckBoxes'
            - module 'wx' has no attribute `EVT_LIST_ITEM_CHECKED`
            - module 'wx' has no attribute `EVT_LIST_ITEM_UNCHECKED`
        """
        def __init__(self,
                     parent,
                     ID,
                     pos=wx.DefaultPosition,
                     size=wx.DefaultSize,
                     style=0
                     ):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
            listmix.CheckListCtrlMixin.__init__(self)
            listmix.ListCtrlAutoWidthMixin.__init__(self)
            # self.setResizeColumn(3)

        def OnCheckItem(self, index, flag):
            """
            Send to parent (class Downloader) index and flag.
            index = int(num) of checked item.
            flag = boolean True or False of the checked or un-checked item
            """
            self.parent.on_checkbox(self)


class Downloader(wx.Panel):
    """
    This panel gives a graphic layout to some features of youtube-dl

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    icons = get.iconset
    BACKGRD = get.appset['icontheme'][1]['BACKGRD']
    GREEN = get.appset['icontheme'][1]['TXT3']
    RED = get.appset['icontheme'][1]['ERR1']
    YELLOW = '#bd9f00'
    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    VIOLET = '#D64E93'

    MSG_1 = _('At least one "Format Code" must be checked for each '
              'URL selected in green.')

    VQUAL = {('Best video resolution'): ('bestvideo+bestaudio/best'),
             ('p1080'): ('bestvideo[height<=?1080]+bestaudio/best'),
             ('p720'): ('bestvideo[height<=?720]+bestaudio/best'),
             ('p480'): ('bestvideo[height<=?480]+bestaudio/best'),
             ('p360'): ('bestvideo[height<=?360]+bestaudio/best'),
             ('p240'): ('bestvideo[height<=?240]+bestaudio/best'),
             ('p144'): ('worstvideo[height>=?144]+worstaudio/worst'),
             ('Worst video resolution'): ('worstvideo+worstaudio/worst'),
             }
    if appdata['downloader'] == 'yt_dlp':
        VPCOMP = {('Best precompiled video'): ('best'),
                  ('Medium precompiled video'): ('18'),
                  ('Worst precompiled video'): ('worst'),
                  }
    else:  # youtube-dl
        VPCOMP = {('Best precompiled video'): ('best'),
                  ('Worst precompiled video'): ('worst'),
                  }

    AFORMATS = {("Default audio format"): ("best"),
                ("wav"): ("wav"),
                ("mp3"): ("mp3"),
                ("aac"): ("aac"),
                ("m4a"): ("m4a"),
                ("vorbis"): ("vorbis"),
                ("opus"): ("opus"),
                ("flac"): ("flac"),
                }
    AQUAL = {('Best quality audio'): ('bestaudio'),
             ('Worst quality audio'): ('worstaudio')}

    CHOICE = [_('Precompiled Videos'),
              _('Download videos by resolution'),
              _('Download split audio and video'),
              _('Download Audio only'),
              _('Download by format code')
              ]
    # -----------------------------------------------------------------#

    def __init__(self, parent):
        """
        The first item of the self.info is a complete list of all
        informations getting by extract_info method from youtube_dl
        module.
        """
        self.parent = parent

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpplay = get_bmp(Downloader.icons['preview'], ((16, 16)))
            bmplistindx = get_bmp(Downloader.icons['listindx'], ((16, 16)))
        else:
            bmpplay = wx.Bitmap(Downloader.icons['preview'],
                                wx.BITMAP_TYPE_ANY)
            bmplistindx = wx.Bitmap(Downloader.icons['listindx'],
                                    wx.BITMAP_TYPE_ANY)

        self.opt = {("NO_PLAYLIST"): True,
                    ("THUMB"): False,
                    ("METADATA"): False,
                    ("V_QUALITY"): Downloader.VPCOMP['Best precompiled video'],
                    ("A_FORMAT"): "best",
                    ("A_QUALITY"): "bestaudio",
                    ("SUBTITLES"): False,
                    }
        self.plidx = {'': ''}
        self.info = []  # has data information for Show More button
        self.format_dict = {}  # format codes order with URL matching
        self.oldwx = None  # test result of hasattr EVT_LIST_ITEM_CHECKED

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_div = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_div, 1, wx.EXPAND)
        boxoptions = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, _('Options')), wx.VERTICAL)
        sizer_div.Add(boxoptions, 0, wx.ALL | wx.EXPAND, 5)
        boxlistctrl = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, ('')), wx.VERTICAL)
        sizer_div.Add(boxlistctrl, 1, wx.ALL | wx.EXPAND, 5)

        # ------------- choice and comboboxes
        self.choice = wx.Choice(self, wx.ID_ANY,
                                choices=Downloader.CHOICE,
                                size=(-1, -1),
                                )
        self.choice.SetSelection(0)
        boxoptions.Add(self.choice, 0, wx.ALL | wx.EXPAND, 5)
        boxoptions.Add((5, 5))
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        boxoptions.Add(line0, 0, wx.ALL | wx.EXPAND, 5)
        boxoptions.Add((5, 5))
        panelscroll = scrolled.ScrolledPanel(self, -1, size=(300, 1000),
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        # fgs1.Add((5, 5))
        self.cmbx_vq = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=(),
                                   size=(-1, -1), style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        # grid_v.Add((20, 20), 0,)
        fgs1.Add(self.cmbx_vq, 0, wx.ALL | wx.EXPAND, 5)
        tip = (_('When not available, the chosen video resolution will '
                 'be replaced with the closest one'))
        self.cmbx_vq.SetToolTip(tip)
        self.rdbvideoformat = wx.RadioBox(panelscroll, wx.ID_ANY,
                                          (_("Preferred video format")),
                                          choices=['Default', 'webm', 'mp4'],
                                          majorDimension=1,
                                          style=wx.RA_SPECIFY_COLS
                                          )
        fgs1.Add(self.rdbvideoformat, 0, wx.ALL | wx.EXPAND, 5)

        self.cmbx_aq = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=list(Downloader.AQUAL.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        self.cmbx_aq.Disable()
        # grid_v.Add((20, 20), 0,)
        fgs1.Add(self.cmbx_aq, 0, wx.ALL | wx.EXPAND, 5)
        self.cmbx_af = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=list(Downloader.AFORMATS.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        fgs1.Add(self.cmbx_af, 0, wx.ALL | wx.EXPAND, 5)
        # ------------- checkboxes
        line1 = wx.StaticLine(panelscroll, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add(line1, 0, wx.ALL | wx.EXPAND, 10)

        self.btn_play = wx.Button(panelscroll, wx.ID_ANY, _("Preview"))
        self.btn_play.SetBitmap(bmpplay, wx.LEFT)
        self.btn_play.Disable()
        fgs1.Add(self.btn_play, 0, wx.ALL | wx.EXPAND, 5)

        self.ckbx_pl = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Download all videos in playlist'))
                                   )
        fgs1.Add(self.ckbx_pl, 0, wx.ALL, 5)

        self.btn_plidx = wx.Button(panelscroll, wx.ID_ANY,
                                   (_('Playlist Editor'))
                                   )
        self.btn_plidx.SetBitmap(bmplistindx, wx.LEFT)
        fgs1.Add(self.btn_plidx, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_plidx.Disable()
        self.ckbx_ssl = wx.CheckBox(panelscroll, wx.ID_ANY,
                                    (_('Don’t check SSL certificate'))
                                    )
        fgs1.Add(self.ckbx_ssl, 0, wx.ALL, 5)
        self.ckbx_thumb = wx.CheckBox(panelscroll, wx.ID_ANY,
                                      (_('Embed thumbnail in audio file'))
                                      )
        fgs1.Add(self.ckbx_thumb, 0, wx.ALL, 5)
        self.ckbx_meta = wx.CheckBox(panelscroll, wx.ID_ANY,
                                     (_('Add metadata to file'))
                                     )
        fgs1.Add(self.ckbx_meta, 0, wx.ALL, 5)
        self.ckbx_sb = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Write subtitles to video'))
                                   )
        fgs1.Add(self.ckbx_sb, 0, wx.ALL, 5)
        sizer_subtitles = wx.BoxSizer(wx.HORIZONTAL)
        self.ckbx_all_sb = wx.CheckBox(panelscroll, wx.ID_ANY,
                                       (_('Download all available subtitles'))
                                       )
        self.ckbx_all_sb.Disable()
        sizer_subtitles.Add((20, 20), 0,)
        sizer_subtitles.Add(self.ckbx_all_sb)
        fgs1.Add(sizer_subtitles, 0, wx.ALL, 5)
        sizer_skipdl = wx.BoxSizer(wx.HORIZONTAL)
        self.ckbx_skip_dl = wx.CheckBox(panelscroll, wx.ID_ANY,
                                        (_('Download subtitles only'))
                                        )
        self.ckbx_skip_dl.Disable()
        sizer_skipdl.Add((20, 20), 0,)
        sizer_skipdl.Add(self.ckbx_skip_dl)
        fgs1.Add(sizer_skipdl, 0, wx.ALL, 5)
        self.ckbx_w = wx.CheckBox(panelscroll, wx.ID_ANY,
                                  (_('Prevent overwriting files'))
                                  )
        fgs1.Add(self.ckbx_w, 0, wx.ALL, 5)
        self.ckbx_id = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Include the video ID\n'
                                      'in the file names'))
                                   )
        fgs1.Add(self.ckbx_id, 0, wx.ALL, 5)

        self.ckbx_restrict_fn = wx.CheckBox(panelscroll, wx.ID_ANY,
                                            (_('Restrict file names'))
                                            )
        fgs1.Add(self.ckbx_restrict_fn, 0, wx.ALL, 5)

        boxoptions.Add(panelscroll, 0, wx.ALL | wx.CENTRE, 0)

        panelscroll.SetSizer(fgs1)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        # -------------listctrl
        if hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
            self.oldwx = False
            self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                     | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        else:
            self.oldwx = True
            t_id = wx.ID_ANY
            self.fcode = TestListCtrl(self, t_id, style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                      )
        boxlistctrl.Add(self.fcode, 1, wx.ALL | wx.EXPAND, 5)
        # -------------textctrl
        labtstr = _('Help viewer')
        self.labtxt = wx.StaticText(self, label=labtstr)
        sizer_base.Add(self.labtxt, 0, wx.LEFT, 5)
        self.cod_text = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE
                                    | wx.TE_READONLY
                                    | wx.TE_RICH2,
                                    size=(-1, 100)
                                    )
        sizer_base.Add(self.cod_text, 0, wx.ALL | wx.EXPAND, 5)
        # -----------------------
        self.cod_text.Hide()
        self.labtxt.Hide()
        self.SetSizer(sizer_base)
        self.Layout()
        # ----------------------- Properties
        # WARNING do not append text on self.cod_text here,
        # see `on_choicebox` method.

        self.cod_text.SetBackgroundColour(Downloader.BACKGRD)

        if Downloader.appdata['ostype'] != 'Darwin':
            self.labtxt.SetLabelMarkup(f"<b>{labtstr}</b>")
        #  tooltips
        self.btn_play.SetToolTip(_('Play selected url'))

        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_choicebox)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_vquality)
        self.rdbvideoformat.Bind(wx.EVT_RADIOBOX, self.on_vformat)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_aformat)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_aquality)
        self.Bind(wx.EVT_BUTTON, self.play_selected_url, self.btn_play)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_playlist)
        self.btn_plidx.Bind(wx.EVT_BUTTON, self.on_playlist_idx)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_metadata)
        self.ckbx_sb.Bind(wx.EVT_CHECKBOX, self.on_subtitles)
        self.fcode.Bind(wx.EVT_CONTEXT_MENU, self.on_context)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.fcode)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.fcode)
        if self.oldwx is False:
            self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_checkbox)
            self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_checkbox)
    # -----------------------------------------------------------------#

    def on_select(self, event):
        """
        self.fcod selection event that enables btn_play
        """
        self.btn_play.Enable()
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        self.fcod de-selection event that disables btn_play
        """
        self.btn_play.Disable()
    # ----------------------------------------------------------------------

    def on_checkbox(self, event):
        """
        get data from the enabled checkbox and set the values
        on corresponding key e.g.:

            `key=url: values=[Audio: code, Video: code]`
        """
        if not self.choice.GetSelection() == 4:
            return

        if not self.parent.sb.GetStatusText() == 'Ready':
            self.parent.statusbar_msg('Ready', None)

        viddisp, auddisp = 'video', 'audio only'

        if self.oldwx is False:
            check = self.fcode.IsItemChecked
        else:
            check = self.fcode.IsChecked

        num = self.fcode.GetItemCount()
        for url in self.parent.data_url:
            self.format_dict[url] = []
            for i in range(num):
                if check(i):
                    if (self.fcode.GetItemText(i, 1)) == url:
                        if viddisp in self.fcode.GetItemText(i, 4):
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dispv)
                        elif auddisp in self.fcode.GetItemText(i, 4):
                            dispa = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Audio: ' + dispa)
                        else:
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dispv)

        self.cod_text.Clear()

        for key, val in self.format_dict.items():
            if not val:
                self.cod_text.SetDefaultStyle(wx.TextAttr(Downloader.YELLOW))
                self.cod_text.AppendText(f'- {key} :\n')
            elif val[0].split(': ')[1] == 'UNSUPPORTED':
                self.cod_text.SetDefaultStyle(wx.TextAttr(Downloader.RED))
                self.cod_text.AppendText(f'- {key} :  '
                                         f'Unable to get format code\n')
            else:
                self.cod_text.SetDefaultStyle(wx.TextAttr(Downloader.GREEN))
                self.cod_text.AppendText(f'- {key} :  {val}\n')
        # print(self.format_dict)
    # ----------------------------------------------------------------------

    def on_context(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID2"):
            popupID2 = wx.ID_ANY
            self.Bind(wx.EVT_MENU, self.on_popup, id=popupID2)

        # build the menu
        menu = wx.Menu()
        menu.Append(popupID2, _("Play selected url"))
        # show the popup menu
        self.PopupMenu(menu)

        menu.Destroy()
    # ----------------------------------------------------------------------

    def on_popup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        if menuItem.GetItemLabel() == _("Play selected url"):
            self.play_selected_url(self)
    # ----------------------------------------------------------------------

    def play_selected_url(self, event):
        """
        Playback urls
        """
        tstamp = f'-vf "{self.parent.cmdtimestamp}"' if \
                 self.parent.checktimestamp else ''

        if self.fcode.GetSelectedItemCount() == 0:
            self.parent.statusbar_msg(_('An item must be selected in the '
                                        'URLs checklist'), Downloader.YELLOW,
                                      Downloader.BLACK)
            return

        self.parent.statusbar_msg(_('Ready'), None)
        item = self.fcode.GetFocusedItem()
        url = self.fcode.GetItemText(item, 1)
        for unsupp in ('/playlists',
                       '/channels',
                       '/playlist',
                       '/channel',
                       '/videos',
                       ):
            if unsupp in url:
                # prevent opening too many of ffplay windows
                wx.MessageBox(_("Only one video can be played at a time.\n\n"
                                "Unsupported '{0}':\n'{1}'"
                                ).format(unsupp.split('/')[1], url),
                              "Videomass", wx.ICON_INFORMATION, self)
                return

        if self.choice.GetSelection() == 0:  # play video only
            quality = self.fcode.GetItemText(item, 3)
        elif self.choice.GetSelection() == 1:  # play video only
            quality = self.fcode.GetItemText(item, 3).split('+')[0]
        elif self.choice.GetSelection() == 2:  # play audio only
            quality = self.fcode.GetItemText(item, 3).split(',')[1]
        elif self.choice.GetSelection() == 3:
            quality = 'bestaudio'
        elif self.choice.GetSelection() == 4:
            quality = self.fcode.GetItemText(item, 0)

        io_tools.url_play(url,
                          quality,
                          tstamp,
                          self.parent.autoexit,
                          self.ckbx_ssl.GetValue()
                          )
    # ----------------------------------------------------------------------

    def get_formatcode(self):
        """
        Get URLs data and format codes by generator object
        *youtubedl_getstatistics* (using youtube_dl library) and set the list
        control with new entries. Return `True` if `meta[1]` (error),
        otherwise return None as exit staus.
        """
        self.fcode.ClearAll()
        if self.oldwx is False:
            self.fcode.EnableCheckBoxes(enable=True)
        self.fcode.InsertColumn(0, (_('Format Code')), width=120)
        self.fcode.InsertColumn(1, (_('Url')), width=60)
        self.fcode.InsertColumn(2, (_('Title')), width=200)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution')), width=160)
        self.fcode.InsertColumn(5, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(6, (_('fps')), width=80)
        self.fcode.InsertColumn(7, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(8, (_('Size')), width=100)
        index = 0
        for link in self.parent.data_url:
            data = io_tools.youtubedl_getstatistics(link,
                                                    self.ckbx_ssl.GetValue()
                                                    )
            for meta in data:
                if meta[1]:
                    return meta[1]

            formats = iter(meta[0].get('formats', [meta[0]]))
            for n, f in enumerate(formats):
                if f.get('vcodec'):
                    vcodec, fps = f['vcodec'], f"{f.get('fps')}fps"
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

                formatid = f.get('format_id', 'UNSUPPORTED')
                self.fcode.InsertItem(index, formatid)
                self.fcode.SetItem(index, 1, link)
                self.fcode.SetItem(index, 2, meta[0].get('title', 'N/A'))
                self.fcode.SetItem(index, 3, f.get('ext', 'N/A'))
                self.fcode.SetItem(index, 4, f.get('format',
                                                   '-N/A').split('-')[1])
                self.fcode.SetItem(index, 5, vcodec)
                self.fcode.SetItem(index, 6, fps)
                self.fcode.SetItem(index, 7, acodec)
                self.fcode.SetItem(index, 8, size)
                if n == 0:
                    if formatid == 'UNSUPPORTED':
                        return _("ERROR: Unable to get format codes.\n\n"
                                 "Unsupported URL:\n'{0}'").format(link)

                    self.fcode.SetItemBackgroundColour(index, Downloader.GREEN)
                index += 1
        return None
    # ----------------------------------------------------------------------

    def get_statistics(self, link):
        """
        Get media URLs informations by generator object
        *youtubedl_getstatistics*:
        This method `Return` a two elements list ['ERROR', (message error)]
        if `meta[1]` (error), [None, dictobject] otherwise.
        Check the first item of list to recognize the exit status, which
        is 'ERROR' or None
        """

        data = io_tools.youtubedl_getstatistics(link, self.ckbx_ssl.GetValue())
        for meta in data:
            if meta[1]:
                return ('ERROR', meta[1])

            if 'entries' in meta[0]:
                try:
                    meta[0]['entries'][0]  # don't parse all playlist
                except IndexError:
                    pass

            if 'duration' in meta[0]:

                ftime = (f"{timehuman(meta[0]['duration'])} "
                         f"({meta[0]['duration']} sec.)")
            else:
                ftime = 'N/A'

            date = meta[0].get('upload_date')
            return (None, {'url': link,
                           'title': meta[0].get('title'),
                           'categories': meta[0].get('categories'),
                           'license': meta[0].get('license'),
                           'format': meta[0].get('format'),
                           'upload_date': date,
                           'uploader': meta[0].get('uploader'),
                           'view': meta[0].get('view_count'),
                           'like': meta[0].get('like_count'),
                           'dislike': meta[0].get('dislike_count'),
                           'avr_rat': meta[0].get('average_rating'),
                           'id': meta[0].get('id'),
                           'duration': ftime,
                           'description': meta[0].get('description'),
                           })
    # -----------------------------------------------------------------#

    def on_urls_list(self, quality=''):
        """
        Populate list control with new incoming as urls and
        related resolutions.

        """
        self.fcode.ClearAll()
        if self.oldwx is False:
            self.fcode.EnableCheckBoxes(enable=False)
        self.fcode.InsertColumn(0, ('#'), width=30)
        self.fcode.InsertColumn(1, (_('Url')), width=400)
        self.fcode.InsertColumn(2, (_('Title')), width=50)
        self.fcode.InsertColumn(3, (_('Quality')), width=250)

        if self.parent.data_url:
            index = 0
            for link in self.parent.data_url:
                self.fcode.InsertItem(index, str(index + 1))
                self.fcode.SetItem(index, 1, link)
                self.fcode.SetItem(index, 2, 'N/A')
                self.fcode.SetItem(index, 3, quality)
                index += 1
    # -----------------------------------------------------------------#

    def on_show_statistics(self):
        """
        show URL data information. This method is called by
        main frame when the 'Show More' button is pressed.

        """
        if not self.info:
            for link in self.parent.data_url:
                ret = self.get_statistics(link)
                if ret[0] == 'ERROR':
                    # self.parent.statusbar_msg('Ready', None)
                    wx.MessageBox(ret[1], 'Videomass', wx.ICON_ERROR)
                    del self.info[:]
                    return

                self.info.append(ret[1])

        miniframe = YdlMediaInfo(self.info, Downloader.appdata['ostype'])
        miniframe.Show()
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        Check data given by `self.get_formatcode()` method
        which allow to enabling download from "Format Code"

        """
        def _error(msg, infoicon):
            if infoicon == 'information':
                icon = wx.ICON_INFORMATION
            elif infoicon == 'error':
                icon = wx.ICON_ERROR

            wx.MessageBox(msg, "Videomass", icon, self)
            self.choice.SetSelection(0)
            self.on_choicebox(self, False)

        for url in self.parent.data_url:
            for unsupp in ('/playlists',
                           '/channels',
                           '/playlist',
                           '/channel',
                           '/videos',
                           ):
                if unsupp in url:
                    msg = _("Unable to get format codes on '{0}'\n\n"
                            "Unsupported '{0}':\n'{1}'"
                            ).format(unsupp.split('/')[1], url)
                    _error(msg, 'information')
                    return

        ret = self.get_formatcode()
        if ret:
            _error(ret, 'error')
            return

    # -----------------------------------------------------------------#

    def on_choicebox(self, event, statusmsg=True):
        """
        Set widgets on switching choice box

        """
        if statusmsg is True:
            if not self.parent.sb.GetStatusText() == 'Ready':
                self.parent.statusbar_msg(_('Ready'), None)

        self.cod_text.Clear()
        self.btn_play.Disable()

        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_vq.Enable()
            self.rdbvideoformat.Disable()
            self.cod_text.Hide()
            self.labtxt.Hide()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VPCOMP.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_urls_list()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 1:
            self.cmbx_af.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_vq.Enable()
            self.rdbvideoformat.Enable()
            self.cod_text.Hide()
            self.labtxt.Hide()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VQUAL.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_urls_list()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 2:
            self.cmbx_af.Disable()
            self.cmbx_aq.Enable()
            self.cmbx_vq.Enable()
            self.rdbvideoformat.Enable()
            self.cod_text.Hide()
            self.labtxt.Hide()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VQUAL.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_urls_list()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 3:
            self.cmbx_vq.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_af.Enable()
            self.rdbvideoformat.Disable()
            self.cod_text.Hide()
            self.labtxt.Hide()
            self.Layout()
            self.on_urls_list(f'bestaudio (format={self.cmbx_af.GetValue()})')

        elif self.choice.GetSelection() == 4:
            self.labtxt.Show()
            self.cod_text.Show()
            self.Layout()
            self.cmbx_vq.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_af.Disable()
            self.ckbx_thumb.Enable()
            self.rdbvideoformat.Disable()
            self.on_format_codes()
    # -----------------------------------------------------------------#

    def on_vquality(self, event):
        """
        Set video qualities during combobox event
        """
        if self.choice.GetSelection() == 0:
            self.opt["V_QUALITY"] = Downloader.VPCOMP[self.cmbx_vq.GetValue()]
        else:
            self.opt["V_QUALITY"] = Downloader.VQUAL[self.cmbx_vq.GetValue()]
        self.on_vformat(self)
    # -----------------------------------------------------------------#

    def on_vformat(self, event):
        """
        Set preferring video format during radiobox event
        """
        index = self.rdbvideoformat.GetSelection()
        vformat = self.rdbvideoformat.GetString(index)

        if self.choice.GetSelection() == 0:
            quality = self.opt["V_QUALITY"]

        elif self.choice.GetSelection() == 1:
            quality = join_opts(optvideo=self.opt["V_QUALITY"],
                                vformat=vformat,
                                selection=self.choice.GetSelection()
                                )
        elif self.choice.GetSelection() == 2:
            quality = join_opts(optvideo=self.opt["V_QUALITY"],
                                optaudio=self.opt["A_QUALITY"],
                                vformat=vformat,
                                selection=self.choice.GetSelection()
                                )
        index = 0
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 3, quality)
            index += 1
    # -----------------------------------------------------------------#

    def on_aformat(self, event):
        """
        Set audio format to exporting during combobox event
        and self.choice selection == 3
        """
        self.opt["A_FORMAT"] = Downloader.AFORMATS.get(self.cmbx_af.GetValue())
        index = 0
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 3,
                               f'bestaudio (format={self.cmbx_af.GetValue()})')
            index += 1
    # -----------------------------------------------------------------#

    def on_aquality(self, event):
        """
        Set audio qualities during combobox event
        and self.choice selection == 1
        """
        self.opt["A_QUALITY"] = Downloader.AQUAL.get(self.cmbx_aq.GetValue())
        self.on_vformat(self)
    # -----------------------------------------------------------------#

    def on_playlist(self, event):
        """
        Enable or disable playlists downloading
        """
        if self.ckbx_pl.IsChecked():
            playlist = [url for url in self.parent.data_url
                        if '/playlist' in url]
            if not playlist:
                wx.MessageBox(_("URLs have no playlist references"),
                              "Videomass", wx.ICON_INFORMATION, self)
                self.ckbx_pl.SetValue(False)
                return
            self.opt["NO_PLAYLIST"] = False
            self.btn_plidx.Enable()

        else:
            self.opt["NO_PLAYLIST"] = True
            self.btn_plidx.SetBackgroundColour(wx.NullColour)
            self.btn_plidx.Disable()
            self.plidx = {'': ''}
    # -----------------------------------------------------------------#

    def on_playlist_idx(self, event):
        """
        Dialog for setting playlist indexing
        """
        with Indexing(self,
                      self.parent.data_url,
                      self.plidx) as idxdialog:
            if idxdialog.ShowModal() == wx.ID_OK:
                data = idxdialog.getvalue()
                if not data:
                    self.btn_plidx.SetBackgroundColour(wx.NullColour)
                    self.plidx = {'': ''}
                else:
                    self.btn_plidx.SetBackgroundColour(
                        wx.Colour(Downloader.VIOLET))
                    self.plidx = data
    # -----------------------------------------------------------------#

    def on_thumbnails(self, event):
        """
        Enable or disable the tumbnails downloading
        """
        if self.ckbx_thumb.IsChecked():
            self.opt["THUMB"] = True
        else:
            self.opt["THUMB"] = False
    # -----------------------------------------------------------------#

    def on_metadata(self, event):
        """
        Enable or disable writing metadata
        """
        if self.ckbx_meta.IsChecked():
            self.opt["METADATA"] = True
        else:
            self.opt["METADATA"] = False
    # -----------------------------------------------------------------#

    def on_subtitles(self, event):
        """
        enable or disable writing subtitles
        """
        if self.ckbx_sb.IsChecked():
            self.opt["SUBTITLES"] = True
            self.ckbx_all_sb.Enable()
            self.ckbx_skip_dl.Enable()

        else:
            self.opt["SUBTITLES"] = False
            self.ckbx_all_sb.Disable()
            self.ckbx_skip_dl.Disable()
            self.ckbx_all_sb.SetValue(False)
            self.ckbx_skip_dl.SetValue(False)
    # -----------------------------------------------------------------#

    def getformatcode(self, urls):
        """
        Called by `on_Start` method. Return format code list

        """
        format_code = []

        for url, key, val in zip(urls,
                                 self.format_dict.keys(),
                                 self.format_dict.values()
                                 ):
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
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                        elif i.startswith('Audio: '):
                            index_2 += 1
                            if index_2 > 1:
                                audio += f"/{i.split('Audio: ')[1]}"
                            else:
                                audio = i.split('Audio: ')[1]
                        else:
                            index_1 += 1
                            if index_1 > 1:
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                if video and audio:
                    format_code.append(f'{video}+{audio}')
                elif video:
                    format_code.append(f'{video}')
                elif audio:
                    format_code.append(f'{audio}')

        if len(format_code) != len(urls):
            return None
        return format_code
    # -----------------------------------------------------------------#

    def on_start(self):
        """
        Builds command string to use with an embed youtube_dl as
        python library or using standard youtube-dl command line.
        """
        urls = self.parent.data_url

        if not self.ckbx_pl.IsChecked():
            if [url for url in urls if 'playlist' in url]:
                if wx.MessageBox(_('The URLs contain playlists. '
                                   'Are you sure you want to continue?'),
                                 _('Please confirm'),
                                 wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                    return
        if [url for url in urls if 'channel' in url]:
            if wx.MessageBox(_('The URLs contain channels. '
                               'Are you sure you want to continue?'),
                             _('Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        if self.ckbx_id.IsChecked():
            _id = '%(title).100s-%(id)s'
        else:
            _id = '%(title).100s'

        logname = f"{Downloader.appdata['downloader']}.log"
        postprocessors = []

        if self.choice.GetSelection() == 3:
            postprocessors.append({'key': 'FFmpegExtractAudio',
                                   'preferredcodec': self.opt["A_FORMAT"],
                                   })
        if self.opt["METADATA"]:
            postprocessors.append({'key': 'FFmpegMetadata'})

        if self.opt["THUMB"]:
            postprocessors.append({'key': 'EmbedThumbnail',
                                   'already_have_thumbnail': False
                                   })
        if self.opt["SUBTITLES"]:
            postprocessors.append({'key': 'FFmpegEmbedSubtitle'})

        sublang = ['all'] if self.ckbx_all_sb.IsChecked() else ''

        if self.choice.GetSelection() in (0, 1):  # precompiled or quality
            code = []
            data = {'format': self.fcode.GetItemText(0, 3),
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': self.ckbx_w.GetValue(),
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'subtitleslangs': sublang,
                    'skip_download': self.ckbx_skip_dl.GetValue(),
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': self.ckbx_restrict_fn.GetValue(),
                    'nocheckcertificate': self.ckbx_ssl.GetValue(),
                    }
        elif self.choice.GetSelection() == 2:  # audio and video splitted
            code = []
            data = {'format': self.fcode.GetItemText(0, 3),
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': self.ckbx_w.GetValue(),
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'subtitleslangs': sublang,
                    'skip_download': self.ckbx_skip_dl.GetValue(),
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': self.ckbx_restrict_fn.GetValue(),
                    'nocheckcertificate': self.ckbx_ssl.GetValue(),
                    }
        elif self.choice.GetSelection() == 3:  # audio only
            code = []
            data = {'format': 'bestaudio',
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': self.ckbx_w.GetValue(),
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.%(ext)s',
                    'extractaudio': True,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'subtitleslangs': sublang,
                    'skip_download': self.ckbx_skip_dl.GetValue(),
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': self.ckbx_restrict_fn.GetValue(),
                    'nocheckcertificate': self.ckbx_ssl.GetValue(),
                    }
        elif self.choice.GetSelection() == 4:  # format code
            code = self.getformatcode(urls)
            if not code:
                self.parent.statusbar_msg(Downloader.MSG_1,
                                          Downloader.RED,
                                          Downloader.WHITE
                                          )
                return
            data = {'format': '',
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': self.ckbx_w.GetValue(),
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'subtitleslangs': sublang,
                    'skip_download': self.ckbx_skip_dl.GetValue(),
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': self.ckbx_restrict_fn.GetValue(),
                    'nocheckcertificate': self.ckbx_ssl.GetValue(),
                    }
        self.parent.switch_to_processing('youtube_dl downloading',
                                         urls,
                                         '',
                                         self.parent.outpath_ydl,
                                         data,
                                         None,
                                         code,
                                         '',
                                         logname,
                                         len(urls),
                                         )
