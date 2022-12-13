---
layout: page
title: Features
nav_order: 2
---
# Features
---

Videomass is a free, open source and cross-platform GUI for FFmpeg and youtube-dl,
concatenate (mux or encode videos), presets manager, conversions.
This audio/video converter is user friendly for beginners and more advanced users. 
Using the step by step interface (GUI) you can simply choose a preset or make your 
own. For the people that are familiar with FFmpeg there is the possbility to easily 
make your own presets using the FFmpeg command line or make a preset through the GUI
and adapt this to your specific needs. It offers out of the box output to all
possible file formats like MP4, MKV, MOV etc. Video: MPEG-4, H.264/AVC, H.265/HEVC,
VP9 and audio: AAC, MP3, OPUS, WAV, FLAC or AC-3 and subtitles and much more! Also
you can copy streams (lossless video and/or audio) and extract audio. Finally it
has a simple timeline editor, extended multimedia information and optional YouTube
downloader.

## Main features
{: .bg-green-300}
---
- No ads
- Multi-Platform, work on Linux, MacOs, Windows, FreeBsd.
- Batch processing.
- Log file automatically saved.
- Multi-panels, switch between panels using keyboard shortcuts.
- Audio video encoding.
- Download videos from hundreds of sites.
- Multi language support (English, French, Italian, Russian, Dutch, Portuguese-BR, simplified Chinese, Spanish)

## Using FFmpeg
{: .bg-green-300}
---
- Drag and drop to add multiple files simultaneously.
- Fully customizable presets and profiles.
- Possibility to create your new presets and profiles from scratch.
- Has useful presets to start with.
- Supports all [formats](https://ffmpeg.org/ffmpeg-formats.html) and [codecs](https://ffmpeg.org/ffmpeg-codecs.html) available with FFmpeg.
- Madia file info and stream analyzer.
- Shows the estimated time of arrival during encodings.
- Concatenate.
- Create video from still image and audio file.
- Extract images from video
- has useful tools for evaluating the supported features of a specific FFmpeg build.
- Audio stream mapping using indexes.
- Advanced dialogs for setting video filters such as:
    - Resizing 
    - Cropping
    - Rotation
    - Deinterlacing
    - Denoise
    - Stabilization
- Audio filters for volume normalization:
    - PEAK, RMS and [EBU-R128](http://ffmpeg.org/ffmpeg-filters.html#loudnorm) normalizers.
    - PEAK and RMS volume analysis reporting.
    - Ability to apply volume normalization only for certain audio streams in videos.
- Timeline editor:
    - Convenient display for viewing the time selection.
- ...and much more

## Using youtube-dl or yt-dlp
{: .bg-green-300}
---
- Possibility to choose between two downloaders:
[youtube-dl](https://github.com/ytdl-org/youtube-dl) or
[yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Download from multiple URLs (YouTube and more sites,
[over 200](http://ytdl-org.github.io/youtube-dl/supportedsites.html) are currently supported).
- 5 download modes:
    - Precompiled Videos (best or worst)
    - By set preferred resolution and format.
    - Download split audio and video.
    - Download Audio only.
    - Download and merge audio and video by selecting "format codes".
- Shows download statistics.
- Ability to playback individual URLs and different qualities.
- Ability to download playlists.
- Ability to index playlists to download.
- You can enable or disable the SSL certificate check.
- Embed thumbnail in audio file (via [atomicparsley](http://atomicparsley.sourceforge.net/)).
- Add metadata to file.
- Write subtitles to video.
- Ability to include IDs in filenames.
- Ability to restrict file names.
- Ability to keep youtube-dl backend updated (only available for *.AppImage).

