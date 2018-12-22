
# **Videomass2** is a cross-platform GUI for FFmpeg   
It provides a graphical interface for audio and video conversions through FFmpeg.


* [Main project page](https://github.com/jeanslack/Videomass2)
* [Support Page and documentation](http://jeanslack.github.io/Videomass2)
* [Downloads source code](https://github.com/jeanslack/Videomass2/releases)
* [Installers for Windows/MacOsX/Linux](https://sourceforge.net/projects/videomass2/)

## Features

- Drag n' Drop interface
- Presets manager interface with fully customizable and expandable profiles  
- Displaying metadata streams information 
- Preview of exported media
- Preview video filters
- Reproduction of imported media
- Video conversions interface 
- Audio conversions interface
- Save jpg images from a video sequence
- Audio peak level analysis with normalization process   
- Grabbing audio streams from video with multilingual selection  
- Selection of the time interval (for exports, previews, reproduction, tests)
- Convert multiple files at once 
- Log management
- Italian and English Languages support
- Work on many platforms where Python and wxPython are supported, 
  including **Linux**, **MacOs** and **Windows**. 

## Essential Dependencies

**Required:**
- Python >= 2.7 (no python >= 3)   
- wxPython >= 3.0 (wxPython classic)

**Optionals:**
- ffmpeg >= 3.2
- ffprobe (for multimedia streams analysis) (can be built-in into ffmpeg)
- ffplay (media player for media preview) (can be built-in into ffmpeg)

## Installation via pip

On Windows:   
    pip install --no-deps videomass2

On MacOsX, Linux, Unix (for single user):   
    pip install --user videomass2

On MacOsX, Linux, Unix (for all users, need root privileges to install):   
    pip install videomass2
