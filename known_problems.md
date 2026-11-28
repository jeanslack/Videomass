---
layout: page
title: Known Problems
has_children: true
nav_order: 6
---

# Known problems and solutions
-------------------------------------------

### Linux Wayland Issues

On some Wayland-based desktop environments, tooltips or certain UI elements may not render or behave properly. If you experience display issues, launch Videomass using the X11 backend (`GDK_BACKEND=x11 videomass`).

👉 See the [Linux Wayland problems and solutions](https://github.com/jeanslack/Videomass/wiki/Linux-Wayland-problems-and-solutions) wiki page for full instructions on how to configure this permanently in your `.desktop` launcher.

---

### Cannot play audio/video files

If you encounter `redraw` filter errors while playing audio/video files (using FFplay), ensure that you are using a build of FFmpeg with `fontconfig` enabled.
