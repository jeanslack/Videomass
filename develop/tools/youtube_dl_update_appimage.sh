#!/bin/bash
#
# Description:
# ------------
#   Update pip and youtube-dl on Videomass*.AppImage
#   Place this script on 'AppDir/usr/bin' with execute permissions.
#   Remember, you need 'appimagetool-x86_64.AppImage' inside the same
#   directory.
#
# Warning:
# --------
#   you can run this script directly, e.g. by calling it in a terminal
#   window and passing it the pathname of the AppImage as argument.
#   However, it is strongly not recommended to run it via AppRun as the
#   generated log file will be saved inside the AppDir and will not be
#   found by Videomass for the exit status.
#
# please visit <https://misc.flogisoft.com/bash/tip_colors_and_formatting>
# for colors code.
#
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2020-2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# Update: Oct.03.2020

set -e  # stop if error

MACHINE_ARCH=$(arch)
SITEPKG="squashfs-root/opt/python3.8/lib/python3.8/site-packages"
APPIMAGE=$1  # selected videomass appimage pathname
BASENAME="$(basename $APPIMAGE)"  # videomass name
DIRNAME="$(dirname $APPIMAGE)"  # videomass directory

# building in temporary directory to keep system clean.
# Don't use /dev/shm as on some Linux distributions it may have noexec set
TEMP_BASE=/tmp

BUILD_DIR=$(mktemp -d -p "$TEMP_BASE" videomass-AppImage-update-XXXXXX)

# make sure to clean up build dir, even if errors occur
cleanup () {
    if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
    fi
    }
trap cleanup EXIT

# switch to build dir
pushd "$BUILD_DIR"

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# extract appimage inside BUILD_DIR/
$APPIMAGE --appimage-extract

# export squashfs-root
export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"

# update pip
./squashfs-root/opt/python3.8/bin/python3.8 -m pip install -U --target=$SITEPKG pip

# update certifi
./squashfs-root/opt/python3.8/bin/python3.8 -m pip install -U --target=$SITEPKG certifi

# update youtube_dl package
./squashfs-root/opt/python3.8/bin/python3.8 -m pip install -U --target=$SITEPKG youtube_dl

# retrieve the Videomass version from the package metadata
export VERSION=$(cat $SITEPKG/videomass-*.dist-info/METADATA | \
    grep "^Version:.*" | cut -d " " -f 2)

# Convert back into an AppImage
"squashfs-root/usr/bin/appimagetool-x86_64.AppImage" squashfs-root/

# move built AppImage back into original DIRNAME
mv -f Videomass*x86_64.AppImage "$DIRNAME/"  # overwrites existent appimage

echo '**Successfully updated**'  # keyword for a successful exit status
# echo -e '\e[5m\e[92myoutube_dl has been successfully updated!\e[25m\e[39m'
# echo -e '\e[1m\e[92m...Now close this terminal and restart Videomass.\e[21m\e[39m'
