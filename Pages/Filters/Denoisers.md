[Back](../../videomass2_use.md)

## Denoisers

Videomass2 supports two of the most popular denoisers used by FFmpeg. The reason for this choice is that the 
denoiser `nlmeans` exists only on newer versions of FFmpeg, while` hqdn3d` exists on both new and older versions of FFmpeg. 
When one of them fails, try the other.

### nlmeans 
Denoise frames using Non-Local Means algorithm is capable of restoring video sequences with even strong noise. 
It is ideal for enhancing the quality of old VHS tapes.   

### hqdn3d
This is a high precision/quality 3d denoise filter. It aims to reduce image noise, producing smooth images and making 
still images really still. It should enhance compressibility.

[Back](../../videomass2_use.md)
