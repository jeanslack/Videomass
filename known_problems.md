---
layout: page
title: Known Problems
has_children: true
nav_order: 6
---

# Known problems and solutions
-------------------------------------------

## Using YouTube Downloader

- Using yt_dlp API is currently not possible stopping downloads clicking the "Stop" button. 
To workaround this issue, switch to `Use the executable for downloads rather than Python module` 
selecting related check box in the `yt-dlp` tab of Options dialog.

- [Drag-and-drop of text and URLs not working with Firefox under Linux](https://github.com/wxWidgets/wxWidgets/issues/17694). 
Using a web browser other than Firefox or dragging and dropping text from a text 
editor seems to work fine. Please note that this issue affect Linux OS's only.
