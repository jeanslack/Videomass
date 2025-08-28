---
layout: default
title: Linux
parent: Downloads
nav_order: 3
---

---

# Linux - Third-Party Repositories

## Ubuntu PPA

This PPA currently publishes packages for [Ubuntu](https://ubuntu.com/) flavors, including 
[official derivatives](https://ubuntu.com/desktop/flavors) and unofficial derivative distributions 
such as [Linuxmint](https://linuxmint.com/), etc.   

To install Videomass add this [PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/videomass) to your system: 
  

`$ sudo apt-add-repository ppa:jeanslack/videomass`   
`$ sudo apt-get update`  
`$ sudo apt install videomass`   

For any other application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.
{: .fs-3 .text-grey-dk-100}   

---

## Slackware

Videomass is available on the [SlackBuilds.org](https://slackbuilds.org/) 
("Sbo") repository, a collection of third-party SlackBuild scripts to build Slackware packages from sources.

It can be downloaded, built and installed automatically using the [sbopkg](https://sbopkg.org/) 
tool, or manually using the traditional method (see howto at [https://slackbuilds.org/howto/](https://slackbuilds.org/howto/))   

---

## ArchLinux

Videomass is available on the Arch User Repository as [AUR package](https://aur.archlinux.org/packages/videomass) .

Can be installed by using `pacaur/yay/etc.` after activating AUR on Arch Linux, 
or in AUR part of Manjaro (Arch Linux derivative) Linux.

---

## Devuan / Debian

The latest pre-compiled, architecture-independent **DEB** package is available here: [videomass_6.1.18-1_all.deb](https://github.com/jeanslack/Videomass/releases/download/v6.1.18/videomass_6.1.18-1_all.deb){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 .mr-2}

Tested on:

- Devuan Chimaera
- Devuan Daedalus
- Debian11 bullseye
- Debian12 bookworm

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

## AppImage format
{: .d-inline-block } 

Portable
{: .label .label-purple }   

About [AppImage](https://appimage.org/) format   
{: .fs-3 .text-grey-dk-100}

### No longer available 
{: .bg-red-300}

The Videomass AppImage format will no longer be available until a wxPython-manylinux 
package (installable on Python-AppImage) compatible with most Linux distributions 
which can be embedded into the AppImage is officially released.   

See the following related issues: 
- [https://github.com/jeanslack/Videomass/issues/186](https://github.com/jeanslack/Videomass/issues/186)
- [https://github.com/niess/python-appimage/issues/58](https://github.com/niess/python-appimage/issues/58)
- [https://discuss.wxpython.org/t/how-to-bundle-wxpython-with-appimage/35289/3](https://discuss.wxpython.org/t/how-to-bundle-wxpython-with-appimage/35289/3)

About manylinux on wxPython documentations:
- [https://wxpython.org/pages/downloads/](https://wxpython.org/pages/downloads/)

For any application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.
{: .fs-3 .text-grey-dk-100}   
