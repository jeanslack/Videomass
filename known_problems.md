[Home](index.md)

## Known problems and solutions of Videomass

- On Windows the ffMPEG version 3.1.5 included ON the installation program, 
denoiser _nlmeans_ filter is not implemented, since it exists only in the most 
recent versions of FFmpeg. Use _hqdn3d_ instead or set Videomass to a path with a 
newer version of FFmpeg.

- For VP9 encoder FFmpeg added support for row based multithreading in version 3.4, released on January 25th, 2018. As of libvpx version 1.7.0 this multithreading enhancement is not enabled by default and needs be manually activated with the -row-mt 1 switch. Note that this feature is not available in version 3.1.5 of FFmpeg pachetized with the Videomass installer for Windows and should be disabled when using this encoder.



[Home](index.md)
