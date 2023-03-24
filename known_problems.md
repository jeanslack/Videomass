---
layout: page
title: Known Problems
has_children: true
nav_order: 6
---

# Known problems and solutions
-------------------------------------------

## Using YouTube Downloader

- It is currently impossible to immediately stop the download by clicking the 
"Abort" button, and this also applies to downloading playlists, which could be a 
bit problematic if you have planned to download hundreds of files from a single 
playlist. 
For clarification, in a list of URLs the abort occurs only after completion of a 
URL in progress. Therefore, it is not the download in progress that will be terminated but the batch processing of a list of queued URLs. 
This is not a Videomass-related issue itself, but the lack of a stop implementation 
on the yt-dlp API.  

