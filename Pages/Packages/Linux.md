---
layout: default
title: Linux
parent: Downloads
nav_order: 1
---

---

## Ubuntu PPA
This PPA currently publishes packages for Ubuntu 20.04 Focal and Ubuntu 20.10 Groovy (for now)   

- To install Videomass add this [PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/videomass) to your system:   

    `$ sudo add-apt-repository ppa:jeanslack/videomass`   
    `$ sudo apt-get update`   
    `$ sudo apt install python3-videomass` 
    
---

## AppImage
Videomass AppImage is available with porting for the GTK2 engine, which only supports the x86_64 architecture.   
Note that Videomass AppImages **do not include** FFmpeg which must be installed separately.       

**Important:** before starting Videomass as AppImage it is necessary to give execution permissions:   

`$ chmod a+x ./Videomass-?.?.?-x86_64.AppImage`   

Then run the program:   

`$ ./Videomass-?.?.?-x86_64.AppImage`   

*Please, Replace "?" with version in use.*

---

[Videomass.AppImage GTK2](https://github.com/jeanslack/Videomass/releases/download/v.3.4.3/Videomass-3.4.3-x86_64.AppImage){: .btn .btn-green }   

Successfully tested on the following Linux distributions:   
* Ubuntu 16.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Ubuntu 18.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Xubuntu 18.04 x86_64 (by installing libsdl2 or ffmpeg first)
* Ubuntu 20.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Linux Mint 19.3 x86_64 Cinnamon
* Debian 9 stretch x86_64
* Debian 10 buster x86_64
* Debian 11 bullseye x86_64
* SparkyLinux 5.11 lxqt x86_64 (stable edition)
* Sparkylinux 2020.06 xfce x86_64 (rolling edition)
* AV-Linux 2019.4.10 x86_64
* AV-Linux 2020.4.10 x86_64
* ~~Fedora 32 (Workstation Edition) x86_64~~ NOT WORK
* Manjaro Linux 20.0.3 (Lysia) x86_64

Minimum requirements, **Ubuntu 16.04 LTS x86_64** to up.   
