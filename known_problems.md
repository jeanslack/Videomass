[Home](index.md)

## Known problems and solutions of Videomass

- If you are using an earlier version of FFmpeg equal to or less than 3.1.5, the 
_nlmeans_ filter it may not have been implemented yet, since it exists only in 
the most recent versions of FFmpeg. Instead, use _hqdn3d_ or set Videomass to a 
path with a newer version of FFmpeg.

- For VP9 encoder FFmpeg added support for row based multithreading in version 
3.4, released on January 25th, 2018. As of libvpx version 1.7.0 this 
multithreading enhancement is not enabled by default and needs be manually 
activated with the -row-mt 1 switch. Note that this feature is not available 
if you are using an older version of the ffMPEG (eg Version 3.1.5) and should 
be disabled when using this encoder.

- Standalone installers for Linux (AppImage only), Windows (exe) and MacOS 
(app) may have some functional limitations:
   * 1) the button for previewing streaming content (Youtube, Facebook, etc) may not work.

   * 2) The 'Show More' button for reading the information of the streaming content (YouTube, Facebook, etc) will give a message regarding disabling the functionality.

[Home](index.md)
