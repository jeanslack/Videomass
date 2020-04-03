# -*- coding: UTF-8 -*-

from ffprobe_parser import FFProbe

filename_url = '/home/gianluca/out_EBU.avi'
ffprobe_url = '/usr/bin/ffprobe'

data = FFProbe(ffprobe_url, 
               filename_url, 
               parse=True, 
               pretty=True, 
               select=None, 
               entries=None,
               show_format=True, 
               show_streams=True, 
               writer='default'
               )

if data.ERROR():
    print ("Some Error:  %s" % (data.error))
    #return
#else:
    #print (data.video_stream())
    #print (data.audio_stream())
    #print (data.subtitle_stream())
    #print (data.data_format())
    #print(data.custom_output())

#print(data)
    
    
