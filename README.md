# **Videomass** is a cross-platform GUI for FFmpeg and yt-dlp.
[![Image](https://img.shields.io/static/v1?label=python&logo=python&message=3.7%20|%203.8%20|%203.9%20|%203.10|%203.11&color=blue)](https://www.python.org/downloads/)
[![Image](https://img.shields.io/badge/license-GPLv3-orange)](https://github.com/jeanslack/Videomass/blob/master/LICENSE)
[![Python application](https://github.com/jeanslack/Videomass/actions/workflows/tests.yml/badge.svg)](https://github.com/jeanslack/Videomass/actions/workflows/tests.yml)

Videomass is a powerful, multitasking and cross-platform graphical user interface 
(GUI) for [FFmpeg](https://www.ffmpeg.org/) and [yt-dlp](https://github.com/yt-dlp/yt-dlp). 
It offers a wide range of features and functions, making it a comprehensive software solution. 

Videomass is [Free (libre) Software](https://en.wikipedia.org/wiki/Free_software), 
created and maintained by [Gianluca (jeanslack) Pernigotto](https://github.com/jeanslack); 
it was written in [Python3](https://www.python.org/) using the 
[wxPython4](https://www.wxpython.org/) toolkit; it is cross-platform and works on 
Linux, MacOs, Windows and FreeBSD.    

The Videomass logo and artwork were created by [Gianluca (jeanslack) Pernigotto](https://github.com/jeanslack)  

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
- **[Python >= 3.7.0](https://www.python.org/)**
- **[wxPython-Phoenix >= 4.0.7](https://wxpython.org/)**
- **[PyPubSub >= 4.0.3](https://pypi.org/project/PyPubSub/)**
- **[requests >= 2.21.0](https://pypi.org/project/requests/)**
- **[ffmpeg >=5.1](https://ffmpeg.org/)**
- **[ffprobe >=5.1](https://ffmpeg.org/ffprobe.html)** (usually bundled with ffmpeg)
- **[ffplay >=5.1](http://ffmpeg.org/ffplay.html)** (usually bundled with ffmpeg)

### Optionals
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**
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
such as wxPython (only for Mac-Os and Windows), PyPubSub, yt-dlp and requests.   
>
> On Linux and FreeBSD a launcher should be even created in the application 
launcher of your desktop environment.   
>
> To start Videomass on Mac-Os and MS-Windows open a console and type 
`videomass` command.   

Visit [Installing dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-dependencies) 
wiki page for more explanations.

# Start Videomass manually from source code

Videomass can be run without installing it, just download and unzip the 
[source code](https://github.com/jeanslack/Videomass/releases) archive and 
executing the "launcher" script inside the directory:   

`python3 launcher`   

> First, make sure you have installed at least all the above required 
dependencies.   

Visit [Installing dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-dependencies) 
wiki page for more explanations.

Videomass can also be run in interactive mode with the Python interpreter, 
always within the same unpacked directory:   

```Python
>>> from videomass import gui_app
>>> gui_app.main()
```

# Resources

* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Videomass on PyPi](https://pypi.org/project/videomass/)
* [Development](https://github.com/jeanslack/Videomass)
* [Official download page](https://github.com/jeanslack/Videomass/releases)
