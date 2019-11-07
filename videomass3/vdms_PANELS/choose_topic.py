# -*- coding: UTF-8 -*-

#########################################################
# Name: audio_conv
# Porpose: choose topic
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: October.25.2019
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

import wx

class Choose_Topic(wx.Panel):
    """
    Helps to choose the appropriate contextual panel
    """
    def __init__(self, parent, OS, videoconv_icn, audioconv_icn, 
                 storepictures_icn, slideshow_icn, audioextract_icn, 
                 merging_icn, youtube_icn, audionorm_icn):

        self.parent = parent
        self.OS = OS

        wx.Panel.__init__(self, parent, -1)
        
        welcome = wx.StaticText(self, wx.ID_ANY, (
                             _("Welcome to Videomass")))
        vers = wx.StaticText(self, wx.ID_ANY, (
                             _("Choose a Topic")))
        welcome.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(welcome, 0, wx.TOP|
                                   wx.ALIGN_CENTER_VERTICAL|
                                   wx.ALIGN_CENTER_HORIZONTAL, 15)
        sizer_base.Add(vers, 0, wx.ALL|
                                wx.ALIGN_CENTER_VERTICAL|
                                wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_buttons = wx.FlexGridSizer(5, 4, 20, 20)
        grid_base = wx.GridSizer(1, 1, 0, 0)
        
        video_lab = _('Video Conversions')
        audio_lab = _('Audio Conversions')
        pict_lab = _('Pictures from Video')
        audgr_lab = _('Extract Audio from Video')
        slide_lab = _('Picture Slideshow Maker')
        audmer_lab = _('Merging Audio and Video')
        youtube_lab =  _('Download from Youtube')
        anorm_lab =  _('Audio Normalization')
        
        self.video = wx.Button(self, wx.ID_ANY, video_lab, size=(-1,-1))
        self.video.SetBitmap(wx.Bitmap(videoconv_icn), wx.TOP)
        self.audio = wx.Button(self, wx.ID_ANY, audio_lab, size=(-1,-1))
        self.audio.SetBitmap(wx.Bitmap(audioconv_icn),wx.TOP)
        self.save_pict = wx.Button(self, wx.ID_ANY, pict_lab, size=(-1,-1))
        self.save_pict.SetBitmap(wx.Bitmap(storepictures_icn),wx.TOP)
        self.audio_extract = wx.Button(self, wx.ID_ANY, audgr_lab, size=(-1,-1))
        self.audio_extract.SetBitmap(wx.Bitmap(audioextract_icn),wx.TOP)
        self.slideshow = wx.Button(self, wx.ID_ANY, slide_lab, size=(-1,-1))
        self.slideshow.SetBitmap(wx.Bitmap(slideshow_icn),wx.TOP)
        self.audio_merge = wx.Button(self, wx.ID_ANY, audmer_lab, size=(-1,-1))
        self.audio_merge.SetBitmap(wx.Bitmap(merging_icn),wx.TOP)
        self.youtube = wx.Button(self, wx.ID_ANY, youtube_lab, size=(-1,-1))
        self.youtube.SetBitmap(wx.Bitmap(youtube_icn),wx.TOP)
        self.anorm = wx.Button(self, wx.ID_ANY, anorm_lab, size=(-1,-1))
        self.anorm.SetBitmap(wx.Bitmap(audionorm_icn),wx.TOP)
        #self.exit = wx.Button(self, wx.ID_EXIT, '', size=(-1,-1))

        grid_buttons.AddMany([(self.video, 0, wx.EXPAND, 5),
                              (self.audio, 0, wx.EXPAND, 5),
                              (self.save_pict, 0, wx.EXPAND, 5),
                              (self.audio_extract, 0, wx.EXPAND, 5),
                              (self.audio_merge, 0, wx.EXPAND, 5),
                              (self.slideshow, 0, wx.EXPAND, 5),
                              (self.youtube, 0, wx.EXPAND, 5),
                              (self.anorm, 0, wx.EXPAND, 5),
                              ])
        grid_base.Add(grid_buttons, 0, wx.ALIGN_CENTER_VERTICAL|
                                       wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        sizer_base.Add(grid_base, 1, wx.EXPAND|
                                        wx.ALIGN_CENTER_VERTICAL|
                                        wx.ALIGN_CENTER_HORIZONTAL, 5)
        #sizer_base.Add(self.exit, 0, wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, 0)
        
        self.SetSizerAndFit(sizer_base)
        
        self.Bind(wx.EVT_BUTTON, self.on_Video, self.video)
        self.Bind(wx.EVT_BUTTON, self.on_Audio, self.audio)
        self.Bind(wx.EVT_BUTTON, self.on_Pictures, self.save_pict)
        self.Bind(wx.EVT_BUTTON, self.on_AudioFromVideo, self.audio_extract)
        self.Bind(wx.EVT_BUTTON, self.on_AudioMerging, self.audio_merge)
        self.Bind(wx.EVT_BUTTON, self.on_Slideshow, self.slideshow)
        self.Bind(wx.EVT_BUTTON, self.on_YoutubeDL, self.youtube)
        #self.Bind(wx.EVT_BUTTON, self.onExit, self.exit)
        
        
    def on_Video(self, event):
        self.parent.File_import(self, 'Video Conversions')
        
    def on_Audio(self, event):
        self.parent.File_import(self, 'Audio Conversions')
    
    def on_Pictures(self, event):
        print('pictures from video')
        
    def on_AudioFromVideo(self, event):
        print('audio from video')
    
    def on_AudioMerging(self, event):
        print('audio merging')
    
    def on_Slideshow(self, event):
        self.parent.File_import(self,'Pictures Slideshow Maker')
    
    def on_YoutubeDL(self, event):
        self.parent.Text_import(self, 'Youtube Downloader')
        #print('python3 youtube-dl --abort-on-error --ignore-config --restrict-filenames --no-overwrites --prefer-free-formats --extract-audio')
        """
        Post-processing Options:
       -x, --extract-audio
              Convert  video  files to audio-only files (requires ffmpeg or avconv and ffprobe or
              avprobe)

       --audio-format FORMAT
              Specify audio format: "best", "aac", "flac", "mp3",  "m4a",  "opus",  "vorbis",  or
              "wav"; "best" by default; No effect without -x

       --audio-quality QUALITY
              Specify  ffmpeg/avconv  audio  quality,  insert  a  value  between 0 (better) and 9
              (worse) for VBR or a specific bitrate like 128K (default 5)

       --recode-video FORMAT
              Encode  the  video  to  another   format   if   necessary   (currently   supported:
              mp4|flv|ogg|webm|mkv|avi)
        
        --postprocessor-args ARGS
              Give these arguments to the postprocessor

       -k, --keep-video
              Keep  the video file on disk after the post- processing; the video is erased by de‐
              fault

       --no-post-overwrites
              Do not overwrite post-processed files; the post-processed files are overwritten  by
              default

       --embed-subs
              Embed subtitles in the video (only for mp4, webm and mkv videos)

       --embed-thumbnail
              Embed thumbnail in the audio as cover art

       --add-metadata
              Write metadata to the video file
        
        --metadata-from-title FORMAT
              Parse  additional metadata like song title / artist from the video title.  The for‐
              mat syntax is the same as --output.  Regular expression with named  capture  groups
              may also be used.  The parsed parameters replace existing values.  Example: --meta‐
              data-from- title "%(artist)s - %(title)s" matches a title  like  "Coldplay  -  Par‐
              adise".  Example (regex): --metadata-from-title "(?P.+?) - (?P
              .+)"

       --xattrs
              Write metadata to the video file's xattrs (using dublin core and xdg standards)

       --fixup POLICY
              Automatically  correct  known  faults of the file.  One of never (do nothing), warn
              (only emit a warning), detect_or_warn (the default; fix file if we can, warn other‐
              wise)

       --prefer-avconv
              Prefer avconv over ffmpeg for running the postprocessors

       --prefer-ffmpeg
              Prefer ffmpeg over avconv for running the postprocessors (default)
        
        --ffmpeg-location PATH
              Location of the ffmpeg/avconv binary; either the path to the binary or its contain‐
              ing directory.

       --exec CMD
              Execute a command on the file after downloading, similar to  find's  -exec  syntax.
              Example: --exec 'adb push {} /sdcard/Music/ && rm {}'

       --convert-subs FORMAT
              Convert the subtitles to other format (currently supported: srt|ass|vtt|lrc)



        """

        #self.parent.File_import(self,'Download from Youtube')
        
    
    def onExit(self, event):
        self.parent.on_close(self)
        
        

        
