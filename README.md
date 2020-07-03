# **Videomass** is a cross-platform GUI for FFmpeg and youtube-dl.
[![Image](https://img.shields.io/static/v1?label=python&logo=python&message=3.7%20|%203.8&color=blue)](https://www.python.org/downloads/)
[![image](https://img.shields.io/badge/wxpython-phoenix-green)](https://www.wxpython.org/)
[![Image](https://img.shields.io/badge/license-GPLv3-orange)](https://github.com/jeanslack/Videomass/blob/master/COPYING)
![image](https://img.shields.io/badge/platform-linux%20|%20freebsd%20|%20macos%20|%20windows-brigthgreen)
[![Build Status](https://travis-ci.org/jeanslack/Videomass.svg?branch=master)](https://travis-ci.org/jeanslack/Videomass)   

Videomass is a GUI that allows more advanced use of [FFmpeg](https://www.ffmpeg.org/) 
than most other FFmpeg-based GUIs. It features graphic tools with high automation 
capabilities such as PEAK, RMS and EBU audio normalization filters with selectable 
audio stream indexing, streams analyzer and more.   

It allows you to create new presets or import/export existing ones, write and
edit new conversion profiles in order to use FFmpeg without limits of formats,
codecs and commands.   

In fact, most of the operations performed with FFmpeg via the command line, can 
be stored as conversion profiles on Videomass and can be performed or modified 
on the fly.   

Videomass also offers a graphical interface for the famous video downloader
[youtube_dl](http://ytdl-org.github.io/youtube-dl/) and allows you to choose 
between various download options like a specific format codes with the ability 
to playback individual URLs with different qualities via mpv player. Allows also 
to download all playlist, embed thumbnail in audio file (via atomicparsley), 
add metadata to file and write subtitles to video.   

Videomass is written in Python3 with the wxPython-Phoenix toolkit.   

**[Changelog](https://github.com/jeanslack/Videomass/blob/master/CHANGELOG)**   
**[Features](https://jeanslack.github.io/Videomass/features.html)**   
**[Screenshots](https://jeanslack.github.io/Videomass/screenshots.html)**   

# Installing and Dependencies

### Requirements
- **[Python ~=3.7](https://www.python.org/)**
- **[wxPython-Phoenix >= 4.0.3](https://wxpython.org/)**
- **[PyPubSub](https://pypi.org/project/PyPubSub/)**
- **[pip](https://pypi.org/project/pip/)**
- **[ffmpeg >=4.1.4](https://ffmpeg.org/)**
- **[ffprobe](https://ffmpeg.org/ffprobe.html)**
- **[ffplay](http://ffmpeg.org/ffplay.html)**
- **[youtube-dl](https://pypi.org/project/youtube_dl/)**

### Optionals
- **[mpv](https://mpv.io/)**
- **[atomicparsley](http://atomicparsley.sourceforge.net/)**

### Install basic dependencies for your OS

| **OS**           | **Basic Dependencies**                              |
|:-----------------|:----------------------------------------------------|
|Linux/FreeBSD     |*python3, wxpython-phoenix, pip for python3, ffmpeg* |
|MS Windows        |*python3, ffmpeg*                                    |
|MacOs             |*python3, pip for python3, ffmpeg*                   |

### Install Videomass using pip

`python3 -m pip install videomass`   

> This should also automatically install the remaining required dependencies 
such as wxPython (Mac-Os and Windows only), PyPubSub and youtube-dl.   
>
> On Linux and FreeBSD a launcher should be even created in the application 
launcher of your desktop environment.   
>
> To start Videomass on Mac-Os and MS-Windows open a console and just write 
`videomass` command.   

Visit [Installing and Dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-and-Dependencies) 
wiki page for more explanations.

# Start Videomass manually from source code

Videomass can be run without installing it, just download and unzip the 
[source code](https://github.com/jeanslack/Videomass/releases) archive and 
executing the "launcher" script inside the directory:   

`python3 launcher`   

> First, make sure you have installed at least all the above required 
dependencies.   

Visit [Installing and Dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-and-Dependencies) 
wiki page for more explanations.

Videomass can also be run in interactive mode with the Python interpreter, 
always within the same unpacked directory:   

`>>> from videomass3 import Videomass3`   
`>>> Videomass3.main()`   

# Resources

* [Executables for Windows, MacOsX and Linux](https://sourceforge.net/projects/videomass2/)
* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Videomass on PyPi](https://pypi.org/project/videomass/)
* [Development](https://github.com/jeanslack/Videomass)
* [Downloads Source Code](https://github.com/jeanslack/Videomass/releases)


