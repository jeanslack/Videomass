#!/bin/bash
#
# Description: Build from scratch a Videomass-*-x86_64.AppImage starting
#              from a python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage
#
# if you plan to install extra packages extract the AppImage, e.g. as:
#
#   ./Videomass*.AppImage --appimage-extract
#   export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container
#
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Update: Sept.15.2020

set -e  # stop if error

SELF="$(readlink -f -- $0)" # this file
HERE="${SELF%/*}"  # dirname

MACHINE_ARCH=$(arch)
PYVERSION="python3.8.5"
OPT="squashfs-root/opt/python3.8"
USR_SHARE="squashfs-root/usr/share"

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# Make directory for building
if [ -d "$PWD/VIDEOMASS_APPIMAGE_GTK3" ]; then
    cd "$PWD/VIDEOMASS_APPIMAGE_GTK3"
    if [ -d squashfs-root ]; then
        echo "ERROR: another 'squashfs-root' dir exists!"
        exit 1
    fi
else
    mkdir -p -m 0775 "$PWD/VIDEOMASS_APPIMAGE_GTK3"
    cd "$PWD/VIDEOMASS_APPIMAGE_GTK3"
fi

# Download Python appimage 3.8 built for manylinux if not exist
if [ ! -f ${PYVERSION}*x86_64.AppImage ]; then
     wget -c https://github.com/niess/python-appimage/releases/download/python3.8/python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage
fi

# Extract this AppImage
if [ ! -x ${PYVERSION}*x86_64.AppImage ]; then
    chmod +x ${PYVERSION}*x86_64.AppImage
fi
./${PYVERSION}*x86_64.AppImage --appimage-extract

# Download required shared library
if [ ! -d usr ]; then

    wget -c http://security.debian.org/debian-security/pool/updates/main/libj/libjpeg-turbo/libjpeg62-turbo_1.5.1-2+deb9u1_amd64.deb \
        http://ftp.de.debian.org/debian/pool/main/j/jbigkit/libjbig0_2.1-3.1+b2_amd64.deb

    # extract data from .deb files
    ar -x libjpeg62-turbo_1.5.1-2+deb9u1_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libjbig0_2.1-3.1+b2_amd64.deb data.tar.xz && tar -xf data.tar.xz
fi

# copy shared libraries
cp -r usr/ squashfs-root/

# update pip
./squashfs-root/AppRun -m pip install -U pip

# installing wxPython4.1 binary wheel
if [ -f wxPython-4.1.0-cp38-cp38-linux_x86_64.whl ]; then
    ./squashfs-root/AppRun -m pip install wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
else
    ./squashfs-root/AppRun -m pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl \
        wxPython
    fi

# Install videomass and its dependencies, PyPubSub, youtube_dl
if [ -f videomass-*.whl ]; then
    ./squashfs-root/AppRun -m pip install videomass-*.whl
else
    ./squashfs-root/AppRun -m pip install videomass
fi

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/videomass|g' ./squashfs-root/AppRun
sed -i -e '/export TKPATH/a # required shared libraries to run Videomass' squashfs-root/AppRun
sed -i -e '/# required shared libraries to run Videomass/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' squashfs-root/AppRun

# set new metainfo
cat <<EOF > $USR_SHARE/metainfo/$PYVERSION.appdata.xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
    <id>videomass</id>
    <metadata_license>MIT</metadata_license>
    <project_license>Python-2.0</project_license>
    <name>Videomass</name>
    <summary>A Python 3.8 runtime with videomass, PyPubSub and wxPython GUI toolkit</summary>
    <description>
        <p>  A relocated Python 3.8 installation containing
             the videomass packages suite (videomass, PyPubSub and wxPython)
             and running from an AppImage.
        </p>
    </description>
    <launchable type="desktop-id">videomass.desktop</launchable>
    <url type="homepage">http://jeanslack.github.io/Videomass</url>
    <provides>
        <binary>python3.8</binary>
    </provides>
</component>
EOF

# Edit the desktop file
mv $USR_SHARE/applications/$PYVERSION.desktop $USR_SHARE/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' $USR_SHARE/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' $USR_SHARE/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf $USR_SHARE/icons/hicolor/256x256
rm squashfs-root/python.png squashfs-root/*.desktop

# Add the new icon
mkdir -p $USR_SHARE/icons/hicolor/128x128/apps/
cp $OPT/share/pixmaps/videomass.png $USR_SHARE/icons/hicolor/128x128/apps/videomass.png

# make simlink
cd squashfs-root
ln -s usr/share/icons/hicolor/128x128/apps/videomass.png videomass.png
ln -s usr/share/applications/videomass.desktop videomass.desktop
cd ..

# retrieve the Videomass version from the package metadata
export VERSION=$(cat $OPT/lib/python3.8/site-packages/videomass-*.dist-info/METADATA | grep "^Version:.*" | cut -d " " -f 2)

# check appimagetool
if [ ! -f appimagetool-x86_64.AppImage ]; then
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
fi

if [ ! -x appimagetool-x86_64.AppImage ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

# for any updates, copy 'appimagetool' and 'youtube_dl_update_appimage.sh' script on bin/
cp appimagetool-x86_64.AppImage "$HERE/youtube_dl_update_appimage.sh" squashfs-root/usr/bin

if [ ! -x squashfs-root/usr/bin/youtube_dl_update_appimage.sh ]; then
    chmod +x squashfs-root/usr/bin/youtube_dl_update_appimage.sh
fi

# Convert back into an AppImage
./appimagetool-x86_64.AppImage -s squashfs-root/
