[Home](index.md)

## Installation

#### Windows and MacOS:
For a typical installation on Microsoft Windows and MacOS operating systems, installers (for x86_64 architecture only) are available at the top of this page. Both installers (with extensions .dmg and .exe) contain everything you need (Python, wxPython, FFmpeg and Videomass2) to be used in standalone mode, with no need for anything else.

Minimum requirements are:
- MacOS High Sierra (64-bit only)
- Microsoft Windows 7 (64-bit only)

#### Debian, Ubuntu (and based):
For Gnu/Linux Debian or Debian distribuition based, is available a **.deb** package at the top of this page, for all architectures (32-bit and 64-bit). Before installing it, you need to install the required dependencies:

```
~$ sudo apt-get install python-wxgtk3 ffmpeg
```
Then proceed to install Videomass2:
```
~$ sudo dpkg -i python-videomass2_1.0.1-1_all.deb
```

#### Slackware, Salix (and based):
There is also a small repository which contains a SlackBuild for Slackware Gnu/Linux distro, to build the precompiled binary of Videomass2 with **.tgz** extension that can be installed with the `installpkg` command: [Videomass SlackBuild](https://github.com/jeanslack/slackbuilds/tree/master/Videomass)     
Of course, it must be edited according to the new Videomass2.

