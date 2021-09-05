---
layout: default
title: Linux
parent: Downloads
nav_order: 1
---

---

## Ubuntu PPA
This PPA currently publishes packages for Ubuntu, including official and 
derivative distributions.   

- Ubuntu 18.04 Bionic
- Ubuntu 20.04 Focal 
- Ubuntu 20.10 Groovy
- Ubuntu 21.04 Hirsute
- Ubuntu 21.10 Impish   

To install Videomass add this 
[PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/videomass) to your system: 
  

`$ sudo add-apt-repository ppa:jeanslack/videomass`   
`$ sudo apt-get update`  
`$ sudo apt install python3-videomass`   
    
---

## AppImage
Videomass [AppImage](https://en.wikipedia.org/wiki/AppImage) is available with 
porting for the GTK3 engine, which only supports the x86_64 architecture.   
Note that Videomass AppImages **do not include** FFmpeg which must be installed separately.       

**Important:** before starting Videomass as AppImage it is necessary to give execution permissions:   

`$ chmod a+x ./Videomass-3.4.5-x86_64.AppImage`   

Then run the program:   

`$ ./Videomass-3.4.5-x86_64.AppImage`   

[Videomass.AppImage GTK2](https://github.com/jeanslack/Videomass/releases/latest/download/Videomass-3.4.5-x86_64.AppImage){: .btn .btn-green }   

Successfully tested on the following Linux distributions:   
* Xubuntu 18.04 LTS x86_64 
* Ubuntu 20.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Debian 10 buster x86_64
* Debian 11 bullseye x86_64
* Fedora 32 x86_64 (Workstation Edition) 
* Manjaro Linux 20.0.3 (Lysia) x86_64

Minimum requirements, **Ubuntu 18.04 LTS x86_64** to up.   

For any application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.   
