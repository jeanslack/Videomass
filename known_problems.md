[Home](index.md)

## Known problems and solutions of Videomass

- If you are using an earlier version of FFmpeg equal to or less than 3.1.5, the
_nlmeans_ filter it may not have been implemented yet, since it exists only in
the most recent versions of FFmpeg. Instead, use _hqdn3d_ or set Videomass to a
path with a newer version of FFmpeg.

- FFmpeg version 3.1 or higher is required for the _loudnorm_ filter (on EBU audio 
normalization). Versions earlier than ffmpeg 3.1 cause `No such filter: loudnorm` 
error on the Videomass 'Log viewing console' and the conversion process will fail.

- For VP9 encoder FFmpeg added support for row based multithreading in version
3.4, released on January 25th, 2018. As of libvpx version 1.7.0 this
multithreading enhancement is not enabled by default and needs be manually
activated with the `-row-mt 1` switch. Note that this feature is not available
if you are using an older version of the FFmpeg (eg Version 3.1.5) and should
be disabled when using this encoder.

- **Videomass.exe** and **Videomass.app** may have some functional limitations:
   * 1) the button for previewing streaming content (Youtube, Facebook, etc) may not work.

   * 2) The 'Show More' button for reading the informations of the streaming
   content (YouTube, Facebook, etc) will give a message regarding disabling the functionality.

- **Videomass.AppImage** for Linux
    * It has been successfully tested on the following Linux distributions:
        * Ubuntu 16.04 LTS x86_64
        * Ubuntu 18.04 LTS x86_64
        * Xubuntu 18.04 x86_64
        * Ubuntu 20.04 LTS x86_64
        * Linux Mint 19.3 x86_64 Cinnamon
        * Debian 9 stretch x86_64
        * Debian 10 buster x86_64
        * SparkyLinux 5.11 lxqt x86_64 (stable edition)
        * Sparkylinux 2020.06 xfce x86_64 (rolling edition)
        * AV-Linux 2019.4.10 x86_64
        * AV-Linux 2020.4.10 x86_64
        * Fedora 32 (Workstation Edition) x86_64
        * Manjaro Linux 20.0.3 (Lysia) x86_64

    * It may be necessary to install FFmpeg since it is not included on the
    appimage. On some distributions it is already installed by default.

[Home](index.md)
