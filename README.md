<div align="center">
<h1>
<img width="64" height="64" src="https://github.com/jeanslack/Videomass/blob/master/art/data/images/com.github.jeanslack.videomass.png" alt="Icon">  Videomass</h1>
<h3 align="center">A open-source and cross-platform GUI for FFmpeg.</h3>
</div>

<p align="center">
<img src="https://github.com/jeanslack/Videomass/blob/master/art/data/images/screenshot.png" alt="Screenshot">
</p>

<div class="center">
<h1 align="center"> Overview </h1>
</div>

**Videomass** is a cross-platform GUI for FFmpeg, It provides a graphical 
interface for managing audio and video streams through FFmpeg.

* [Important Note!](#important-note)
* [Features](#features)
* [Official WebPage](http://jeanslack.github.io/Videomass)
* [Downloads](https://github.com/jeanslack/Videomass/releases)
* [System Requirements](#system-requirements)
* [Essential Dependencies](#essential-dependencies)
* [Use](#use)
* [Build Package](#build-package)
* [Make a debian packages](#make-a-debian-packages)
* [Make a Slackware package](#make-a-slackware-package)
* [MacOs](#MacOs)
* [Windows](#windows)
* [License](#license)

## Important Note!

Videomass do not include binaries/executables of the FFmpeg.
If FFmpeg is not yet installed on your system please, install it. Videomass will not work without the essential FFmpeg

## Features

Videomass presents itself with an interface completely renewed and enhanced by many features

- Drag n Drop interface 
- Presets manager interface with fully customizable profiles ready to use
- Data streams information interface with details section
- Preview of exported media
- Video conversion interface 
- Audio conversion interface
- Audio peak level analysis implementation and audio normalization
- Grabbing audio streams from video with multilingual selection
- Batch processors
- Log management
- ..and more

## System Requirements

* Gnu/Linux
* OSX 10.13 or later
* Windows 7 or later

## Essential Dependencies

**Required:**
- Python >= 2.7 (no python >= 3)   
- wxPython >= 3.0

**Extra required:**
- ffmpeg >= 3.2
- ffprobe (for multimedia streams analysis) (can be built-in into ffmpeg)
- ffplay (media player for media preview) (can be built-in into ffmpeg)

**Optionals:**
- libx264 (has to be explicitly enabled when compiling ffmpeg)
- libmp3lame (has to be explicitly enabled when compiling ffmpeg)
- libfdk-aac (has to be explicitly enabled when compiling ffmpeg)
- libfdk-aac (has to be explicitly enabled when compiling ffmpeg)
- xvidcore (has to be explicitly enabled when compiling ffmpeg)
- libvpx (has to be explicitly enabled when compiling ffmpeg)
- libvorbis (has to be explicitly enabled when compiling ffmpeg)
- wavpack (has to be explicitly enabled when compiling ffmpeg)

## Use

- ***nix**: To start **videomass** without installing in the system, simply run the "videomass" file into 
unzipped sources folder, like this: `~$ python videomass` or `~$ ./videomass`. 
Be sure to check the execution permissions first.

- **Windows**: To start **videomass** without installing in the system, unzip the Videomass sources 
folder that you just download, open a dos window and position you in the folder you just 
unzipped, then type: `python videomass`


## Build Package

For building a redistributable package, using setup.py script in the sources folder.
There are several way to use it, this depends on the operating system used since each 
operating system has its own packaging tools. However, the common need tools and useful 
for simple python distibutions are *distutils* and *setuptools*.

- **distutils** is still the standard tool for packaging in python. It is included in the
standard library that can be easily imported.   

- **setuptools** which is not included in the standard library, must be
separately installed if not present in your system.
Update: setuptools is included from python 2.7

## Make a debian packages

If you want make a *.deb* binary package installable in your debian system and 
compatible with others debian-based systems, you need install those following tools: 
`~# apt-get update && apt-get install python-all python-stdeb fakeroot`. 
This installs all the need dependencies, including python-setuptools.   

Then, go into Videomass unzipped folder with your user (not root) and type:   
`~$ python setup.py --command-packages=stdeb.command bdist_deb`   
This should create a *python-videomass_version_all.deb* in the new deb_dist directory, 
installable with `~# dpkg -i python-videomass_version_all.deb` command.

See also [setup.py](https://github.com/jeanslack/Videomass/blob/master/setup.py) 
script for insights.

## Make a Slackware package

Is available a SlackBuild script to build a package *.tgz* for Slackware and Slackware based 
distributions. 
See here [videomass.SlackBuild](https://github.com/jeanslack/slackbuilds/tree/master/Videomass)

## MacOs

**As portable application (Run from sources code):**

You can run Videomass without install it, but make sure you have installed the following requests:

* WxPthon 3.0 (from homebrew)
* FFmpeg >= 3.2 (from hombrew)
* git

Then, clone the latest sources with git: `~$ git clone https://github.com/jeanslack/Videomass`

or download Videomass sources at github site: <https://github.com/jeanslack/Videomass>
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

If you have successfully performed the points described above, then you can try do the Videomass App for macOs.
For build the Videomass.app there you need Xcode and command-line-tools available to the app store. 
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
Note that on Videomass sources already exists a setup.py, then activate your virtual env and run setup.py:   
    
    `~$ python setup.py py2app` 

## Windows

**Notice!**:
Videomass do not include binaries/executables of the ffmpeg, ffprobe and ffplay.
If ffmpeg is not yet installed on your system please, download the compatible executable
of the FFmpeg for your Windows OS and set the pathname with Videomass setup dialog, otherwise
Videomass will not work.
You may be interested the following explanation:
<https://video.stackexchange.com/questions/20495/how-do-i-set-up-and-use-ffmpeg-in-windows>

**As portable application script (Run from sources code):**

- Download the latest release of the Python2.7 from 

<https://www.python.org/downloads/> and install it.

- Download the latest release of wxPython3.0 (.exe) toolkit for python 2.7 from:

<https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/> and install it.

- Download the Videomass sources from:

<https://github.com/jeanslack/Videomass>

and see [Use](#use)   

**Make a .exe executable**

If you have successfully completed the points described above, now download and Install the **py2exe** utility for python 2.7 by:

<https://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/>

if need update it and follow this how-to:

<https://www.blog.pythonlibrary.org/2010/07/31/a-py2exe-tutorial-build-a-binary-series/>

Then open a dos window and position you in the Videomass folder you just unzipped and type:

`python setup.py py2exe`

A folder named 'dist' will be created where there will be the magic executable of Videomass.exe

## License

Copyright © 2013 - 2018 by jeanslack   
Author and Developer: Gianluca Pernigotto   
Mail: <jeanlucperni@gmail.com>   
License: GPL3 (see LICENSE file in the docs folder)
