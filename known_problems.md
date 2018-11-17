[Home](index.md)

## Known problems and solutions

- On Windows, with the version of FFmpeg 3.1.5 included in the installer, the **nlmeans** denoiser filter is not implemented, 
as it exists only in the most recent versions of FFmpeg. Use **hqdn3d** instead, or set Videomass2 to a path with a newer version of FFmpeg.

- Non-ASCII and UTF8 characters are not yet supported on Videomass2. Before importing files with non-ASCII/UTF8 names, 
please rename them appropriately. This problem affects all platforms (Windows, MacOsx and Linux).

- On MacOSx, if there are problems with the Videomass2 configuration folder, or when the configuration file version 
changes during updates with a new version of the program, the warning windows may disappear immediately when Videomass2 
is started. One solution is to permanently delete the configuration folder located in ```~/.videomass2``` and re-open 
the Videomass2 program.

[Home](index.md)
