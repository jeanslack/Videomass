[Home](index.md)

## Known problems and solutions of Videomass on Python2

- Non-ASCII and UTF8 characters are not yet supported on Videomass. 
Before importing files with non-ASCII/UTF8 names, please rename them appropriately. 
This problem affects all platforms (Windows, MacOsx and Linux).

- On MacOSx, if there are problems with the Videomass configuration folder, or 
when the configuration file version changes during updates with a new version 
of the program, the warning windows may disappear immediately when Videomass is 
started, making it impossible to read the warnings. One solution is to 
permanently delete the configuration folder located in ```~/.videomass``` 
and re-open the Videomass program.


## Known problems and solutions of Videomass on Python3 and Python2

- On Windows, with the version of FFmpeg 3.1.5 included in the installer, the 
**nlmeans** denoiser filter is not implemented, as it exists only in the most 
recent versions of FFmpeg. Use **hqdn3d** instead, or set Videomass to a path 
with a newer version of FFmpeg.

[Home](index.md)
