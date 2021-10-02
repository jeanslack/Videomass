# -*- coding: UTF-8 -*-
"""
Name: playlist_indexing.py
Porpose: shows a dialog box for setting playlist indexing
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.28.2021
Code checker: pycodestyle / flake8 --ignore=F821,W503
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
import wx
import wx.lib.mixins.listctrl as listmix


class ListCtrl(wx.ListCtrl,
               listmix.ListCtrlAutoWidthMixin,
               listmix.TextEditMixin):
    """
    A listctrl with the ability to be editable.
    """

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.populate()
        listmix.TextEditMixin.__init__(self)

    def populate(self):
        """populate with default colums"""
        self.InsertColumn(0, '#', width=30)
        self.InsertColumn(1, _('URL'), width=400)
        self.InsertColumn(2, _('Playlist Items'), width=200)


class Indexing(wx.Dialog):
    """
    Shows a dialog box for setting playlist indexing.

    """
    get = wx.GetApp()  # get data from bootstrap
    OS = get.appset['ostype']
    appdata = get.appset

    HELPME = _('Click on "Playlist Items" column to specify indices of '
               'the videos in the playlist separated by commas like: '
               '"1,2,5,8" if you want to download videos indexed 1, 2, '
               '5, 8 in the playlist.\n\n'
               'You can specify range: "1-3,7,10-13" it will download the '
               'videos at index 1, 2, 3, 7, 10, 11, 12 and 13.\n'
               )

    def __init__(self, parent, url, data):
        """
        NOTE Use 'parent, -1' param. to make parent, use 'None' otherwise

        """
        self.clrs = Indexing.appdata['icontheme'][1]
        self.urls = url
        self.data = data

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ------ Add widget controls
        self.lctrl = ListCtrl(self,
                              wx.ID_ANY,
                              style=wx.LC_REPORT
                              | wx.SUNKEN_BORDER
                              | wx.LC_SINGLE_SEL
                              | wx.LC_HRULES
                              | wx.LC_VRULES
                              )
        self.tctrl = wx.TextCtrl(self,
                                 wx.ID_ANY, "",
                                 style=wx.TE_MULTILINE
                                 | wx.TE_READONLY
                                 | wx.TE_RICH2
                                 )

        # ------ Properties
        self.SetTitle(_('Playlist video items to download'))
        self.SetMinSize((800, 400))
        self.lctrl.SetMinSize((800, 200))
        self.tctrl.SetMinSize((800, 200))

        # ------ set Layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.lctrl, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_1 = wx.GridSizer(1, 1, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.tctrl, 0, wx.ALL | wx.EXPAND, 5)

        # ------ bottom layout for buttons
        grid_btn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))
        grid_btn.Add(btn_reset, 0, wx.ALL, 5)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(self.btn_ok, 0, wx.ALL, 5)
        grid_btn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        # ------ final settings:
        sizer_1.Add(grid_btn, 0, wx.EXPAND)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        index = 0

        for link in url:
            self.lctrl.InsertItem(index, str(index + 1))
            self.lctrl.SetItem(index, 1, link)
            if '/playlist?list' in link:
                self.lctrl.SetItemBackgroundColour(index, self.clrs['TXT3'])

            if not self.data == {'': ''}:
                for key, val in self.data.items():
                    if key == link:
                        self.lctrl.SetItem(index, 2, val)
            index += 1

        if Indexing.OS == 'Darwin':
            self.lctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            self.tctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.lctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            self.tctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.tctrl.SetBackgroundColour(self.clrs['BACKGRD'])

        # ----------------------Binding (EVT)----------------------#
        self.lctrl.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.on_edit_begin)
        self.lctrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_edit_end)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        self.textstyle()

    def textstyle(self):
        """
        clear log messages and set text style on textctrl box
        """

        self.tctrl.Clear()
        self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['TXT1']))
        self.tctrl.AppendText(f'{Indexing.HELPME}')
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        """
        diz = {}
        for row, url in enumerate(self.urls):
            if self.lctrl.GetItem(row, 2).GetText():
                diz[url] = self.lctrl.GetItem(row, 2).GetText()
        return diz

    # ----------------------Event handler (callback)----------------------#

    def on_edit_end(self, event):
        """
        Checking the strings entered
        """
        wxd = wx.DateTime.Now()
        date = wxd.Format('%H:%M:%S')
        msg = dict(errdigit=_('ERROR: Enter only digits, commas and hyphens. '
                              'If you have multiple items, use commas to '
                              'separate them. Use the hyphen for the range. '
                              'Spaces are not allowed.'),
                   errdigit2=_('ERROR: You have to start and end with '
                               'a digit.'),
                   errhyph=_('ERROR: Make sure the hyphen is between '
                             'two digits.'),
                   errhyph3=_('ERROR: A range must include only two digits '
                              'and a hyphen, for example "20-25" .'),
                   errcomma=_('ERROR: Make sure you use commas only to '
                              'separate indices and / or ranges, for example '
                              '"1,3,5,10-15"'),
                   errgen=_('ERROR: The entered string contains redundant '
                            'characters.'),
                   )
        # row_id = event.GetIndex()  # Get the current row
        # col_id = event.GetColumn()  # Get the current column
        new_data = event.GetLabel()  # Get the changed data
        # cols = self.lctrl.GetColumnCount()  # Get the total number of col
        # rows = self.lctrl.GetItemCount()  # Get the total number of rows

        if not new_data == '':
            last = len(new_data) - 1
            csplit = new_data.split(',')  # split by commas
            hsplit = new_data.split('-')  # split by hyphens
            allow = ['-', ',', '0', '1', '2', '3',
                     '4', '5', '6', '7', '8', '9']

            keywords = {'char': ([char for char in new_data
                                  if char not in allow],
                                 f'\n{date}: {msg["errdigit"]}'),
                        'startsdigit': (not new_data[0].isdigit(),
                                        f'\n{date}: {msg["errdigit2"]}'),
                        'endsdigit': (not new_data[last].isdigit(),
                                      f'\n{date}: {msg["errdigit2"]}'),
                        'starshyph': ([hyph for hyph in csplit if
                                       hyph.startswith('-')],
                                      f'\n{date}: {msg["errhyph"]}'),
                        'endshyph': ([hyph for hyph in csplit if
                                      hyph.endswith('-')],
                                     f'\n{date}: {msg["errhyph"]}'),
                        'startscomma': ([comma for comma in hsplit if
                                         comma.startswith(',')],
                                        f'\n{date}: {msg["errcomma"]}'),
                        'redund1': ('' in csplit,
                                    f'\n{date}: {msg["errgen"]}'),
                        'redund2': ('' in hsplit,
                                    f'\n{date}: {msg["errgen"]}'),
                        'errrange': ([rng.split('-') for rng in csplit if
                                      '-' in rng if len(rng.split('-')) > 2],
                                     f'\n{date}: {msg["errhyph3"]}')}

            for val in keywords.items():
                if val[1][0]:
                    self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['ERR1']))
                    self.tctrl.AppendText(val[1][1])
                    event.Veto()
                    return

            self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['TXT3']))
            self.tctrl.AppendText(f'\n{date}: Assigned: {new_data} ')
    # ------------------------------------------------------------------#

    def on_edit_begin(self, event):
        """
        Columns 0 and 1 must not be editable for link without playlist.
        """
        row_id = event.GetIndex()

        wxd = wx.DateTime.Now()
        date = wxd.Format('%H:%M:%S')
        invalidmsg = _('WARNING: The selected URL does not refer to a '
                       'playlist. Only lines marked green can be indexed.')

        colour = self.clrs['TXT3']

        if event.GetColumn() in (0, 1):
            event.Veto()
        elif event.GetColumn() == 2:
            # It looks like the HTML color codes are translated to RGB here
            if self.lctrl.GetItemBackgroundColour(row_id) != colour:
                self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['WARN']))
                self.tctrl.AppendText(f'\n{date}: {invalidmsg}')
                event.Veto()
            else:
                event.Skip()  # or event.Allow()
        else:
            event.Skip()  # or event.Allow()
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all items on editable columns and clear log messages
        """
        rows = self.lctrl.GetItemCount()  # Get the total number of rows
        for row in range(rows):
            self.lctrl.SetItem(row, 2, '')

        self.textstyle()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close the dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if
        not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window (for exemple).
        """
        self.getvalue()
        # self.Destroy()
        event.Skip()
