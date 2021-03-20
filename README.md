# **Videomass** is a cross-platform GUI for FFmpeg and youtube-dl.
[![Image](https://img.shields.io/static/v1?label=python&logo=python&message=3.7%20|%203.8&color=blue)](https://www.python.org/downloads/)
[![image](https://img.shields.io/badge/wxpython-phoenix-green)](https://www.wxpython.org/)
[![Image](https://img.shields.io/badge/license-GPLv3-orange)](https://github.com/jeanslack/Videomass/blob/master/LICENSE)
![image](https://img.shields.io/badge/platform-linux%20|%20freebsd%20|%20macos%20|%20windows-brigthgreen)
[![Build Status](https://travis-ci.org/jeanslack/Videomass.svg?branch=master)](https://travis-ci.org/jeanslack/Videomass)   

Videomass is a cross-platform GUI designed for [FFmpeg](https://www.ffmpeg.org/) 
enthusiasts who need to manage custom profiles to automate conversion/transcoding 
processes.   

It is based on an advanced use of presets and profiles in order to use most of 
the [FFmpeg](https://www.ffmpeg.org/) commands without limits of formats and 
codecs.   

It features graphical tools for viewing, analyzing and processing multimedia 
streams and downloading videos via [youtube-dl](https://youtube-dl.org/).   

Videomass is written in Python3 with the wxPython-Phoenix toolkit.   

**[Changelog](https://github.com/jeanslack/Videomass/blob/master/CHANGELOG)**   
**[Features](https://jeanslack.github.io/Videomass/features.html)**   
**[Screenshots](https://jeanslack.github.io/Videomass/screenshots.html)**   

# Installing and Dependencies

> ### For regular users (non-developers)   
> If you are not a programmer or if you are not familiar with the command line 
you can skip the whole part below and visit the 
[Download and installation](https://jeanslack.github.io/Videomass/download_installation.html) 
web page, which provides the information required to install Videomass on 
each operating system.

### Requirements
- **[Python >= 3.6.9](https://www.python.org/)**
- **[wxPython-Phoenix >= 4.0.3](https://wxpython.org/)**
- **[PyPubSub >= 4.0.3](https://pypi.org/project/PyPubSub/)**
- **[requests >= 2.21.0](https://pypi.org/project/requests/)**
- **[pip](https://pypi.org/project/pip/)**
- **[ffmpeg >=3.2](https://ffmpeg.org/)**
- **[ffprobe](https://ffmpeg.org/ffprobe.html)** (usually bundled with ffmpeg)
- **[ffplay](http://ffmpeg.org/ffplay.html)** (usually bundled with ffmpeg)
- **[youtube-dl](https://pypi.org/project/youtube_dl/)**

### Optionals
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
such as wxPython (only for Mac-Os and Windows), PyPubSub, youtube-dl and requests.   
>
> On Linux and FreeBSD a launcher should be even created in the application 
launcher of your desktop environment.   
>
> To start Videomass on Mac-Os and MS-Windows open a console and type 
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

```Python
>>> from videomass3 import Videomass3
>>> Videomass3.main()
```

# Resources

* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Videomass on PyPi](https://pypi.org/project/videomass/)
* [Development](https://github.com/jeanslack/Videomass)
* [Official download page](https://github.com/jeanslack/Videomass/releases)
* [Alternative download page](https://sourceforge.net/projects/videomass2/)
