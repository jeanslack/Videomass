---
layout: default
title: Linux
parent: Downloads
nav_order: 3
---

---

# Linux

## Ubuntu/Mint PPA

This PPA currently publishes packages for [Ubuntu](https://ubuntu.com/), including official and 
derivative distributions.   

- [Ubuntu 23.04 Lunar](https://cdimage.ubuntu.com/daily-live/current/)
- [Ubuntu 22.10 Kinetic](https://releases.ubuntu.com/kinetic/)
- [Ubuntu 22.04 Jammy](https://releases.ubuntu.com/22.04/)
- [Ubuntu 20.04 Focal](https://releases.ubuntu.com/focal/)   


To install Videomass add this 
[PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/videomass) to your system: 
  

`$ sudo apt-add-repository ppa:jeanslack/videomass`   
`$ sudo apt-get update`  
`$ sudo apt install python3-videomass`   

For any other application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.
{: .fs-3 .text-grey-dk-100}   

---

## MX-Linux

Videomass is available on [test repo](https://mxlinux.org/community-repos/) 
of [MX-Linux](https://mxlinux.org/) which is accessible from 
[MX package installer](https://mxlinux.org/wiki/help-files/help-mx-package-installer/).
So, to install Videomass you will need to enable this repo and proceed with the 
installation .

---

## ArchLinux

Videomass is available on the Arch User Repository as [AUR package](https://aur.archlinux.org/packages/videomass) .

Can be installed by using `pacaur/yay/etc.` after activating AUR on Arch Linux, or in AUR part of Manjaro (Arch Linux derivative) Linux.

---

## Mageia 8

Exists a third-party repository for Mageia 8 that have a rpm package for videomass.
The repository comes from [BlogDrake](https://blogdrake.net/) The Official Community 
for Spanish Talking Users.

To add this repo, first you have to configure the Official [Mageia](https://www.mageia.org/en/) 
repositories then:

For i586 - 32bit systems
{: .fs-3 .text-grey-dk-100}

```
su -
urpmi.addmedia --wget --distrib https://ftp.blogdrake.net/mageia/mageia8/i586
urpmi videomass
exit
```

For x86_64 - 64bit systems
{: .fs-3 .text-grey-dk-100}

```
su -
urpmi.addmedia --wget --distrib https://ftp.blogdrake.net/mageia/mageia8/x86_64
urpmi videomass
exit
```
---

## SparkyLinux

The Videomass tool is available for Debian "Bullseye"/Sparky “Po Tolo” only.

Installation:   

`sudo apt update`   
`sudo apt install videomass`   

or via Sparky [APTus](https://sparkylinux.org/sparky-aptus-0-4-36/)-> VideoTools tab.

---

## AppImage format
{: .d-inline-block } 

Portable
{: .label .label-purple }   

About [AppImage](https://appimage.org/) format   
{: .fs-3 .text-grey-dk-100}

Minimum requirements:   
- All [Ubuntu flavors](https://ubuntu.com/download/flavours) based on 
[18.04 LTS x86_64](https://releases.ubuntu.com/18.04.5/) version.
- [x86_64](https://en.wikipedia.org/wiki/X86-64) architecture.
- [FFmpeg](https://www.ffmpeg.org/) version 3.1.5 

[Videomass 5.0.1 AppImage](https://github.com/jeanslack/Videomass/releases/latest/download/Videomass-5.0.1-x86_64.AppImage){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 }  

Successfully tested on the following Linux distributions:   
* [Xubuntu](https://xubuntu.org/) 18.04 LTS x86_64 
* [Ubuntu](https://ubuntu.com/) 20.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* [Debian](https://www.debian.org/index.en.html) 10 buster x86_64
* [Debian](https://www.debian.org/index.en.html) 11 bullseye x86_64
* [Fedora](https://getfedora.org/en/) 32 x86_64 (Workstation Edition) 
* [Manjaro](https://manjaro.org/) 20.0.3 (Lysia) x86_64 
* [Devuan](https://www.devuan.org/) 4.0 Chimaera amd64
* [Slackware](http://www.slackware.com/) 15.0 x86_64 (full installation from DVD)

For any application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.
{: .fs-3 .text-grey-dk-100}   
