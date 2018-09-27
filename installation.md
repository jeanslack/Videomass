[Home](index.md)

## Installation

#### Windows and MacOS:
For a typical installation on Microsoft Windows and MacOS operating systems, installers are available at the top of this page. They are only available for x86_64 (64-bit) architecture. Both installers contain everything you need to be used in standalone mode, without the need for anything else.

Minimum requirements are:
- MacOS High Sierra (64-bit only)
- Microsoft Windows 7 to Windows 10 (64-bit only)

...That's all

#### Debian, Ubuntu (and based):
For Gnu/Linux Debian or Debian distribuition based, is available a **.deb** package at the top of this page, for all architectures (32-bit and 64-bit). Before installing it, you need to install the required dependencies:

```
~$ sudo apt-get install python-wxgtk3.0 ffmpeg
```
Then proceed to install Videomass2, example:
```
~$ sudo dpkg -i python-videomass2_1.0.1-1_all.deb
```

#### Slackware, Salix (and based):
There is also a small repository which contains a [SlackBuild](https://github.com/jeanslack/slackbuilds/tree/master/Videomass) script to build the precompiled binary of Videomass2 with **.tgz** extension that can be installed with the installpkg command.    
Of course, it must be edited according to the new Videomass2.

