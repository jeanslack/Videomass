[Home](index.md)

# Known problems and solutions of Videomass
-------------------------------------------

## Common problems

- If you are using an earlier version of FFmpeg equal to or less than 3.1.5, the
_nlmeans_ filter it may not have been implemented yet, since it exists only in
the most recent versions of FFmpeg. Instead, use _hqdn3d_ or get a newer version of FFmpeg.

- FFmpeg version 3.1 or higher is required for the _loudnorm_ filter for EBU audio 
normalization. Versions earlier than ffmpeg 3.1 cause `No such filter: loudnorm` 
error on the Videomass 'Log viewing console' and the conversion process will fail.

- For VP9 encoder FFmpeg added support for row based multithreading in version
3.4, released on January 25th, 2018. As of libvpx version 1.7.0 this
multithreading enhancement is not enabled by default and needs be manually
activated with the `-row-mt 1` switch. Note that this feature is not available
if you are using an older version of the FFmpeg (eg Version 3.1.5) and should
be disabled when using this encoder.

- [Other issues](https://github.com/jeanslack/Videomass/issues)     

[Home](index.md)
