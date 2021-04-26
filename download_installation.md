[Home](index.md)

# Download and installation
--------------

## Linux

### Ubuntu PPA
This PPA currently publishes packages for Ubuntu 20.04 Focal and Ubuntu 20.10 Groovy (for now)   

- To install Videomass add this [PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/videomass) 
to your system:   

    `$ sudo add-apt-repository ppa:jeanslack/videomass`   
    `$ sudo apt-get update`   
    `$ sudo apt install python3-videomass` 

### AppImage
There are currently two ports for GTK2 and GTK3 engines, which only support 
64-bit architectures. Videomass AppImages do not include FFmpeg which must be 
installed separately.   

Find out below which port is best suited to your Linux distribution.     
 
[Videomass for GTK2](https://github.com/jeanslack/Videomass/releases)   

Successfully tested on the following Linux distributions:   
* Ubuntu 16.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Ubuntu 18.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Xubuntu 18.04 x86_64 (by installing libsdl2 or ffmpeg first)
* Ubuntu 20.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Linux Mint 19.3 x86_64 Cinnamon
* Debian 9 stretch x86_64
* Debian 10 buster x86_64
* SparkyLinux 5.11 lxqt x86_64 (stable edition)
* Sparkylinux 2020.06 xfce x86_64 (rolling edition)
* AV-Linux 2019.4.10 x86_64
* AV-Linux 2020.4.10 x86_64
* ~~Fedora 32 (Workstation Edition) x86_64~~ NOT WORK
* Manjaro Linux 20.0.3 (Lysia) x86_64

Minimum requirements:
- **Ubuntu 16.04 LTS x86_64** to up   
 
[Videomass for GTK3](https://sourceforge.net/projects/videomass2/files/)   

Successfully tested on the following Linux distributions:   
* ~~Ubuntu 16.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)~~ NOT WORK
* Ubuntu 18.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Xubuntu 18.04 x86_64 (by installing libsdl2 or ffmpeg first)
* Ubuntu 20.04 LTS x86_64 (by installing libsdl2 or ffmpeg first)
* Linux Mint 19.3 x86_64 Cinnamon
* Debian 9 stretch x86_64
* Debian 10 buster x86_64
* SparkyLinux 5.11 lxqt x86_64 (stable edition)
* Sparkylinux 2020.06 xfce x86_64 (rolling edition)
* AV-Linux 2019.4.10 x86_64
* AV-Linux 2020.4.10 x86_64
* Fedora 32 (Workstation Edition) x86_64
* Manjaro Linux 20.0.3 (Lysia) x86_64

Minimum requirements:
- **Debian 9 stretch x86_64** to up   

## MS Windows
Installer available at:
- [GitHub Releases](https://github.com/jeanslack/Videomass/releases)    

**New:** starting from Videomass v3.3.0 a portable version is also available, 
choose the one that works best for you!  

Minimum requirements:
- Microsoft **Windows 7** to up (64-bit only)
- If you use Videomass to download videos from YouTube.com and other video 
sites, [Microsoft Visual C ++ 2010 Redistributable Package (x86)](https://www.microsoft.com/en-US/download/details.aspx?id=5555) 
is required.

## MacOs
MacOs users should use the disk image file (.**dmg**) available at:
- [GitHub Releases](https://github.com/jeanslack/Videomass/releases)   

Minimum requirements:
- MacOS **High Sierra** to up.
The binary is compiled for **Mac OS X 10.13.6 64-bit** and later. 
It will not run on earlier versions.

## Limitations 
For some functional limitations related to the above packages (not for Ubuntu 
PPA) see [Known Problems](https://jeanslack.github.io/Videomass/known_problems.html).   

## For developpers
please visit
- [Development page](https://github.com/jeanslack/Videomass)   
- [Wiki page](https://github.com/jeanslack/Videomass/wiki)   
- [Pypi page](https://pypi.org/project/videomass/)

[Home](index.md)

