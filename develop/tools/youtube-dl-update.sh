#!/bin/bash
#
# Description: Update pip and youtube-dl on Videomass.AppImage
# Place this script on 'AppDir/usr/bin' with execute permissions.
# Remember, you need 'appimagetool-x86_64.AppImage' inside the same
# directory.
#
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Update: Sept.15.2020

set -e  # stop if error

MACHINE_ARCH=$(arch)
OPT="squashfs-root/opt/python3.8"
USR_SHARE="squashfs-root/usr/share"
APPIMAGE=$1
BASENAME="$(basename $APPIMAGE)"
DIRNAME="$(dirname $APPIMAGE)"

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# make temporary folder for work
mkdir -p -m 0775 $DIRNAME/.TMP_APPDIR
cd $DIRNAME/.TMP_APPDIR
../$BASENAME --appimage-extract

# export squashfs-root
export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"

# update pip
./squashfs-root/opt/python3.8/bin/python3.8 -m pip install -U \
    --target=$OPT/lib/python3.8/site-packages pip
./squashfs-root/opt/python3.8/bin/python3.8 -m pip install -U \
    --target=$OPT/lib/python3.8/site-packages youtube_dl

# Convert back into an AppImage
export VERSION=$(cat $OPT/lib/python3.8/site-packages/videomass-*.dist-info/METADATA \
    | grep "^Version:.*" | cut -d " " -f 2)

"squashfs-root/usr/bin/appimagetool-x86_64.AppImage" squashfs-root/

mv -f Videomass*x86_64.AppImage ../ # overwrites existent appimage
cd ..
rm -fr .TMP_APPDIR
echo
echo -e '\e[5m\e[92myoutube_dl has been successfully updated!\e[25m\e[39m'
echo -e '\e[1m\e[92m...Now close this terminal and restart Videomass.\e[21m\e[39m'
