# **Videomass** is a cross-platform GUI for FFmpeg and youtube-dl.
Videomass provides a graphical interface to create presets and write profiles 
in order to use [FFmpeg](https://www.ffmpeg.org/) without limits on formats and 
codecs with wide automation capabilities. Among the various tools it also 
includes a graphical interface for the famous video downloader 
[youtube_dl](http://ytdl-org.github.io/youtube-dl/).   

[![Image](https://img.shields.io/static/v1?label=python&logo=python&message=3.7%20|%203.8&color=blue)]()
[![image](https://img.shields.io/badge/wxpython-phoenix-green)]()
[![Image](https://img.shields.io/badge/license-GPLv3-orange)](https://github.com/jeanslack/Videomass/blob/master/COPYING)
![image](https://img.shields.io/badge/platform-linux%20|%20freebsd%20|%20macos%20|%20windows-lightgrey)
[![image](https://img.shields.io/badge/features-yes-brigthgreen)](https://jeanslack.github.io/Videomass/features.html)
[![image](https://img.shields.io/badge/screenshots-yes-brigthgreen)](https://jeanslack.github.io/Videomass/screenshots.html)

# Installing and Dependencies

### Requirements
- **[Python ~=3.7](https://www.python.org/)**
- **[wxPython-Phoenix >= 4.0](https://wxpython.org/)**
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

Visit [Installing and Dependencies](https://github.com/jeanslack/Videomass/wiki/Dependencies) 
wiki page for more explanations.

# Start Videomass manually from source code

Videomass can be run without installing it, just download and unzip the 
[source code](https://github.com/jeanslack/Videomass/releases) archive and 
executing the "launcher" script inside the directory:   

`python3 launcher`   

> First, make sure you have installed at least all the above required 
dependencies.   

Visit [Installing and Dependencies](https://github.com/jeanslack/Videomass/wiki/Dependencies) 
wiki page for more explanations.

Videomass can also be run in interactive mode with the Python interpreter, 
always within the same unpacked directory:   

`>>> from videomass3 import Videomass3`   
`>>> Videomass3.main()`   

# Resources
* [Videomass on PyPi](https://pypi.org/project/videomass/)
* [GitHub Page](https://github.com/jeanslack/Videomass)
* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Downloads Source Code](https://github.com/jeanslack/Videomass/releases)
* [Installers for Windows and MacOsX](https://sourceforge.net/projects/videomass2/)


