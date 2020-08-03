#!/bin/bash
#
# Description: Update to the latest version the videomass package
#              from https://pypi.org/ starting from Videomass-*-x86_64.AppImage

set -e

# Extract this AppImage
chmod +x Videomass-*-x86_64.AppImage
./Videomass-*-x86_64.AppImage --appimage-extract

# Add AppDir to environment variables
export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"

# Update videomass into the extracted AppDir
pip install --no-deps -U videomass

# Test that it works
#./squashfs-root/AppRun

# Convert back into an AppImage
export VERSION=$(cat squashfs-root/opt/python3.7/lib/python3.7/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
./appimagetool-x86_64.AppImage squashfs-root/
