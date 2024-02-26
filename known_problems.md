---
layout: page
title: Known Problems
has_children: true
nav_order: 6
---

# Known problems and solutions
-------------------------------------------

## Using YouTube Downloader

- Stopping a current download by clicking the "Abort" button is currently not possible as 
this feature is not yet implemented in the yt-dlp [API](https://en.wikipedia.org/wiki/API).   
Only subsequent downloads in a URL list can be stopped programmatically by clicking the "Abort" button.  

- [Drag-and-drop of text and URLs not working with Firefox under Linux](https://github.com/wxWidgets/wxWidgets/issues/17694). 
Using a web browser other than Firefox or dragging and dropping text from a text 
editor seems to work fine. Please note that this issue affect Linux OS's only.
