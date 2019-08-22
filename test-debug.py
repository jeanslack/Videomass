#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##############################################################
import os
import wx
import subprocess



PWD = os.getcwd() # work current directory (where is Videomsass?)
DIRNAME = os.path.expanduser('~') # /home/user (current user directory)
    
def readlog(logname):
    """
    Make a parsing of the configuration file localized on 
    ``~/.videomass/videomass.conf`` and return object list 
    of the current program settings.
    """
    
    if os.path.exists(logname) and os.path.isfile(logname):

        with open (logname, 'r') as f:
            lines = f.read()
            print(lines)

#logname = "/home/gianluca/.videomass/Videomass_PresetsManager.log"
 
#readlog(logname)

class GeneralProcess(wx.Panel):

    def __init__(self, parent,):

        wx.Panel.__init__(self, parent=parent)

        lbl = wx.StaticText(self, label=(u"Log View Console:"))
        self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
                                    )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY,(u"Enable the FFmpeg "
                                            u"scroll output in real time"))
        self.barProg = wx.Gauge(self, wx.ID_ANY, range = 0)
        self.labPerc = wx.StaticText(self, label="Percentage: 0%")
        self.button_stop = wx.Button(self, wx.ID_STOP, (u"Abort"))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(1, 2, 5, 5)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.OutText, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        sizer.Add(self.labPerc, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5 )
        sizer.Add(self.barProg, 0, wx.EXPAND|wx.ALL, 5 )
        sizer.Add(grid, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        grid.Add(self.button_stop, 0, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)

        # set_properties:
        #self.OutText.SetBackgroundColour((217, 255, 255))
        #self.SetSizer(sizer)
        self.SetSizerAndFit(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
    #---------------------------------------------------------#
    def on_stop(self, event):
        
        ffmpeg_link = 'ffmpeg'
        type_opt = '-filters'
        #search = None
        search = 'si'
        
        try: # grab buildconf:
            #--------------- 1)
            p = subprocess.run([ffmpeg_link, 
                                '-loglevel', 
                                'error', 
                                '%s' % type_opt],
                                capture_output=True,)
            
        except FileNotFoundError as e:
            print('si')
            self.OutText.AppendText('Not found\n %s' % e)
            return
        
        #row = (p.stdout.split(b'\n'))
        row = "%s" % p.stdout.decode()
        #print(row)
        
        if search: # if vuoi una ricerca specifica (è come grep)
            find = []
            for a in row.split('\n'): 
                if 'filters' in a:
                    find.append(a)
            if not find:
                self.OutText.AppendText('\n  Not found....')
            else:
                for x in find:
                    self.OutText.AppendText('\n  %s' % x)
        else:
            
            self.OutText.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.OutText.AppendText(row)
    
        

        
    #--------------------------------------------------------------#
        
        
class MainFrame(wx.Frame):

    def __init__(self,):
        
        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        
        self.OPanel = GeneralProcess(self,)
        
        siz = wx.BoxSizer(wx.VERTICAL)
        siz.Add(self.OPanel, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSize((900, 530))
        self.SetSizer(siz)
        self.Layout()
        self.Show()
        
if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
##########################################################################


