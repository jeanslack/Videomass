**Videomass2** is a cross-platform GUI for FFmpeg, It provides a graphical 
interface for managing audio and video streams through FFmpeg.

* [Features](#features)
* [Official WebPage](http://jeanslack.github.io/Videomass2)
* [Downloads](https://github.com/jeanslack/Videomass2/releases)
* [Essential Dependencies](#essential-dependencies)
* [Run without installing](#run-without-installing)
* [Build Package](#build-package)
* [Make a debian packages](#make-a-debian-packages)
* [Make a Slackware package](#make-a-slackware-package)
* [MacOs](#macos)
* [Windows](#windows)
* [Donation](#donation)
* [License](#license)

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
- Work on many platforms where Python and wxPython are supported, 
  including **Linux**, **MacOs** and **Windows**. 

## Essential Dependencies

**Required:**
- Python >= 2.7 (no python >= 3)   
- wxPython >= 3.0

**Optionals:**
- ffmpeg >= 3.2
- ffprobe (for multimedia streams analysis) (can be built-in into ffmpeg)
- ffplay (media player for media preview) (can be built-in into ffmpeg)


## Run without installing

You can even launch the application without installing it, by running the
launcher script:

## Build Package

See the setup.py 

## MacOs

**As portable application (Run from sources code):**

You can run Videomass2 without install it, but make sure you have installed the following requests:

* WxPthon 3.0 (from homebrew)
* FFmpeg >= 3.2 (from hombrew)
* git

Then, clone the latest sources with git: `~$ git clone https://github.com/jeanslack/Videomass2`

or download Videomass2 sources at github site: <https://github.com/jeanslack/Videomass2>
and see [Use](#use)   

However, ffmpeg, ffprobe and ffplay must be installed in your system. 
Also, wxPython must be installed in your system.
You can install everything you need through homebrew: <https://brew.sh/>

If you want to get the ffmpeg, ffprobe and ffplay installers statically compiled and ready to install, you can download them at the following site:

<http://www.evermeet.cx/ffmpeg/>   
<http://www.evermeet.cx/ffprobe/>   
<http://www.evermeet.cx/ffplay/>

Note, however, that they may have limitations for reasons related to distribution (such as lack of AAC support)

**Build a OSX App**

If you have successfully performed the points described above, then you can try do the Videomass2 App for macOs.
For build the Videomass2.app there you need Xcode and command-line-tools available to the app store. 
Anyway, need following requirements:

* Xcode 
* Command-line-tools
* Python 2.7 from hombrew
* WxPython 3.0 from homebrew
* ffmpeg >= 3.2 (with ffprobe and ffplay also)
* Py2app installed with pip tools `sudo pip install py2app`

See the script setup.py for others information.

Open a terminal in the path where is setup.py and run the script with:   
    
    `~$ python setup.py py2app`   
    
If there are no errors, go to the dist folder and launch the application.   
If you want you can move the app to the * Applications * folder.   

If you get errors, probably  you need to create a virtual environment:   
    
<https://docs.python-guide.org/dev/virtualenvs/>   
<https://wiki.wxpython.org/wxPythonVirtualenvOnMac>   
And then buld the standalone application for MacOs, here's something useful to read:   
<https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>   
Note that on Videomass2 sources already exists a setup.py, then activate your virtual env and run setup.py:   
    
    `~$ python setup.py py2app` 

## Windows

**Notice!**:
Videomass2 do not include binaries/executables of the ffmpeg, ffprobe and ffplay.
If ffmpeg is not yet installed on your system please, download the compatible executable
of the FFmpeg for your Windows OS and set the pathname with Videomass2 setup dialog, otherwise
Videomass2 will not work.
You may be interested the following explanation:
<https://video.stackexchange.com/questions/20495/how-do-i-set-up-and-use-ffmpeg-in-windows>

**As portable application script (Run from sources code):**

- Download the latest release of the Python2.7 from 

<https://www.python.org/downloads/> and install it.

- Download the latest release of wxPython3.0 (.exe) toolkit for python 2.7 from:

<https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/> and install it.

- Download the Videomass2 sources from:

<https://github.com/jeanslack/Videomass2>

and see [Use](#use)   

**Make a .exe executable**

If you have successfully completed the points described above, now download and Install the **py2exe** utility for python 2.7 by:

<https://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/>

if need update it and follow this how-to:

<https://www.blog.pythonlibrary.org/2010/07/31/a-py2exe-tutorial-build-a-binary-series/>

Then open a dos window and position you in the Videomass2 folder you just unzipped and type:

`python setup.py py2exe`

A folder named 'dist' will be created where there will be the magic executable of Videomass2.exe

## Donation

If you like Videomass2 and you want to support its development, consider donating via:
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=UKYM7S5U542SJ)

## License

Copyright © 2013 - 2018 by Gianluca Pernigotto
Author and Developer: Gianluca Pernigotto   
Mail: <jeanlucperni@gmail.com>   
License: GPL3 (see LICENSE file in the docs folder)
