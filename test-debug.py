#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##############################################################
#import os
#import wx

#PWD = os.getcwd() # work current directory (where is Videomsass?)
#DIRNAME = os.path.expanduser('~') # /home/user (current user directory)
    
#def readlog(logname):
    #"""
    #Make a parsing of the configuration file localized on 
    #``~/.videomass/videomass.conf`` and return object list 
    #of the current program settings.
    #"""
    
    #if os.path.exists(logname) and os.path.isfile(logname):

        #with open (logname, 'r') as f:
            #lines = f.read()
            #print(lines)

##logname = "/home/gianluca/.videomass/Videomass_PresetsManager.log"
 
##readlog(logname)

#class GeneralProcess(wx.Panel):

    #def __init__(self, parent,):

        #wx.Panel.__init__(self, parent=parent)

        #lbl = wx.StaticText(self, label=(u"Log View Console:"))
        #self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                        #style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
                                    #)
        #self.ckbx_text = wx.CheckBox(self, wx.ID_ANY,(u"Enable the FFmpeg "
                                            #u"scroll output in real time"))
        #self.barProg = wx.Gauge(self, wx.ID_ANY, range = 0)
        #self.labPerc = wx.StaticText(self, label="Percentage: 0%")
        #self.button_stop = wx.Button(self, wx.ID_STOP, (u"Abort"))
        #self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        #sizer = wx.BoxSizer(wx.VERTICAL)
        #grid = wx.GridSizer(1, 2, 5, 5)
        #sizer.Add(lbl, 0, wx.ALL, 5)
        #sizer.Add(self.OutText, 1, wx.EXPAND|wx.ALL, 5)
        #sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        #sizer.Add(self.labPerc, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5 )
        #sizer.Add(self.barProg, 0, wx.EXPAND|wx.ALL, 5 )
        #sizer.Add(grid, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        #grid.Add(self.button_stop, 0, wx.ALL, 5)
        #grid.Add(self.button_close, 1, wx.ALL, 5)

        ## set_properties:
        ##self.OutText.SetBackgroundColour((217, 255, 255))
        ##self.SetSizer(sizer)
        #self.SetSizerAndFit(sizer)
        
        #self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        
        #self.append()
        
    #def on_stop(self, event):
        
        #style = wx.Font(10, wx.SWISS, wx.ITALIC, wx.BOLD)
        #self.OutText.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.BOLD))
        #self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 164, 30)))
        ##self.OutText.SetFont(wx.TextAttr(style))
        #self.OutText.AppendText('\n  Done !\n\n')
        ##lunga = len(self.OutText.GetValue())
        #print(self.OutText.GetRange(lunga-11,lunga))
        #print(self.OutText.GetStringSelection())
        #print(self.OutText.GetSelection())
        
    #def append(self):
        #self.OutText.AppendText('\n  Messaggi dalla console\n\netct etc etc')
        
        
#class MainFrame(wx.Frame):

    #def __init__(self,):
        
        #wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        
        #self.OPanel = GeneralProcess(self,)
        
        #siz = wx.BoxSizer(wx.VERTICAL)
        #siz.Add(self.OPanel, 1, wx.EXPAND|wx.ALL, 0)
        #self.SetSizer(siz)
        #self.Layout()
        #self.Show()
        
#if __name__ == '__main__':
    #app = wx.App()
    #frame = MainFrame()
    #app.MainLoop()
##########################################################################
import subprocess

f = "/media/gianluca/DATI/PROVE_Conversioni/joemorello exercise 22.mov"

#args = ['ffmpeg', '-loglevel', 'error', '-stats','-cacca', 'bastone',]

args = ['ffmpeg', '-loglevel', 'error', '-stats','-i', f, '-af', 'volumedetect','-vn', '-sn', '-dn', '-f', 'null', '/dev/null',
]

p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                      bufsize=1, universal_newlines=True)
#print(p.stderr)

for line in p.stdout:
    print('>>>>>>>>>>>>>>>> OUT:')
    print(line)

for lineserr in p.stderr:
    print('>>>>>>>>>>>>>>>> ERRORI:')
    print(lineserr)


